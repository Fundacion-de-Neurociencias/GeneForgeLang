"""Tests for external knowledge connectors (Fase 3)."""

import pytest

from geneforgelang.ir.external import (
    HuggingScienceConnector,
    OpenMedConnector,
    RetrievedEvidence,
    RetrievalService,
)
from geneforgelang.ir.knowledge_grounding import KnowledgeBase
from geneforgelang.ir.state import BiologicalState, Entity, EntityType
from geneforgelang.ir.strategy import Objective


class TestOpenMedConnector:
    """Test OpenMed connector functionality."""

    def test_get_embedding_returns_vector(self):
        connector = OpenMedConnector()
        emb = connector.get_embedding("TP53")

        assert emb is not None
        assert len(emb) == 768  # Expected embedding dimension
        assert all(-1 <= x <= 1 for x in emb)  # Normalized range

    def test_get_embedding_deterministic_mock(self):
        """Mock embeddings should be deterministic for same entity."""
        connector = OpenMedConnector()
        emb1 = connector.get_embedding("UNKNOWN_GENE")
        emb2 = connector.get_embedding("UNKNOWN_GENE")

        assert emb1 == emb2

    def test_find_similar_entities(self):
        connector = OpenMedConnector()
        similar = connector.find_similar_entities("TP53", top_k=3)

        assert isinstance(similar, list)
        # Should find KRAS, BRCA1 as similar (all cancer-related)
        assert len(similar) > 0
        assert all(hasattr(s, "similarity") for s in similar)
        assert all(0 <= s.similarity <= 1 for s in similar)

    def test_extract_entities_from_text(self):
        connector = OpenMedConnector(enable_privacy_filter=False)
        text = "TP53 mutations are found in cancer patients with KRAS alterations"
        entities = connector.extract_entities(text)

        entity_texts = [e.text.upper() for e in entities]
        assert "TP53" in entity_texts
        assert "KRAS" in entity_texts or "CANCER" in entity_texts

    def test_privacy_filter_applied(self):
        connector = OpenMedConnector(enable_privacy_filter=True)
        text = "Patient John Smith has TP53 mutation"
        cleaned = connector._apply_privacy_filter(text)

        assert "John Smith" not in cleaned
        assert "[PATIENT_NAME]" in cleaned or "Patient" in cleaned

    def test_deidentify_clinical_note(self):
        connector = OpenMedConnector()
        note = "Patient: John Doe, DOB: 01/15/1980, Email: john@email.com"
        result = connector.deidentify_clinical_note(note)

        assert result["privacy_cleared"] is True
        assert len(result["cleaned_text"]) < len(note) or "[PATIENT_NAME]" in result["cleaned_text"]
        assert "entities" in result

    def test_search_literature(self):
        connector = OpenMedConnector()
        results = connector.search_literature("TP53 AND cancer", max_results=5)

        assert isinstance(results, list)
        # Should return mock TP53 results
        if results:
            assert "pmid" in results[0]
            assert "title" in results[0]

    def test_get_entity_knowledge(self):
        connector = OpenMedConnector()
        knowledge = connector.get_entity_knowledge("TP53")

        assert knowledge["entity_id"] == "TP53"
        assert "function" in knowledge
        assert knowledge["source"] == "OpenMed"


class TestHuggingScienceConnector:
    """Test HuggingScience connector functionality."""

    def test_reason_about_hypothesis(self):
        connector = HuggingScienceConnector()
        result = connector.reason_about_hypothesis("Knockout TP53 in cancer cells")

        assert result.conclusion != ""
        assert 0 <= result.confidence <= 1
        assert len(result.reasoning_chain) > 0
        assert "TP53" in str(result.reasoning_chain).upper()

    def test_reason_about_kras(self):
        connector = HuggingScienceConnector()
        result = connector.reason_about_hypothesis("Activate KRAS in lung cancer")

        assert "KRAS" in result.conclusion.upper() or "oncogenic" in result.conclusion.lower()
        assert result.confidence > 0

    def test_synthesize_evidence(self):
        connector = HuggingScienceConnector()
        evidence = [
            {"relevance": 0.9, "source": "pubmed"},
            {"relevance": 0.8, "source": "pubmed"},
            {"relevance": 0.2, "source": "uncertain"},
        ]
        result = connector.synthesize_evidence("TP53 knockout viability", evidence)

        assert "confidence_score" in result
        assert result["supporting_evidence_count"] >= 2 if "supporting_evidence_count" in result else len(result.get("supporting_evidence", [])) >= 2
        assert len(result.get("contradicting_evidence", [])) >= 1

    def test_answer_question(self):
        connector = HuggingScienceConnector()
        answer = connector.answer_question("What is the function of TP53?")

        assert "tumor suppressor" in answer["answer"].lower()
        assert answer["confidence"] > 0

    def test_batch_reason(self):
        connector = HuggingScienceConnector()
        hypotheses = [
            "Knockout TP53",
            "Activate KRAS",
            "Repair BRCA1",
        ]
        results = connector.batch_reason(hypotheses)

        assert len(results) == 3
        assert all(r.confidence > 0 for r in results)


class TestRetrievalService:
    """Test unified retrieval service."""

    def test_retrieve_for_objective(self):
        service = RetrievalService(enable_openmed=True, enable_huggingscience=True)
        objective = Objective(description="Knockout TP53 in cancer", target_entity="TP53")

        context = service.retrieve_for_objective(objective)

        assert context.target_entity == "TP53"
        assert len(context.similar_entities) > 0
        assert context.reasoning_result is not None
        assert context.combined_confidence > 0

    def test_retrieve_for_objective_no_target(self):
        service = RetrievalService()
        objective = Objective(description="Unknown gene knockout")

        context = service.retrieve_for_objective(objective)

        assert context.target_entity is None

    def test_retrieve_for_state(self):
        service = RetrievalService(enable_openmed=True)
        state = BiologicalState()
        state.add_entity(Entity(id="TP53", type=EntityType.GENE, attrs={"sequence": "ATCG"}))

        evidence = service.retrieve_for_state(state)

        assert len(evidence) > 0
        assert any(e.entity_id == "TP53" for e in evidence)

    def test_retrieve_for_state_disabled(self):
        service = RetrievalService(enable_openmed=False)
        state = BiologicalState()
        state.add_entity(Entity(id="TP53", type=EntityType.GENE))

        evidence = service.retrieve_for_state(state)

        assert len(evidence) == 0

    def test_reason_about_edit(self):
        service = RetrievalService(enable_huggingscience=True)
        result = service.reason_about_edit("TP53", "knockout")

        assert result is not None
        assert result.confidence > 0


class TestKnowledgeBaseWithRetrieval:
    """Test KnowledgeBase integration with external retrieval."""

    def test_knowledge_base_with_external_disabled(self):
        """Without external enabled, should use local curated data."""
        kb = KnowledgeBase(enable_external=False)
        knowledge = kb.query("TP53")

        assert knowledge["function"] == "tumor_suppressor"
        assert knowledge.get("source") == "curated"

    def test_knowledge_base_with_external_enabled(self):
        """With external enabled, should merge external data."""
        retrieval = RetrievalService(enable_openmed=True)
        kb = KnowledgeBase(retrieval_service=retrieval, enable_external=True)

        knowledge = kb.query("TP53")

        # Should have both curated and potentially external data
        assert knowledge["function"] == "tumor_suppressor"
        assert "sources" in knowledge

    def test_retrieve_for_objective_via_kb(self):
        retrieval = RetrievalService(enable_openmed=True, enable_huggingscience=True)
        kb = KnowledgeBase(retrieval_service=retrieval, enable_external=True)

        objective = Objective(description="Investigate TP53", target_entity="TP53")
        result = kb.retrieve_for_objective(objective)

        assert result["enabled"] is True
        assert result["target_entity"] == "TP53"

    def test_retrieve_for_objective_disabled(self):
        kb = KnowledgeBase(enable_external=False)
        objective = Objective(description="Test")

        result = kb.retrieve_for_objective(objective)

        assert result["enabled"] is False

    def test_enrich_with_retrieval(self):
        retrieval = RetrievalService(enable_openmed=True)
        kb = KnowledgeBase(retrieval_service=retrieval, enable_external=True)

        state = BiologicalState()
        state.add_entity(Entity(id="TP53", type=EntityType.GENE))

        enriched = kb.enrich_with_retrieval(state)

        # Should have enriched the entity with external data
        entity = enriched.get_entity("TP53")
        assert entity is not None

    def test_get_retrieval_service(self):
        retrieval = RetrievalService()
        kb = KnowledgeBase(retrieval_service=retrieval, enable_external=True)

        service = kb.get_retrieval_service()
        assert service is not None
        assert isinstance(service, RetrievalService)
