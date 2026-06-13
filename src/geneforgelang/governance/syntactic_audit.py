from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

GOVERNANCE_SCORE_THRESHOLD = 0.9

REQUIRED_JUSTIFICATION_FIELDS = (
    "why_existing_primitives_fail",
    "formal_loss_if_reduced",
)

FORBIDDEN_EXTENSION_TERMS = (
    "causal",
    "infer",
    "predict",
    "pathogenic",
    "mechanism",
    "effect propagation",
)

GUARDRAIL_CONTEXT_MARKERS = (
    "_FORBIDDEN",
    "forbidden",
    "reject",
    "rejected",
    "disallow",
    "must not",
    "cannot",
    "no ",
    "non-causal",
    "syntax-only",
    "semantic operations",
    "rejected_operations",
    "ValidationError",
)

WEAK_JUSTIFICATION_PHRASES = (
    "specialized use case",
    "specific use case",
    "needed",
    "useful",
    "custom",
    "better",
)

SUNSETABILITY_FORBIDDEN_EXTENSION_IMPORT_PREFIXES = (
    "geneforgelang.semantic",
    "geneforgelang.core.inference",
    "geneforgelang.core.execution",
    "geneforgelang.semantic.lattice",
    "geneforgelang.semantic.ontology",
    "geneforgelang.semantic.evidence",
)


@dataclass(frozen=True)
class AuditViolation:
    code: str
    path: Path
    message: str
    line: int | None = None

    def format(self, root: Path) -> str:
        location = self.path.relative_to(root).as_posix()
        if self.line is not None:
            location = f"{location}:{self.line}"
        return f"{self.code} {location} - {self.message}"


@dataclass(frozen=True)
class GovernanceComplianceScore:
    reduction_rigor: float
    provider_neutrality: float
    primitive_necessity: float
    semantic_contamination_risk: float
    sunsetability: float

    @property
    def overall(self) -> float:
        return min(
            self.reduction_rigor,
            self.provider_neutrality,
            self.primitive_necessity,
            self.semantic_contamination_risk,
            self.sunsetability,
        )


def audit_repository(root: Path) -> list[AuditViolation]:
    """Run ADR-0002 syntactic minimality checks."""

    root = root.resolve()
    violations: list[AuditViolation] = []
    extension_dir = root / "src" / "geneforgelang" / "extensions"

    if extension_dir.exists():
        for path in extension_dir.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            violations.extend(audit_ast_primitives(path))
            violations.extend(audit_semantic_contamination(path))

    violations.extend(audit_invariance_regression(root))
    violations.extend(audit_extension_sunsetability(root))
    score = score_governance(violations)
    if score.overall < GOVERNANCE_SCORE_THRESHOLD:
        violations.append(
            AuditViolation(
                code="ADR0003_GOVERNANCE_SCORE_BELOW_THRESHOLD",
                path=root,
                message=(
                    f"Governance compliance score {score.overall:.2f} is below " f"{GOVERNANCE_SCORE_THRESHOLD:.2f}."
                ),
            )
        )
    return violations


def audit_ast_primitives(path: Path) -> list[AuditViolation]:
    """Require irreducibility proofs for extension AST node primitives."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    node_classes = [item.name for item in tree.body if isinstance(item, ast.ClassDef) and item.name.endswith("Node")]
    if not node_classes:
        return []

    justifications = _literal_module_assignment(tree, "IRREDUCIBILITY_JUSTIFICATION")
    violations: list[AuditViolation] = []
    if not isinstance(justifications, dict):
        return [
            AuditViolation(
                code="ADR0002_IRREDUCIBILITY_MISSING",
                path=path,
                message="AST node primitives require IRREDUCIBILITY_JUSTIFICATION.",
            )
        ]

    for class_name in node_classes:
        entry = justifications.get(class_name)
        if not isinstance(entry, dict):
            violations.append(
                AuditViolation(
                    code="ADR0002_PRIMITIVE_UNJUSTIFIED",
                    path=path,
                    message=f"{class_name} lacks an irreducibility justification.",
                )
            )
            continue
        for field in REQUIRED_JUSTIFICATION_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                violations.append(
                    AuditViolation(
                        code="ADR0002_JUSTIFICATION_INCOMPLETE",
                        path=path,
                        message=f"{class_name}.{field} must be a non-empty string.",
                    )
                )
                continue
            lowered = value.lower()
            if len(value.strip()) < 40 or any(phrase in lowered for phrase in WEAK_JUSTIFICATION_PHRASES):
                violations.append(
                    AuditViolation(
                        code="ADR0002_JUSTIFICATION_WEAK",
                        path=path,
                        message=f"{class_name}.{field} does not meet reduction rigor.",
                    )
                )

    return violations


def audit_semantic_contamination(path: Path) -> list[AuditViolation]:
    """Detect semantic terminology in extensions outside explicit guardrails."""

    violations: list[AuditViolation] = []
    source = path.read_text(encoding="utf-8")
    guardrail_lines = _guardrail_line_numbers(source)
    for line_number, line in enumerate(source.splitlines(), start=1):
        if line_number in guardrail_lines:
            continue
        lowered = line.lower()
        for term in FORBIDDEN_EXTENSION_TERMS:
            if term not in lowered:
                continue
            if any(marker.lower() in lowered for marker in GUARDRAIL_CONTEXT_MARKERS):
                continue
            violations.append(
                AuditViolation(
                    code="ADR0002_SEMANTIC_CONTAMINATION",
                    path=path,
                    line=line_number,
                    message=f"Extension syntax contains semantic term '{term}' outside guardrail context.",
                )
            )
    return violations


def _guardrail_line_numbers(source: str) -> set[int]:
    tree = ast.parse(source)
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target_names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if target_names.intersection({"_FORBIDDEN_KEYS", "disallowed_terms"}):
                lines.update(range(node.lineno, getattr(node, "end_lineno", node.lineno) + 1))
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "rejected_operations":
                    lines.update(range(value.lineno, getattr(value, "end_lineno", value.lineno) + 1))
    return lines


def audit_invariance_regression(root: Path) -> list[AuditViolation]:
    """Require semantic null-effect regression tests for extension interoperability."""

    tests_dir = root / "tests" / "extensions"
    invariance_tests = list(tests_dir.glob("*semantic_invariance*.py")) if tests_dir.exists() else []
    if not invariance_tests:
        return [
            AuditViolation(
                code="ADR0002_INVARIANCE_TEST_MISSING",
                path=tests_dir,
                message="Extension work requires semantic invariance regression tests.",
            )
        ]

    required_terms = ("EpistemicState", "SemanticOntology")
    for test_file in invariance_tests:
        content = test_file.read_text(encoding="utf-8")
        if all(term in content for term in required_terms):
            return []

    return [
        AuditViolation(
            code="ADR0002_INVARIANCE_TEST_INCOMPLETE",
            path=invariance_tests[0],
            message="Semantic invariance tests must cover lattice and ontology null-effect.",
        )
    ]


def audit_extension_sunsetability(root: Path) -> list[AuditViolation]:
    """Ensure extensions can be removed without core language contamination."""

    root = root.resolve()
    src_dir = root / "src" / "geneforgelang"
    extension_dir = src_dir / "extensions"
    violations: list[AuditViolation] = []

    if src_dir.exists():
        for path in src_dir.rglob("*.py"):
            if "extensions" in path.parts or "governance" in path.parts:
                continue
            violations.extend(_audit_no_core_extension_import(path))

    if extension_dir.exists():
        for path in extension_dir.rglob("*.py"):
            violations.extend(_audit_no_extension_semantic_import(path))

    return violations


def score_governance(violations: Sequence[AuditViolation]) -> GovernanceComplianceScore:
    """Compute a blocking governance score from audit violations."""

    return GovernanceComplianceScore(
        reduction_rigor=_dimension_score(
            violations,
            {
                "ADR0002_IRREDUCIBILITY_MISSING",
                "ADR0002_PRIMITIVE_UNJUSTIFIED",
                "ADR0002_JUSTIFICATION_INCOMPLETE",
                "ADR0002_JUSTIFICATION_WEAK",
            },
        ),
        provider_neutrality=_dimension_score(
            violations,
            {"ADR0003_EXTENSION_IMPORTS_SEMANTIC_RUNTIME"},
        ),
        primitive_necessity=_dimension_score(
            violations,
            {
                "ADR0002_IRREDUCIBILITY_MISSING",
                "ADR0002_PRIMITIVE_UNJUSTIFIED",
                "ADR0002_JUSTIFICATION_WEAK",
            },
        ),
        semantic_contamination_risk=_dimension_score(
            violations,
            {"ADR0002_SEMANTIC_CONTAMINATION"},
        ),
        sunsetability=_dimension_score(
            violations,
            {
                "ADR0003_CORE_IMPORTS_EXTENSION",
                "ADR0003_EXTENSION_IMPORTS_SEMANTIC_RUNTIME",
            },
        ),
    )


def _audit_no_core_extension_import(path: Path) -> list[AuditViolation]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[AuditViolation] = []
    for node in ast.walk(tree):
        module = _imported_module_name(node)
        if module and module.startswith("geneforgelang.extensions"):
            violations.append(
                AuditViolation(
                    code="ADR0003_CORE_IMPORTS_EXTENSION",
                    path=path,
                    line=getattr(node, "lineno", None),
                    message="Core language modules must not import optional extensions.",
                )
            )
    return violations


def _audit_no_extension_semantic_import(path: Path) -> list[AuditViolation]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[AuditViolation] = []
    for node in ast.walk(tree):
        module = _imported_module_name(node)
        if module and module.startswith(SUNSETABILITY_FORBIDDEN_EXTENSION_IMPORT_PREFIXES):
            violations.append(
                AuditViolation(
                    code="ADR0003_EXTENSION_IMPORTS_SEMANTIC_RUNTIME",
                    path=path,
                    line=getattr(node, "lineno", None),
                    message="Extensions must not depend on semantic runtime or ontology modules.",
                )
            )
    return violations


def _imported_module_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Import):
        return next((alias.name for alias in node.names), None)
    if isinstance(node, ast.ImportFrom):
        return node.module
    return None


def _dimension_score(violations: Sequence[AuditViolation], codes: set[str]) -> float:
    count = sum(1 for violation in violations if violation.code in codes)
    return max(0.0, 1.0 - (0.25 * count))


def _literal_module_assignment(tree: ast.Module, name: str) -> object | None:
    for item in tree.body:
        if not isinstance(item, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in item.targets):
            continue
        try:
            return ast.literal_eval(item.value)
        except (SyntaxError, ValueError):
            return None
    return None


def run(paths: Sequence[str] | None = None) -> int:
    root = Path(paths[0] if paths else ".").resolve()
    violations = audit_repository(root)
    score = score_governance([v for v in violations if v.code != "ADR0003_GOVERNANCE_SCORE_BELOW_THRESHOLD"])
    if not violations:
        print("ADR-0002/0003 governance audit passed " f"(score={score.overall:.2f}).")
        return 0

    print("ADR-0002 syntactic minimality audit failed:")
    for violation in violations:
        print(f"- {violation.format(root)}")
    return 1


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run ADR-0002 syntactic minimality audit.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to audit.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    return run([args.root])


if __name__ == "__main__":
    raise SystemExit(main())
