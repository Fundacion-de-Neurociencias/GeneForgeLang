from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from geneforgelang.semantic.capabilities import CapabilityEngine, EmbeddingVector


@dataclass(frozen=True)
class LatentNeighbor:
    item_id: str
    similarity: float
    embedding: EmbeddingVector


class LatentSpaceService:
    def __init__(self, engine: CapabilityEngine):
        self.engine = engine

    def similarity(self, left: str, right: str) -> float:
        return self._cosine(self.engine.embedding(left).values, self.engine.embedding(right).values)

    def nearest(self, query: str, candidates: dict[str, str], top_k: int = 5) -> list[LatentNeighbor]:
        query_embedding = self.engine.embedding(query)
        scored: list[LatentNeighbor] = []
        for item_id, sequence in candidates.items():
            embedding = self.engine.embedding(sequence)
            scored.append(
                LatentNeighbor(
                    item_id=item_id,
                    similarity=self._cosine(query_embedding.values, embedding.values),
                    embedding=embedding,
                )
            )
        return sorted(scored, key=lambda item: item.similarity, reverse=True)[:top_k]

    @staticmethod
    def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
        if len(left) != len(right):
            raise ValueError("embedding dimensions must match")
        left_norm = sqrt(sum(value * value for value in left))
        right_norm = sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
