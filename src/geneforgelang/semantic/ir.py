from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any


class BiologicalScale:
    PHENOTYPE = "phenotype"
    PATHWAY = "pathway"
    PROTEIN_INTERACTION = "protein_interaction"
    TRANSCRIPT = "transcript"
    GENOMIC_LOCI = "genomic_loci"
    SEQUENCE_CONSTRAINTS = "sequence_constraints"


class UncertaintyKind:
    ALEATORIC = "aleatoric"
    EPISTEMIC = "epistemic"
    STRUCTURAL = "structural"
    OBSERVABILITY = "observability"
    CAUSAL = "causal"
    SCALE = "scale"


@dataclass(frozen=True)
class EvidenceNode:
    id: str
    source: str
    claim: str
    score: float | None = None
    method: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UncertaintyNode:
    id: str
    value: float
    kind: str
    sources: tuple[str, ...] = ()
    method: str = "unspecified"

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 1:
            raise ValueError("uncertainty value must be in [0, 1]")


@dataclass(frozen=True)
class ObservationNode:
    id: str
    target: str
    status: str
    resolution: str | None = None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class InferenceNode:
    id: str
    conclusion: str
    premises: tuple[str, ...] = ()
    uncertainty: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConstraintNode:
    id: str
    expression: str
    scale: str | None = None
    hard: bool = False


@dataclass(frozen=True)
class InvalidationNode:
    id: str
    target: str
    reason: str
    triggered_by: str | None = None


@dataclass(frozen=True)
class HypothesisNode:
    id: str
    statement: str
    confidence: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class LatentHypothesisNode(HypothesisNode):
    embedding_source: str = "unspecified"
    latent_region: str | None = None


@dataclass(frozen=True)
class PhenotypeNode:
    id: str
    label: str
    traits: dict[str, Any] = field(default_factory=dict)
    scale: str = BiologicalScale.PHENOTYPE


@dataclass(frozen=True)
class PerturbationNode:
    id: str
    target: str
    perturbation_type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    uncertainty: str | None = None


@dataclass(frozen=True)
class RegulationNode:
    id: str
    regulator: str
    target: str
    direction: str
    mechanism: str | None = None


@dataclass(frozen=True)
class CausalityEdge:
    source: str
    target: str
    relation: str = "causes"
    confidence: float | None = None
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class TrajectoryNode:
    id: str
    states: tuple[str, ...]
    temporal_order: tuple[int, ...] = ()


@dataclass
class SemanticDocument:
    nodes: list[object] = field(default_factory=list)
    edges: list[CausalityEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "gfl.semantic.v2",
            "nodes": [self._serialize_node(node) for node in self.nodes],
            "edges": [self._serialize_dataclass(edge) for edge in self.edges],
            "metadata": self.metadata,
        }

    @staticmethod
    def _serialize_node(node: object) -> dict[str, Any]:
        data = SemanticDocument._serialize_dataclass(node) if is_dataclass(node) else {"value": node}
        data["node_type"] = type(node).__name__
        return data

    @staticmethod
    def _serialize_dataclass(node: object) -> dict[str, Any]:
        if not is_dataclass(node) or isinstance(node, type):
            raise TypeError("expected a dataclass instance")
        return {item.name: getattr(node, item.name) for item in fields(node)}
