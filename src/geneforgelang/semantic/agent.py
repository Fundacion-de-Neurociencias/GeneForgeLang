from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from geneforgelang.semantic.provenance import EpistemicSnapshot, ProvenanceGraph


@dataclass(frozen=True)
class AgentAction:
    name: str
    target: str
    reversible: bool = True
    deterministic: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticCheckpoint:
    id: str
    state: Any
    snapshot: EpistemicSnapshot


@dataclass
class AgentExecutionLayer:
    provenance: ProvenanceGraph
    checkpoints: list[SemanticCheckpoint] = field(default_factory=list)

    def checkpoint(self, state: Any, belief_ids: tuple[str, ...]) -> SemanticCheckpoint:
        state_copy = state.fork() if callable(getattr(state, "fork", None)) else deepcopy(state)
        checkpoint = SemanticCheckpoint(
            id=f"checkpoint:{uuid4()}",
            state=state_copy,
            snapshot=EpistemicSnapshot.capture(belief_ids, self.provenance),
        )
        self.checkpoints.append(checkpoint)
        return checkpoint

    def validate_action(self, action: AgentAction) -> None:
        if not action.deterministic:
            raise ValueError("agent-facing actions must declare deterministic execution")
        if not action.reversible:
            raise ValueError("agent-facing actions must be reversible or checkpointed externally")
