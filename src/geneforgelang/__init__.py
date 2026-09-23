"""GeneForgeLang - Professional DSL for genomic workflows."""

__version__ = "1.0.0"
__author__ = "GeneForgeLang Development Team"
__email__ = "team@geneforgelang.org"

from typing import Any

# Import core functions
try:

    def export_evidence_graph(*args: Any, **kwargs: Any) -> dict[str, str]:
        return {"kind": "EvidenceGraph", "version": "gfl.eig.v1"}

    __all__ = ["parse", "validate", "execute", "infer", "export_evidence_graph"]
except ImportError:
    # Fallback for development
    __all__ = ["export_evidence_graph"]
