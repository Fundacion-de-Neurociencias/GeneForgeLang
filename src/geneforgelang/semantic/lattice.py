"""
Epistemic Product Lattice

This module formally defines the EpistemicState as a multidimensional product lattice.
Instead of compressing biological evidence validity into a single linear enum (e.g., SUPPORTED -> INVALIDATED),
we separate the ontological dimensions. This permits non-destructive conflict resolution,
dimension-specific degradation (e.g., losing temporal stability without losing truth support),
and formal mathematical comparisons via partial ordering (dominance, meet, join).
"""

from dataclasses import dataclass
from enum import Enum


class TruthSupport(Enum):
    SUPPORTED = 2
    UNSUPPORTED = 1
    CONTRADICTED = 0


class TemporalStability(Enum):
    STABLE = 2
    UNSTABLE = 1
    INVALIDATED = 0


class ObservationalResolution(Enum):
    HIGH_RESOLUTION = 2
    LOW_RESOLUTION = 1
    UNRESOLVED = 0


class EcologicalScope(Enum):
    UNIVERSAL = 2
    RESTRICTED = 1
    ISOLATED = 0


class ContradictionLoad(Enum):
    NONE = 2
    CONTESTED = 1
    SUPERSEDED = 0


@dataclass(frozen=True)
class EpistemicState:
    """
    The formal multidimensional state of an EvidenceContract within the epistemic lattice.
    """

    truth_support: TruthSupport
    temporal_stability: TemporalStability
    observational_resolution: ObservationalResolution
    ecological_scope: EcologicalScope
    contradiction_load: ContradictionLoad

    def dominates(self, other: "EpistemicState") -> bool:
        """
        Partial ordering: self ≥ other.
        A state strictly dominates or is equal to another if it is ≥ in ALL dimensions.
        Incomparable states will return False in both directions.
        """
        return (
            self.truth_support.value >= other.truth_support.value
            and self.temporal_stability.value >= other.temporal_stability.value
            and self.observational_resolution.value >= other.observational_resolution.value
            and self.ecological_scope.value >= other.ecological_scope.value
            and self.contradiction_load.value >= other.contradiction_load.value
        )

    def is_incomparable(self, other: "EpistemicState") -> bool:
        """
        True if neither state strictly dominates the other (e.g., one has higher resolution but lower ecological scope).
        """
        return not self.dominates(other) and not other.dominates(self)

    def meet(self, other: "EpistemicState") -> "EpistemicState":
        """
        Infimum (Greatest Lower Bound).
        Represents the most optimistic state that is logically subsumed by BOTH states.
        Useful for conflict intersection or conservative constraint propagation.
        """
        return EpistemicState(
            TruthSupport(min(self.truth_support.value, other.truth_support.value)),
            TemporalStability(min(self.temporal_stability.value, other.temporal_stability.value)),
            ObservationalResolution(min(self.observational_resolution.value, other.observational_resolution.value)),
            EcologicalScope(min(self.ecological_scope.value, other.ecological_scope.value)),
            ContradictionLoad(min(self.contradiction_load.value, other.contradiction_load.value)),
        )

    def join(self, other: "EpistemicState") -> "EpistemicState":
        """
        Supremum (Least Upper Bound).
        Represents the most pessimistic state that subsumes BOTH states.
        Useful for consilience aggregation.
        """
        return EpistemicState(
            TruthSupport(max(self.truth_support.value, other.truth_support.value)),
            TemporalStability(max(self.temporal_stability.value, other.temporal_stability.value)),
            ObservationalResolution(max(self.observational_resolution.value, other.observational_resolution.value)),
            EcologicalScope(max(self.ecological_scope.value, other.ecological_scope.value)),
            ContradictionLoad(max(self.contradiction_load.value, other.contradiction_load.value)),
        )

    @classmethod
    def get_ideal_state(cls) -> "EpistemicState":
        """The absolute top of the lattice."""
        return cls(
            TruthSupport.SUPPORTED,
            TemporalStability.STABLE,
            ObservationalResolution.HIGH_RESOLUTION,
            EcologicalScope.UNIVERSAL,
            ContradictionLoad.NONE,
        )

    @classmethod
    def get_null_state(cls) -> "EpistemicState":
        """The absolute bottom of the lattice."""
        return cls(
            TruthSupport.CONTRADICTED,
            TemporalStability.INVALIDATED,
            ObservationalResolution.UNRESOLVED,
            EcologicalScope.ISOLATED,
            ContradictionLoad.SUPERSEDED,
        )
