"""OpenMed Connector for GFL IR.

Stub of the OpenMed ecosystem. No OpenMed service is called: every result comes
from a small hardcoded table, hash-derived vectors or keyword matching, and is
labelled with provenance ``stub``.

Planned integration (not implemented):
- Biomedical embeddings (entity similarity)
- Clinical NER (entity extraction from text)
- Privacy filter (PII de-identification)
- PubMed retrieval (literature evidence)

No privacy guarantee is provided. The pattern-based redaction in
``_apply_privacy_filter`` is not a de-identification method and its output must
not be treated as anonymised.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from geneforgelang.provenance import (
    Provenance,
    ProvenancedDict,
    ProvenancedList,
    register_simulated_component,
    warn_first_use,
)

logger = logging.getLogger(__name__)

PROVENANCE = Provenance(
    "stub",
    "geneforgelang.ir.external.openmed_connector.OpenMedConnector",
    "unversioned",
)
register_simulated_component(
    "OpenMedConnector",
    PROVENANCE,
    "src/geneforgelang/ir/external/openmed_connector.py",
    "A connected OpenMed service and, for privacy, a validated de-identification filter "
    "with a recall test on labelled notes",
)


@dataclass
class OpenMedEntity:
    """A biomedical entity extracted by OpenMed NER."""

    text: str
    entity_type: str  # GENE, DISEASE, PHENOTYPE, etc.
    start: int
    end: int
    confidence: float
    normalized_id: str | None = None  # e.g., "HGNC:11998" for TP53
    provenance: Provenance = PROVENANCE


@dataclass
class SimilarEntity:
    """Entity with similarity score from embeddings."""

    entity_id: str
    entity_type: str
    similarity: float
    metadata: dict[str, Any]
    provenance: Provenance = PROVENANCE


class OpenMedConnector:
    """Connector to OpenMed biomedical knowledge services.

    Architecture placeholder - production would delegate to:
    - OpenMed API endpoints (embeddings, NER)
    - Local model inference (privacy-filter-nemotron)
    - PubMed Entrez for literature retrieval

    Today it calls none of them. Results are labelled ``stub`` and decision
    paths refuse them unless ``allow_simulated=True``. ``base_url`` and
    ``api_key`` are stored but never used.
    """

    provenance = PROVENANCE

    def __init__(
        self,
        api_key: str | None = None,
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

    def get_embedding(self, entity_id: str) -> list[float] | None:
        """Retrieve biomedical embedding for an entity.

        Production: Call OpenMed embeddings API.
        """
        warn_first_use("OpenMedConnector", PROVENANCE)
        entity_id = entity_id.upper()
        if entity_id in self._mock_knowledge:
            return ProvenancedList(self._mock_knowledge[entity_id]["embedding"], PROVENANCE)

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
        embedding = (embedding * (768 // len(embedding) + 1))[:768] if embedding else [0.0] * 768
        return ProvenancedList(embedding, PROVENANCE)

    def find_similar_entities(
        self, entity_id: str, entity_type: str | None = None, top_k: int = 5
    ) -> list[SimilarEntity]:
        """Find entities with similar embeddings.

        Uses cosine similarity over biomedical embeddings.
        """
        warn_first_use("OpenMedConnector", PROVENANCE)
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

        return ProvenancedList(
            [
                SimilarEntity(
                    entity_id=eid,
                    entity_type=self._mock_knowledge.get(eid, {}).get("function", "unknown"),
                    similarity=sim,
                    metadata=self._mock_knowledge.get(eid, {}),
                )
                for eid, sim in scores[:top_k]
            ],
            PROVENANCE,
        )

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        # Cosine similarity is bounded by [-1, 1]; clamp to remove floating-point
        # rounding that can push it marginally outside (e.g. 1.0000000000000033).
        # Round to 12 decimals so parallel vectors give exactly 1.0 instead of
        # 0.9999999999999999 (float noise far below any meaningful resolution).
        return max(-1.0, min(1.0, round(dot / (norm_a * norm_b), 12)))

    # ------------------------------------------------------------------
    # Named Entity Recognition (NER)
    # ------------------------------------------------------------------

    def extract_entities(self, text: str) -> list[OpenMedEntity]:
        """Extract biomedical entities from clinical/scientific text.

        Production: Call OpenMed NER model (openmed-clinical-ner).
        """
        warn_first_use("OpenMedConnector", PROVENANCE)
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

        return ProvenancedList(entities, PROVENANCE)

    # ------------------------------------------------------------------
    # Privacy Filter
    # ------------------------------------------------------------------

    def _apply_privacy_filter(self, text: str) -> str:
        """Redact four regular-expression patterns (name-like pairs, SSN, dates, emails).

        This is not de-identification and gives no privacy guarantee: it misses
        most identifiers and redacts non-identifiers.

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
        """Redact a clinical note with the stub filter and extract entities.

        Returns dict with cleaned text and extracted entities. ``privacy_cleared``
        is always ``False``: no real privacy filter is connected, so the text must
        not be treated as de-identified.
        """
        warn_first_use("OpenMedConnector", PROVENANCE)
        cleaned = self._apply_privacy_filter(note)
        entities = self.extract_entities(cleaned)

        return ProvenancedDict(
            {
                "original_length": len(note),
                "cleaned_text": cleaned,
                "cleaned_length": len(cleaned),
                "entities": [self._entity_to_dict(e) for e in entities],
                "privacy_cleared": False,  # RFC 002 flag: no real filter is connected
                "privacy_note": "stub redaction only; no privacy guarantee is provided",
            },
            PROVENANCE,
        )

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

    def search_literature(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search PubMed for relevant literature.

        Production: Use Biopython Entrez with OpenMed query expansion.
        """
        # Mock implementation - production calls PubMed API. The records below are
        # fabricated placeholders, not PubMed entries.
        warn_first_use("OpenMedConnector", PROVENANCE)
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

        return ProvenancedList(
            [ProvenancedDict(item, PROVENANCE) for item in mock_results[:max_results]],
            PROVENANCE,
        )

    def get_entity_knowledge(self, entity_id: str) -> dict[str, Any]:
        """Retrieve the stub knowledge entry for a biomedical entity."""
        warn_first_use("OpenMedConnector", PROVENANCE)
        entity_id = entity_id.upper()

        # Check mock database
        if entity_id in self._mock_knowledge:
            knowledge = dict(self._mock_knowledge[entity_id])
            knowledge["entity_id"] = entity_id
            knowledge["source"] = "OpenMed (stub)"
            return ProvenancedDict(knowledge, PROVENANCE)

        # Default: return minimal structure
        return ProvenancedDict(
            {
                "entity_id": entity_id,
                "function": "unknown",
                "pathways": [],
                "diseases": [],
                "source": "OpenMed (stub, not found)",
            },
            PROVENANCE,
        )
