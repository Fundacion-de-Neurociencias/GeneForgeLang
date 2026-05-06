from __future__ import annotations

from typing import Any, Dict, List, Optional

from geneforgelang.ir.state import BiologicalState, Entity


class KnowledgeBase:
    """Ground biological entities with curated / retrieved biomedical knowledge.

    This is an *architecture* placeholder.  In production it would delegate to
    OpenMed embeddings, HuggingScience models, or a real biomedical KG.
    """

    def __init__(self, entries: Optional[Dict[str, Dict[str, Any]]] = None):
        self._entries = entries or {
            "TP53": {
                "function": "tumor_suppressor",
                "pathways": ["apoptosis", "cell_cycle_arrest", "dna_repair"],
                "interactors": ["MDM2", "ATM", "BAX", "CDKN1A"],
                "viability": "essential_in_most_contexts",
                "knockout_phenotype": "cell_cycle_dysregulation",
            },
            "KRAS": {
                "function": "signal_transducer",
                "pathways": ["MAPK", "PI3K_AKT"],
                "interactors": ["RAF1", "PIK3CA", "EGFR"],
                "viability": "context_dependent",
                "common_mutations": ["G12D", "G12V"],
            },
            "MDM2": {
                "function": "e3_ubiquitin_ligase",
                "pathways": ["p53_regulation"],
                "interactors": ["TP53"],
                "viability": "essential",
            },
            "BRCA1": {
                "function": "dna_repair",
                "pathways": ["homologous_recombination"],
                "interactors": ["BRCA2", "RAD51"],
                "viability": "essential_for_dna_repair",
            },
        }

    def query(self, concept: str) -> Dict[str, Any]:
        return self._entries.get(concept.upper(), {})

    def enrich_state(self, state: BiologicalState) -> BiologicalState:
        """Return a new state where every entity carries its grounded knowledge."""
        enriched = state.fork()
        for eid, entity in enriched.entities.items():
            knowledge = self.query(eid)
            if knowledge:
                entity.set_attr("knowledge", knowledge)
        return enriched

    def suggest_constraints(self, entity_id: str) -> List[str]:
        """Return biomedical constraints for an entity (e.g. 'essential', 'toxic')."""
        knowledge = self.query(entity_id)
        constraints: List[str] = []
        if knowledge.get("viability") == "essential_in_most_contexts":
            constraints.append("knockout_may_be_lethal")
        if knowledge.get("viability") == "essential":
            constraints.append("essential_gene")
        return constraints

    def is_viable_edit(self, entity_id: str, edit_description: str) -> bool:
        """Heuristic viability check — extensible to real predictive models."""
        knowledge = self.query(entity_id)
        viability = knowledge.get("viability", "")
        if "essential" in viability and "knockout" in edit_description.lower():
            return False
        return True
