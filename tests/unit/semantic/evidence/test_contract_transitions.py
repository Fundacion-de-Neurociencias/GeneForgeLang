import pytest
from geneforgelang.semantic.evidence.contract import ContractStateTransitionMatrix, ContradictionState


def test_legal_transitions():
    assert ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.SUPPORTED, ContradictionState.CONTESTED, "conflict_detected"
    )
    assert ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.SUPPORTED, ContradictionState.INVALIDATED, "invalidation_propagation"
    )
    assert ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.SUPPORTED, ContradictionState.RETRACTED, "source_mutation"
    )


def test_illegal_transitions():
    assert not ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.RETRACTED, ContradictionState.SUPPORTED, "conflict_resolved"
    )
    assert not ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.INVALIDATED, ContradictionState.SUPPORTED, "evidence_update"
    )

    # Needs a new provenance lineage to go from RETRACTED to SUPPORTED
    assert ContractStateTransitionMatrix.is_valid_transition(
        ContradictionState.RETRACTED, ContradictionState.SUPPORTED, "new_provenance_lineage"
    )
