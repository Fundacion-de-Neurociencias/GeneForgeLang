from datetime import datetime, timedelta

import pytest
from geneforgelang.semantic.evidence.contract import (
    CompressibilityProfile,
    ContradictionState,
    EvidenceContract,
    InvalidationDependency,
    ObservabilityProfile,
    Provenance,
    ScaleAnchor,
    TemporalValidity,
)


def test_high_compressibility_low_identifiability():
    # Alta compresibilidad lossless + baja identifiability extrema.
    obs = ObservabilityProfile(
        reachability=1.0, visibility=1.0, accessibility=1.0, identifiability=0.05, resolution="high"
    )
    comp = CompressibilityProfile(algorithmic_complexity=0.1, information_gain=0.9, lossless=True)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    temp = TemporalValidity(
        valid_from=datetime.now(), valid_until=None, stability_expectation=1.0, decay_model="stable"
    )

    with pytest.raises(
        ValueError, match="Incoherent semantics: Lossless high compressibility requires high identifiability"
    ):
        EvidenceContract(
            contract_id="1",
            claim="test",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=0.1,
            provenance=prov,
            invalidation_dependencies=dep,
        )


def test_low_observability_high_information_gain():
    obs = ObservabilityProfile(0.1, 0.1, 0.1, 0.1, "low")
    comp = CompressibilityProfile(0.5, 0.95, False)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    temp = TemporalValidity(datetime.now(), None, 1.0, "stable")

    with pytest.raises(
        ValueError, match="Incoherent semantics: Extremely low observability cannot yield massive information gain"
    ):
        EvidenceContract(
            contract_id="1",
            claim="test",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=0.1,
            provenance=prov,
            invalidation_dependencies=dep,
        )


def test_no_resolution_lossless():
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "none")
    comp = CompressibilityProfile(0.5, 0.5, True)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    temp = TemporalValidity(datetime.now(), None, 1.0, "stable")

    with pytest.raises(ValueError, match="Incoherent semantics: Lossless compression requires non-null resolution"):
        EvidenceContract(
            contract_id="1",
            claim="test",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=0.1,
            provenance=prov,
            invalidation_dependencies=dep,
        )
