"""Canonical metadata-only AST nodes for protein evidence references."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ProteinNode:
    """Protein identifier metadata carrier."""

    identifier: str
    node_type: Literal["ProteinNode"] = "ProteinNode"
    semantic_role: Literal["metadata_only"] = "metadata_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_type": self.node_type,
            "identifier": self.identifier,
            "semantic_role": self.semantic_role,
        }


@dataclass(frozen=True)
class SequenceNode:
    """Protein sequence metadata carrier."""

    sequence: str
    node_type: Literal["SequenceNode"] = "SequenceNode"
    semantic_role: Literal["metadata_only"] = "metadata_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_type": self.node_type,
            "sequence": self.sequence,
            "semantic_role": self.semantic_role,
        }


@dataclass(frozen=True)
class EmbeddingReferenceNode:
    """External embedding provider reference metadata carrier."""

    provider: str
    node_type: Literal["EmbeddingReferenceNode"] = "EmbeddingReferenceNode"
    semantic_role: Literal["metadata_only"] = "metadata_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_type": self.node_type,
            "provider": self.provider,
            "semantic_role": self.semantic_role,
        }


@dataclass(frozen=True)
class EvidenceScoreNode:
    """External evidence score metadata carrier."""

    score_kind: Literal["structure_confidence", "plausibility_score"]
    value: float
    node_type: Literal["EvidenceScoreNode"] = "EvidenceScoreNode"
    semantic_role: Literal["metadata_only"] = "metadata_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_type": self.node_type,
            "score_kind": self.score_kind,
            "value": self.value,
            "semantic_role": self.semantic_role,
        }
