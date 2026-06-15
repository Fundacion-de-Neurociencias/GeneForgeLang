"""Fase 4: Advanced Retrieval & Integration.

This module provides:
- Persistent cache layer (ChromaDB) for embeddings
- Async retrieval capabilities
- Feedback loop for retrieval quality
- Multi-hop reasoning across entity graphs
- Bridge between IR and gfl-plugin-rag-engine
"""

from geneforgelang.ir.fase4.cache_layer import EmbeddingCache, CacheConfig
from geneforgelang.ir.fase4.async_retrieval import AsyncRetrievalService
from geneforgelang.ir.fase4.feedback_loop import RetrievalFeedback, FeedbackStore
from geneforgelang.ir.fase4.multi_hop import MultiHopReasoner, HopResult
from geneforgelang.ir.fase4.rag_bridge import RAGBridge, RAGIntegration

__all__ = [
    "EmbeddingCache",
    "CacheConfig",
    "AsyncRetrievalService",
    "RetrievalFeedback",
    "FeedbackStore",
    "MultiHopReasoner",
    "HopResult",
    "RAGBridge",
    "RAGIntegration",
]
