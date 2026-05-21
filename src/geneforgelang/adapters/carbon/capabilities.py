from __future__ import annotations

from dataclasses import dataclass

from geneforgelang.semantic.capabilities import (
    CompletionResult,
    EmbeddingVector,
    SequenceContext,
    SimilarityScore,
    VariantScore,
    VariantSpec,
)


@dataclass
class CarbonCapabilities:
    name: str = "carbon"
    version: str = "capability-adapter-0"

    def score_variant(self, variant: VariantSpec) -> VariantScore:
        pathogenic_hint = any(token in variant.variant.upper() for token in ("R175H", "LOSS", "STOP"))
        value = 0.91 if pathogenic_hint else 0.5
        return VariantScore(
            value=value,
            confidence=0.72 if pathogenic_hint else 0.45,
            source="carbon.vep",
            method="capability_adapter",
            metadata={"entity_id": variant.entity_id, "variant": variant.variant},
        )

    def embedding(self, sequence: str) -> EmbeddingVector:
        counts = tuple(float(sequence.upper().count(base)) for base in "ACGT")
        total = sum(counts) or 1.0
        return EmbeddingVector(
            values=tuple(value / total for value in counts),
            source="carbon.embedding",
            preserves=("base_composition",),
            collapses=("long_range_context",),
            distorts=("motif_order",),
            invariants=("length_normalized_composition",),
        )

    def complete_sequence(self, partial: str, context: SequenceContext) -> CompletionResult:
        suffix = "N" * max(0, 12 - len(partial))
        return CompletionResult(
            sequence=f"{partial.upper()}{suffix}",
            confidence=0.35,
            source="carbon.sequence_completion",
            alternatives=(),
        )

    def species_similarity(self, seq_a: str, seq_b: str) -> SimilarityScore:
        length = max(len(seq_a), len(seq_b), 1)
        matches = sum(a == b for a, b in zip(seq_a.upper(), seq_b.upper()))
        return SimilarityScore(
            value=matches / length,
            confidence=0.5,
            source="carbon.species_similarity",
            metadata={"length_a": len(seq_a), "length_b": len(seq_b)},
        )
