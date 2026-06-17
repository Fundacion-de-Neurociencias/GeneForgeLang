from __future__ import annotations

from dataclasses import dataclass

from geneforgelang.semantic.ir import BiologicalScale


@dataclass(frozen=True)
class ScaleCompilation:
    source_scale: str
    target_scale: str
    steps: tuple[str, ...]
    confidence: float


class ScaleCompiler:
    _order = (
        BiologicalScale.PHENOTYPE,
        BiologicalScale.PATHWAY,
        BiologicalScale.PROTEIN_INTERACTION,
        BiologicalScale.TRANSCRIPT,
        BiologicalScale.GENOMIC_LOCI,
        BiologicalScale.SEQUENCE_CONSTRAINTS,
    )

    def compile(self, source_scale: str, target_scale: str) -> ScaleCompilation:
        if source_scale not in self._order or target_scale not in self._order:
            raise ValueError("unknown biological scale")
        source_index = self._order.index(source_scale)
        target_index = self._order.index(target_scale)
        if source_index <= target_index:
            steps = self._order[source_index : target_index + 1]
        else:
            steps = tuple(reversed(self._order[target_index : source_index + 1]))
        distance = abs(target_index - source_index)
        return ScaleCompilation(
            source_scale=source_scale,
            target_scale=target_scale,
            steps=tuple(steps),
            confidence=max(0.1, 1.0 - 0.12 * distance),
        )
