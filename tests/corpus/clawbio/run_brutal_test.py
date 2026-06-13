"""
ClawBio × GFL Brutal Test Runner
=================================
Executes the GFL parser and validator against 100 ClawBio-derived fixtures.
Calculates expressivity, verbosity, ambiguity and finds recurrent gaps.

Usage:
    python tests/corpus/clawbio/run_brutal_test.py
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Resolve repo root and add to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
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


@dataclass
class BrutalTestResult:
    filename: str
    parse_success: bool = False
    parse_error: str | None = None
    validate_success: bool = False
    validate_errors: list[str] = field(default_factory=list)
    validate_warnings: list[str] = field(default_factory=list)
    ast_node_count: int = 0
    line_count: int = 0
    verbosity_ratio: float = 0.0


@dataclass
class BrutalTestMetrics:
    total_workflows: int = 0
    expressivity_parse_rate: float = 0.0
    expressivity_valid_rate: float = 0.0
    avg_verbosity_ratio: float = 0.0
    total_ambiguities: int = 0  # Total warnings
    recurrent_gaps: dict[str, int] = field(default_factory=dict)
    workflows: list[BrutalTestResult] = field(default_factory=list)


def count_ast_nodes(ast) -> int:
    if isinstance(ast, dict):
        return 1 + sum(count_ast_nodes(v) for v in ast.values())
    elif isinstance(ast, list):
        return sum(count_ast_nodes(v) for v in ast)
    else:
        return 1


def run_brutal_test() -> BrutalTestMetrics:
    metrics = BrutalTestMetrics()
    if not GFL_AVAILABLE:
        print(f"[FATAL] Cannot import geneforgelang: {_IMPORT_ERROR}")
        return metrics

    gfl_files = list(CORPUS_DIR.glob("*.gfl"))
    metrics.total_workflows = len(gfl_files)
    print(f"Discovered {len(gfl_files)} workflows for the brutal test.")

    total_ast_nodes = 0
    total_lines = 0
    parse_passed = 0
    validate_passed = 0
    all_errors = []

    for path in gfl_files:
        gfl_source = path.read_text(encoding="utf-8")
        lines = len(gfl_source.splitlines())

        result = BrutalTestResult(filename=path.name, line_count=lines)

        # Parse
        try:
            ast = parse_gfl(gfl_source)
            result.parse_success = True
            parse_passed += 1
            result.ast_node_count = count_ast_nodes(ast)
            total_ast_nodes += result.ast_node_count
            total_lines += lines
            if lines > 0:
                result.verbosity_ratio = result.ast_node_count / lines
        except Exception as exc:
            result.parse_error = str(exc)

        # Validate
        if result.parse_success:
            try:
                validator = EnhancedSemanticValidator(file_path=str(path))
                validation_result = validator.validate_ast(ast)

                result.validate_errors = [str(e) for e in validation_result.errors]
                result.validate_warnings = [str(w) for w in validation_result.warnings]

                if validation_result.is_valid:
                    result.validate_success = True
                    validate_passed += 1

                metrics.total_ambiguities += len(result.validate_warnings)
                all_errors.extend(result.validate_errors)
                all_errors.extend(result.validate_warnings)

            except Exception as exc:
                result.validate_errors = [f"Exception: {exc}"]

        metrics.workflows.append(result)

    metrics.expressivity_parse_rate = (parse_passed / len(gfl_files)) * 100 if gfl_files else 0
    metrics.expressivity_valid_rate = (validate_passed / len(gfl_files)) * 100 if gfl_files else 0
    metrics.avg_verbosity_ratio = (total_ast_nodes / total_lines) if total_lines else 0

    # Cluster gaps
    error_counter = Counter()
    for err in all_errors:
        if "Unknown top-level block" in err:
            error_counter["UNKNOWN_TOP_LEVEL"] += 1
        elif "Unknown strategy" in err:
            error_counter["UNKNOWN_STRATEGY"] += 1
        elif "Unknown experiment type" in err:
            error_counter["UNKNOWN_EXPERIMENT_TYPE"] += 1
        elif "Unknown tool" in err:
            error_counter["UNKNOWN_TOOL"] += 1
        else:
            # use a generic grouping
            error_counter["OTHER_SEMANTIC_ISSUE"] += 1

    metrics.recurrent_gaps = dict(error_counter.most_common())
    return metrics


if __name__ == "__main__":
    metrics = run_brutal_test()
    out_file = REPO_ROOT / "docs" / "gaps" / "brutal_test_metrics.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(asdict(metrics), indent=2), encoding="utf-8")

    print("\n--- BRUTAL TEST RESULTS ---")
    print(f"Total workflows: {metrics.total_workflows}")
    print(f"Expressivity (Parse rate): {metrics.expressivity_parse_rate:.1f}%")
    print(f"Expressivity (Valid rate): {metrics.expressivity_valid_rate:.1f}%")
    print(f"Verbosity (Avg AST nodes / line): {metrics.avg_verbosity_ratio:.2f}")
    print(f"Ambiguity (Total warnings): {metrics.total_ambiguities}")
    print("Recurrent Gaps:")
    for k, v in metrics.recurrent_gaps.items():
        print(f"  {k}: {v}")
    print(f"\nMetrics written to {out_file}")
