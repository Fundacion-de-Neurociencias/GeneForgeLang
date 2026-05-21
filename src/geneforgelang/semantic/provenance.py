from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class KnowledgeValidityWindow:
    valid_from: datetime
    valid_until: datetime | None = None
    asserted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_active(self, at: datetime | None = None) -> bool:
        point = at or datetime.now(timezone.utc)
        return self.valid_from <= point and (self.valid_until is None or point < self.valid_until)


@dataclass(frozen=True)
class ProvenanceNode:
    id: str
    kind: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)
    validity: KnowledgeValidityWindow | None = None


@dataclass(frozen=True)
class ProvenanceEdge:
    source: str
    target: str
    relation: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceGraph:
    nodes: dict[str, ProvenanceNode] = field(default_factory=dict)
    edges: list[ProvenanceEdge] = field(default_factory=list)

    def add_node(self, node: ProvenanceNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: ProvenanceEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("provenance edge endpoints must exist")
        self.edges.append(edge)

    def record_inference(
        self,
        claim: str,
        sources: tuple[str, ...],
        engine_name: str,
        engine_version: str,
        confidence: float,
    ) -> str:
        inference_id = f"inference:{uuid4()}"
        self.add_node(
            ProvenanceNode(
                id=inference_id,
                kind="inference",
                label=claim,
                metadata={
                    "engine_name": engine_name,
                    "engine_version": engine_version,
                    "confidence": confidence,
                },
                validity=KnowledgeValidityWindow(valid_from=datetime.now(timezone.utc)),
            )
        )
        for source in sources:
            if source not in self.nodes:
                self.add_node(ProvenanceNode(id=source, kind="evidence_source", label=source))
            self.add_edge(ProvenanceEdge(source=source, target=inference_id, relation="supports"))
        return inference_id

    def downstream_of(self, node_id: str) -> tuple[str, ...]:
        seen: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge.source == current and edge.target not in seen:
                    seen.add(edge.target)
                    frontier.append(edge.target)
        return tuple(seen)


@dataclass(frozen=True)
class EpistemicSnapshot:
    id: str
    captured_at: datetime
    belief_ids: tuple[str, ...]
    provenance_node_ids: tuple[str, ...]

    @classmethod
    def capture(cls, belief_ids: tuple[str, ...], provenance: ProvenanceGraph) -> EpistemicSnapshot:
        return cls(
            id=f"snapshot:{uuid4()}",
            captured_at=datetime.now(timezone.utc),
            belief_ids=belief_ids,
            provenance_node_ids=tuple(provenance.nodes),
        )
