"""GeneForgeLang (GFL) - A typed DSL for genomic workflows.

GFL provides a stable, typed API for parsing, validating, and reasoning
about genomic experiments and workflows.
"""

import importlib.util

# Version information
__version__ = "0.2.0"
__api_version__ = "2.0.0"

# New stable API imports
from .api import infer, parse, parse_enhanced, validate

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
    GFLAST = None
    Experiment = None
    Analysis = None
    ValidationResult = None
    ValidationError = None
    InferenceResult = None
    ExperimentType = None
    AnalysisStrategy = None

# Optional grammar parser (requires PLY)
try:
    from .grammar_parser import create_lexer, create_parser, parse_gfl_grammar

    HAS_GRAMMAR_PARSER = True
except ImportError:
    HAS_GRAMMAR_PARSER = False

# Plugin system (optional import)
try:
    # Auto-register example plugins
    from .plugins import auto_register
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
    "parse_enhanced",
]
# Add types to exports if available
if HAS_TYPES:
    # Import globals into module namespace when types are available
    globals().update(
        {
            "GFLAST": GFLAST,
            "Experiment": Experiment,
            "Analysis": Analysis,
            "ValidationResult": ValidationResult,
            "ValidationError": ValidationError,
            "InferenceResult": InferenceResult,
            "ExperimentType": ExperimentType,
            "AnalysisStrategy": AnalysisStrategy,
        }
    )

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

# Add grammar parser if available
if HAS_GRAMMAR_PARSER:
    __all__.extend(["parse_gfl_grammar", "create_lexer", "create_parser"])

# Optional NL translator (legacy)
_has_transformers = importlib.util.find_spec("transformers") is not None
if _has_transformers:
    try:
        __all__.append("LanguageTranslator")
    except Exception:
        pass
