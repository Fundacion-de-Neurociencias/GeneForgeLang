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


def test_scale_inconsistency():
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "high")
    comp = CompressibilityProfile(0.5, 0.5, False)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    temp = TemporalValidity(datetime.now(), None, 1.0, "stable")

    with pytest.raises(
        ValueError,
        match="Scale inconsistency: Sequence anchor attached to phenotypic claim without explicit projection bridging.",
    ):
        EvidenceContract(
            contract_id="1",
            claim="This mutation causes an aggressive phenotype",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=0.1,
            provenance=prov,
            invalidation_dependencies=dep,
        )


def test_valid_scale():
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "high")
    comp = CompressibilityProfile(0.5, 0.5, False)
    prov = Provenance("test", "1", datetime.now(), [])
    dep = InvalidationDependency([], [])
    temp = TemporalValidity(datetime.now(), None, 1.0, "stable")

    contract = EvidenceContract(
        contract_id="1",
        claim="Missense mutation A->T",
        scale_anchor=ScaleAnchor.SEQUENCE,
        observability=obs,
        compressibility=comp,
        temporal_validity=temp,
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=0.1,
        provenance=prov,
        invalidation_dependencies=dep,
    )
    assert contract.scale_anchor == ScaleAnchor.SEQUENCE
