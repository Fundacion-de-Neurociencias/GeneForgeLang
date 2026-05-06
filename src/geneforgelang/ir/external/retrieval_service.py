"""Retrieval Service for GFL IR.

Integrates external knowledge sources (OpenMed, HuggingScience, PubMed)
into a unified retrieval pipeline for the reasoning loop.

Architecture:
- Retrieves evidence from multiple sources
- Ranks and synthesizes evidence
- Provides context for reasoning and planning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import logging

from geneforgelang.ir.external.huggingscience_connector import (
    HuggingScienceConnector,
    ReasoningResult,
)
from geneforgelang.ir.external.openmed_connector import OpenMedConnector, SimilarEntity
from geneforgelang.ir.state import BiologicalState
from geneforgelang.ir.strategy import Objective

logger = logging.getLogger(__name__)


@dataclass
class RetrievedEvidence:
    """Evidence retrieved from external sources."""

    source: str  # "openmed", "pubmed", "huggingscience"
    entity_id: Optional[str] = None
    evidence_type: str = "unknown"  # "similarity", "literature", "reasoning"
    content: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    relevance_score: float = 0.0


@dataclass
class RetrievalContext:
    """Complete retrieval context for a biological objective."""

    objective: Objective
    target_entity: Optional[str] = None
    similar_entities: list[SimilarEntity] = field(default_factory=list)
    literature_evidence: list[dict[str, Any]] = field(default_factory=list)
    reasoning_result: Optional[ReasoningResult] = None
    knowledge_summary: dict[str, Any] = field(default_factory=dict)
    combined_confidence: float = 0.0


class RetrievalService:
    """Unified retrieval service for external knowledge integration.

    Connects the GFL IR reasoning loop with:
    - OpenMed (embeddings, NER, literature)
    - HuggingScience (reasoning models)
    - PubMed (scientific literature)
    """

    def __init__(
        self,
        openmed: Optional[OpenMedConnector] = None,
        huggingscience: Optional[HuggingScienceConnector] = None,
        enable_openmed: bool = True,
        enable_huggingscience: bool = True,
    ):
        self.openmed = openmed or OpenMedConnector() if enable_openmed else None
        self.huggingscience = huggingscience or HuggingScienceConnector() if enable_huggingscience else None

        self.enable_openmed = enable_openmed
        self.enable_huggingscience = enable_huggingscience

    # ------------------------------------------------------------------
    # Core Retrieval Pipeline
    # ------------------------------------------------------------------

    def retrieve_for_objective(
        self,
        objective: Objective,
        state: Optional[BiologicalState] = None,
        max_literature: int = 5,
    ) -> RetrievalContext:
        """Execute full retrieval pipeline for a biological objective.

        This is the main entry point for integrating external knowledge
        into the GFL reasoning loop.
        """
        # Determine target entity (treat empty string as None)
        target = objective.target_entity
        if target == "":
            target = None
        if not target and state:
            target = self._infer_target_from_state(objective.description, state)

        context = RetrievalContext(
            objective=objective,
            target_entity=target,
        )

        if not target:
            logger.warning(f"Could not determine target entity for: {objective.description}")
            return context

        # 1. Retrieve similar entities (OpenMed embeddings)
        if self.enable_openmed and self.openmed:
            context.similar_entities = self.openmed.find_similar_entities(target, top_k=5)

        # 2. Retrieve literature evidence
        if self.enable_openmed and self.openmed:
            query = self._build_literature_query(target, objective.description)
            context.literature_evidence = self.openmed.search_literature(query, max_results=max_literature)

        # 3. Apply scientific reasoning
        if self.enable_huggingscience and self.huggingscience:
            hypothesis = f"{objective.description} for {target}"
            context.reasoning_result = self.huggingscience.reason_about_hypothesis(
                hypothesis, context.literature_evidence
            )

        # 4. Build knowledge summary
        context.knowledge_summary = self._build_knowledge_summary(target, context)

        # 5. Calculate combined confidence
        context.combined_confidence = self._calculate_combined_confidence(context)

        return context

    def retrieve_for_state(
        self,
        state: BiologicalState,
        query: Optional[str] = None,
    ) -> list[RetrievedEvidence]:
        """Retrieve evidence relevant to a biological state.

        Useful for enriching state before planning.
        """
        evidence: list[RetrievedEvidence] = []

        # Extract entities from state
        entity_ids = list(state.entities.keys())

        for eid in entity_ids:
            # Get OpenMed knowledge
            if self.enable_openmed and self.openmed:
                knowledge = self.openmed.get_entity_knowledge(eid)
                if knowledge.get("function") != "unknown":
                    evidence.append(
                        RetrievedEvidence(
                            source="openmed",
                            entity_id=eid,
                            evidence_type="knowledge",
                            content=knowledge,
                            confidence=0.9,
                            relevance_score=1.0,
                        )
                    )

                # Get similar entities
                similar = self.openmed.find_similar_entities(eid, top_k=3)
                for sim in similar:
                    evidence.append(
                        RetrievedEvidence(
                            source="openmed",
                            entity_id=eid,
                            evidence_type="similarity",
                            content={"similar_entity": sim.entity_id, "similarity": sim.similarity},
                            confidence=sim.similarity,
                            relevance_score=sim.similarity,
                        )
                    )

        return evidence

    # ------------------------------------------------------------------
    # Retrieval Methods
    # ------------------------------------------------------------------

    def get_entity_knowledge(self, entity_id: str) -> dict[str, Any]:
        """Get comprehensive knowledge about an entity."""
        if not self.enable_openmed or not self.openmed:
            return {"entity_id": entity_id, "source": "disabled"}

        return self.openmed.get_entity_knowledge(entity_id)

    def find_similar_entities(self, entity_id: str, top_k: int = 5) -> list[SimilarEntity]:
        """Find biologically similar entities."""
        if not self.enable_openmed or not self.openmed:
            return []

        return self.openmed.find_similar_entities(entity_id, top_k=top_k)

    def reason_about_edit(
        self, entity_id: str, edit_description: str
    ) -> Optional[ReasoningResult]:
        """Apply scientific reasoning to evaluate an edit."""
        if not self.enable_huggingscience or not self.huggingscience:
            return None

        hypothesis = f"{edit_description} on {entity_id}"
        return self.huggingscience.reason_about_hypothesis(hypothesis)

    def synthesize_evidence(
        self, hypothesis: str, evidence: list[RetrievedEvidence]
    ) -> dict[str, Any]:
        """Synthesize multiple evidence sources."""
        if not self.enable_huggingscience or not self.huggingscience:
            return {"synthesized": False, "hypothesis": hypothesis}

        # Convert to format expected by HuggingScience
        sources = [e.content for e in evidence if e.content]
        result = self.huggingscience.synthesize_evidence(hypothesis, sources)

        return {
            "synthesized": True,
            "hypothesis": result.hypothesis,
            "confidence": result.confidence_score,
            "supporting_count": len(result.supporting_evidence),
            "contradicting_count": len(result.contradicting_evidence),
            "knowledge_gaps": result.knowledge_gaps,
        }

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _infer_target_from_state(self, description: str, state: BiologicalState) -> Optional[str]:
        """Infer target entity from objective description and state."""
        # Try to match entity IDs mentioned in description
        desc_upper = description.upper()
        for eid in state.entities:
            if eid.upper() in desc_upper:
                return eid
        return None

    def _build_literature_query(self, target: str, description: str) -> str:
        """Build effective PubMed query."""
        # Extract key terms
        terms = [target]

        desc_lower = description.lower()
        if "knockout" in desc_lower or "loss" in desc_lower:
            terms.append("knockout")
        if "cancer" in desc_lower:
            terms.append("cancer")
        if "repair" in desc_lower:
            terms.append("DNA repair")

        return " AND ".join(terms)

    def _build_knowledge_summary(
        self, target: str, context: RetrievalContext
    ) -> dict[str, Any]:
        """Summarize retrieved knowledge."""
        summary: dict[str, Any] = {
            "target_entity": target,
            "similar_entities_count": len(context.similar_entities),
            "literature_count": len(context.literature_evidence),
            "has_reasoning": context.reasoning_result is not None,
        }

        # Add similar entities info
        if context.similar_entities:
            summary["similar_entities"] = [
                {"id": e.entity_id, "similarity": e.similarity} for e in context.similar_entities[:3]
            ]

        # Add reasoning conclusion
        if context.reasoning_result:
            summary["reasoning_conclusion"] = context.reasoning_result.conclusion
            summary["reasoning_confidence"] = context.reasoning_result.confidence

        return summary

    def _calculate_combined_confidence(self, context: RetrievalContext) -> float:
        """Calculate overall confidence from multiple sources."""
        scores = []

        # Literature evidence
        if context.literature_evidence:
            avg_relevance = sum(e.get("relevance", 0.5) for e in context.literature_evidence)
            avg_relevance /= len(context.literature_evidence)
            scores.append(avg_relevance)

        # Similar entities
        if context.similar_entities:
            avg_sim = sum(e.similarity for e in context.similar_entities)
            avg_sim /= len(context.similar_entities)
            scores.append(avg_sim)

        # Reasoning confidence
        if context.reasoning_result:
            scores.append(context.reasoning_result.confidence)

        if not scores:
            return 0.0

        return sum(scores) / len(scores)
