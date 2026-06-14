import argparse
import ast
import json
import sys
from pathlib import Path


def load_manifest(manifest_path):
    if not manifest_path.exists():
        print(f"[FATAL] Cannot find public manifest at {manifest_path}")
        sys.exit(1)
    with open(manifest_path) as f:
        return json.load(f)


def audit_directory(target_dir, manifest):
    target_path = Path(target_dir)
    if not target_path.exists() or not target_path.is_dir():
        print(f"[FATAL] Target directory {target_dir} does not exist.")
        sys.exit(1)

    public_modules = set(manifest.get("public_modules", []))
    exports = manifest.get("exports", {})

    errors = 0
    warnings = 0
    notices = 0

    print(f"Auditing boundary compliance in: {target_path}")

    for py_file in target_path.rglob("*.py"):
        if ".venv" in py_file.parts or "node_modules" in py_file.parts:
            continue

        try:
            with open(py_file, encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("geneforgelang."):
                        if alias.name not in public_modules:
                            print(
                                f"[ERROR] {py_file.name}:{node.lineno} - Prohibited import of internal module: '{alias.name}'"
                            )
                            errors += 1
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("geneforgelang."):
                    if node.module not in public_modules:
                        print(
                            f"[ERROR] {py_file.name}:{node.lineno} - Prohibited import from internal module: '{node.module}'"
                        )
                        errors += 1
                    else:
                        # Module is public, check symbols
                        module_exports = exports.get(node.module, {})
                        for alias in node.names:
                            symbol = alias.name
                            if symbol == "*":
                                continue  # Hard to analyze statically without full environment

                            if symbol not in module_exports:
                                print(
                                    f"[ERROR] {py_file.name}:{node.lineno} - Prohibited import of internal symbol: '{symbol}' from '{node.module}'"
                                )
                                errors += 1
                            else:
                                state = module_exports[symbol].get("state", "stable")
                                if state == "experimental":
                                    print(
                                        f"[WARNING] {py_file.name}:{node.lineno} - Importing experimental symbol: '{symbol}'"
                                    )
                                    warnings += 1
                                elif state == "deprecated":
                                    print(
                                        f"[NOTICE] {py_file.name}:{node.lineno} - Importing deprecated symbol: '{symbol}'. Please migrate."
                                    )
                                    notices += 1

    print("\n--- BOUNDARY AUDIT SUMMARY ---")
    print(f"Errors: {errors} | Warnings: {warnings} | Notices: {notices}")

    if errors > 0:
        print("\n[FAILED] Boundary violations detected. Downstream systems cannot depend on GFL internals.")
        sys.exit(1)
    else:
        print("\n[PASSED] Boundary compliance verified.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GFL API Boundary Auditor")
    parser.add_argument("--target-path", required=True, help="Path to the downstream repository to audit")

    # We assume this script is running from inside the installed geneforgelang package
    default_manifest = Path(__file__).parent / "public_manifest.json"
    parser.add_argument("--manifest-path", default=str(default_manifest), help="Path to public_manifest.json")

    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest_path))
    audit_directory(args.target_path, manifest)
