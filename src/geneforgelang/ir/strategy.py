from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from geneforgelang.ir.instruction import Instruction


@dataclass
class Constraint:
    expression: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Objective:
    description: str
    target_entity: str = ""
    desired_outcome: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Strategy:
    objective: Objective
    constraints: List[Constraint] = field(default_factory=list)
    steps: List[Instruction] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": {
                "description": self.objective.description,
                "target_entity": self.objective.target_entity,
                "desired_outcome": self.objective.desired_outcome,
            },
            "constraints": [c.expression for c in self.constraints],
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class PlanNode:
    """A node in a conditional plan graph.

    If *condition* evaluates to True the *action* is executed and traversal
    continues to *next_nodes*.  If the condition is None the action is
    unconditional.
    """

    condition: Optional[str] = None
    action: Optional[Any] = None  # Instruction or None for pure decision nodes
    next_nodes: List["PlanNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_decision(self) -> bool:
        return self.condition is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition": self.condition,
            "action": self.action.to_dict() if self.action else None,
            "next_nodes": [n.to_dict() for n in self.next_nodes],
            "metadata": self.metadata,
        }


class PlanGraph:
    """A directed graph of PlanNodes that represents a branching strategy."""

    def __init__(self, objective: Objective, root: PlanNode):
        self.objective = objective
        self.root = root

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": {
                "description": self.objective.description,
                "target_entity": self.objective.target_entity,
                "desired_outcome": self.objective.desired_outcome,
            },
            "root": self.root.to_dict(),
        }
