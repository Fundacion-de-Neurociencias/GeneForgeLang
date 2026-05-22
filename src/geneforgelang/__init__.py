"""GeneForgeLang - Professional DSL for genomic workflows."""

__version__ = "1.0.0"
__author__ = "GeneForgeLang Development Team"
__email__ = "team@geneforgelang.org"

# Import core functions
try:
    pass

    __all__ = ["parse", "validate", "execute", "infer"]
except ImportError:
    # Fallback for development
    __all__ = []
