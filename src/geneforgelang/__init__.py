"""GeneForgeLang - Professional DSL for genomic workflows."""

__version__ = "1.0.0"
__author__ = "GeneForgeLang Development Team"
__email__ = "team@geneforgelang.org"

# Import core functions
try:
    from .core.api import execute, infer, parse, validate

    __all__ = ["parse", "validate", "execute", "infer"]
except ImportError:
    # Fallback for development
    __all__ = []
