"""
Constitutional Architectural Audit for GeneForgeLang

Enforces ADR-0003: Extension Orthogonality under Excision.
Statically analyzes AST to compute the import graph and guarantee the strict
boundary between the Constitutional Core, Compilation Core, and Extension Surface.
Also simulates physical excision and parses the Governance Score.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ArchitecturalAudit:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.src_dir = self.root_dir / "src"
        if not self.src_dir.exists():
            # Fallback if run directly inside src/
            if (self.root_dir / "geneforgelang").exists():
                self.src_dir = self.root_dir
            else:
                self.src_dir = self.root_dir / "src"

        self.violations: list[str] = []
        self.escalations: list[str] = []
        self.import_graph: dict[str, set[str]] = {}
        self.module_to_file: dict[str, Path] = {}

    def run(self) -> bool:
        print("=" * 80)
        print("STARTING GENEFORGELANG CONSTITUTIONAL ARCHITECTURAL AUDIT")
        print("=" * 80)

        # 1. Build import graph
        self._build_import_graph()

        # 2. Run transitive contamination audits
        self._audit_core_contamination()
        self._audit_reverse_contamination()

        # 3. Run structured governance scoring
        self._audit_governance_scoring()

        # 4. Run physical excision simulation
        self._simulate_physical_excision()

        # Print results
        print("\n" + "=" * 80)
        print("AUDIT RESULTS SUMMARY")
        print("=" * 80)

        if self.escalations:
            print("\n[WARNING] MANDATORY HUMAN ESCALATIONS REQUIRED:")
            for esc in self.escalations:
                print(f"  - {esc}")

        if self.violations:
            print("\n[FAIL] CONSTITUTIONAL VIOLATIONS FOUND:")
            for violation in self.violations:
                print(f"  - {violation}")
            print("\n[RESULT] ARCHITECTURAL AUDIT FAILED. Merge rejected to protect language constitution.")
            print("=" * 80)
            return False

        print("\n[PASS] ARCHITECTURAL AUDIT PASSED!")
        print("Extension Orthogonality under Excision is mathematically and physically verified.")
        print("=" * 80)
        return True

    def _path_to_module(self, filepath: Path) -> str:
        try:
            rel = filepath.relative_to(self.src_dir)
            return ".".join(rel.with_suffix("").parts)
        except ValueError:
            return filepath.stem

    def _build_import_graph(self):
        print("[1/4] Building full transitive import graph via AST analysis...")
        for filepath in self.src_dir.rglob("*.py"):
            if "tests" in filepath.parts or "docs" in filepath.parts or ".venv" in filepath.parts:
                continue

            module_name = self._path_to_module(filepath)
            self.module_to_file[module_name] = filepath
            self.import_graph[module_name] = set()

            with open(filepath, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=str(filepath))
                except SyntaxError as e:
                    self.violations.append(f"Syntax error in {filepath}: {e}")
                    continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.import_graph[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Handle relative imports inside geneforgelang packages
                        target_module = node.module
                        if node.level > 0:
                            # Relative import, resolve base module name
                            parts = module_name.split(".")
                            # node.level of 1 means parent directory of current file, etc.
                            base_parts = parts[: -node.level]
                            target_module = ".".join(base_parts + [node.module])
                        self.import_graph[module_name].add(target_module)

    def _find_path(self, start: str, predicate) -> list[str]:
        """Finds a path in the import graph from start to any module satisfying predicate."""
        visited = set()
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if predicate(node):
                return path
            if node in visited:
                continue
            visited.add(node)
            # Find matching module or prefix matches in the graph
            for neighbor in self.import_graph.get(node, set()):
                queue.append(path + [neighbor])
            # Handle exact file submodules not explicitly in import_graph
            for registered_mod in self.import_graph:
                if registered_mod.startswith(node + "."):
                    queue.append(path + [registered_mod])
        return []

    def _audit_core_contamination(self):
        print("[2/4] Auditing Core Contamination (Zone 1: extensions -> core)...")
        forbidden_cores = [
            "geneforgelang.semantic.lattice",
            "geneforgelang.semantic.conflict",
            "geneforgelang.semantic.constraints",
            "geneforgelang.semantic.runtime",
        ]

        # For every module inside geneforgelang.extensions
        for module in self.import_graph:
            if module.startswith("geneforgelang.extensions"):
                for forbidden in forbidden_cores:

                    def is_forbidden_match(mod: str):
                        return mod == forbidden or mod.startswith(forbidden + ".")

                    path = self._find_path(module, is_forbidden_match)
                    if path:
                        path_str = " -> ".join(path)
                        filename = self.module_to_file[module].name
                        self.violations.append(
                            f"[CORE CONTAMINATION VIOLATION] {filename} -> Extension module '{module}' "
                            f"illegally imports Constitutional Core transitively:\n    Path: {path_str}"
                        )

    def _audit_reverse_contamination(self):
        print("[3/4] Auditing Reverse Contamination (Zone 2: core -> extensions)...")
        # Every core module must not import any extension
        for module in self.import_graph:
            # Skip the extensions module itself and the governance/plugin loaders/registries
            if module.startswith("geneforgelang.extensions"):
                continue
            if "governance" in module or "plugins" in module:
                continue

            def is_extension_match(mod: str):
                return mod.startswith("geneforgelang.extensions")

            path = self._find_path(module, is_extension_match)
            if path:
                path_str = " -> ".join(path)
                filename = self.module_to_file[module].name
                self.violations.append(
                    f"[REVERSE CONTAMINATION VIOLATION] {filename} -> Core module '{module}' "
                    f"illegally imports Extension transitively:\n    Path: {path_str}"
                )

    def _audit_governance_scoring(self):
        print("[4/4] Auditing Structured Governance Scoring...")
        extensions_dir = self.src_dir / "geneforgelang" / "extensions"
        if not extensions_dir.exists():
            return

        for ext_path in extensions_dir.iterdir():
            if ext_path.is_dir() and ext_path.name != "__pycache__":
                gov_file = ext_path / "governance.json"
                if not gov_file.exists():
                    self.violations.append(
                        f"[GOVERNANCE VIOLATION] Extension '{ext_path.name}' lacks a mandatory governance.json."
                    )
                    continue

                try:
                    with open(gov_file, encoding="utf-8") as f:
                        gov_data = json.load(f)
                except Exception as e:
                    self.violations.append(
                        f"[GOVERNANCE VIOLATION] Failed to parse governance.json for '{ext_path.name}': {e}"
                    )
                    continue

                # Validate score structure
                dimensions = [
                    "irreducibility_depth",
                    "ontological_neutrality",
                    "provider_abstraction_purity",
                    "primitive_necessity",
                    "sunsetability_confidence",
                ]
                scoring = gov_data.get("scoring", {})
                dims_data = scoring.get("dimensions", {})

                total_calculated = 0
                missing_dims = []
                invalid_scores = []

                for dim in dimensions:
                    if dim not in dims_data:
                        missing_dims.append(dim)
                    else:
                        score = dims_data[dim].get("score")
                        if not isinstance(score, int) or not (0 <= score <= 5):
                            invalid_scores.append(f"{dim} ({score})")
                        else:
                            total_calculated += score

                if missing_dims:
                    self.violations.append(
                        f"[GOVERNANCE VIOLATION] Extension '{ext_path.name}' is missing governance dimensions: {', '.join(missing_dims)}"
                    )
                    continue

                if invalid_scores:
                    self.violations.append(
                        f"[GOVERNANCE VIOLATION] Extension '{ext_path.name}' has invalid dimension scores (must be 0-5): {', '.join(invalid_scores)}"
                    )
                    continue

                declared_total = scoring.get("total_score")
                if declared_total != total_calculated:
                    self.violations.append(
                        f"[GOVERNANCE VIOLATION] Extension '{ext_path.name}' score mismatch: declared {declared_total}, calculated {total_calculated}."
                    )

                # Process decisions based on Thresholds
                if total_calculated < 15:
                    self.violations.append(
                        f"[GOVERNANCE BLOCKER] Extension '{ext_path.name}' score ({total_calculated}/25) is below the minimum threshold of 15. Automatic rejection."
                    )
                elif 15 <= total_calculated <= 20:
                    self.escalations.append(
                        f"Extension '{ext_path.name}' score ({total_calculated}/25) triggers MANDATORY HUMAN REVIEW ESCALATION.\n"
                        f"    Justification Summary: {ext_path.name} is in the transitional governance tier (15-20)."
                    )
                else:
                    print(
                        f"  - Extension '{ext_path.name}' scored {total_calculated}/25 (Passed governance threshold)."
                    )

    def _simulate_physical_excision(self):
        print("\nExecuting Physical Excision Simulations (Sunsetability validation)...")
        extensions_dir = self.src_dir / "geneforgelang" / "extensions"
        if not extensions_dir.exists():
            return

        extensions_to_test = []
        for ext_path in extensions_dir.iterdir():
            if ext_path.is_dir() and ext_path.name != "__pycache__":
                extensions_to_test.append(ext_path)

        for ext_path in extensions_to_test:
            ext_name = ext_path.name
            excised_path = ext_path.parent / f"{ext_name}_EXCISED"

            print(f"  -> Excising '{ext_name}' physically and executing test suite...")
            try:
                # Rename the extension directory physically to completely hide it
                ext_path.rename(excised_path)

                import os

                env = os.environ.copy()
                env["PYTHONPATH"] = "src"

                # Check 1: Base parser and grammar validation tests
                print("     Running base parser completeness tests...")
                cmd_parser = [
                    str(self.root_dir / ".venv" / "Scripts" / "python.exe"),
                    "-m",
                    "pytest",
                    "tests/unit/test_parser.py",
                ]
                res_parser = subprocess.run(cmd_parser, cwd=str(self.root_dir), env=env, capture_output=True, text=True)

                # Check 2: Core Semantic test suite (test_closure.py, etc.)
                print("     Running core semantic closure proofs...")
                cmd_semantic = [
                    str(self.root_dir / ".venv" / "Scripts" / "python.exe"),
                    "-m",
                    "pytest",
                    "tests/unit/semantic",
                ]
                res_semantic = subprocess.run(
                    cmd_semantic, cwd=str(self.root_dir), env=env, capture_output=True, text=True
                )

                if res_parser.returncode != 0:
                    self.violations.append(
                        f"[SUNSETABILITY FAILURE] Base parser failed when extension '{ext_name}' was excised.\n"
                        f"    Parser Test Stderr:\n{res_parser.stderr or res_parser.stdout}"
                    )

                if res_semantic.returncode != 0:
                    self.violations.append(
                        f"[SUNSETABILITY FAILURE] Core semantic closure proofs failed when extension '{ext_name}' was excised.\n"
                        f"    Semantic Test Stderr:\n{res_semantic.stderr or res_semantic.stdout}"
                    )

                if res_parser.returncode == 0 and res_semantic.returncode == 0:
                    print(
                        f"     [PASS] Excised verification passed for '{ext_name}'. Base compiler operations are fully orthogonal."
                    )

            except Exception as e:
                self.violations.append(
                    f"[SUNSETABILITY EXCEPTION] Exception during excision simulation of '{ext_name}': {e}"
                )
            finally:
                # Always restore the directory, no matter what happens
                if excised_path.exists():
                    excised_path.rename(ext_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_dir", type=str, nargs="?", default=".", help="Root directory of the project")
    args = parser.parse_args()

    audit = ArchitecturalAudit(Path(args.root_dir))
    if not audit.run():
        sys.exit(1)
    sys.exit(0)
