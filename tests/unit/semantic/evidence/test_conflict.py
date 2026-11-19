from datetime import datetime, timedelta

import pytest
from geneforgelang.semantic.evidence.conflict import ConflictType, EvidenceConflictResolver, ResolutionAction
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


def create_mock(id: str, scale: ScaleAnchor, ident: float, date_offset: int) -> EvidenceContract:
    base_time = datetime(2026, 5, 28, 12, 0, 0)
    return EvidenceContract(
        contract_id=id,
        claim=f"claim_{id}",
        scale_anchor=scale,
        observability=ObservabilityProfile(0.8, 0.8, 0.8, ident, "high"),
        compressibility=CompressibilityProfile(0.5, 0.5, False),
        temporal_validity=TemporalValidity(base_time + timedelta(days=date_offset), None, 1.0, "stable"),
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=0.1,
        provenance=Provenance("sys", id, base_time, []),
        invalidation_dependencies=InvalidationDependency([], []),
    )


def test_scale_misalignment():
    c1 = create_mock("1", ScaleAnchor.SEQUENCE, 0.8, 0)
    c2 = create_mock("2", ScaleAnchor.PHENOTYPE, 0.8, 0)
    res = EvidenceConflictResolver.resolve(c1, c2)
    assert res.conflict_type == ConflictType.SCALE_MISALIGNMENT
    assert res.action == ResolutionAction.ISOLATE


def test_experimental_supersession():
    c1 = create_mock("1", ScaleAnchor.SEQUENCE, 0.4, 0)
    c2 = create_mock("2", ScaleAnchor.SEQUENCE, 0.9, 0)
    res = EvidenceConflictResolver.resolve(c1, c2)
    assert res.conflict_type == ConflictType.EXPERIMENTAL
    assert res.action == ResolutionAction.SUPERSEDE
    assert res.dominating_contract_id == "2"


def test_hard_observational_collision():
    c1 = create_mock("1", ScaleAnchor.SEQUENCE, 0.8, 0)
    c2 = create_mock("2", ScaleAnchor.SEQUENCE, 0.8, 0)
    res = EvidenceConflictResolver.resolve(c1, c2)
    assert res.conflict_type == ConflictType.OBSERVATIONAL
    assert res.action == ResolutionAction.CONTEST
