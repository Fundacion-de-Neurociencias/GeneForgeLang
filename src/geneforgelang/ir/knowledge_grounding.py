from __future__ import annotations

from typing import Any, Optional

from geneforgelang.ir.external.retrieval_service import RetrievalService
from geneforgelang.ir.state import BiologicalState, Entity
from geneforgelang.ir.strategy import Objective


class KnowledgeBase:
    """Ground biological entities with curated / retrieved biomedical knowledge.

    Integrates local curated knowledge with external sources via RetrievalService:
    - OpenMed: Embeddings, NER, literature (per GFL Ecosystem Spec)
    - HuggingScience: Reasoning models for hypothesis validation

    Architecture follows TRANSFER_MEMORANDUM.md: GFL is the ground truth,
    external systems are observation providers (Axis 3).
    """

    def __init__(
        self,
        entries: Optional[dict[str, dict[str, Any]]] = None,
        retrieval_service: Optional[RetrievalService] = None,
        enable_external: bool = False,  # Opt-in for external API calls
    ):
        # Local curated knowledge (fallback / authoritative)
        self._entries = entries or {
            "TP53": {
                "function": "tumor_suppressor",
                "pathways": ["apoptosis", "cell_cycle_arrest", "dna_repair"],
                "interactors": ["MDM2", "ATM", "BAX", "CDKN1A"],
                "viability": "essential_in_most_contexts",
                "knockout_phenotype": "cell_cycle_dysregulation",
                "source": "curated",
            },
            "KRAS": {
                "function": "signal_transducer",
                "pathways": ["MAPK", "PI3K_AKT"],
                "interactors": ["RAF1", "PIK3CA", "EGFR"],
                "viability": "context_dependent",
                "common_mutations": ["G12D", "G12V"],
                "source": "curated",
            },
            "MDM2": {
                "function": "e3_ubiquitin_ligase",
                "pathways": ["p53_regulation"],
                "interactors": ["TP53"],
                "viability": "essential",
                "source": "curated",
            },
            "BRCA1": {
                "function": "dna_repair",
                "pathways": ["homologous_recombination"],
                "interactors": ["BRCA2", "RAD51"],
                "viability": "essential_for_dna_repair",
                "source": "curated",
            },
        }

        # External knowledge retrieval (Fase 3 integration)
        self._retrieval = retrieval_service
        self._enable_external = enable_external
        self._external_cache: dict[str, dict[str, Any]] = {}

    def query(self, concept: str) -> dict[str, Any]:
        """Query knowledge for a concept. Returns merged local + external data if enabled."""
        concept_upper = concept.upper()

        # Start with local curated knowledge
        local = self._entries.get(concept_upper, {})

        # Fetch from external if enabled and not in cache
        if self._enable_external and self._retrieval and concept_upper not in self._external_cache:
            try:
                external = self._retrieval.get_entity_knowledge(concept)
                self._external_cache[concept_upper] = external
            except Exception:
                self._external_cache[concept_upper] = {}

        # Merge external if available
        external = self._external_cache.get(concept_upper, {})
        if external and external.get("function") != "unknown":
            merged = dict(local)
            merged.update(external)
            merged["sources"] = ["curated", "openmed"]
            return merged

        return local

    def enrich_state(self, state: BiologicalState) -> BiologicalState:
        """Return a new state where every entity carries its grounded knowledge."""
        enriched = state.fork()
        for eid, entity in enriched.entities.items():
            knowledge = self.query(eid)
            if knowledge:
                entity.set_attr("knowledge", knowledge)
        return enriched

    def suggest_constraints(self, entity_id: str) -> list[str]:
        """Return biomedical constraints for an entity (e.g. 'essential', 'toxic')."""
        knowledge = self.query(entity_id)
        constraints: list[str] = []
        if knowledge.get("viability") == "essential_in_most_contexts":
            constraints.append("knockout_may_be_lethal")
        if knowledge.get("viability") == "essential":
            constraints.append("essential_gene")

        # Enhanced constraints via external reasoning (Fase 3)
        if self._enable_external and self._retrieval:
            reasoning = self._retrieval.reason_about_edit(entity_id, "any_edit")
            if reasoning and reasoning.confidence < 0.5:
                constraints.append("low_confidence_prediction")

        return constraints

    def is_viable_edit(self, entity_id: str, edit_description: str) -> bool:
        """Heuristic viability check — extensible to real predictive models."""
        knowledge = self.query(entity_id)
        viability = knowledge.get("viability", "")
        if "essential" in viability and "knockout" in edit_description.lower():
            return False

        # Enhanced viability check via HuggingScience reasoning (Fase 3)
        if self._enable_external and self._retrieval:
            reasoning = self._retrieval.reason_about_edit(entity_id, edit_description)
            if reasoning and reasoning.confidence < 0.3:
                return False

        return True

    # ------------------------------------------------------------------
    # Fase 3: External Knowledge Integration Methods
    # ------------------------------------------------------------------

    def retrieve_for_objective(
        self, objective: Objective, state: Optional[BiologicalState] = None
    ) -> dict[str, Any]:
        """Retrieve external knowledge for a biological objective.

        Returns comprehensive retrieval context including:
        - Similar entities (embeddings)
        - Literature evidence
        - Reasoning conclusions
        """
        if not self._enable_external or not self._retrieval:
            return {"enabled": False}

        from geneforgelang.ir.external.retrieval_service import RetrievalContext

        context = self._retrieval.retrieve_for_objective(objective, state)
        return {
            "enabled": True,
            "target_entity": context.target_entity,
            "similar_entities": [e.entity_id for e in context.similar_entities],
            "literature_count": len(context.literature_evidence),
            "reasoning_confidence": context.reasoning_result.confidence if context.reasoning_result else None,
            "combined_confidence": context.combined_confidence,
        }

    def enrich_with_retrieval(self, state: BiologicalState) -> BiologicalState:
        """Enrich state with retrieved external knowledge for all entities."""
        if not self._enable_external or not self._retrieval:
            return state

        enriched = state.fork()

        for eid in enriched.entities:
            # Get external knowledge
            ext_knowledge = self._retrieval.get_entity_knowledge(eid)
            if ext_knowledge.get("function") != "unknown":
                entity = enriched.get_entity(eid)
                if entity:
                    current = entity.get_attr("knowledge", {})
                    current["external"] = ext_knowledge
                    entity.set_attr("knowledge", current)

            # Get similar entities
            similar = self._retrieval.find_similar_entities(eid, top_k=3)
            if similar:
                entity = enriched.get_entity(eid)
                if entity:
                    entity.set_attr("similar_entities", [s.entity_id for s in similar])

        return enriched

    def get_retrieval_service(self) -> Optional[RetrievalService]:
        """Access the underlying retrieval service for advanced usage."""
        return self._retrieval
