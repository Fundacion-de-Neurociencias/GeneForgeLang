"""Normalize parsed protein evidence references into canonical AST nodes."""

from __future__ import annotations

from typing import Any

from .ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)
from .grammar import parse_protein_evidence


CanonicalProteinEvidenceNode = (
    ProteinNode | SequenceNode | EmbeddingReferenceNode | EvidenceScoreNode
)


def normalize_protein_evidence(source: str) -> list[CanonicalProteinEvidenceNode]:
    """Parse and normalize protein evidence syntax into metadata-only nodes."""

    raw_nodes = parse_protein_evidence(source)
    return [normalize_raw_node(node) for node in raw_nodes]


def normalize_raw_node(node: dict[str, Any]) -> CanonicalProteinEvidenceNode:
    """Normalize one raw parser node into a canonical metadata node."""

    kind = node.get("kind")
    value = node.get("value")

    if kind == "PROTEIN":
        return ProteinNode(identifier=str(value))
    if kind == "SEQUENCE":
        return SequenceNode(sequence=str(value))
    if kind == "EMBEDDING_REF":
        return EmbeddingReferenceNode(provider=str(value))
    if kind == "STRUCTURE_CONFIDENCE":
        return EvidenceScoreNode(score_kind="structure_confidence", value=float(value))
    if kind == "PLAUSIBILITY_SCORE":
        return EvidenceScoreNode(score_kind="plausibility_score", value=float(value))

    raise ValueError(f"Unsupported protein evidence node kind: {kind}")


def to_metadata_ast(source: str) -> list[dict[str, Any]]:
    """Return a serializable metadata AST with no biological semantics."""

    return [node.to_dict() for node in normalize_protein_evidence(source)]
