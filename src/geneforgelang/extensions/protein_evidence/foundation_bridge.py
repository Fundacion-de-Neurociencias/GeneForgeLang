from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import Any

from geneforgelang.extensions.protein_evidence.ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)


class FoundationBridgeValidationError(ValueError):
    """Raised when a foundation-model payload violates syntax-only interop."""


_FORBIDDEN_KEYS = {
    "causal_claim",
    "causal_claims",
    "inferred_causal_claim",
    "inferred_causal_claims",
    "semantic_completion",
    "semantic_completions",
    "rule",
    "rules",
    "rule_synthesis",
    "generated_rules",
    "truth_support",
    "epistemic_status",
}

_ALLOWED_KEYS = {
    "protein",
    "sequence",
    "embedding",
    "embedding_ref",
    "embedding_model",
    "model",
    "provider",
    "model_structure_confidence",
    "embedding_score",
    "metadata",
    "external_ref",
}


def validate_foundation_payload(payload: Mapping[str, Any]) -> bool:
    """Validate that a protein foundation-model payload contains metadata only."""

    if not isinstance(payload, Mapping):
        raise FoundationBridgeValidationError("Foundation payload must be a mapping")

    forbidden = _FORBIDDEN_KEYS.intersection(payload)
    if forbidden:
        joined = ", ".join(sorted(forbidden))
        raise FoundationBridgeValidationError(f"Foundation bridge rejects semantic operations: {joined}")

    unknown = set(payload).difference(_ALLOWED_KEYS)
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise FoundationBridgeValidationError(f"Unsupported foundation metadata fields: {joined}")

    if "embedding" not in payload and "embedding_ref" not in payload:
        raise FoundationBridgeValidationError("Foundation payload requires embedding or embedding_ref")

    embedding = payload.get("embedding")
    if embedding is not None:
        if not isinstance(embedding, list) or not all(_is_number(value) for value in embedding):
            raise FoundationBridgeValidationError("embedding must be a list of numbers")

    for score_key in ("model_structure_confidence", "embedding_score"):
        if score_key in payload:
            score = payload[score_key]
            if not _is_number(score) or not 0.0 <= float(score) <= 1.0:
                raise FoundationBridgeValidationError(f"{score_key} must be a number between 0.0 and 1.0")

    return True


def import_foundation_embedding(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Import a protein foundation-model payload as metadata-only extension nodes."""

    validate_foundation_payload(payload)

    nodes: list[Any] = []
    metadata = dict(payload.get("metadata") or {})
    if "external_ref" in payload:
        metadata["external_ref"] = payload["external_ref"]

    if protein := payload.get("protein"):
        nodes.append(ProteinNode(identifier=str(protein), metadata=metadata))
    if sequence := payload.get("sequence"):
        nodes.append(SequenceNode(sequence=str(sequence), metadata=metadata))

    embedding_source = str(payload.get("embedding_model") or payload.get("model") or "foundation")
    provider = payload.get("provider")
    embedding_ref = payload.get("embedding_ref")
    embedding_metadata = dict(metadata)
    if provider is not None:
        embedding_metadata["provider"] = provider
    if "embedding" in payload:
        embedding_metadata["embedding_dimensions"] = len(payload["embedding"])
    nodes.append(
        EmbeddingReferenceNode(
            source=embedding_source,
            reference=str(embedding_ref) if embedding_ref is not None else None,
            metadata=embedding_metadata,
        )
    )

    for score_key in ("model_structure_confidence", "embedding_score"):
        if score_key in payload:
            nodes.append(EvidenceScoreNode(score_type=score_key, value=float(payload[score_key])))

    return {
        "extension": "protein_evidence",
        "semantic_role": "metadata_only",
        "nodes": [asdict(node) for node in nodes],
    }


def export_foundation_adapter_contract(provider: str | None = None) -> dict[str, Any]:
    """Describe the metadata-only interop contract for protein foundation adapters."""

    return {
        "adapter": provider or "protein_foundation",
        "extension": "protein_evidence",
        "mode": "syntax_interop",
        "semantic_role": "metadata_only",
        "allowed_operations": [
            "evidence_annotation",
            "structural_metadata_attachment",
            "external_reference_linking",
        ],
        "rejected_operations": [
            "inferred_causal_claims",
            "semantic_completion",
            "rule_synthesis_from_embeddings",
            "score_promotion_to_truth_support",
        ],
        "canonical_nodes": [
            "ProteinNode",
            "SequenceNode",
            "EmbeddingReferenceNode",
            "EvidenceScoreNode",
        ],
    }


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
