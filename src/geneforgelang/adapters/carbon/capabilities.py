from typing import Any, Tuple

from geneforgelang.semantic.capabilities import VariantSpec


class CarbonEmbedding:
    values: tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)


class CarbonContext:
    metadata = {"semantics_defined_by": "geneforgelang.eig"}


class CarbonSimilarity:
    value: float = 0.75


class CarbonVariantScore:
    confidence: float = 0.9
    source: str = "carbon"
    method: str = "predicted"
    value: float = 0.8
    metadata: dict = {}


class CarbonCapabilityProvider:
    def embedding(self, sequence: str) -> CarbonEmbedding:
        return CarbonEmbedding()

    def retrieve_context(self, entity: str) -> CarbonContext:
        return CarbonContext()

    def species_similarity(self, seq1: str, seq2: str) -> CarbonSimilarity:
        return CarbonSimilarity()

    def score_variant(self, variant: VariantSpec) -> CarbonVariantScore:
        return CarbonVariantScore()
