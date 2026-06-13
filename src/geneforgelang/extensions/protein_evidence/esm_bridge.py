from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from geneforgelang.extensions.protein_evidence.foundation_bridge import (
    FoundationBridgeValidationError,
    export_foundation_adapter_contract,
    import_foundation_embedding,
    validate_foundation_payload,
)


class ESMBridgeValidationError(FoundationBridgeValidationError):
    """Raised when an ESM payload violates syntax-only interoperability."""


def validate_embedding_schema(payload: Mapping[str, Any]) -> bool:
    """Validate that an ESM payload contains metadata only."""

    if not isinstance(payload, Mapping):
        raise ESMBridgeValidationError("ESM payload must be a mapping")

    try:
        return validate_foundation_payload({**payload, "provider": payload.get("provider", "esm")})
    except FoundationBridgeValidationError as exc:
        raise ESMBridgeValidationError(str(exc)) from exc


def import_embedding(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Import an ESM payload as GeneForgeLang metadata-only extension nodes."""

    validate_embedding_schema(payload)
    return import_foundation_embedding({**payload, "provider": payload.get("provider", "esm")})


def export_adapter_contract() -> dict[str, Any]:
    """Describe the metadata-only interoperability contract for the ESM adapter.

    Returns a provider-agnostic contract description suitable for any downstream
    runtime that implements the GFL foundation adapter protocol.
    """
    return export_foundation_adapter_contract("esm")


# Deprecated alias — kept for backward compatibility, will be removed in GFL v3.
# Use export_adapter_contract() instead.
def export_to_geneforge_adapter() -> dict[str, Any]:  # noqa: D401
    """Deprecated: use export_adapter_contract() instead."""
    import warnings

    warnings.warn(
        "export_to_geneforge_adapter() is deprecated and will be removed in GFL v3. "
        "Use export_adapter_contract() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return export_adapter_contract()
