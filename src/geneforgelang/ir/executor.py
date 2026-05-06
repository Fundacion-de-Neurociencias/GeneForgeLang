from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from geneforgelang.ir.instruction import Instruction
from geneforgelang.ir.state import BiologicalState
from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.strategy import Objective, PlanGraph, PlanNode, Strategy


class ExecutionError(Exception):
    pass


@dataclass
class StepRecord:
    instruction: Instruction
    state_before: BiologicalState
    state_after: BiologicalState
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTrace:
    initial_state: BiologicalState
    records: list[StepRecord] = field(default_factory=list)

    def add(self, record: StepRecord) -> None:
        self.records.append(record)

    def final_state(self) -> BiologicalState:
        if not self.records:
            return self.initial_state
        return self.records[-1].state_after


def apply(state: BiologicalState, instruction: Instruction) -> BiologicalState:
    """Apply a single instruction to a state, returning a new state."""
    return instruction.apply(state)


class StrategyExecutor:
    def __init__(self, strategy: Strategy, evaluator: Optional[StateEvaluator] = None):
        self.strategy = strategy
        self.trace: Optional[StateTrace] = None
        self.evaluator = evaluator or StateEvaluator()

    def execute(self, initial_state: BiologicalState) -> StateTrace:
        state = initial_state.fork()
        trace = StateTrace(initial_state=initial_state.fork())
        self.trace = trace

        for idx, step in enumerate(self.strategy.steps):
            state_before = state
            try:
                state = apply(state, step)
            except Exception as exc:
                raise ExecutionError(f"Step {idx} failed ({step}): {exc}") from exc
            trace.add(
                StepRecord(
                    instruction=step,
                    state_before=state_before,
                    state_after=state,
                    metadata={"step_index": idx},
                )
            )

        return trace

    def evaluate_progress(self, state: BiologicalState) -> float:
        """Return a score in [0, 1] measuring progress toward the strategy objective."""
        score: float = self.evaluator.evaluate(state, self.strategy.objective)
        return score

    def get_trace(self) -> Optional[StateTrace]:
        return self.trace


class GraphExecutor:
    """Execute a conditional PlanGraph by traversing nodes and evaluating conditions."""

    def __init__(self, plan: PlanGraph, evaluator: Optional[StateEvaluator] = None):
        self.plan = plan
        self.trace = StateTrace(initial_state=BiologicalState())
        self.evaluator = evaluator or StateEvaluator()

    def execute(self, initial_state: BiologicalState) -> StateTrace:
        state = initial_state.fork()
        self.trace = StateTrace(initial_state=initial_state.fork())
        self._traverse(self.plan.root, state, depth=0)
        return self.trace

    def _traverse(self, node: PlanNode, state: BiologicalState, depth: int) -> None:
        if node is None:
            return

        # Evaluate condition if present
        if node.condition is not None:
            if not self._eval_condition(node.condition, state):
                return

        # Execute action if present
        if node.action is not None:
            state_before = state
            state = apply(state, node.action)
            self.trace.add(
                StepRecord(
                    instruction=node.action,
                    state_before=state_before,
                    state_after=state,
                    metadata={"depth": depth, "condition": node.condition},
                )
            )

        # Recurse into next nodes
        for child in node.next_nodes:
            self._traverse(child, state, depth=depth + 1)

    def _eval_condition(self, condition: str, state: BiologicalState) -> bool:
        # Robust condition evaluator using regex patterns.
        # Supports:  entity.status == "knocked_out" (with optional spaces)
        #            score > 0.5, score >= 0.5
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Score-based conditions: "score > 0.5" or "score >= 0.5"
            score_match = re.match(r"score\s*([>=]+)\s*(\d+(?:\.\d+)?)", condition.strip())
            if score_match:
                op = score_match.group(1)
                threshold = float(score_match.group(2))
                score: float = self.evaluator.evaluate(state, self.plan.objective)
                if op == ">=":
                    result: bool = score >= threshold
                elif op == ">":
                    result = score > threshold
                else:
                    logger.warning(f"Unknown operator in condition: {condition}")
                    return False
                return result

            # Entity attribute checks: "TP53.status == knocked_out" (flexible spacing/quotes)
            attr_match = re.match(
                r"(\w+)\.status\s*==\s*['\"]?(\w+)['\"]?", condition.strip()
            )
            if attr_match:
                eid = attr_match.group(1)
                val = attr_match.group(2)
                ent = state.get_entity(eid)
                return ent is not None and ent.get_attr("status") == val

            return True  # default pass-through for unknown conditions
        except (ValueError, TypeError, AttributeError) as exc:
            logger.debug(f"Condition evaluation failed: {condition} - {exc}")
            return False
