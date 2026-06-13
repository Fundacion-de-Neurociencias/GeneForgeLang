from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any, cast


class BiologicalScale(str, Enum):
    VARIANT = "variant"
    GENE = "gene"
    TRANSCRIPT = "transcript"
    PROTEIN = "protein"
    DOMAIN = "domain"
    PATHWAY = "pathway"
    CELL = "cell"
    TISSUE = "tissue"
    PHENOTYPE = "phenotype"
    DISEASE = "disease"


class RelationType(str, Enum):
    BINDS = "binds"
    INTERACTS_WITH = "interacts_with"
    FORMS_COMPLEX = "forms_complex"
    ACTIVATES = "activates"
    INHIBITS = "inhibits"
    ENCODES = "encodes"
    TRANSCRIBES_TO = "transcribes_to"
    TRANSLATES_TO = "translates_to"
    PARTICIPATES_IN = "participates_in"
    MODULATES = "modulates"
    ASSOCIATED_WITH = "associated_with"
    PERTURBS = "perturbs"
    CONSTRAINS = "constrains"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INFERS = "infers"
    COMPILES_TO = "compiles_to"


@dataclass(frozen=True)
class BiologicalEvidence:
    id: str
    claim: str
    source: str
    confidence: float
    method: str = "unspecified"
    counter_evidence: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_probability(self.confidence, "evidence confidence")


@dataclass(frozen=True)
class BiologicalEntity:
    id: str
    label: str
    scale: BiologicalScale
    namespace: str = "gfl"
    identifiers: dict[str, str] = field(default_factory=dict)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BiologicalRelation:
    id: str
    source: str
    target: str
    relation: RelationType
    confidence: float
    evidence: tuple[str, ...] = ()
    uncertainty: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_probability(self.confidence, "relation confidence")
        _validate_probability(self.uncertainty, "relation uncertainty")


@dataclass(frozen=True)
class BiologicalConstraint:
    id: str
    claim: str
    scope: tuple[str, ...]
    scale: BiologicalScale | None = None
    confidence: float = 1.0
    evidence: tuple[str, ...] = ()
    hard: bool = False

    def __post_init__(self) -> None:
        _validate_probability(self.confidence, "constraint confidence")


@dataclass(frozen=True)
class BiologicalHypothesis:
    id: str
    claim: str
    confidence: float
    evidence: tuple[str, ...] = ()
    counter_evidence: tuple[str, ...] = ()
    inferred_entities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_probability(self.confidence, "hypothesis confidence")


@dataclass(frozen=True)
class BiologicalPerturbation:
    id: str
    target: str
    perturbation_type: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[str, ...] = ()


@dataclass
class EvidenceGraph:
    nodes: list[BiologicalEntity] = field(default_factory=list)
    edges: list[BiologicalRelation] = field(default_factory=list)
    evidence: list[BiologicalEvidence] = field(default_factory=list)
    constraints: list[BiologicalConstraint] = field(default_factory=list)
    hypotheses: list[BiologicalHypothesis] = field(default_factory=list)
    perturbations: list[BiologicalPerturbation] = field(default_factory=list)
    uncertainty: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_evidence_first_claim(
        self,
        *,
        claim: str,
        confidence: float,
        evidence: tuple[str, ...],
        counter_evidence: tuple[str, ...] = (),
        inferred_entities: tuple[str, ...] = (),
        hypothesis_id: str | None = None,
    ) -> BiologicalHypothesis:
        hypothesis = BiologicalHypothesis(
            id=hypothesis_id or _stable_id("hypothesis", claim),
            claim=claim,
            confidence=confidence,
            evidence=evidence,
            counter_evidence=counter_evidence,
            inferred_entities=inferred_entities,
        )
        self.hypotheses.append(hypothesis)
        self.uncertainty[hypothesis.id] = round(1.0 - confidence, 6)
        return hypothesis

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "gfl.eig.v1",
            "kind": "EvidenceGraph",
            "nodes": [_serialize(item) for item in self.nodes],
            "edges": [_serialize(item) for item in self.edges],
            "evidence": [_serialize(item) for item in self.evidence],
            "constraints": [_serialize(item) for item in self.constraints],
            "hypotheses": [_serialize(item) for item in self.hypotheses],
            "perturbations": [_serialize(item) for item in self.perturbations],
            "uncertainty": self.uncertainty,
            "metadata": self.metadata,
        }


def _stable_id(prefix: str, value: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    return f"{prefix}:{normalized[:80] or 'unknown'}"


def _serialize(item: object) -> dict[str, Any]:
    if not is_dataclass(item) or isinstance(item, type):
        raise TypeError("expected dataclass instance")
    data = cast(dict[str, Any], asdict(cast(Any, item)))
    for key, value in tuple(data.items()):
        if isinstance(value, Enum):
            data[key] = value.value
    data["semantic_type"] = type(item).__name__
    return data


def _validate_probability(value: float, label: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be in [0, 1]")
