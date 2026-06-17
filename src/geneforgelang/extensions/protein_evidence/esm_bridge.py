"""Interoperability helpers for GeneForge ESM evidence payloads."""

from __future__ import annotations

from typing import Any, Mapping


REQUIRED_ESM_FIELDS = frozenset(
    {
        "sequence_embedding",
        "structure_confidence",
        "neighborhood_hits",
        "plausibility_score",
        "source_model",
        "provenance",
    }
)

FORBIDDEN_SEMANTIC_FIELDS = frozenset(
    {
        "pathogenicity_prediction",
        "causal_effect",
        "inferred_mechanism",
        "disease_likelihood",
    }
)


class ESMBridgeValidationError(ValueError):
    """Raised when an ESM evidence payload violates the metadata contract."""


class SemanticBoundaryViolation(ESMBridgeValidationError):
    """Raised when a payload attempts to cross from metadata into semantics."""


def validate_embedding_schema(payload: Mapping[str, Any]) -> bool:
    """Validate the GeneForge ESM adapter payload shape.

    Validation is structural only. It does not assign biological meaning.
    """

    _reject_forbidden_semantic_fields(payload)

    missing = REQUIRED_ESM_FIELDS - set(payload)
    if missing:
        raise ESMBridgeValidationError(f"Missing ESM payload fields: {sorted(missing)}")

    embedding = payload["sequence_embedding"]
    if not isinstance(embedding, list) or not all(_is_number(value) for value in embedding):
        raise ESMBridgeValidationError("sequence_embedding must be a list of numbers")

    _validate_score(payload["structure_confidence"], "structure_confidence")
    _validate_score(payload["plausibility_score"], "plausibility_score")

    if not isinstance(payload["neighborhood_hits"], list):
        raise ESMBridgeValidationError("neighborhood_hits must be a list")
    if not isinstance(payload["source_model"], str) or not payload["source_model"]:
        raise ESMBridgeValidationError("source_model must be a non-empty string")

    provenance = payload["provenance"]
    if not isinstance(provenance, Mapping):
        raise ESMBridgeValidationError("provenance must be an object")
    if provenance.get("semantic_mutation") is not False:
        raise ESMBridgeValidationError("ESM payload must declare semantic_mutation=false")
    if provenance.get("causal_completion") is not False:
        raise ESMBridgeValidationError("ESM payload must declare causal_completion=false")

    return True


def import_embedding(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Import an ESM payload as a metadata-only bridge record."""

    validate_embedding_schema(payload)
    return {
        "node_type": "EmbeddingReferenceNode",
        "provider": payload["source_model"],
        "semantic_role": "metadata_only",
        "embedding": list(payload["sequence_embedding"]),
        "provenance": dict(payload["provenance"]),
    }


def export_to_geneforge_adapter() -> dict[str, Any]:
    """Describe the external adapter contract expected from GeneForge."""

    return {
        "adapter": "esm",
        "role": "external_read_only_evidence",
        "required_fields": sorted(REQUIRED_ESM_FIELDS),
        "forbidden_fields": sorted(FORBIDDEN_SEMANTIC_FIELDS),
        "semantic_mutation": False,
        "causal_completion": False,
    }


def _reject_forbidden_semantic_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        forbidden = FORBIDDEN_SEMANTIC_FIELDS.intersection(value)
        if forbidden:
            raise SemanticBoundaryViolation(
                f"ESM bridge rejects semantic fields: {sorted(forbidden)}"
            )
        for nested_value in value.values():
            _reject_forbidden_semantic_fields(nested_value)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_semantic_fields(item)


def _validate_score(value: Any, field_name: str) -> None:
    if not _is_number(value) or not 0.0 <= float(value) <= 1.0:
        raise ESMBridgeValidationError(f"{field_name} must be a number between 0 and 1")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
