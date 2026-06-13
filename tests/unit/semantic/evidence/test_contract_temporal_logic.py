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


def create_valid_profiles():
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "high")
    comp = CompressibilityProfile(0.5, 0.5, False)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    return obs, comp, prov, dep


def test_inverted_temporal_window():
    obs, comp, prov, dep = create_valid_profiles()
    with pytest.raises(ValueError, match="valid_from > valid_until"):
        TemporalValidity(
            valid_from=datetime.now(),
            valid_until=datetime.now() - timedelta(days=1),
            stability_expectation=1.0,
            decay_model="stable",
        )


def test_supported_state_expired_window():
    obs, comp, prov, dep = create_valid_profiles()
    temp = TemporalValidity(
        valid_from=datetime.now() - timedelta(days=2),
        valid_until=datetime.now() - timedelta(days=1),
        stability_expectation=1.0,
        decay_model="stable",
    )
    with pytest.raises(ValueError, match="is SUPPORTED but temporal validity window has expired"):
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


def test_invalidated_state_open_window():
    obs, comp, prov, dep = create_valid_profiles()
    temp = TemporalValidity(
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        stability_expectation=1.0,
        decay_model="stable",
    )
    with pytest.raises(ValueError, match="is INVALIDATED but temporal validity window remains open"):
        EvidenceContract(
            contract_id="1",
            claim="test",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.INVALIDATED,
            uncertainty=0.1,
            provenance=prov,
            invalidation_dependencies=dep,
        )
