"""Feedback loop for retrieval quality improvement.

Tracks retrieval outcomes and learns to improve future retrievals.
Provides:
- Success/failure tracking per query type
- Quality scoring for retrieved evidence
- Adaptive retrieval strategies based on feedback
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class RetrievalFeedback:
    """Feedback record for a retrieval operation."""

    query: str
    query_type: str  # "entity", "literature", "reasoning", "objective"
    target_entity: Optional[str] = None

    # Outcome
    success: bool = True
    confidence_score: float = 0.0
    user_rating: Optional[int] = None  # 1-5 scale

    # Retrieved data quality
    results_count: int = 0
    relevance_scores: list[float] = field(default_factory=list)

    # Timing
    retrieval_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Context
    iteration: int = 0  # Reasoning loop iteration
    final_objective_achieved: Optional[bool] = None

    def quality_score(self) -> float:
        """Calculate overall quality score from feedback."""
        if self.user_rating:
            return self.user_rating / 5.0

        if self.relevance_scores:
            avg_relevance = sum(self.relevance_scores) / len(self.relevance_scores)
            return avg_relevance * self.confidence_score

        return self.confidence_score


class FeedbackStore:
    """Store and analyze retrieval feedback for learning.

    Persistent storage of feedback with analytics for
    improving retrieval strategies.
    """

    def __init__(self, storage_path: str = "./gfl_feedback.jsonl"):
        self.storage_path = Path(storage_path)
        self._feedback_cache: list[RetrievalFeedback] = []
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing feedback from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        feedback = RetrievalFeedback(**data)
                        self._feedback_cache.append(feedback)
                    except Exception:
                        continue
            logger.info(f"Loaded {len(self._feedback_cache)} feedback records")
        except Exception as e:
            logger.warning(f"Failed to load feedback: {e}")

    def record(self, feedback: RetrievalFeedback) -> bool:
        """Record new feedback."""
        self._feedback_cache.append(feedback)

        try:
            # Append to file
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback.__dict__, default=str) + "\n")
            return True
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def get_stats(self, query_type: Optional[str] = None) -> dict[str, Any]:
        """Get statistics for feedback records."""
        records = self._feedback_cache
        if query_type:
            records = [r for r in records if r.query_type == query_type]

        if not records:
            return {"count": 0}

        success_rate = sum(1 for r in records if r.success) / len(records)
        avg_confidence = sum(r.confidence_score for r in records) / len(records)
        avg_quality = sum(r.quality_score() for r in records) / len(records)
        avg_time = sum(r.retrieval_time_ms for r in records) / len(records)

        return {
            "count": len(records),
            "success_rate": success_rate,
            "avg_confidence": avg_confidence,
            "avg_quality": avg_quality,
            "avg_retrieval_time_ms": avg_time,
        }

    def get_entity_stats(self, entity_id: str) -> dict[str, Any]:
        """Get feedback statistics for a specific entity."""
        records = [r for r in self._feedback_cache if r.target_entity == entity_id.upper()]

        if not records:
            return {"entity": entity_id, "count": 0}

        return {
            "entity": entity_id,
            "count": len(records),
            "stats": self.get_stats(),
            "last_success": any(r.success for r in records[-5:]),
        }

    def suggest_improvements(self, query: str, query_type: str) -> list[str]:
        """Suggest improvements based on similar past queries."""
        suggestions = []

        # Find similar past queries
        similar = [
            r for r in self._feedback_cache
            if r.query_type == query_type and self._similarity(r.query, query) > 0.7
        ]

        if not similar:
            return suggestions

        # Analyze failures
        failures = [r for r in similar if not r.success]
        if len(failures) > len(similar) * 0.3:
            suggestions.append("High failure rate detected - consider alternative query formulation")

        # Check timing
        avg_time = sum(r.retrieval_time_ms for r in similar) / len(similar)
        if avg_time > 5000:  # > 5 seconds
            suggestions.append("Slow retrieval times - consider caching or prefetching")

        # Check confidence
        avg_conf = sum(r.confidence_score for r in similar) / len(similar)
        if avg_conf < 0.5:
            suggestions.append("Low confidence scores - verify data sources or query specificity")

        return suggestions

    def _similarity(self, a: str, b: str) -> float:
        """Simple word overlap similarity."""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        return len(intersection) / max(len(words_a), len(words_b))

    def get_best_practices(self) -> dict[str, list[str]]:
        """Extract best practices from successful retrievals."""
        best_practices = {}

        for query_type in ["entity", "literature", "reasoning", "objective"]:
            records = [r for r in self._feedback_cache if r.query_type == query_type]
            successful = [r for r in records if r.success and r.confidence_score > 0.7]

            if not successful:
                continue

            # Extract common patterns
            avg_results = sum(r.results_count for r in successful) / len(successful)
            avg_time = sum(r.retrieval_time_ms for r in successful) / len(successful)

            practices = [
                f"Optimal results count: {avg_results:.1f}",
                f"Target retrieval time: {avg_time:.0f}ms",
            ]

            if len(successful) > 10:
                practices.append(f"High reliability ({len(successful)} successful retrievals)")

            best_practices[query_type] = practices

        return best_practices


class AdaptiveRetriever:
    """Retriever that adapts based on feedback."""

    def __init__(self, base_retriever: Any, feedback_store: FeedbackStore):
        self.base = base_retriever
        self.feedback = feedback_store
        self._strategy_cache: dict[str, str] = {}

    async def retrieve_with_adaptation(
        self, query: str, query_type: str, **kwargs
    ) -> tuple[Any, RetrievalFeedback]:
        """Retrieve with automatic strategy adaptation."""
        import time

        start = time.time()

        # Check for suggested improvements
        suggestions = self.feedback.suggest_improvements(query, query_type)

        # Adapt strategy based on feedback
        if "alternative query formulation" in str(suggestions):
            query = self._reformulate_query(query)

        # Execute retrieval
        result = await self._execute_retrieval(query, query_type, **kwargs)

        elapsed = (time.time() - start) * 1000

        # Create feedback record
        feedback = RetrievalFeedback(
            query=query,
            query_type=query_type,
            success=result is not None,
            retrieval_time_ms=elapsed,
        )

        # Record feedback
        self.feedback.record(feedback)

        return result, feedback

    async def _execute_retrieval(self, query: str, query_type: str, **kwargs) -> Any:
        """Execute the actual retrieval."""
        # This would integrate with the actual retriever
        # For now, placeholder
        return None

    def _reformulate_query(self, query: str) -> str:
        """Reformulate query based on learned patterns."""
        # Simple reformulation: add common terms that worked
        if "knockout" in query.lower():
            return query + " viability"
        return query
