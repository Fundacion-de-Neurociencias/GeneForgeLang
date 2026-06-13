import importlib
import inspect
import json
import sys
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "public_manifest.json"


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def audit_upstream():
    """
    Validates that the currently exported symbols in the codebase exactly match
    what is declared in the public_manifest.json.
    """
    print("Running Upstream API Boundary Audit...")
    manifest = load_manifest()

    errors = []

    # Check all modules declared in the manifest
    for module_name, exports in manifest.get("exports", {}).items():
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            errors.append(f"[ERROR] Declared public module '{module_name}' could not be imported.")
            continue

        # 1. Check for missing symbols (declared but not present)
        for symbol_name, symbol_info in exports.items():
            if not hasattr(module, symbol_name):
                errors.append(
                    f"[ERROR] Symbol '{symbol_name}' is declared in manifest for '{module_name}' but missing in code."
                )

        # 2. Check for unauthorized expansion (present in __all__ but not declared)
        if hasattr(module, "__all__"):
            for symbol_name in module.__all__:
                if symbol_name not in exports:
                    errors.append(
                        f"[ERROR] Unauthorized export: '{symbol_name}' in '{module_name}'. Update the manifest via RFC to expose this."
                    )
        else:
            # If no __all__ is defined, we should ideally restrict exports or warn
            errors.append(
                f"[WARNING] Module '{module_name}' does not define __all__. This makes the public surface implicit."
            )

    if errors:
        print("\n--- UPSTREAM AUDIT FAILED ---")
        for err in errors:
            print(err)
        print(
            "\nPublic Contract Sovereignty violated. Downstream convenience cannot justify upstream surface expansion."
        )
        sys.exit(1)

    print("\n[OK] Upstream API strictly matches public manifest.")
    sys.exit(0)


if __name__ == "__main__":
    audit_upstream()
