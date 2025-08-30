"""GeneForgeLang (GFL) - A typed DSL for genomic workflows.

GFL provides a stable, typed API for parsing, validating, and reasoning
about genomic experiments and workflows.
"""

import importlib.util

# Version information
__version__ = "0.2.0"
__api_version__ = "2.0.0"

# New stable API imports
from .api import infer, parse, validate

# Legacy YAML parser imports for backward compatibility
from .yaml_lang.parser import GflYamlParseError, YamlParseError
from .yaml_lang.parser import parse_file as parse_gfl_yaml_file
from .yaml_lang.parser import parse_text as parse_gfl_yaml

# Core types for typed usage (optional import)
try:
    from .types import (
        GFLAST,
        Analysis,
        AnalysisStrategy,
        Experiment,
        ExperimentType,
        InferenceResult,
        ValidationError,
        ValidationResult,
    )

    HAS_TYPES = True
except ImportError:
    HAS_TYPES = False

# Plugin system (optional import)
try:
    from .plugins.plugin_registry import plugin_registry

    HAS_PLUGINS = True
except ImportError:
    HAS_PLUGINS = False
    plugin_registry = None

# Legacy exports for backward compatibility
__all__ = [
    # Legacy YAML parser
    "parse_gfl_yaml",
    "parse_gfl_yaml_file",
    "GflYamlParseError",
    "YamlParseError",
    # Version info
    "__version__",
    "__api_version__",
    # New stable API
    "parse",
    "validate",
    "infer",
]

# Add types to exports if available
if HAS_TYPES:
    __all__.extend(
        [
            "GFLAST",
            "Experiment",
            "Analysis",
            "ValidationResult",
            "ValidationError",
            "InferenceResult",
            "ExperimentType",
            "AnalysisStrategy",
        ]
    )

# Add plugin registry if available
if HAS_PLUGINS:
    __all__.append("plugin_registry")

# Optional NL translator (legacy)
_has_transformers = importlib.util.find_spec("transformers") is not None
if _has_transformers:
    try:
        __all__.append("LanguageTranslator")
    except Exception:
        pass
