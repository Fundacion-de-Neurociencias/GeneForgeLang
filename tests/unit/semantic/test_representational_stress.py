import json
from pathlib import Path

from geneforgelang.semantic.representational_audit import run_representational_audit
from geneforgelang.semantic.semantic_equivalence import canonical_key, semantic_equivalent
from geneforgelang.semantic.state_space import SemanticStateSpaceAudit


def test_semantic_equivalence_admits_only_explicit_lattice_identity():
    states = sorted(SemanticStateSpaceAudit().all_states, key=canonical_key)

    assert semantic_equivalent(states[0], states[0])
    assert not semantic_equivalent(states[0], states[-1])


def test_phase_5_6_representational_stress_report_schema():
    config = Path("fixtures/semantic/audit_config.json")
    report_path = _report_path()

    try:
        report = run_representational_audit(config, report_path)
        serialized = json.loads(report_path.read_text(encoding="utf-8"))
    finally:
        report_path.unlink(missing_ok=True)

    assert set(serialized) == {
        "rsi",
        "fpcr",
        "illegal_collapses",
        "monotonicity_breaches",
        "canonicalization_failures",
        "freeze_decision",
    }
    assert serialized["freeze_decision"] in {"PASS", "FAIL"}
    assert serialized["freeze_decision"] == report.freeze_decision


def test_phase_5_6_representational_stress_passes_freeze_gate():
    config = Path("fixtures/semantic/audit_config.json")
    report_path = _report_path()

    try:
        report = run_representational_audit(config, report_path)
    finally:
        report_path.unlink(missing_ok=True)

    assert report.rsi >= 0.999
    assert report.fpcr == 0.0
    assert report.illegal_collapses == []
    assert report.monotonicity_breaches == []
    assert report.canonicalization_failures == []
    assert report.freeze_decision == "PASS"


def _report_path() -> Path:
    return Path(__file__).with_name("representational_audit_report.json")
