from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from geneforgelang.ir.executor import ExecutionError, StateTrace, StrategyExecutor
from geneforgelang.ir.state import BiologicalState
from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.strategy import Objective, Strategy


class PlannerBackend:
    """Abstract interface for a planner that can revise its plan given feedback."""

    def plan(
        self,
        state: BiologicalState,
        objective: Objective,
        previous_attempts: List[Tuple[StateTrace, float]],
    ) -> Strategy:
        raise NotImplementedError


class MockPlannerBackend(PlannerBackend):
    """A mock planner that returns hard-coded strategies.

    In production this would be an LLM prompt with chain-of-thought and
    retrieval-augmented context.
    """

    def plan(
        self,
        state: BiologicalState,
        objective: Objective,
        previous_attempts: List[Tuple[StateTrace, float]],
    ) -> Strategy:
        from geneforgelang.ir.instruction import Substitute, Delete

        target = objective.target_entity or "TP53"
        entity = state.get_entity(target)
        if entity is None:
            return Strategy(objective=objective)

        # If previous attempts failed (low score), try more aggressive edits.
        if previous_attempts:
            best_score = max((sc for _, sc in previous_attempts), default=0.0)
            if best_score < 0.3:
                # Aggressive: large deletion
                seq = entity.get_attr("sequence", "")
                if len(seq) > 3:
                    return Strategy(
                        objective=objective,
                        steps=[
                            Delete(
                                gene_id=target,
                                start=0,
                                end=min(3, len(seq)),
                            )
                        ],
                    )
            if best_score < 0.6:
                # Moderate: damaging substitution
                seq = entity.get_attr("sequence", "")
                if len(seq) >= 2:
                    return Strategy(
                        objective=objective,
                        steps=[
                            Substitute(
                                gene_id=target,
                                position=1,
                                ref=seq[1],
                                alt="N",
                            )
                        ],
                    )

        # Default: gentle substitution
        seq = entity.get_attr("sequence", "")
        if seq:
            return Strategy(
                objective=objective,
                steps=[
                    Substitute(
                        gene_id=target,
                        position=0,
                        ref=seq[0],
                        alt="N",
                    )
                ],
            )
        return Strategy(objective=objective)


@dataclass
class ReasoningResult:
    trace: Optional[StateTrace]
    score: float
    iterations: int
    attempts: List[Tuple[StateTrace, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReasoningLoop:
    """Plan → execute → evaluate → revise loop.

    This is the minimal architecture for *thinking* in GFL.  Without this loop
    the LLM planner is a one-shot generator; with it the system can adapt.
    """

    def __init__(
        self,
        planner: PlannerBackend,
        evaluator: StateEvaluator,
        max_iterations: int = 5,
        score_threshold: float = 0.95,
    ):
        self.planner = planner
        self.evaluator = evaluator
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold

    def run(
        self,
        initial_state: BiologicalState,
        objective: Objective,
    ) -> ReasoningResult:
        state = initial_state.fork()
        attempts: List[Tuple[StateTrace, float]] = []
        best_trace: Optional[StateTrace] = None
        best_score = -1.0

        for iteration in range(1, self.max_iterations + 1):
            strategy = self.planner.plan(state, objective, attempts)
            executor = StrategyExecutor(strategy)

            try:
                trace = executor.execute(state)
            except ExecutionError as exc:
                # Record failure with score 0 and continue revising.
                attempts.append((None, 0.0))
                continue

            score = self.evaluator.evaluate(trace.final_state(), objective)
            attempts.append((trace, score))

            if score > best_score:
                best_score = score
                best_trace = trace
                state = trace.final_state()

            if score >= self.score_threshold:
                break

        return ReasoningResult(
            trace=best_trace,
            score=best_score,
            iterations=len(attempts),
            attempts=attempts,
            metadata={"threshold": self.score_threshold},
        )
