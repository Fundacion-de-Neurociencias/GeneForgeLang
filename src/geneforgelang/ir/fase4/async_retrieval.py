"""Async retrieval capabilities for non-blocking knowledge fetching.

Provides:
- Async versions of all retrieval operations
- Concurrent fetching from multiple sources
- Background prefetching for anticipated queries
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Optional

from geneforgelang.ir.external.openmed_connector import OpenMedConnector
from geneforgelang.ir.external.huggingscience_connector import HuggingScienceConnector
from geneforgelang.ir.external.retrieval_service import (
    RetrievalContext,
    RetrievalService,
)
from geneforgelang.ir.fase4.cache_layer import EmbeddingCache
from geneforgelang.ir.state import BiologicalState
from geneforgelang.ir.strategy import Objective

logger = logging.getLogger(__name__)


@dataclass
class AsyncRetrievalResult:
    """Result from async retrieval operation."""

    context: Optional[RetrievalContext] = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    cache_hit: bool = False


class AsyncRetrievalService:
    """Async wrapper around RetrievalService with caching.

    Enables non-blocking retrieval for integration in event loops
    and concurrent fetching from multiple sources.
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        cache: Optional[EmbeddingCache] = None,
        max_workers: int = 4,
    ):
        self.retrieval = retrieval_service or RetrievalService()
        self.cache = cache or EmbeddingCache()
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._prefetch_queue: asyncio.Queue[str] = asyncio.Queue()
        self._prefetch_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Async Core Methods
    # ------------------------------------------------------------------

    async def retrieve_for_objective_async(
        self,
        objective: Objective,
        state: Optional[BiologicalState] = None,
        use_cache: bool = True,
    ) -> AsyncRetrievalResult:
        """Async version of retrieve_for_objective.

        Non-blocking retrieval with optional caching.
        """
        import time

        start = time.time()

        # Check cache first
        if use_cache and objective.target_entity:
            cache_key = f"obj:{objective.target_entity}:{hash(objective.description) % 10000}"
            cached = self.cache.get(cache_key)
            if cached and "context_data" in cached:
                # Reconstruct context from cache
                context = self._reconstruct_context(cached["context_data"], objective)
                elapsed = (time.time() - start) * 1000
                return AsyncRetrievalResult(
                    context=context,
                    elapsed_ms=elapsed,
                    cache_hit=True,
                )

        # Run sync retrieval in thread pool
        try:
            loop = asyncio.get_event_loop()
            context = await loop.run_in_executor(
                self._executor,
                self.retrieval.retrieve_for_objective,
                objective,
                state,
            )

            elapsed = (time.time() - start) * 1000

            # Cache result
            if use_cache:
                cache_key = f"obj:{objective.target_entity}:{hash(objective.description) % 10000}"
                self.cache.put(
                    cache_key,
                    {"context_data": self._serialize_context(context), "timestamp": time.time()},
                )

            return AsyncRetrievalResult(
                context=context,
                elapsed_ms=elapsed,
                cache_hit=False,
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"Async retrieval failed: {e}")
            return AsyncRetrievalResult(
                error=str(e),
                elapsed_ms=elapsed,
            )

    async def batch_retrieve_async(
        self,
        objectives: list[Objective],
        state: Optional[BiologicalState] = None,
    ) -> list[AsyncRetrievalResult]:
        """Retrieve for multiple objectives concurrently."""
        tasks = [
            self.retrieve_for_objective_async(obj, state) for obj in objectives
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def get_entity_knowledge_async(
        self, entity_id: str, use_cache: bool = True
    ) -> dict[str, Any]:
        """Async entity knowledge fetch."""
        # Check cache
        if use_cache:
            cached_emb = self.cache.get_embedding(entity_id)
            if cached_emb:
                # Also check if we have full knowledge cached
                cache_key = f"knowledge:{entity_id.upper()}"
                cached = self.cache.get(cache_key)
                if cached:
                    return cached.get("knowledge", {})

        # Fetch from OpenMed
        if self.retrieval.openmed:
            try:
                loop = asyncio.get_event_loop()
                knowledge = await loop.run_in_executor(
                    self._executor,
                    self.retrieval.openmed.get_entity_knowledge,
                    entity_id,
                )

                # Cache result
                if use_cache:
                    cache_key = f"knowledge:{entity_id.upper()}"
                    self.cache.put(cache_key, {"knowledge": knowledge, "entity_id": entity_id})
                    if "embedding" in knowledge:
                        self.cache.put_embedding(entity_id, knowledge["embedding"])

                return knowledge
            except Exception as e:
                logger.warning(f"Async knowledge fetch failed for {entity_id}: {e}")

        return {"entity_id": entity_id, "source": "error"}

    async def search_literature_async(
        self, query: str, max_results: int = 10, use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Async literature search with caching."""
        import hashlib

        # Check cache
        if use_cache:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
            cached = self.cache.get_literature(query_hash)
            if cached:
                logger.debug(f"Literature cache hit for: {query[:50]}...")
                return cached

        # Fetch from OpenMed
        if self.retrieval.openmed:
            try:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    self._executor,
                    self.retrieval.openmed.search_literature,
                    query,
                    max_results,
                )

                # Cache results
                if use_cache:
                    self.cache.put_literature(query, results)

                return results
            except Exception as e:
                logger.warning(f"Async literature search failed: {e}")

        return []

    # ------------------------------------------------------------------
    # Background Prefetching
    # ------------------------------------------------------------------

    def start_prefetching(self, prefetch_func: Optional[Callable[[str], Any]] = None) -> None:
        """Start background prefetching task."""
        if self._prefetch_task is None:
            self._prefetch_task = asyncio.create_task(
                self._prefetch_loop(prefetch_func)
            )
            logger.info("Started background prefetching")

    def stop_prefetching(self) -> None:
        """Stop background prefetching."""
        if self._prefetch_task:
            self._prefetch_task.cancel()
            self._prefetch_task = None
            logger.info("Stopped background prefetching")

    async def _prefetch_loop(self, prefetch_func: Optional[Callable[[str], Any]]) -> None:
        """Background loop for prefetching."""
        while True:
            try:
                entity_id = await asyncio.wait_for(
                    self._prefetch_queue.get(), timeout=1.0
                )
                # Prefetch knowledge
                await self.get_entity_knowledge_async(entity_id)
                logger.debug(f"Prefetched knowledge for {entity_id}")
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Prefetch error: {e}")

    def queue_prefetch(self, entity_id: str) -> None:
        """Queue an entity for background prefetching."""
        try:
            self._prefetch_queue.put_nowait(entity_id)
        except asyncio.QueueFull:
            logger.debug(f"Prefetch queue full, skipping {entity_id}")

    # ------------------------------------------------------------------
    # Concurrent Multi-Source Retrieval
    # ------------------------------------------------------------------

    async def retrieve_from_all_sources(
        self,
        entity_id: str,
        include_similar: bool = True,
        include_literature: bool = True,
        include_reasoning: bool = True,
    ) -> dict[str, Any]:
        """Concurrently retrieve from all available sources."""
        tasks = []

        # Knowledge
        tasks.append(("knowledge", self.get_entity_knowledge_async(entity_id)))

        # Similar entities
        if include_similar and self.retrieval.openmed:
            loop = asyncio.get_event_loop()
            tasks.append(
                (
                    "similar",
                    loop.run_in_executor(
                        self._executor,
                        self.retrieval.openmed.find_similar_entities,
                        entity_id,
                        None,
                        5,
                    ),
                )
            )

        # Literature
        if include_literature and self.retrieval.openmed:
            tasks.append(
                (
                    "literature",
                    self.search_literature_async(f"{entity_id} AND cancer", max_results=5),
                )
            )

        # Reasoning
        if include_reasoning and self.retrieval.huggingscience:
            loop = asyncio.get_event_loop()
            tasks.append(
                (
                    "reasoning",
                    loop.run_in_executor(
                        self._executor,
                        self.retrieval.huggingscience.reason_about_hypothesis,
                        f"Investigate {entity_id}",
                    ),
                )
            )

        # Execute all concurrently
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.warning(f"Source {name} failed: {e}")
                results[name] = None

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _serialize_context(self, context: RetrievalContext) -> dict[str, Any]:
        """Serialize context for caching."""
        return {
            "target_entity": context.target_entity,
            "similar_entities": [
                {"id": e.entity_id, "sim": e.similarity} for e in context.similar_entities
            ],
            "literature_count": len(context.literature_evidence),
            "has_reasoning": context.reasoning_result is not None,
            "combined_confidence": context.combined_confidence,
        }

    def _reconstruct_context(
        self, data: dict[str, Any], objective: Objective
    ) -> RetrievalContext:
        """Reconstruct context from cached data."""
        from geneforgelang.ir.external.openmed_connector import SimilarEntity

        similar = [
            SimilarEntity(
                entity_id=e["id"],
                entity_type="unknown",
                similarity=e["sim"],
                metadata={},
            )
            for e in data.get("similar_entities", [])
        ]

        return RetrievalContext(
            objective=objective,
            target_entity=data.get("target_entity"),
            similar_entities=similar,
            literature_evidence=[],  # Not cached, refetch if needed
            reasoning_result=None,  # Not cached, refetch if needed
            combined_confidence=data.get("combined_confidence", 0.0),
        )

    def close(self) -> None:
        """Cleanup resources."""
        self.stop_prefetching()
        self._executor.shutdown(wait=True)
