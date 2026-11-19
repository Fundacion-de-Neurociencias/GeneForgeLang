from datetime import datetime

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
from geneforgelang.semantic.evidence.invalidation import EvidenceGraph, EvidenceInvalidationBridge, SourceMutationEvent


def create_mock_contract(id: str, upstreams: list) -> EvidenceContract:
    return EvidenceContract(
        contract_id=id,
        claim="test",
        scale_anchor=ScaleAnchor.SEQUENCE,
        observability=ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "high"),
        compressibility=CompressibilityProfile(0.5, 0.5, False),
        temporal_validity=TemporalValidity(datetime.now(), None, 1.0, "stable"),
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=0.1,
        provenance=Provenance("sys", id, datetime.now(), []),
        invalidation_dependencies=InvalidationDependency(upstreams, []),
    )


def test_invalidation_cascade():
    graph = EvidenceGraph()
    c_root = create_mock_contract("root", [])
    c_child1 = create_mock_contract("child1", ["root"])
    c_child2 = create_mock_contract("child2", ["child1"])

    graph.add_contract(c_root)
    graph.add_contract(c_child1)
    graph.add_contract(c_child2)

    bridge = EvidenceInvalidationBridge(graph)

    # Mutate root -> RETRACTED
    event = SourceMutationEvent("root", ContradictionState.RETRACTED, "source_mutation")
    result = bridge.propagate_mutation(event)

    assert "root" in result.recalibrated_contracts
    assert "child1" in result.invalidated_contracts
    assert "child2" in result.invalidated_contracts

    assert graph.get_contract("root").contradiction_state == ContradictionState.RETRACTED
    assert graph.get_contract("child1").contradiction_state == ContradictionState.INVALIDATED
    assert graph.get_contract("child2").contradiction_state == ContradictionState.INVALIDATED


def test_illegal_mutation_halt():
    graph = EvidenceGraph()
    c_root = create_mock_contract("root", [])
    # Hack the state directly to test transition block
    import datetime as dt

    from geneforgelang.semantic.evidence.contract import TemporalValidity

    now = dt.datetime.now()
    new_tv = TemporalValidity(
        c_root.temporal_validity.valid_from,
        now,
        c_root.temporal_validity.stability_expectation,
        c_root.temporal_validity.decay_model,
    )
    c_root = EvidenceContract(
        **{**c_root.__dict__, "contradiction_state": ContradictionState.RETRACTED, "temporal_validity": new_tv}
    )
    graph.add_contract(c_root)

    bridge = EvidenceInvalidationBridge(graph)

    # Try illegal transition RETRACTED -> SUPPORTED via evidence_update (needs new_provenance_lineage)
    event = SourceMutationEvent("root", ContradictionState.SUPPORTED, "evidence_update")
    result = bridge.propagate_mutation(event)

    assert len(result.failed_transitions) == 1
    assert "Illegal transition" in result.failed_transitions[0]
    assert "root" not in result.recalibrated_contracts
    assert graph.get_contract("root").contradiction_state == ContradictionState.RETRACTED
