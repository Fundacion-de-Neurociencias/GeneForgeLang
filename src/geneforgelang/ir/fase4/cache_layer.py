"""Persistent cache layer for embeddings and retrieval results.

Uses ChromaDB for vector storage with disk persistence.
Provides caching for:
- Entity embeddings
- Similarity search results
- Literature retrieval results
- Reasoning outputs
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for embedding cache."""

    db_path: str = "./gfl_cache"
    collection_name: str = "embeddings"
    max_entries: int = 10000
    ttl_seconds: Optional[int] = None  # None = no expiration
    similarity_threshold: float = 0.95  # For deduplication


class EmbeddingCache:
    """Persistent cache for embeddings using ChromaDB.

    Architecture: Layer between IR connectors and external APIs.
    Reduces API calls and improves latency.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._client: Any = None
        self._collection: Any = None
        self._memory_cache: dict[str, Any] = {}  # L1: in-memory
        self._initialized = False

    def _init_chromadb(self) -> bool:
        """Initialize ChromaDB client."""
        if self._initialized:
            return True

        try:
            import chromadb
            from chromadb.config import Settings

            Path(self.config.db_path).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.Client(
                Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=self.config.db_path,
                )
            )

            self._collection = self._client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={"description": "GFL IR embedding cache"},
            )

            self._initialized = True
            logger.info(f"EmbeddingCache initialized: {self.config.db_path}")
            return True

        except ImportError:
            logger.warning("ChromaDB not available, using memory-only cache")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False

    # ------------------------------------------------------------------
    # Core Cache Operations
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Retrieve cached value by key."""
        # L1: Memory cache
        if key in self._memory_cache:
            return self._memory_cache[key]

        # L2: ChromaDB
        if self._init_chromadb() and self._collection:
            try:
                result = self._collection.get(ids=[key])
                if result and result.get("documents"):
                    # Parse stored JSON
                    data = json.loads(result["documents"][0])
                    # Promote to L1
                    self._memory_cache[key] = data
                    return data
            except Exception as e:
                logger.debug(f"Cache miss for {key}: {e}")

        return None

    def put(self, key: str, value: dict[str, Any], embedding: Optional[list[float]] = None) -> bool:
        """Store value in cache."""
        # L1: Always store in memory
        self._memory_cache[key] = value

        # L2: ChromaDB if available
        if self._init_chromadb() and self._collection:
            try:
                # Serialize value
                document = json.dumps(value)

                # Generate embedding if not provided
                if embedding is None:
                    embedding = self._generate_dummy_embedding(key)

                # Store with embedding for similarity search
                self._collection.add(
                    ids=[key],
                    documents=[document],
                    embeddings=[embedding],
                    metadatas=[{"cached_at": json.dumps(value.get("timestamp", ""))}],
                )
                return True
            except Exception as e:
                logger.warning(f"Failed to cache in ChromaDB: {e}")

        return True  # At least cached in memory

    def get_similar(
        self, embedding: list[float], n_results: int = 5, threshold: float = 0.9
    ) -> list[dict[str, Any]]:
        """Find similar cached entries by embedding similarity."""
        if not self._init_chromadb() or not self._collection:
            return []

        try:
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=min(n_results, self._collection.count()),
            )

            matches = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i] if results.get("distances") else 1.0
                    similarity = 1.0 - distance

                    if similarity >= threshold:
                        data = json.loads(doc)
                        data["_cache_similarity"] = similarity
                        matches.append(data)

            return matches

        except Exception as e:
            logger.warning(f"Similarity query failed: {e}")
            return []

    def invalidate(self, key: str) -> bool:
        """Remove entry from cache."""
        # L1
        self._memory_cache.pop(key, None)

        # L2
        if self._init_chromadb() and self._collection:
            try:
                self._collection.delete(ids=[key])
                return True
            except Exception as e:
                logger.warning(f"Failed to invalidate {key}: {e}")

        return True

    def clear(self) -> bool:
        """Clear all cached entries."""
        self._memory_cache.clear()

        if self._init_chromadb() and self._collection:
            try:
                # Delete and recreate collection
                self._client.delete_collection(self.config.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.config.collection_name,
                    metadata={"description": "GFL IR embedding cache"},
                )
                return True
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")

        return True

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "memory_entries": len(self._memory_cache),
            "db_path": self.config.db_path,
        }

        if self._init_chromadb() and self._collection:
            try:
                stats["persistent_entries"] = self._collection.count()
            except Exception:
                stats["persistent_entries"] = 0

        return stats

    # ------------------------------------------------------------------
    # Higher-level Operations
    # ------------------------------------------------------------------

    def get_embedding(self, entity_id: str) -> Optional[list[float]]:
        """Get cached embedding for entity."""
        cache_key = f"emb:{entity_id.upper()}"
        data = self.get(cache_key)

        if data and "embedding" in data:
            return data["embedding"]
        return None

    def put_embedding(self, entity_id: str, embedding: list[float], metadata: Optional[dict] = None) -> bool:
        """Cache embedding for entity."""
        cache_key = f"emb:{entity_id.upper()}"
        value = {
            "entity_id": entity_id,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": self._now(),
        }
        return self.put(cache_key, value, embedding)

    def get_literature(self, query_hash: str) -> Optional[list[dict]]:
        """Get cached literature results."""
        cache_key = f"lit:{query_hash}"
        data = self.get(cache_key)

        if data and "results" in data:
            return data["results"]
        return None

    def put_literature(self, query: str, results: list[dict]) -> bool:
        """Cache literature search results."""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        cache_key = f"lit:{query_hash}"

        value = {
            "query": query,
            "results": results,
            "timestamp": self._now(),
        }
        # No embedding for literature cache
        return self.put(cache_key, value, None)

    def get_reasoning(self, hypothesis_hash: str) -> Optional[dict]:
        """Get cached reasoning result."""
        cache_key = f"reason:{hypothesis_hash}"
        return self.get(cache_key)

    def put_reasoning(self, hypothesis: str, result: dict) -> bool:
        """Cache reasoning result."""
        hypothesis_hash = hashlib.md5(hypothesis.encode()).hexdigest()[:16]
        cache_key = f"reason:{hypothesis_hash}"

        value = {
            "hypothesis": hypothesis,
            "result": result,
            "timestamp": self._now(),
        }
        return self.put(cache_key, value, None)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _generate_dummy_embedding(self, key: str) -> list[float]:
        """Generate deterministic dummy embedding from key."""
        hash_val = hashlib.md5(key.encode()).hexdigest()
        embedding = []
        for i in range(0, len(hash_val), 2):
            chunk = hash_val[i : i + 2]
            if len(chunk) == 2:
                val = (int(chunk, 16) / 255.0) * 2 - 1  # Normalize to [-1, 1]
                embedding.append(val)
        # Pad/repeat to 768 dimensions
        if embedding:
            embedding = (embedding * ((768 // len(embedding)) + 1))[:768]
        else:
            embedding = [0.0] * 768
        return embedding

    def _now(self) -> str:
        """Current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()
