from __future__ import annotations

from dataclasses import asdict
from typing import Any

from geneforgelang.extensions.protein_evidence.ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)
from geneforgelang.extensions.protein_evidence.grammar import (
    ProteinEvidenceCall,
    parse_protein_evidence,
)


def normalize_protein_evidence(source: str) -> list[Any]:
    """Normalize protein evidence extension syntax into metadata-only AST nodes."""

    calls = parse_protein_evidence(source)
    return normalize_calls(calls)


def normalize_calls(calls: list[ProteinEvidenceCall]) -> list[Any]:
    nodes: list[Any] = []
    for call in calls:
        if call.name == "PROTEIN":
            nodes.append(ProteinNode(identifier=str(call.argument)))
        elif call.name == "SEQUENCE":
            nodes.append(SequenceNode(sequence=str(call.argument)))
        elif call.name == "EMBEDDING_REF":
            nodes.append(EmbeddingReferenceNode(source=str(call.argument)))
        elif call.name == "MODEL_STRUCTURE_CONFIDENCE":
            nodes.append(EvidenceScoreNode(score_type="model_structure_confidence", value=float(call.argument)))
        elif call.name == "EMBEDDING_SCORE":
            nodes.append(EvidenceScoreNode(score_type="embedding_score", value=float(call.argument)))
    return nodes


def normalize_to_dict(source: str) -> dict[str, Any]:
    """Return a serializable extension AST without semantic interpretation."""

    return {
        "extension": "protein_evidence",
        "semantic_role": "metadata_only",
        "nodes": [asdict(node) for node in normalize_protein_evidence(source)],
    }
