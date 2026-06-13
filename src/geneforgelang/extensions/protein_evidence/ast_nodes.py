from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

IRREDUCIBILITY_JUSTIFICATION = {
    "ProteinNode": {
        "why_existing_primitives_fail": (
            "Protein identifiers need validation separate from sequence strings and " "external reference handles."
        ),
        "formal_loss_if_reduced": (
            "Reducing to a generic reference would lose the distinction between named "
            "protein target metadata and embedding reference metadata."
        ),
    },
    "SequenceNode": {
        "why_existing_primitives_fail": (
            "Protein sequences require sequence-specific structural validation as raw "
            "metadata without becoming semantic entities."
        ),
        "formal_loss_if_reduced": (
            "Reducing to a generic string would lose the ability to validate sequence "
            "payload boundaries independently from identifiers."
        ),
    },
    "EmbeddingReferenceNode": {
        "why_existing_primitives_fail": (
            "Embedding references must carry provider-neutral source and reference "
            "metadata without storing or interpreting latent vectors."
        ),
        "formal_loss_if_reduced": (
            "Reducing to a generic evidence node would blur external latent reference "
            "linking with biological evidence claims."
        ),
    },
    "EvidenceScoreNode": {
        "why_existing_primitives_fail": (
            "Model-scoped numeric annotations need bounded validation while remaining "
            "disconnected from epistemic confidence."
        ),
        "formal_loss_if_reduced": (
            "Reducing to untyped metadata would lose the no-score-promotion validation " "surface required by ADR-0002."
        ),
    },
}


@dataclass(frozen=True)
class ProteinNode:
    """Metadata carrier for an externally referenced protein identifier."""

    identifier: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    node_type: str = "ProteinNode"
    semantic_role: str = "metadata_only"


@dataclass(frozen=True)
class SequenceNode:
    """Metadata carrier for a protein sequence string."""

    sequence: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    node_type: str = "SequenceNode"
    semantic_role: str = "metadata_only"


@dataclass(frozen=True)
class EmbeddingReferenceNode:
    """Metadata carrier for an external embedding reference."""

    source: str
    reference: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    node_type: str = "EmbeddingReferenceNode"
    semantic_role: str = "metadata_only"


@dataclass(frozen=True)
class EvidenceScoreNode:
    """Metadata carrier for non-causal external evidence scores."""

    score_type: str
    value: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    node_type: str = "EvidenceScoreNode"
    semantic_role: str = "metadata_only"
