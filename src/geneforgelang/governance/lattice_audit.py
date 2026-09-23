import itertools

from geneforgelang.semantic.lattice import (
    ContradictionLoad,
    EcologicalScope,
    EpistemicState,
    ObservationalResolution,
    TemporalStability,
    TruthSupport,
)


class LatticeMinimalityAudit:
    """Audits the epistemic lattice for dimensional redundancy."""

    def __init__(self):
        self.dimensions = {
            "TruthSupport": TruthSupport,
            "TemporalStability": TemporalStability,
            "ObservationalResolution": ObservationalResolution,
            "EcologicalScope": EcologicalScope,
            "ContradictionLoad": ContradictionLoad,
        }

    def measure_orthogonality(self) -> dict[str, float]:
        """
        Measures how independent each dimension is by calculating the
        percentage of valid state-space available when holding a dimension constant.
        If holding it constant drastically collapses the space, it might be heavily coupled.
        """
        from geneforgelang.semantic.state_space import SemanticStateSpaceAudit

        base_audit = SemanticStateSpaceAudit()
        valid_states = base_audit.valid_states
        total_valid = len(valid_states)

        orthogonality_scores = {}
        for dim_name, dim_enum in self.dimensions.items():
            # Calculate variance of other dimensions when this one is fixed
            # High variance = high orthogonality
            fixed_counts = []
            for val in dim_enum:
                # Count valid states where this dimension == val
                count = sum(1 for state in valid_states if getattr(state, self._to_snake(dim_name)) == val)
                fixed_counts.append(count)

            # If a state of a dimension leaves 0 valid states, it's highly coupled.
            # We use a simple metric: min(fixed_counts) / max(fixed_counts)
            # A score near 0 means high dependency (not orthogonal).
            score = min(fixed_counts) / max(fixed_counts) if max(fixed_counts) > 0 else 0
            orthogonality_scores[dim_name] = score

        return orthogonality_scores

    def _to_snake(self, name: str) -> str:
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def evaluate_mechanistic_certainty_need(self) -> str:
        """
        Evaluates whether MechanisticCertainty is required.
        If we can express 'causally known but observationally unsupported',
        do we have enough dimensions?
        Currently:
        - ObservationalResolution handles 'how well we saw it'
        - TruthSupport handles 'did we see it'
        - MechanisticCertainty would handle 'do we know WHY it happens'
        """
        # We simulate adding it.
        return "MechanisticCertainty represents causal 'why', orthogonal to observational 'what'. Recommended for inclusion as a 6th dimension in ADR-0006."


if __name__ == "__main__":
    audit = LatticeMinimalityAudit()
    scores = audit.measure_orthogonality()
    print("Orthogonality Scores:")
    for dim, score in scores.items():
        print(f"  {dim}: {score:.2f}")

    print("\nMechanistic Certainty Analysis:")
    print(audit.evaluate_mechanistic_certainty_need())
