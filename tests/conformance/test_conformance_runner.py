"""Tests of the conformance runner (F006).

The runner calls the real parser and validator; nothing here replaces them. The meta-tests
prove the property the runner exists for: a case whose expectation is wrong makes the run
fail, in process and as a command (exit code).
"""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from geneforgelang import conformance as cf

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests" / "conformance_suite"

VALID_DOC = 'experiment:\n  tool: "CRISPR_cas9"\n  type: "gene_editing"\n'
MISSING_TYPE_DOC = 'experiment:\n  tool: "CRISPR_cas9"\n'
BROKEN_YAML_DOC = "experiment: [unclosed\n"


def _case(
    folder: Path,
    name: str,
    text: str,
    status: str,
    codes: list[str] | None = None,
    expected: bool = True,
) -> Path:
    gfl = folder / f"{name}.gfl"
    gfl.write_text(text, encoding="utf-8")
    if expected:
        gfl.with_suffix(cf.EXPECTED_SUFFIX).write_text(
            json.dumps({"status": status, "codes": codes or []}), encoding="utf-8"
        )
    return gfl


def _outcomes(report: cf.SuiteReport) -> dict[str, str]:
    return {r.case: r.outcome for r in report.results}


def _run_command(*args: str) -> subprocess.CompletedProcess[str]:
    # The repository root is the working directory: plugin_registry imports ``src.geneforgelang``.
    return subprocess.run(
        [sys.executable, "-m", "geneforgelang.conformance", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )


class TestEvaluate:
    def test_valid_document(self) -> None:
        assert cf.evaluate(VALID_DOC) == cf.Actual("valid", ())

    def test_validator_error_is_reported_with_its_code(self) -> None:
        actual = cf.evaluate(MISSING_TYPE_DOC)
        assert actual.status == "invalid"
        assert "SEMANTIC001" in actual.codes

    def test_unparseable_document_is_a_syntax_error(self) -> None:
        assert cf.evaluate(BROKEN_YAML_DOC) == cf.Actual("invalid", (cf.SYNTAX_ERROR_CODE,))


class TestMatches:
    @pytest.mark.parametrize(
        ("expected", "actual", "result"),
        [
            (cf.Expected("valid"), cf.Actual("valid"), True),
            (cf.Expected("valid"), cf.Actual("invalid", ("X",)), False),
            (cf.Expected("invalid"), cf.Actual("valid"), False),
            (cf.Expected("invalid"), cf.Actual("invalid", ("A",)), True),
            (cf.Expected("invalid", ("A",)), cf.Actual("invalid", ("A", "B")), True),
            (cf.Expected("invalid", ("A", "C")), cf.Actual("invalid", ("A", "B")), False),
        ],
    )
    def test_status_and_code_subset(self, expected: cf.Expected, actual: cf.Actual, result: bool) -> None:
        assert cf.matches(expected, actual) is result


class TestLoadExpected:
    def _write(self, tmp_path: Path, content: str) -> Path:
        path = tmp_path / "a.expected.json"
        path.write_text(content, encoding="utf-8")
        return path

    def test_reads_status_and_codes(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, '{"status": "invalid", "codes": ["SEMANTIC001"]}')
        assert cf.load_expected(path) == cf.Expected("invalid", ("SEMANTIC001",))

    @pytest.mark.parametrize(
        "content",
        [
            "not json",
            "[]",
            '{"status": "maybe"}',
            '{"codes": []}',
            '{"status": "valid", "codes": "A"}',
            '{"status": "valid", "codes": [1]}',
            '{"status": "valid", "extra": 1}',
        ],
    )
    def test_malformed_expectation_is_rejected(self, tmp_path: Path, content: str) -> None:
        with pytest.raises(cf.ConformanceError):
            cf.load_expected(self._write(tmp_path, content))


class TestRunSuite:
    def test_correct_expectations_pass(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_valid", VALID_DOC, "valid")
        _case(tmp_path, "02_invalid", MISSING_TYPE_DOC, "invalid", ["SEMANTIC001"])
        _case(tmp_path, "03_syntax", BROKEN_YAML_DOC, "invalid", [cf.SYNTAX_ERROR_CODE])
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_valid.gfl": "pass", "02_invalid.gfl": "pass", "03_syntax.gfl": "pass"}
        assert report.ok

    def test_wrong_status_fails(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_wrong", MISSING_TYPE_DOC, "valid")
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_wrong.gfl": "fail"}
        assert not report.ok

    def test_wrong_code_fails(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_code", MISSING_TYPE_DOC, "invalid", ["NO_SUCH_CODE"])
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_code.gfl": "fail"}
        assert "NO_SUCH_CODE" in report.results[0].detail

    def test_case_without_expectation_is_an_error(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_none", VALID_DOC, "valid", expected=False)
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_none.gfl": "error"}
        assert not report.ok

    def test_orphan_expectation_is_an_error(self, tmp_path: Path) -> None:
        (tmp_path / "01_orphan.expected.json").write_text('{"status": "valid"}', encoding="utf-8")
        _case(tmp_path, "02_valid", VALID_DOC, "valid")
        report = cf.run_suite(tmp_path)
        assert _outcomes(report)["01_orphan.expected.json"] == "error"
        assert not report.ok

    def test_empty_suite_is_an_error(self, tmp_path: Path) -> None:
        assert not cf.run_suite(tmp_path).ok

    def test_missing_suite_directory_raises(self, tmp_path: Path) -> None:
        with pytest.raises(cf.ConformanceError):
            cf.run_suite(tmp_path / "absent")

    def test_validator_crash_is_a_case_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _case(tmp_path, "01_valid", VALID_DOC, "valid")

        def boom(text: str) -> cf.Actual:
            raise RuntimeError("validator exploded")

        monkeypatch.setattr(cf, "evaluate", boom)
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_valid.gfl": "error"}
        assert "validator exploded" in report.results[0].detail


class TestKnownFailures:
    def _known(self, folder: Path, entries: dict) -> None:
        (folder / cf.KNOWN_FAILURES_FILE).write_text(json.dumps(entries), encoding="utf-8")

    def test_listed_failure_is_reported_and_does_not_fail_the_run(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_gap", MISSING_TYPE_DOC, "valid")
        self._known(tmp_path, {"01_gap.gfl": {"reason": "validator gap", "tracking": "ref-1"}})
        report = cf.run_suite(tmp_path)
        result = report.results[0]
        assert (result.outcome, result.tracking, result.detail) == ("known-failure", "ref-1", "validator gap")
        assert report.ok

    def test_listed_case_that_passes_fails_the_run(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_fixed", VALID_DOC, "valid")
        self._known(tmp_path, {"01_fixed.gfl": {"reason": "was broken", "tracking": "ref-1"}})
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_fixed.gfl": "unexpected-pass"}
        assert not report.ok

    def test_unlisted_failure_still_fails_the_run(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_gap", MISSING_TYPE_DOC, "valid")
        _case(tmp_path, "02_other", MISSING_TYPE_DOC, "valid")
        self._known(tmp_path, {"01_gap.gfl": {"reason": "validator gap", "tracking": "ref-1"}})
        report = cf.run_suite(tmp_path)
        assert _outcomes(report) == {"01_gap.gfl": "known-failure", "02_other.gfl": "fail"}
        assert not report.ok

    def test_entry_for_a_missing_case_is_an_error(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_valid", VALID_DOC, "valid")
        self._known(tmp_path, {"gone.gfl": {"reason": "r", "tracking": "t"}})
        assert not cf.run_suite(tmp_path).ok

    @pytest.mark.parametrize("entry", [{"reason": "r"}, {"tracking": "t"}, {"reason": "", "tracking": "t"}, "text"])
    def test_entry_without_reason_and_tracking_is_rejected(self, tmp_path: Path, entry: object) -> None:
        _case(tmp_path, "01_valid", VALID_DOC, "valid")
        self._known(tmp_path, {"01_valid.gfl": entry})
        with pytest.raises(cf.ConformanceError):
            cf.run_suite(tmp_path)


class TestJunit:
    def test_report_lists_every_outcome(self, tmp_path: Path) -> None:
        suite = tmp_path / "suite"
        suite.mkdir()
        _case(suite, "01_pass", VALID_DOC, "valid")
        _case(suite, "02_fail", MISSING_TYPE_DOC, "valid")
        _case(suite, "03_known", MISSING_TYPE_DOC, "valid")
        (suite / cf.KNOWN_FAILURES_FILE).write_text(
            json.dumps({"03_known.gfl": {"reason": "gap", "tracking": "ref-1"}}), encoding="utf-8"
        )
        out = tmp_path / "out" / "report.xml"
        cf.write_junit(cf.run_suite(suite), out)
        root = ET.parse(out).getroot()
        assert (root.get("tests"), root.get("failures"), root.get("skipped")) == ("3", "1", "1")
        by_name = {c.get("name"): c for c in root.findall("testcase")}
        assert by_name["02_fail.gfl"].find("failure") is not None
        assert "ref-1" in by_name["03_known.gfl"].find("skipped").get("message")
        assert len(by_name["01_pass.gfl"]) == 0


class TestCommand:
    """Exit codes of ``python -m geneforgelang.conformance`` (the meta-test of F006)."""

    def test_wrong_expected_json_makes_the_command_exit_non_zero(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_wrong", MISSING_TYPE_DOC, "valid")  # the validator rejects this document
        result = _run_command(str(tmp_path))
        assert result.returncode == 1
        assert "FAIL" in result.stdout and "01_wrong.gfl" in result.stdout

    def test_correct_expected_json_makes_the_command_exit_zero(self, tmp_path: Path) -> None:
        _case(tmp_path, "01_right", MISSING_TYPE_DOC, "invalid", ["SEMANTIC001"])
        result = _run_command(str(tmp_path), "--junit", str(tmp_path / "report.xml"))
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / "report.xml").is_file()

    def test_missing_suite_exits_two(self, tmp_path: Path) -> None:
        result = _run_command(str(tmp_path / "absent"))
        assert result.returncode == 2
        assert "suite directory not found" in result.stderr


class TestShippedSuite:
    def test_every_case_has_an_expectation_and_the_run_is_clean(self) -> None:
        report = cf.run_suite(SUITE)
        assert report.ok, cf.format_report(report)
        assert report.count("error") == 0
        assert report.count("pass") + report.count("known-failure") == len(report.results)

    def test_known_failures_have_a_reason_and_tracking(self) -> None:
        known = json.loads((SUITE / cf.KNOWN_FAILURES_FILE).read_text(encoding="utf-8"))
        assert known
        assert all(v["reason"] and v["tracking"] for v in known.values())

    def test_runner_does_not_simulate_results(self) -> None:
        source = Path(cf.__file__).read_text(encoding="utf-8")
        assert "Mocking" not in source
        assert "actual = expected" not in source
