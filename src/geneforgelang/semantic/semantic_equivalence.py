from __future__ import annotations

from dataclasses import dataclass

from geneforgelang.semantic.lattice import EpistemicState


@dataclass(frozen=True)
class CanonicalSemanticState:
    """Canonical representation of an epistemic product-lattice state."""

    truth_support: str
    temporal_stability: str
    observational_resolution: str
    ecological_scope: str
    contradiction_load: str

    def as_tuple(self) -> tuple[str, str, str, str, str]:
        return (
            self.truth_support,
            self.temporal_stability,
            self.observational_resolution,
            self.ecological_scope,
            self.contradiction_load,
        )


def canonicalize_state(state: EpistemicState) -> CanonicalSemanticState:
    """Canonicalize without quotienting any semantic lattice dimension."""

    return CanonicalSemanticState(
        truth_support=state.truth_support.name,
        temporal_stability=state.temporal_stability.name,
        observational_resolution=state.observational_resolution.name,
        ecological_scope=state.ecological_scope.name,
        contradiction_load=state.contradiction_load.name,
    )


def semantic_equivalent(left: EpistemicState, right: EpistemicState) -> bool:
    """Define legitimate collapse under the current lattice semantics.

    Phase 5.6 intentionally admits no non-trivial quotient relation: distinct
    product-lattice coordinates remain distinct unless every semantic dimension
    is identical. Any future relaxation must be explicit and tested here first.
    """

    return canonicalize_state(left) == canonicalize_state(right)


def canonical_key(state: EpistemicState) -> tuple[str, str, str, str, str]:
    """Return the stable key used by representational stress audits."""

    return canonicalize_state(state).as_tuple()
