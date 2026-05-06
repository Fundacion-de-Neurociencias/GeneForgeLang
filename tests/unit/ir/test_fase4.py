"""Tests for Fase 4: Advanced Retrieval & Integration."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from geneforgelang.ir.fase4 import (
    AsyncRetrievalService,
    CacheConfig,
    EmbeddingCache,
    FeedbackStore,
    HopResult,
    MultiHopReasoner,
    RAGBridge,
    RAGIntegration,
    RetrievalFeedback,
)
from geneforgelang.ir.external import RetrievalService
from geneforgelang.ir.state import BiologicalState, Entity, EntityType, RelationType
from geneforgelang.ir.strategy import Objective


class TestEmbeddingCache:
    """Test persistent cache layer."""

    def test_cache_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = CacheConfig(db_path=tmpdir, collection_name="test")
            cache = EmbeddingCache(config)
            assert cache.config.db_path == tmpdir

    def test_cache_put_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = CacheConfig(db_path=tmpdir)
            cache = EmbeddingCache(config)

            # Store value
            cache.put("test_key", {"data": "value"}, embedding=[0.1] * 768)

            # Retrieve
            result = cache.get("test_key")
            assert result is not None
            assert result["data"] == "value"

    def test_cache_embedding_operations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(CacheConfig(db_path=tmpdir))

            # Store embedding
            emb = [0.5] * 768
            cache.put_embedding("TP53", emb, metadata={"function": "tumor_suppressor"})

            # Retrieve
            result = cache.get_embedding("TP53")
            assert result is not None
            assert len(result) == 768

    def test_cache_literature(self):
        import hashlib

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(CacheConfig(db_path=tmpdir))

            # Store literature results
            query = "TP53 cancer"
            results = [{"pmid": "123", "title": "Test"}]
            cache.put_literature(query, results)

            # Retrieve using same hash generation logic
            query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
            cached = cache.get_literature(query_hash)

            # Should work in memory-only mode too
            assert cached is not None
            assert len(cached) == 1

    def test_cache_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EmbeddingCache(CacheConfig(db_path=tmpdir))
            cache.put("key1", {"a": 1})
            cache.put("key2", {"b": 2})

            stats = cache.stats()
            assert stats["memory_entries"] == 2


class TestAsyncRetrievalService:
    """Test async retrieval capabilities."""

    @pytest.mark.asyncio
    async def test_async_retrieve_for_objective(self):
        service = AsyncRetrievalService()
        objective = Objective(description="Knockout TP53", target_entity="TP53")

        result = await service.retrieve_for_objective_async(objective)

        assert result.error is None
        assert result.context is not None
        assert result.elapsed_ms > 0

    @pytest.mark.asyncio
    async def test_async_entity_knowledge(self):
        service = AsyncRetrievalService()

        knowledge = await service.get_entity_knowledge_async("TP53")

        assert "entity_id" in knowledge
        assert knowledge["entity_id"] == "TP53"

    @pytest.mark.asyncio
    async def test_async_literature_search(self):
        service = AsyncRetrievalService()

        results = await service.search_literature_async("TP53 cancer", max_results=3)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_concurrent_multi_source(self):
        service = AsyncRetrievalService()

        results = await service.retrieve_from_all_sources(
            "TP53",
            include_similar=True,
            include_literature=True,
            include_reasoning=True,
        )

        assert "knowledge" in results


class TestFeedbackStore:
    """Test feedback loop functionality."""

    def test_record_feedback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FeedbackStore(storage_path=f"{tmpdir}/feedback.jsonl")

            feedback = RetrievalFeedback(
                query="TP53 knockout",
                query_type="entity",
                target_entity="TP53",
                success=True,
                confidence_score=0.9,
            )

            assert store.record(feedback) is True

    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FeedbackStore(storage_path=f"{tmpdir}/feedback.jsonl")

            # Record multiple feedbacks
            for i in range(5):
                store.record(
                    RetrievalFeedback(
                        query=f"query{i}",
                        query_type="entity",
                        success=True,
                        confidence_score=0.8,
                    )
                )

            stats = store.get_stats()
            assert stats["count"] == 5
            assert stats["success_rate"] == 1.0

    def test_suggest_improvements(self):
        store = FeedbackStore(storage_path="/dev/null")  # Don't persist

        # Record some feedback
        store.record(
            RetrievalFeedback(
                query="slow query",
                query_type="entity",
                success=False,
                retrieval_time_ms=10000,
            )
        )

        suggestions = store.suggest_improvements("slow query", "entity")
        assert len(suggestions) > 0

    def test_entity_stats(self):
        store = FeedbackStore(storage_path="/dev/null")

        store.record(
            RetrievalFeedback(
                query="TP53",
                query_type="entity",
                target_entity="TP53",
                success=True,
            )
        )

        stats = store.get_entity_stats("TP53")
        assert stats["entity"] == "TP53"
        assert stats["count"] == 1


class TestMultiHopReasoner:
    """Test multi-hop reasoning."""

    def test_reason_across_path(self):
        reasoner = MultiHopReasoner(max_hops=3)

        path = reasoner.reason_across_path(
            start_entity="TP53",
            end_entity=None,  # Explore
            hypothesis="Test hypothesis",
        )

        assert len(path.hops) > 0
        assert path.hops[0].entity_id == "TP53"
        assert path.overall_confidence >= 0

    def test_find_paths(self):
        from geneforgelang.ir.state import Relation

        state = BiologicalState()
        state.add_entity(Entity(id="TP53", type=EntityType.GENE))
        state.add_entity(Entity(id="MDM2", type=EntityType.GENE))
        state.add_relation(Relation(
            type=RelationType.REGULATES, source="TP53", target="MDM2"
        ))

        reasoner = MultiHopReasoner()
        paths = reasoner.find_paths("TP53", "MDM2", state, max_paths=2)

        assert isinstance(paths, list)
        # Should find at least one path via the relation

    def test_explain_relationship(self):
        reasoner = MultiHopReasoner()

        explanation = reasoner.explain_relationship("TP53", "KRAS")

        assert "relationship" in explanation
        assert "explanation" in explanation

    def test_hop_result_chain(self):
        path = HopResult(hop_number=0, entity_id="TP53")
        path.next_hop_candidates = ["MDM2", "BAX"]

        assert path.entity_id == "TP53"
        assert len(path.next_hop_candidates) == 2

    def test_multi_hop_path_explanation(self):
        from geneforgelang.ir.fase4.multi_hop import MultiHopPath

        hop1 = HopResult(hop_number=0, entity_id="TP53")
        hop2 = HopResult(hop_number=1, entity_id="MDM2")
        hop2.incoming_relations = [{"source": "TP53", "target": "MDM2", "type": "REGULATES"}]

        path = MultiHopPath(start_entity="TP53", end_entity="MDM2", hops=[hop1, hop2])

        chain = path.to_chain()
        assert chain == ["TP53", "MDM2"]

        explanation = path.explanation()
        assert "TP53" in explanation


class TestRAGBridge:
    """Test RAG integration bridge."""

    def test_bridge_init(self):
        bridge = RAGBridge()
        assert bridge.rag_plugin_path is not None

    def test_query_literature_mock(self):
        bridge = RAGBridge()

        # Without actual RAG plugin, should return empty or mock
        evidence = bridge.query_literature("TP53 cancer", n_results=3)
        assert isinstance(evidence, list)

    def test_enrich_state_with_rag(self):
        bridge = RAGBridge()

        state = BiologicalState()
        state.add_entity(Entity(id="TP53", type=EntityType.GENE, attrs={"sequence": "ATCG"}))

        enriched = bridge.enrich_state_with_rag(state)

        entity = enriched.get_entity("TP53")
        assert entity is not None

    def test_validate_objective(self):
        bridge = RAGBridge()
        objective = Objective(description="Test TP53", target_entity="TP53")

        result = bridge.validate_objective(objective)

        assert result.objective == objective
        assert hasattr(result, "is_valid")
        assert hasattr(result, "confidence")

    def test_get_rag_stats(self):
        bridge = RAGBridge()

        stats = bridge.get_rag_stats()
        assert "available" in stats


class TestRAGIntegration:
    """Test high-level RAG integration."""

    def test_retrieve_comprehensive(self):
        integration = RAGIntegration()
        objective = Objective(description="Investigate TP53", target_entity="TP53")

        result = integration.retrieve_comprehensive(objective)

        assert "ir_context" in result
        assert "rag_validation" in result
        assert "combined_confidence" in result

    def test_combine_confidences(self):
        integration = RAGIntegration()

        # Both confidences present
        combined = integration._combine_confidences(0.8, 0.6)
        assert combined > 0

        # One zero
        combined = integration._combine_confidences(0.8, 0.0)
        assert combined == 0.8

        # Both zero
        combined = integration._combine_confidences(0.0, 0.0)
        assert combined == 0.0
