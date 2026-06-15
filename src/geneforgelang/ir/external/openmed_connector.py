"""OpenMed Connector for GFL IR.

Integrates with OpenMed ecosystem:
- Biomedical embeddings (entity similarity)
- Clinical NER (entity extraction from text)
- Privacy filter (PII de-identification)
- PubMed retrieval (literature evidence)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import logging

logger = logging.getLogger(__name__)


@dataclass
class OpenMedEntity:
    """A biomedical entity extracted by OpenMed NER."""

    text: str
    entity_type: str  # GENE, DISEASE, PHENOTYPE, etc.
    start: int
    end: int
    confidence: float
    normalized_id: Optional[str] = None  # e.g., "HGNC:11998" for TP53


@dataclass
class SimilarEntity:
    """Entity with similarity score from embeddings."""

    entity_id: str
    entity_type: str
    similarity: float
    metadata: dict[str, Any]


class OpenMedConnector:
    """Connector to OpenMed biomedical knowledge services.

    Architecture placeholder - production would delegate to:
    - OpenMed API endpoints (embeddings, NER)
    - Local model inference (privacy-filter-nemotron)
    - PubMed Entrez for literature retrieval
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openmed.fdn.org/v1",
        enable_privacy_filter: bool = True,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.enable_privacy_filter = enable_privacy_filter

        # Mock embeddings database for development
        # Production: connect to OpenMed embeddings service
        self._mock_embeddings: dict[str, list[float]] = {}
        self._mock_knowledge: dict[str, dict[str, Any]] = {
            "TP53": {
                "embedding": [0.1] * 768,
                "function": "tumor_suppressor",
                "pathways": ["apoptosis", "cell_cycle_arrest"],
                "diseases": ["Li-Fraumeni_syndrome", "cancer"],
            },
            "KRAS": {
                "embedding": [0.2] * 768,
                "function": "signal_transducer",
                "pathways": ["MAPK", "PI3K_AKT"],
                "diseases": ["cancer", "Noonan_syndrome"],
            },
            "BRCA1": {
                "embedding": [0.3] * 768,
                "function": "dna_repair",
                "pathways": ["homologous_recombination"],
                "diseases": ["breast_cancer", "ovarian_cancer"],
            },
        }

    # ------------------------------------------------------------------
    # Embeddings & Similarity
    # ------------------------------------------------------------------

    def get_embedding(self, entity_id: str) -> Optional[list[float]]:
        """Retrieve biomedical embedding for an entity.

        Production: Call OpenMed embeddings API.
        """
        entity_id = entity_id.upper()
        if entity_id in self._mock_knowledge:
            return self._mock_knowledge[entity_id].get("embedding")

        # Fallback: generate deterministic mock embedding
        import hashlib

        hash_val = hashlib.md5(entity_id.encode()).hexdigest()
        # Use 2-char hex chunks, ensure we have at least 64 values by cycling
        embedding = []
        for i in range(0, len(hash_val), 2):
            chunk = hash_val[i : i + 2]
            if len(chunk) == 2:
                embedding.append(((int(chunk, 16) / 255.0) - 0.5) * 2)
        # Pad to 768 dimensions by repeating
        if embedding:
            embedding = (embedding * ((768 // len(embedding)) + 1))[:768]
        else:
            embedding = [0.0] * 768
        return embedding

    def find_similar_entities(
        self, entity_id: str, entity_type: Optional[str] = None, top_k: int = 5
    ) -> list[SimilarEntity]:
        """Find entities with similar embeddings.

        Uses cosine similarity over biomedical embeddings.
        """
        query_emb = self.get_embedding(entity_id)
        if query_emb is None:
            return []

        scores: list[tuple[str, float]] = []
        for other_id, knowledge in self._mock_knowledge.items():
            if other_id == entity_id.upper():
                continue
            if entity_type and knowledge.get("type") != entity_type:
                continue

            other_emb = knowledge.get("embedding")
            if other_emb:
                sim = self._cosine_similarity(query_emb, other_emb)
                scores.append((other_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)

        return [
            SimilarEntity(
                entity_id=eid,
                entity_type=self._mock_knowledge.get(eid, {}).get("function", "unknown"),
                similarity=sim,
                metadata=self._mock_knowledge.get(eid, {}),
            )
            for eid, sim in scores[:top_k]
        ]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    # ------------------------------------------------------------------
    # Named Entity Recognition (NER)
    # ------------------------------------------------------------------

    def extract_entities(self, text: str) -> list[OpenMedEntity]:
        """Extract biomedical entities from clinical/scientific text.

        Production: Call OpenMed NER model (openmed-clinical-ner).
        """
        if self.enable_privacy_filter:
            text = self._apply_privacy_filter(text)

        # Mock NER - production uses OpenMed clinical NER
        entities: list[OpenMedEntity] = []
        text_upper = text.upper()

        # Simple keyword matching for mock implementation
        known_genes = ["TP53", "KRAS", "BRCA1", "BRCA2", "MDM2", "EGFR", "MYC"]
        known_diseases = ["CANCER", "TUMOR", "CARCINOMA", "LEUKEMIA"]

        for gene in known_genes:
            idx = text_upper.find(gene)
            if idx >= 0:
                entities.append(
                    OpenMedEntity(
                        text=text[idx : idx + len(gene)],
                        entity_type="GENE",
                        start=idx,
                        end=idx + len(gene),
                        confidence=0.95,
                        normalized_id=gene,
                    )
                )

        for disease in known_diseases:
            idx = text_upper.find(disease)
            if idx >= 0:
                entities.append(
                    OpenMedEntity(
                        text=text[idx : idx + len(disease)],
                        entity_type="DISEASE",
                        start=idx,
                        end=idx + len(disease),
                        confidence=0.85,
                    )
                )

        return entities

    # ------------------------------------------------------------------
    # Privacy Filter
    # ------------------------------------------------------------------

    def _apply_privacy_filter(self, text: str) -> str:
        """De-identify PII from clinical text.

        Production: Use OpenMed/privacy-filter-nemotron.
        RFC 002: GFL Privacy Layer integration.
        """
        # Mock implementation - production uses Nemotron privacy filter
        import re

        # Simple PII patterns (production uses ML model)
        patterns = [
            (r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[PATIENT_NAME]"),  # Names
            (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),  # SSN
            (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "[DATE]"),  # Dates
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),  # Emails
        ]

        filtered = text
        for pattern, replacement in patterns:
            filtered = re.sub(pattern, replacement, filtered)

        return filtered

    def deidentify_clinical_note(self, note: str) -> dict[str, Any]:
        """Full de-identification pipeline for clinical notes.

        Returns dict with cleaned text and extracted entities.
        """
        cleaned = self._apply_privacy_filter(note)
        entities = self.extract_entities(cleaned)

        return {
            "original_length": len(note),
            "cleaned_text": cleaned,
            "cleaned_length": len(cleaned),
            "entities": [self._entity_to_dict(e) for e in entities],
            "privacy_cleared": True,  # Flag per RFC 002
        }

    def _entity_to_dict(self, entity: OpenMedEntity) -> dict[str, Any]:
        return {
            "text": entity.text,
            "type": entity.entity_type,
            "span": [entity.start, entity.end],
            "confidence": entity.confidence,
            "normalized_id": entity.normalized_id,
        }

    # ------------------------------------------------------------------
    # Literature Retrieval (PubMed Integration)
    # ------------------------------------------------------------------

    def search_literature(
        self, query: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Search PubMed for relevant literature.

        Production: Use Biopython Entrez with OpenMed query expansion.
        """
        # Mock implementation - production calls PubMed API
        logger.info(f"Searching literature: {query}")

        # Return mock results based on query keywords
        mock_results = []
        query_upper = query.upper()

        if "TP53" in query_upper or "P53" in query_upper:
            mock_results.append(
                {
                    "pmid": "12345678",
                    "title": "TP53 mutations in cancer progression",
                    "abstract": "TP53 is a tumor suppressor gene...",
                    "journal": "Nature",
                    "year": 2024,
                    "relevance": 0.95,
                }
            )

        if "KRAS" in query_upper:
            mock_results.append(
                {
                    "pmid": "23456789",
                    "title": "KRAS G12D mutations in pancreatic cancer",
                    "abstract": "KRAS mutations drive oncogenesis...",
                    "journal": "Science",
                    "year": 2023,
                    "relevance": 0.92,
                }
            )

        return mock_results[:max_results]

    def get_entity_knowledge(self, entity_id: str) -> dict[str, Any]:
        """Retrieve comprehensive knowledge about a biomedical entity."""
        entity_id = entity_id.upper()

        # Check mock database
        if entity_id in self._mock_knowledge:
            knowledge = dict(self._mock_knowledge[entity_id])
            knowledge["entity_id"] = entity_id
            knowledge["source"] = "OpenMed"
            return knowledge

        # Default: return minimal structure
        return {
            "entity_id": entity_id,
            "function": "unknown",
            "pathways": [],
            "diseases": [],
            "source": "OpenMed (not found)",
        }
