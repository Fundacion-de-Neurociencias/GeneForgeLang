from datetime import datetime, timedelta

import pytest
from geneforgelang.semantic.evidence.algebra import ContractAlgebra
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


def create_contract(
    id: str, claim: str, uncertainty: float, date_offset: int = 0, scale: ScaleAnchor = ScaleAnchor.SEQUENCE
) -> EvidenceContract:
    return EvidenceContract(
        contract_id=id,
        claim=claim,
        scale_anchor=scale,
        observability=ObservabilityProfile(0.8, 0.8, 0.8, 0.8, "high"),
        compressibility=CompressibilityProfile(0.5, 0.5, False),
        temporal_validity=TemporalValidity(
            valid_from=datetime.now() + timedelta(days=date_offset),
            valid_until=None,
            stability_expectation=0.9,
            decay_model="stable",
        ),
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=uncertainty,
        provenance=Provenance("sys", id, datetime.now(), []),
        invalidation_dependencies=InvalidationDependency([], []),
    )


def test_compose_consilience_reduces_uncertainty():
    c1 = create_contract("1", "A->T", 0.5)
    c2 = create_contract("2", "A->T", 0.5)
    composed = ContractAlgebra.compose(c1, c2)
    assert composed.contradiction_state == ContradictionState.SUPPORTED
    assert composed.uncertainty == 0.25  # 0.5 * 0.5


def test_compose_contradiction_increases_uncertainty():
    c1 = create_contract("1", "A->T", 0.5)
    c2 = create_contract("2", "A->G", 0.4)
    composed = ContractAlgebra.compose(c1, c2)
    assert composed.contradiction_state == ContradictionState.CONTESTED
    assert composed.uncertainty > 0.5


def test_compose_different_scales_fails():
    c1 = create_contract("1", "A->T", 0.5, scale=ScaleAnchor.SEQUENCE)
    c2 = create_contract("2", "A->T", 0.5, scale=ScaleAnchor.PROTEIN)
    with pytest.raises(ValueError, match="Cannot compose contracts across different scale anchors"):
        ContractAlgebra.compose(c1, c2)


def test_supersede_chronology():
    older = create_contract("old", "A", 0.1, date_offset=-5)
    newer = create_contract("new", "B", 0.1, date_offset=0)
    superseded = ContractAlgebra.supersede(older, newer)
    assert superseded.contradiction_state == ContradictionState.SUPERSEDED
    assert newer.contract_id in superseded.invalidation_dependencies.upstream_contract_ids


def test_supersede_chronology_fails_inverted():
    older = create_contract("old", "A", 0.1, date_offset=0)
    newer = create_contract("new", "B", 0.1, date_offset=-5)
    with pytest.raises(ValueError, match="Cannot supersede with a chronologically older contract"):
        ContractAlgebra.supersede(older, newer)
