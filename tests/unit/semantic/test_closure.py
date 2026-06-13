import pytest
from geneforgelang.semantic.algebra_audit import SemanticAlgebraAudit
from geneforgelang.semantic.lattice import EpistemicState
from geneforgelang.semantic.state_space import SemanticStateSpaceAudit


def test_full_state_space_audit():
    audit = SemanticStateSpaceAudit()
    assert len(audit.illegal_states) > 0, "Failed to prune illegal states"
    assert len(audit.detect_dead_regions()) == 0, "Dead regions detected in state space"
    assert len(audit.detect_illegal_cycles()) == 0, "Illegal resurrection cycles detected"
    assert audit.verify_monotonicity(), "Monotonicity violated"
    assert audit.verify_lattice_completeness(), "Lattice is incomplete"


def test_full_algebra_audit():
    audit = SemanticStateSpaceAudit()
    algebra = SemanticAlgebraAudit(list(audit.valid_states))
    assert algebra.verify_closure(), "Closure violated"
    assert algebra.verify_idempotence(), "Idempotence violated"
    assert algebra.verify_commutative_properties(), "Commutativity violated"
