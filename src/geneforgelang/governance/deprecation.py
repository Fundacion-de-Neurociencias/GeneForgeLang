import functools
import json
import warnings
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "public_manifest.json"


def _load_sunset_schedule():
    if not MANIFEST_PATH.exists():
        return {}
    try:
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
            return manifest.get("deprecations", {})
    except Exception:
        return {}


_SUNSET_SCHEDULE = _load_sunset_schedule()


class GFLDeprecationWarning(DeprecationWarning):
    """Custom warning category for GFL API deprecations."""

    pass


def deprecated(symbol_name: str, module_name: str = "unknown"):
    """
    Decorator to mark a function or class as deprecated.
    Reads the sunset schedule from the public manifest to provide
    contextual warnings to downstream consumers.
    """

    def decorator(func_or_class):
        @functools.wraps(func_or_class)
        def wrapper(*args, **kwargs):
            deprecation_info = _SUNSET_SCHEDULE.get(f"{module_name}.{symbol_name}", {})
            migration_path = deprecation_info.get("migration", "No migration path specified.")
            sunset_version = deprecation_info.get("sunset_version", "a future major release")

            msg = (
                f"\n[GFL NOTICE] Usage of deprecated symbol '{symbol_name}' from '{module_name}'.\n"
                f"This symbol is scheduled for removal in GFL {sunset_version}.\n"
                f"Migration Action: {migration_path}"
            )
            warnings.warn(msg, category=GFLDeprecationWarning, stacklevel=2)

            return func_or_class(*args, **kwargs)

        return wrapper

    return decorator
