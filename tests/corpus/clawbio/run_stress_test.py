"""
ClawBio × GFL Stress Test Runner
=================================
Executes the GFL real parser and validator against 10 ClawBio-derived fixtures.
Produces a structured gap report in JSON and Markdown.

Usage:
    # From GeneForgeLang repo root:
    python tests/corpus/clawbio/run_stress_test.py

    # Skip execution mode (parse + validate only, no ClawBio install needed):
    python tests/corpus/clawbio/run_stress_test.py --parse-only

    # Save reports:
    python tests/corpus/clawbio/run_stress_test.py --output docs/gaps/
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ── Resolve repo root and add to path ────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent.parent.parent  # tests/corpus/clawbio/ → GeneForgeLang/
SRC_PATH = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

try:
    from geneforgelang.core.parser import parse_gfl
    from geneforgelang.core.validator import EnhancedSemanticValidator

    GFL_AVAILABLE = True
except ImportError as e:
    GFL_AVAILABLE = False
    _IMPORT_ERROR = str(e)

CORPUS_DIR = Path(__file__).parent
FIXTURES = [
    ("CB_001", "pharmgx_reporter.gfl", "PharmGx Reporter", "pharmacogenomics"),
    ("CB_002", "crispr_screen_triage.gfl", "CRISPR Screen Triage", "functional-genomics"),
    ("CB_003", "rnaseq_de.gfl", "RNA-seq DE", "transcriptomics"),
    ("CB_004", "gwas_lookup.gfl", "GWAS Lookup", "population-genomics"),
    ("CB_005", "scrnaseq_orchestrator.gfl", "scRNA Orchestrator", "single-cell"),
    ("CB_006", "equity_scorer.gfl", "Equity Scorer", "population-diversity"),
    ("CB_007", "pathway_enricher.gfl", "Pathway Enricher", "functional-genomics"),
    ("CB_008", "dnasp.gfl", "DnaSP Population Genetics", "population-genetics"),
    ("CB_009", "metagenomics_profiler.gfl", "Metagenomics Profiler", "metagenomics"),
    ("CB_010", "genome_compare.gfl", "Genome Compare", "comparative-genomics"),
]


# ── Result types ──────────────────────────────────────────────────────────────


@dataclass
class FixtureResult:
    fixture_id: str
    skill_name: str
    domain: str
    filename: str
    parse_success: bool = False
    parse_error: str | None = None
    validate_success: bool = False
    validate_errors: list[str] = field(default_factory=list)
    validate_warnings: list[str] = field(default_factory=list)
    gap_probes: list[dict[str, Any]] = field(default_factory=list)
    elapsed_ms: float = 0.0
    raw_ast_keys: list[str] = field(default_factory=list)


@dataclass
class StressTestReport:
    run_timestamp: str
    gfl_available: bool
    total_fixtures: int
    parse_passed: int = 0
    parse_failed: int = 0
    validate_passed: int = 0
    validate_warned: int = 0
    validate_failed: int = 0
    results: list[FixtureResult] = field(default_factory=list)
    identified_gaps: list[dict[str, Any]] = field(default_factory=list)


# ── Core runner ───────────────────────────────────────────────────────────────


def run_stress_test(parse_only: bool = False) -> StressTestReport:
    from datetime import datetime, timezone

    report = StressTestReport(
        run_timestamp=datetime.now(timezone.utc).isoformat(),
        gfl_available=GFL_AVAILABLE,
        total_fixtures=len(FIXTURES),
    )

    if not GFL_AVAILABLE:
        print(f"[FATAL] Cannot import geneforgelang: {_IMPORT_ERROR}", file=sys.stderr)
        print("        Make sure you run from GeneForgeLang repo root with PYTHONPATH=src", file=sys.stderr)
        return report

    for fixture_id, filename, skill_name, domain in FIXTURES:
        path = CORPUS_DIR / filename
        result = FixtureResult(
            fixture_id=fixture_id,
            skill_name=skill_name,
            domain=domain,
            filename=filename,
        )

        if not path.exists():
            result.parse_error = f"File not found: {path}"
            report.results.append(result)
            report.parse_failed += 1
            continue

        gfl_source = path.read_text(encoding="utf-8")

        # ── Step 1: Parse ─────────────────────────────────────────────────
        t0 = time.perf_counter()
        try:
            ast = parse_gfl(gfl_source)
            result.parse_success = True
            result.raw_ast_keys = list(ast.keys()) if isinstance(ast, dict) else []
            report.parse_passed += 1
            print(f"  [PARSE  OK] {fixture_id} {skill_name}")
        except Exception as exc:
            result.parse_error = str(exc)
            report.parse_failed += 1
            print(f"  [PARSE ERR] {fixture_id} {skill_name}: {exc}")

        # ── Step 2: Validate ──────────────────────────────────────────────
        if result.parse_success and not parse_only:
            try:
                validator = EnhancedSemanticValidator(file_path=str(path))
                validation_result = validator.validate_ast(ast)

                errors = [str(e) for e in validation_result.errors]
                warnings = [str(w) for w in validation_result.warnings]
                result.validate_errors = errors
                result.validate_warnings = warnings

                if validation_result.is_valid:
                    if warnings:
                        result.validate_success = True
                        report.validate_warned += 1
                        print(f"  [VALID WRN] {fixture_id} {skill_name}: {len(warnings)} warnings")
                    else:
                        result.validate_success = True
                        report.validate_passed += 1
                        print(f"  [VALID  OK] {fixture_id} {skill_name}")
                else:
                    result.validate_success = False
                    report.validate_failed += 1
                    print(f"  [VALID ERR] {fixture_id} {skill_name}: {len(errors)} errors")
                    for e in errors[:3]:
                        print(f"              → {e}")

            except Exception as exc:
                result.validate_errors = [f"Validator exception: {exc}"]
                result.validate_success = False
                report.validate_failed += 1
                print(f"  [VALID EXC] {fixture_id} {skill_name}: {exc}")

        # ── Step 3: Collect gap probes from fixture metadata ──────────────
        if result.parse_success and isinstance(ast, dict):
            meta = ast.get("metadata", {})
            if isinstance(meta, dict) and "gap_probe" in meta:
                probe = meta["gap_probe"]
                probe["fixture_id"] = fixture_id
                probe["skill_name"] = skill_name
                result.gap_probes.append(probe)
                report.identified_gaps.append(probe)

        result.elapsed_ms = (time.perf_counter() - t0) * 1000
        report.results.append(result)

    # ── Synthesize gap analysis from errors ───────────────────────────────────
    _synthesize_gaps_from_errors(report)

    return report


def _synthesize_gaps_from_errors(report: StressTestReport) -> None:
    """Analyse validation errors across all fixtures to identify systematic gaps."""
    error_patterns: dict[str, list[str]] = {}

    for result in report.results:
        for err in result.validate_errors + result.validate_warnings:
            # Cluster by error type
            for pattern in [
                "Unknown top-level block",
                "Unknown strategy",
                "Unknown experiment type",
                "Unknown tool",
                "Missing required field",
                "Contract",
                "Invalid",
            ]:
                if pattern.lower() in err.lower():
                    error_patterns.setdefault(pattern, []).append(f"{result.fixture_id}: {err[:120]}")
                    break

    for pattern, examples in error_patterns.items():
        report.identified_gaps.append(
            {
                "type": "VALIDATION_PATTERN",
                "pattern": pattern,
                "count": len(examples),
                "examples": examples[:5],
            }
        )


# ── Report writers ────────────────────────────────────────────────────────────


def write_json_report(report: StressTestReport, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "clawbio_stress_test_report.json"
    out.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def write_markdown_report(report: StressTestReport, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "clawbio_stress_test_report.md"

    lines: list[str] = [
        "# ClawBio × GFL Stress Test Report",
        "",
        f"**Run**: `{report.run_timestamp}`  ",
        f"**GFL available**: {'✅' if report.gfl_available else '❌'}  ",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total fixtures | {report.total_fixtures} |",
        f"| Parse passed | {report.parse_passed} |",
        f"| Parse failed | {report.parse_failed} |",
        f"| Validate passed (clean) | {report.validate_passed} |",
        f"| Validate warned | {report.validate_warned} |",
        f"| Validate failed | {report.validate_failed} |",
        "",
        "## Per-Fixture Results",
        "",
    ]

    for r in report.results:
        parse_icon = "✅" if r.parse_success else "❌"
        validate_icon = "✅" if r.validate_success else ("⚠️" if r.validate_warnings else "❌")
        lines.append(f"### {r.fixture_id} — {r.skill_name}")
        lines.append("")
        lines.append(f"- **Domain**: {r.domain}")
        lines.append(f"- **Parse**: {parse_icon}")
        lines.append(f"- **Validate**: {validate_icon}")
        if r.parse_error:
            lines.append(f"- **Parse error**: `{r.parse_error}`")
        if r.validate_errors:
            lines.append(f"- **Errors ({len(r.validate_errors)})**:")
            for e in r.validate_errors[:5]:
                lines.append(f"  - `{e}`")
        if r.validate_warnings:
            lines.append(f"- **Warnings ({len(r.validate_warnings)})**:")
            for w in r.validate_warnings[:5]:
                lines.append(f"  - `{w}`")
        if r.gap_probes:
            for probe in r.gap_probes:
                lines.append(f"- **Gap probe** (`{probe.get('type')}`): {probe.get('recommendation', '')}")
        lines.append(f"- **Elapsed**: {r.elapsed_ms:.1f} ms")
        lines.append("")

    lines += [
        "## Identified Gaps",
        "",
        "Gaps are derived from explicit `gap_probe` annotations in fixtures",
        "and from systematic patterns in validation errors.",
        "",
    ]

    for i, gap in enumerate(report.identified_gaps, 1):
        lines.append(f"### Gap {i}: {gap.get('type', 'UNKNOWN')}")
        lines.append("")
        for k, v in gap.items():
            if k in ("type", "fixture_id", "skill_name"):
                continue
            if isinstance(v, list):
                lines.append(f"- **{k}**:")
                for item in v:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- **{k}**: {v}")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClawBio × GFL Stress Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--parse-only",
        action="store_true",
        help="Only run the parser, skip semantic validation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "gaps",
        help="Output directory for reports (default: docs/gaps/)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ClawBio × GFL Stress Test")
    print(f"Corpus: {CORPUS_DIR}")
    print(f"Fixtures: {len(FIXTURES)}")
    print("=" * 60)

    report = run_stress_test(parse_only=args.parse_only)

    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print(f"  Parse:    {report.parse_passed}/{report.total_fixtures} passed")
    print(
        f"  Validate: {report.validate_passed} clean | {report.validate_warned} warned | {report.validate_failed} failed"
    )
    print(f"  Gaps identified: {len(report.identified_gaps)}")
    print("=" * 60)

    json_out = write_json_report(report, args.output)
    md_out = write_markdown_report(report, args.output)

    print("\nReports written to:")
    print(f"  JSON: {json_out}")
    print(f"  MD:   {md_out}")

    # Exit 1 if parse failures exist (hard failures, not warnings)
    sys.exit(1 if report.parse_failed > 0 else 0)


if __name__ == "__main__":
    main()
