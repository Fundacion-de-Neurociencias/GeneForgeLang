"""
Evidence Contract Fabric

This module defines the foundational EvidenceContract, an epistemological primitive
in GeneForgeLang. It provides the formal semantics for converting any external
observation (from biomolecular APIs, papers, synthetic reasoning) into an auditable,
computationally actionable contract.

All contracts must specify their observability profile, compressibility, temporal
validity, contradiction state, and scale anchor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class ContradictionState(Enum):
    SUPPORTED = "SUPPORTED"
    CONTESTED = "CONTESTED"
    CONDITIONALLY_VALID = "CONDITIONALLY_VALID"
    INVALIDATED = "INVALIDATED"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"


class ScaleAnchor(Enum):
    SEQUENCE = "SEQUENCE"
    TRANSCRIPT = "TRANSCRIPT"
    PROTEIN = "PROTEIN"
    PATHWAY = "PATHWAY"
    PHENOTYPE = "PHENOTYPE"
    POPULATION = "POPULATION"


class ContractStateTransitionMatrix:
    """
    Formal DFA for semantic state transitions of an EvidenceContract.
    """

    _valid_transitions = {
        (ContradictionState.SUPPORTED, ContradictionState.CONTESTED, "conflict_detected"),
        (ContradictionState.SUPPORTED, ContradictionState.INVALIDATED, "invalidation_propagation"),
        (ContradictionState.SUPPORTED, ContradictionState.SUPERSEDED, "supersession"),
        (ContradictionState.SUPPORTED, ContradictionState.RETRACTED, "source_mutation"),
        (ContradictionState.CONTESTED, ContradictionState.SUPPORTED, "conflict_resolved"),
        (ContradictionState.CONTESTED, ContradictionState.INVALIDATED, "invalidation_propagation"),
        (ContradictionState.CONTESTED, ContradictionState.RETRACTED, "source_mutation"),
        (ContradictionState.CONDITIONALLY_VALID, ContradictionState.SUPPORTED, "conditions_proven"),
        (ContradictionState.CONDITIONALLY_VALID, ContradictionState.INVALIDATED, "conditions_failed"),
        (ContradictionState.CONDITIONALLY_VALID, ContradictionState.RETRACTED, "source_mutation"),
        (ContradictionState.SUPERSEDED, ContradictionState.RETRACTED, "source_mutation"),
        (ContradictionState.INVALIDATED, ContradictionState.RETRACTED, "source_mutation"),
        # Restoration requires an entirely new provenance lineage
        (ContradictionState.RETRACTED, ContradictionState.SUPPORTED, "new_provenance_lineage"),
        (ContradictionState.INVALIDATED, ContradictionState.SUPPORTED, "new_provenance_lineage"),
    }

    @classmethod
    def is_valid_transition(cls, from_state: ContradictionState, to_state: ContradictionState, trigger: str) -> bool:
        return (from_state, to_state, trigger) in cls._valid_transitions


@dataclass(frozen=True)
class ObservabilityProfile:
    reachability: float
    visibility: float
    accessibility: float
    identifiability: float
    resolution: str

    def __post_init__(self):
        for attr in ["reachability", "visibility", "accessibility", "identifiability"]:
            val = getattr(self, attr)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"ObservabilityProfile.{attr} must be in range [0.0, 1.0]")


@dataclass(frozen=True)
class CompressibilityProfile:
    algorithmic_complexity: float
    information_gain: float
    lossless: bool


@dataclass(frozen=True)
class TemporalValidity:
    valid_from: datetime
    valid_until: Optional[datetime]
    stability_expectation: float
    decay_model: str

    def __post_init__(self):
        if self.valid_until and self.valid_from > self.valid_until:
            raise ValueError("Temporal validity window is logically inverted: valid_from > valid_until")
        if not (0.0 <= self.stability_expectation <= 1.0):
            raise ValueError("stability_expectation must be a probability in range [0.0, 1.0]")


@dataclass(frozen=True)
class Provenance:
    source_system: str
    source_id: str
    extraction_timestamp: datetime
    extraction_assumptions: list[str]


@dataclass(frozen=True)
class InvalidationDependency:
    upstream_contract_ids: list[str]
    invalidation_hooks: list[str]


@dataclass(frozen=True)
class EvidenceContract:
    contract_id: str
    claim: Any
    scale_anchor: ScaleAnchor
    observability: ObservabilityProfile
    compressibility: CompressibilityProfile
    temporal_validity: TemporalValidity
    contradiction_state: ContradictionState
    uncertainty: float
    provenance: Provenance
    invalidation_dependencies: InvalidationDependency

    def __post_init__(self):
        if not (0.0 <= self.uncertainty <= 1.0):
            raise ValueError("EvidenceContract.uncertainty must be in range [0.0, 1.0]")

        # Temporal logic validation
        if self.contradiction_state == ContradictionState.SUPPORTED and self.temporal_validity.valid_until:
            if self.temporal_validity.valid_until < datetime.now():
                raise ValueError("Evidence contract is SUPPORTED but temporal validity window has expired.")

        if self.contradiction_state in {ContradictionState.INVALIDATED, ContradictionState.RETRACTED}:
            if self.temporal_validity.valid_until is None or self.temporal_validity.valid_until > datetime.now():
                raise ValueError(
                    f"Evidence contract is {self.contradiction_state.name} but temporal validity window remains open."
                )

        # Cross-semantic contradiction validation
        if self.compressibility.lossless and self.observability.identifiability < 0.1:
            raise ValueError("Incoherent semantics: Lossless high compressibility requires high identifiability.")

        if (
            sum([self.observability.reachability, self.observability.visibility, self.observability.accessibility])
            < 0.5
            and self.compressibility.information_gain > 0.8
        ):
            raise ValueError("Incoherent semantics: Extremely low observability cannot yield massive information gain.")

        if self.compressibility.lossless and self.observability.resolution == "none":
            raise ValueError("Incoherent semantics: Lossless compression requires non-null resolution.")

        # Scale coherence check
        if self.scale_anchor == ScaleAnchor.SEQUENCE and "phenotype" in str(self.claim).lower():
            raise ValueError(
                "Scale inconsistency: Sequence anchor attached to phenotypic claim without explicit projection bridging."
            )
