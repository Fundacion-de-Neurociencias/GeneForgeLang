"""Conformance runner: run the real parser and validator over the suite and compare.

Case format (one pair of files per case, next to each other)::

    NN_name.gfl             the input document
    NN_name.expected.json   {"status": "valid" | "invalid", "codes": ["SEMANTIC001", ...]}

``status`` is ``invalid`` when parsing raises or the validator reports at least one
error or critical finding. ``codes`` lists reason codes that must all appear among
the reported ones (extra reported codes are allowed); an empty list checks the
status only. A parse failure is reported with the code ``SYNTAX_ERROR``.

Cases that are known to fail are listed in ``known_failures.json`` at the suite root
(``{"<relative/path.gfl>": {"reason": "...", "tracking": "..."}}``). A listed case that
fails is reported as ``known-failure`` and does not fail the run; a listed case that
passes is reported as ``unexpected-pass`` and fails the run, so the list cannot go stale.

Run from the repository root::

    python -m geneforgelang.conformance tests/conformance_suite --junit report.xml
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from geneforgelang.core.api import parse, validate
from geneforgelang.core.errors import ErrorSeverity

SYNTAX_ERROR_CODE = "SYNTAX_ERROR"
KNOWN_FAILURES_FILE = "known_failures.json"
EXPECTED_SUFFIX = ".expected.json"
STATUSES = ("valid", "invalid")

# Outcomes that make the run fail.
FAILING_OUTCOMES = ("fail", "error", "unexpected-pass")


class ConformanceError(ValueError):
    """The suite itself is malformed (missing or invalid expectation file)."""


@dataclass(frozen=True)
class Expected:
    """Expected result of one case."""

    status: str
    codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Actual:
    """Result of running the real parser and validator on one case."""

    status: str
    codes: tuple[str, ...] = ()


@dataclass
class CaseResult:
    """Outcome of one case: pass, fail, error, known-failure or unexpected-pass."""

    case: str
    outcome: str
    expected: Expected | None = None
    actual: Actual | None = None
    detail: str = ""
    tracking: str = ""


@dataclass
class SuiteReport:
    """All case results of one run."""

    results: list[CaseResult] = field(default_factory=list)

    def count(self, outcome: str) -> int:
        return sum(1 for r in self.results if r.outcome == outcome)

    @property
    def ok(self) -> bool:
        return not any(r.outcome in FAILING_OUTCOMES for r in self.results)


def load_expected(path: Path) -> Expected:
    """Read and validate one ``*.expected.json`` file.

    Raises:
        ConformanceError: If the file is not valid JSON or does not follow the format.
    """
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConformanceError(f"{path.name}: cannot read expectation: {exc}") from exc
    if not isinstance(data, dict) or set(data) - {"status", "codes"}:
        raise ConformanceError(f"{path.name}: expected an object with 'status' and 'codes' only")
    status = data.get("status")
    if status not in STATUSES:
        raise ConformanceError(f"{path.name}: 'status' must be one of {STATUSES}, got {status!r}")
    codes = data.get("codes", [])
    if not isinstance(codes, list) or not all(isinstance(c, str) for c in codes):
        raise ConformanceError(f"{path.name}: 'codes' must be a list of strings")
    return Expected(status=status, codes=tuple(codes))


def evaluate(text: str) -> Actual:
    """Run the real parser and validator on ``text``.

    The parser prints diagnostics to stdout and stderr; they are discarded so that the
    runner's own output stays readable.
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            ast = parse(text)
        except (yaml.YAMLError, ValueError):
            return Actual(status="invalid", codes=(SYNTAX_ERROR_CODE,))
        result = validate(ast, enhanced=True)
    blocking = (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL)
    codes = tuple(sorted({e.code for e in result.errors if e.severity in blocking}))
    return Actual(status="invalid" if codes else "valid", codes=codes)


def matches(expected: Expected, actual: Actual) -> bool:
    """True when the status is equal and every expected code was reported."""
    return expected.status == actual.status and set(expected.codes) <= set(actual.codes)


def _load_known_failures(suite: Path) -> dict[str, dict[str, str]]:
    path = suite / KNOWN_FAILURES_FILE
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConformanceError(f"{KNOWN_FAILURES_FILE}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or not all(
        isinstance(v, dict) and v.get("reason") and v.get("tracking") for v in data.values()
    ):
        raise ConformanceError(f"{KNOWN_FAILURES_FILE}: every entry needs a non-empty 'reason' and 'tracking'")
    return data


def run_case(gfl: Path, suite: Path, known: dict[str, dict[str, str]]) -> CaseResult:
    """Run one case and classify the outcome."""
    rel = gfl.relative_to(suite).as_posix()
    expected_path = gfl.with_suffix(EXPECTED_SUFFIX)
    if not expected_path.is_file():
        return CaseResult(rel, "error", detail=f"missing {expected_path.name}")
    try:
        expected = load_expected(expected_path)
    except ConformanceError as exc:
        return CaseResult(rel, "error", detail=str(exc))
    try:
        actual = evaluate(gfl.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - a crashing validator is a case error, not a crash of the run
        return CaseResult(rel, "error", expected, detail=f"{type(exc).__name__}: {exc}")

    passed = matches(expected, actual)
    entry = known.get(rel)
    if entry is None:
        outcome = "pass" if passed else "fail"
        return CaseResult(rel, outcome, expected, actual, "" if passed else _diff(expected, actual))
    if passed:
        return CaseResult(
            rel, "unexpected-pass", expected, actual, "listed in known_failures.json but passes", entry["tracking"]
        )
    return CaseResult(rel, "known-failure", expected, actual, entry["reason"], entry["tracking"])


def _diff(expected: Expected, actual: Actual) -> str:
    missing = sorted(set(expected.codes) - set(actual.codes))
    text = f"expected {expected.status}, got {actual.status}"
    if missing:
        text += f"; missing codes {missing}; reported codes {list(actual.codes)}"
    return text


def run_suite(suite: Path) -> SuiteReport:
    """Run every ``.gfl`` case under ``suite``; orphan expectation files are errors."""
    if not suite.is_dir():
        raise ConformanceError(f"suite directory not found: {suite}")
    known = _load_known_failures(suite)
    report = SuiteReport()
    cases = sorted(suite.rglob("*.gfl"))
    for gfl in cases:
        report.results.append(run_case(gfl, suite, known))
    for expected_path in sorted(suite.rglob(f"*{EXPECTED_SUFFIX}")):
        stem = expected_path.name[: -len(EXPECTED_SUFFIX)]
        if not expected_path.with_name(stem + ".gfl").is_file():
            rel = expected_path.relative_to(suite).as_posix()
            report.results.append(CaseResult(rel, "error", detail="expectation without a .gfl input"))
    if not cases:
        report.results.append(CaseResult(".", "error", detail="the suite contains no .gfl case"))
    for rel in sorted(set(known) - {r.case for r in report.results}):
        report.results.append(CaseResult(rel, "error", detail="listed in known_failures.json but no such case"))
    return report


def write_junit(report: SuiteReport, path: Path) -> None:
    """Write the report as JUnit XML. Known failures are reported as skipped, with the reason."""
    suite = ET.Element(
        "testsuite",
        name="gfl-conformance",
        tests=str(len(report.results)),
        failures=str(report.count("fail") + report.count("unexpected-pass")),
        errors=str(report.count("error")),
        skipped=str(report.count("known-failure")),
    )
    for r in report.results:
        case = ET.SubElement(suite, "testcase", classname="conformance", name=r.case)
        if r.outcome in ("fail", "unexpected-pass"):
            ET.SubElement(case, "failure", message=r.detail)
        elif r.outcome == "error":
            ET.SubElement(case, "error", message=r.detail)
        elif r.outcome == "known-failure":
            ET.SubElement(case, "skipped", message=f"known failure ({r.tracking}): {r.detail}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def format_report(report: SuiteReport) -> str:
    """Plain-text report, one line per case that is not a plain pass, then the counts."""
    lines = [f"{r.outcome.upper():<15} {r.case}: {r.detail}" for r in report.results if r.outcome != "pass"]
    counts = ", ".join(f"{report.count(o)} {o}" for o in ("pass", "fail", "error", "known-failure", "unexpected-pass"))
    lines.append(f"conformance: {len(report.results)} cases: {counts}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point. Returns 0 only when no case fails, errors or passes unexpectedly."""
    parser = argparse.ArgumentParser(prog="geneforgelang.conformance", description=__doc__.split("\n")[0])
    parser.add_argument("suite", type=Path, help="suite directory holding the .gfl and .expected.json pairs")
    parser.add_argument("--junit", type=Path, help="write a JUnit XML report to this path")
    args = parser.parse_args(argv)
    try:
        report = run_suite(args.suite)
    except ConformanceError as exc:
        print(f"conformance: {exc}", file=sys.stderr)
        return 2
    if args.junit:
        write_junit(report, args.junit)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
