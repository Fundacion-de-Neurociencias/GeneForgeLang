"""Protein evidence metadata extension.

The extension is syntax-only. It carries external protein evidence references
without assigning causal or biological semantics.
"""

from .ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)
from .grammar import parse_protein_evidence
from .normalizer import normalize_protein_evidence

__all__ = [
    "EmbeddingReferenceNode",
    "EvidenceScoreNode",
    "ProteinNode",
    "SequenceNode",
    "normalize_protein_evidence",
    "parse_protein_evidence",
]
