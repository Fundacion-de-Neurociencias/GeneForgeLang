from pathlib import Path

from geneforgelang.governance.syntactic_audit import (
    audit_ast_primitives,
    audit_extension_sunsetability,
    audit_repository,
    audit_semantic_contamination,
    score_governance,
)


def test_ast_primitives_require_irreducibility_justification():
    module = _fixture("missing_irreducibility.py")

    violations = audit_ast_primitives(module)

    assert [violation.code for violation in violations] == ["ADR0002_IRREDUCIBILITY_MISSING"]


def test_ast_primitive_justification_must_cover_required_fields():
    module = _fixture("valid_irreducibility.py")

    assert audit_ast_primitives(module) == []


def test_weak_irreducibility_justification_is_rejected():
    module = _fixture("weak_irreducibility.py")

    violations = audit_ast_primitives(module)

    assert [violation.code for violation in violations] == [
        "ADR0002_JUSTIFICATION_WEAK",
        "ADR0002_JUSTIFICATION_WEAK",
    ]


def test_semantic_contamination_scan_allows_guardrail_context():
    module = _fixture("semantic_contamination.py")

    violations = audit_semantic_contamination(module)

    assert [violation.code for violation in violations] == [
        "ADR0002_SEMANTIC_CONTAMINATION",
        "ADR0002_SEMANTIC_CONTAMINATION",
    ]


def test_sunsetability_rejects_core_importing_extension():
    root = _fixture_dir("sunsetability_core_import")

    violations = audit_extension_sunsetability(root)

    assert any(violation.code == "ADR0003_CORE_IMPORTS_EXTENSION" for violation in violations)


def test_sunsetability_rejects_extension_importing_semantic_runtime():
    root = _fixture_dir("sunsetability_extension_import")

    violations = audit_extension_sunsetability(root)

    assert any(violation.code == "ADR0003_EXTENSION_IMPORTS_SEMANTIC_RUNTIME" for violation in violations)


def test_governance_score_penalizes_violations():
    violations = audit_ast_primitives(_fixture("weak_irreducibility.py"))
    score = score_governance(violations)

    assert score.reduction_rigor < 1.0
    assert score.overall < 1.0


def test_current_repository_passes_syntactic_minimality_audit():
    root = Path(__file__).parents[2]

    assert audit_repository(root) == []


def _fixture(name: str) -> Path:
    return Path(__file__).parents[1] / "fixtures" / "syntactic_audit" / name


def _fixture_dir(name: str) -> Path:
    return Path(__file__).parents[1] / "fixtures" / "syntactic_audit" / name
