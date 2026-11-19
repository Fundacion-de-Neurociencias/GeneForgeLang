import difflib
import importlib
import json
import sys
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "public_manifest.json"


def get_current_manifest():
    if not MANIFEST_PATH.exists():
        return {
            "version": "0.0.0",
            "public_modules": [],
            "exports": {},
            "type_signatures": {},
            "deprecations": {},
            "compatibility_window": {},
        }
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def generate_candidate_exports(public_modules):
    exports = {}
    for module_name in public_modules:
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            print(f"[ERROR] Could not import {module_name}")
            continue

        module_exports = {}
        if hasattr(module, "__all__"):
            for symbol in module.__all__:
                # We default to stable for new auto-detected, but a human must review
                module_exports[symbol] = {
                    "type": "unknown",
                    "state": "experimental",  # Force human to promote to stable
                    "introduced_in": "TBD",
                }
        exports[module_name] = module_exports
    return exports


def main():
    current = get_current_manifest()

    candidate = current.copy()
    candidate["exports"] = generate_candidate_exports(current.get("public_modules", []))

    current_json = json.dumps(current, indent=2, sort_keys=True)
    candidate_json = json.dumps(candidate, indent=2, sort_keys=True)

    if current_json == candidate_json:
        print("No changes detected in the API surface.")
        sys.exit(0)

    print("--- CANDIDATE MANIFEST DIFF ---")
    diff = difflib.unified_diff(
        current_json.splitlines(),
        candidate_json.splitlines(),
        fromfile="current_manifest.json",
        tofile="candidate_manifest.json",
        lineterm="",
    )
    for line in diff:
        print(line)

    print("\n[REQUIRED] Human review is required to accept this manifest change.")
    print("Do not overwrite public_manifest.json silently. Any API expansion must be approved via GFL-RFC.")


if __name__ == "__main__":
    main()
