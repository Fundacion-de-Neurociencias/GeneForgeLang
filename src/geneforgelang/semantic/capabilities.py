from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class VariantSpec:
    entity_id: str
    variant: str
    coordinate_system: str = "protein"
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class VariantScore:
    value: float
    confidence: float
    source: str
    method: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EmbeddingVector:
    values: tuple[float, ...]
    source: str
    preserves: tuple[str, ...] = ()
    collapses: tuple[str, ...] = ()
    distorts: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()


@dataclass(frozen=True)
class SequenceContext:
    species: str | None = None
    locus: str | None = None
    scale: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CompletionResult:
    sequence: str
    confidence: float
    source: str
    alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimilarityScore:
    value: float
    confidence: float
    source: str
    metadata: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class CapabilityEngine(Protocol):
    name: str
    version: str

    def score_variant(self, variant: VariantSpec) -> VariantScore:
        raise NotImplementedError

    def embedding(self, sequence: str) -> EmbeddingVector:
        raise NotImplementedError

    def complete_sequence(self, partial: str, context: SequenceContext) -> CompletionResult:
        raise NotImplementedError

    def species_similarity(self, seq_a: str, seq_b: str) -> SimilarityScore:
        raise NotImplementedError


class CapabilityRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, CapabilityEngine] = {}

    def register(self, engine: CapabilityEngine) -> None:
        missing = [
            method
            for method in (
                "score_variant",
                "embedding",
                "complete_sequence",
                "species_similarity",
            )
            if not callable(getattr(engine, method, None))
        ]
        if missing:
            raise TypeError(f"Capability engine {engine!r} is missing: {', '.join(missing)}")
        self._engines[engine.name] = engine

    def get(self, name: str) -> CapabilityEngine:
        return self._engines[name]

    def available(self) -> tuple[str, ...]:
        return tuple(self._engines)

    def engines(self) -> tuple[CapabilityEngine, ...]:
        return tuple(self._engines.values())
