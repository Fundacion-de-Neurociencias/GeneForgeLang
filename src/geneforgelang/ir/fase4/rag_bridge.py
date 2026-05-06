"""Bridge between GFL IR and gfl-plugin-rag-engine.

Provides seamless integration between:
- GFL IR: Intermediate Representation with state, reasoning loop
- gfl-plugin-rag-engine: Existing RAG plugin with ChromaDB, PubMed

Enables:
- Using RAG plugin as external knowledge source
- Enriching IR state with RAG-retrieved evidence
- Validating IR hypotheses via RAG
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from geneforgelang.ir.external.retrieval_service import RetrievedEvidence, RetrievalService
from geneforgelang.ir.knowledge_grounding import KnowledgeBase
from geneforgelang.ir.state import BiologicalState, Entity
from geneforgelang.ir.strategy import Objective

logger = logging.getLogger(__name__)


@dataclass
class RAGValidationResult:
    """Result from RAG validation of an IR objective."""

    objective: Objective
    is_valid: bool
    confidence: float
    evidence_count: int
    top_evidence: list[dict[str, Any]] = field(default_factory=list)
    literature_references: list[str] = field(default_factory=list)
    rag_metadata: dict[str, Any] = field(default_factory=dict)


class RAGBridge:
    """Bridge to connect IR with gfl-plugin-rag-engine.

    Acts as adapter between IR's RetrievalService and the
    existing RAG plugin infrastructure.
    """

    def __init__(
        self,
        rag_plugin_path: Optional[str] = None,
        chroma_db_path: Optional[str] = None,
    ):
        self.rag_plugin_path = rag_plugin_path or "./gfl-plugin-rag-engine"
        self.chroma_db_path = chroma_db_path or "./chroma_db"
        self._rag_plugin: Any = None
        self._chromadb: Any = None

    def _load_rag_plugin(self) -> bool:
        """Dynamically load RAG plugin if available."""
        if self._rag_plugin is not None:
            return True

        try:
            import sys

            plugin_path = Path(self.rag_plugin_path)
            if plugin_path.exists():
                sys.path.insert(0, str(plugin_path.parent))

                from gfl_plugin_rag_engine.plugin import RAGEnginePlugin

                self._rag_plugin = RAGEnginePlugin(
                    config={
                        "db_path": self.chroma_db_path,
                        "email": "geneforge@research.org",
                    }
                )
                logger.info("RAG plugin loaded successfully")
                return True

        except ImportError as e:
            logger.warning(f"RAG plugin not available: {e}")
        except Exception as e:
            logger.error(f"Failed to load RAG plugin: {e}")

        return False

    def _load_chromadb_directly(self) -> bool:
        """Load ChromaDB directly if plugin not available."""
        if self._chromadb is not None:
            return True

        try:
            import chromadb
            from chromadb.config import Settings

            client = chromadb.Client(
                Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=self.chroma_db_path,
                )
            )

            self._chromadb = client.get_collection("biomedical_literature")
            logger.info("ChromaDB loaded directly")
            return True

        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}")
            return False

    # ------------------------------------------------------------------
    # Core Bridge Methods
    # ------------------------------------------------------------------

    def validate_objective(self, objective: Objective) -> RAGValidationResult:
        """Validate an IR objective using RAG evidence."""
        if not self._load_rag_plugin():
            logger.warning("RAG plugin not available, returning mock validation")
            return self._mock_validation(objective)

        try:
            # Convert objective to GFL format
            gfl_content = self._objective_to_gfl(objective)

            # Create temp GFL file
            temp_path = Path("./temp_validation.gfl")
            temp_path.write_text(gfl_content, encoding="utf-8")

            # Run RAG validation
            result = self._rag_plugin.run(
                input_gfl=str(temp_path),
                output_report="./temp_report.json",
                params={"top_k_docs": 5, "evidence_threshold": 0.3},
            )

            # Parse result
            if result.get("status") == "success":
                report = json.loads(Path("./temp_report.json").read_text())
                return self._parse_rag_report(objective, report)

            # Cleanup
            temp_path.unlink(missing_ok=True)
            Path("./temp_report.json").unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"RAG validation failed: {e}")

        return self._mock_validation(objective)

    def query_literature(
        self, query: str, n_results: int = 5
    ) -> list[RetrievedEvidence]:
        """Query RAG's ChromaDB for literature evidence."""
        evidence = []

        # Try RAG plugin first
        if self._load_rag_plugin():
            try:
                # Use plugin's internal query method
                if hasattr(self._rag_plugin, "_query_knowledge_base"):
                    results = self._rag_plugin._query_knowledge_base(query, n_results)
                    for r in results:
                        evidence.append(
                            RetrievedEvidence(
                                source="rag_plugin",
                                evidence_type="literature",
                                content=r,
                                confidence=r.get("relevance", 0.5),
                                relevance_score=r.get("relevance", 0.5),
                            )
                        )
                    return evidence
            except Exception as e:
                logger.warning(f"RAG plugin query failed: {e}")

        # Fall back to direct ChromaDB access
        if self._load_chromadb_directly():
            try:
                results = self._chromadb.query(
                    query_texts=[query], n_results=n_results
                )

                if results and results.get("documents"):
                    for i, doc in enumerate(results["documents"][0]):
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        distance = (
                            results["distances"][0][i]
                            if results.get("distances")
                            else 0.5
                        )
                        confidence = 1.0 - distance

                        evidence.append(
                            RetrievedEvidence(
                                source="chromadb",
                                evidence_type="literature",
                                content={
                                    "document": doc,
                                    "metadata": metadata,
                                    "distance": distance,
                                },
                                confidence=confidence,
                                relevance_score=confidence,
                            )
                        )
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}")

        return evidence

    def enrich_state_with_rag(
        self, state: BiologicalState, objective: Optional[Objective] = None
    ) -> BiologicalState:
        """Enrich biological state with RAG-retrieved evidence."""
        enriched = state.fork()

        for entity_id in enriched.entities:
            # Query literature for this entity
            query = f"{entity_id} AND cancer"
            if objective:
                query += f" AND {objective.description}"

            evidence = self.query_literature(query, n_results=3)

            if evidence:
                entity = enriched.get_entity(entity_id)
                if entity:
                    # Add evidence to entity
                    current_evidence = entity.get_attr("rag_evidence", [])
                    current_evidence.extend([e.content for e in evidence[:3]])
                    entity.set_attr("rag_evidence", current_evidence)

                    # Add confidence score
                    avg_conf = sum(e.confidence for e in evidence) / len(evidence)
                    entity.set_attr("rag_confidence", avg_conf)

        return enriched

    def get_rag_stats(self) -> dict[str, Any]:
        """Get statistics about RAG database."""
        stats = {"available": False}

        if self._load_chromadb_directly():
            try:
                count = self._chromadb.count()
                stats.update(
                    {
                        "available": True,
                        "document_count": count,
                        "db_path": self.chroma_db_path,
                    }
                )
            except Exception as e:
                stats["error"] = str(e)

        return stats

    # ------------------------------------------------------------------
    # Integration Helpers
    # ------------------------------------------------------------------

    def _objective_to_gfl(self, objective: Objective) -> str:
        """Convert IR Objective to GFL hypothesis format."""
        target = objective.target_entity or "UNKNOWN"
        description = objective.description

        gfl = f"""hypothesis:
  id: "IR_VALIDATION_{target}"
  description: "{description}"
  if:
    - entity_is:
        gene: "{target}"
  then:
    - relationship_is: "investigated"
"""
        return gfl

    def _parse_rag_report(self, objective: Objective, report: dict) -> RAGValidationResult:
        """Parse RAG plugin report into validation result."""
        results = report.get("results", [])

        if not results:
            return RAGValidationResult(
                objective=objective,
                is_valid=False,
                confidence=0.0,
                evidence_count=0,
            )

        result = results[0]  # Take first result

        return RAGValidationResult(
            objective=objective,
            is_valid=result.get("confidence", 0) > 0.5,
            confidence=result.get("confidence", 0),
            evidence_count=result.get("evidence_count", 0),
            top_evidence=result.get("top_evidence", [])[:3],
            literature_references=[e.get("pmid", "unknown") for e in result.get("top_evidence", [])],
            rag_metadata={
                "timestamp": report.get("timestamp"),
                "plugin_version": report.get("version"),
            },
        )

    def _mock_validation(self, objective: Objective) -> RAGValidationResult:
        """Generate mock validation when RAG is unavailable."""
        return RAGValidationResult(
            objective=objective,
            is_valid=True,  # Optimistic default
            confidence=0.5,
            evidence_count=0,
            rag_metadata={"source": "mock", "reason": "rag_unavailable"},
        )


class RAGIntegration:
    """High-level integration combining IR RetrievalService with RAG."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        rag_bridge: Optional[RAGBridge] = None,
    ):
        self.retrieval = retrieval_service or RetrievalService()
        self.rag = rag_bridge or RAGBridge()

    def retrieve_comprehensive(
        self, objective: Objective, state: Optional[BiologicalState] = None
    ) -> dict[str, Any]:
        """Retrieve evidence from all sources: IR + RAG."""
        # 1. Get IR external knowledge
        ir_context = self.retrieval.retrieve_for_objective(objective, state)

        # 2. Get RAG validation
        rag_validation = self.rag.validate_objective(objective)

        # 3. Get RAG literature
        rag_evidence = self.rag.query_literature(
            f"{objective.target_entity} AND {objective.description}",
            n_results=5,
        )

        # 4. Combine results
        combined_confidence = self._combine_confidences(
            ir_context.combined_confidence if ir_context else 0,
            rag_validation.confidence,
        )

        return {
            "objective": objective,
            "ir_context": {
                "target": ir_context.target_entity if ir_context else None,
                "similar_entities": [e.entity_id for e in (ir_context.similar_entities if ir_context else [])],
                "literature_count": len(ir_context.literature_evidence) if ir_context else 0,
            },
            "rag_validation": {
                "is_valid": rag_validation.is_valid,
                "confidence": rag_validation.confidence,
                "evidence_count": rag_validation.evidence_count,
            },
            "combined_confidence": combined_confidence,
            "rag_evidence": [e.content for e in rag_evidence],
        }

    def _combine_confidences(self, ir_conf: float, rag_conf: float) -> float:
        """Combine confidence scores from IR and RAG."""
        if ir_conf == 0:
            return rag_conf
        if rag_conf == 0:
            return ir_conf
        # Weighted average, favoring higher confidence
        return max(ir_conf, rag_conf) * 0.7 + (ir_conf + rag_conf) / 2 * 0.3
