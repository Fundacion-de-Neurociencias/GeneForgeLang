"""
Test Suite: Reasoning and Scoring
==================================

Tests for the neuro-symbolic reasoning engine and confidence scoring.
Validates the core intelligence of the RAG system.
"""

import pytest
from unittest.mock import patch, MagicMock

try:
    from gfl_plugin_rag_engine import RAGEnginePlugin
except ImportError:
    pytest.skip("Plugin not installed", allow_module_level=True)


class TestConfidenceScoring:
    """Test confidence score computation from evidence."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_confidence_scoring_above_threshold(
        self, mock_gfl, mock_entrez, mock_chromadb, mock_evidence_high_confidence
    ):
        """Test confidence scoring with high-quality evidence (above threshold)."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Compute confidence with high-quality evidence
        confidence = plugin._compute_confidence(mock_evidence_high_confidence)

        # Should be high confidence (low distances mean high similarity)
        assert confidence > 0.65
        assert 0.0 <= confidence <= 1.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_confidence_scoring_below_threshold(
        self, mock_gfl, mock_entrez, mock_chromadb, mock_evidence_low_confidence
    ):
        """Test confidence scoring with low-quality evidence (below threshold)."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Compute confidence with low-quality evidence
        confidence = plugin._compute_confidence(mock_evidence_low_confidence)

        # Should be low confidence (high distances mean low similarity)
        assert confidence < 0.50
        assert 0.0 <= confidence <= 1.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_confidence_scoring_with_no_evidence(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test confidence scoring with no evidence."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Compute confidence with no evidence
        confidence = plugin._compute_confidence([])

        # Should be zero confidence
        assert confidence == 0.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_confidence_scoring_with_mixed_evidence(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test confidence scoring with mixed-quality evidence."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Mixed evidence (some good, some bad)
        mixed_evidence = [
            {"document": "Highly relevant", "metadata": {}, "distance": 0.1},
            {"document": "Somewhat relevant", "metadata": {}, "distance": 0.5},
            {"document": "Not relevant", "metadata": {}, "distance": 0.9},
        ]

        confidence = plugin._compute_confidence(mixed_evidence)

        # Should be moderate confidence
        assert 0.3 < confidence < 0.7
        assert 0.0 <= confidence <= 1.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_confidence_scoring_bounds(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that confidence scores are always bounded [0, 1]."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Test extreme cases
        extreme_evidence = [
            {"document": "Perfect match", "metadata": {}, "distance": 0.0},
            {"document": "No match", "metadata": {}, "distance": 1.0},
            {"document": "Beyond", "metadata": {}, "distance": 2.0},
        ]

        confidence = plugin._compute_confidence(extreme_evidence)

        # Must be bounded
        assert 0.0 <= confidence <= 1.0


class TestHypothesisValidation:
    """Test complete hypothesis validation pipeline."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_validate_hypothesis_with_evidence(
        self, mock_gfl, mock_entrez, mock_chromadb, sample_hypothesis, mock_abstracts
    ):
        """Test hypothesis validation with available evidence."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [["TP53 is associated with lung cancer"]],
            "metadatas": [[{"pmid": "12345", "gene": "TP53"}]],
            "distances": [[0.15]],
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock PubMed
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            {"IdList": ["12345", "67890"]},
            {
                "PubmedArticle": [
                    {
                        "MedlineCitation": {
                            "PMID": "12345",
                            "Article": {
                                "ArticleTitle": "TP53 in lung cancer",
                                "Abstract": {"AbstractText": ["Study of TP53"]},
                            },
                        }
                    }
                ]
            },
        ]
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()

        # Validate hypothesis
        result = plugin._validate_hypothesis(sample_hypothesis, top_k=5)

        # Verify result structure
        assert "hypothesis_id" in result
        assert "gene" in result
        assert "disease" in result
        assert "evidence_count" in result
        assert "confidence" in result
        assert "top_evidence" in result

        # Verify data
        assert result["hypothesis_id"] == sample_hypothesis["id"]
        assert result["gene"] == sample_hypothesis["gene"]
        assert result["disease"] == sample_hypothesis["disease"]
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_validate_hypothesis_without_evidence(
        self, mock_gfl, mock_entrez, mock_chromadb, sample_hypothesis
    ):
        """Test hypothesis validation when no evidence is found."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock empty PubMed results
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": []}

        plugin = RAGEnginePlugin()

        # Validate hypothesis
        result = plugin._validate_hypothesis(sample_hypothesis, top_k=5)

        # Should still return valid structure
        assert "hypothesis_id" in result
        assert "confidence" in result
        assert result["evidence_count"] == 0
        assert result["confidence"] == 0.0


class TestNeuroSymbolicReasoning:
    """Test neuro-symbolic reasoning integration."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_reasoning_combines_symbolic_and_neural(
        self, mock_gfl, mock_entrez, mock_chromadb, sample_hypothesis, mock_evidence_high_confidence
    ):
        """Test that reasoning combines symbolic constraints with neural retrieval."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        # Mock query to return high-confidence evidence
        mock_collection.query.return_value = {
            "documents": [[e["document"] for e in mock_evidence_high_confidence]],
            "metadatas": [[e["metadata"] for e in mock_evidence_high_confidence]],
            "distances": [[e["distance"] for e in mock_evidence_high_confidence]],
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock PubMed
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            {"IdList": ["12345"]},
            {
                "PubmedArticle": [
                    {
                        "MedlineCitation": {
                            "PMID": "12345",
                            "Article": {
                                "ArticleTitle": "Test",
                                "Abstract": {"AbstractText": ["Test abstract"]},
                            },
                        }
                    }
                ]
            },
        ]
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()

        # Perform validation
        result = plugin._validate_hypothesis(sample_hypothesis, top_k=5)

        # Symbolic component: Gene and disease from hypothesis
        assert result["gene"] == sample_hypothesis["gene"]
        assert result["disease"] == sample_hypothesis["disease"]

        # Neural component: Evidence from semantic search
        assert len(result["top_evidence"]) > 0

        # Synthesis: Confidence score combining both
        assert result["confidence"] > 0.0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_reasoning_handles_contradictory_evidence(
        self, mock_gfl, mock_entrez, mock_chromadb, sample_hypothesis
    ):
        """Test reasoning with contradictory evidence."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        # Mock contradictory evidence (very different distances)
        mock_collection.query.return_value = {
            "documents": [
                ["TP53 strongly associated with cancer", "No evidence linking TP53 to cancer"]
            ],
            "metadatas": [[{"pmid": "1"}, {"pmid": "2"}]],
            "distances": [[0.1, 0.9]],  # One says yes, one says no
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock PubMed
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            {"IdList": ["1"]},
            {
                "PubmedArticle": [
                    {
                        "MedlineCitation": {
                            "PMID": "1",
                            "Article": {
                                "ArticleTitle": "Test",
                                "Abstract": {"AbstractText": ["Test"]},
                            },
                        }
                    }
                ]
            },
        ]
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()

        # Validate
        result = plugin._validate_hypothesis(sample_hypothesis, top_k=5)

        # Should still produce a confidence score (averaged)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
        # With contradictory evidence, confidence should be moderate
        assert result["confidence"] < 0.9


class TestThresholdFiltering:
    """Test evidence threshold filtering."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_threshold_filters_low_confidence(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl, temp_dir
    ):
        """Test that low-confidence hypotheses are filtered by threshold."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        # Mock low-confidence evidence
        mock_collection.query.return_value = {
            "documents": [["Irrelevant document"]],
            "metadatas": [[{"pmid": "999"}]],
            "distances": [[0.95]],  # Very high distance = low confidence
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser
        mock_gfl.return_value = {
            "hypothesis": [
                {
                    "id": "H_LowConf",
                    "if": [{"entity_is": {"gene": "TEST"}}, {"entity_is": {"disease": "Test"}}],
                }
            ]
        }

        # Mock PubMed
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": []}

        plugin = RAGEnginePlugin()
        output = temp_dir / "output.json"

        # Run with high threshold
        result = plugin.run(
            str(valid_hypothesis_gfl), str(output), params={"evidence_threshold": 0.80}
        )

        # Should filter out low-confidence hypothesis
        assert (
            result["hypotheses_validated"] == 0
            or result["hypotheses_validated"] < result["hypotheses_total"]
        )

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_threshold_accepts_high_confidence(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl, temp_dir
    ):
        """Test that high-confidence hypotheses pass threshold."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        # Mock high-confidence evidence
        mock_collection.query.return_value = {
            "documents": [["Highly relevant document about the hypothesis"]],
            "metadatas": [[{"pmid": "12345", "gene": "TP53"}]],
            "distances": [[0.1]],  # Low distance = high confidence
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser
        mock_gfl.return_value = {
            "hypothesis": [
                {
                    "id": "H_HighConf",
                    "if": [{"entity_is": {"gene": "TP53"}}, {"entity_is": {"disease": "Cancer"}}],
                }
            ]
        }

        # Mock PubMed with good results
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            {"IdList": ["12345"]},
            {
                "PubmedArticle": [
                    {
                        "MedlineCitation": {
                            "PMID": "12345",
                            "Article": {
                                "ArticleTitle": "TP53 in cancer",
                                "Abstract": {"AbstractText": ["Study of TP53 in cancer"]},
                            },
                        }
                    }
                ]
            },
        ]
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()
        output = temp_dir / "output.json"

        # Run with moderate threshold
        result = plugin.run(
            str(valid_hypothesis_gfl), str(output), params={"evidence_threshold": 0.50}
        )

        # Should accept high-confidence hypothesis
        assert result["status"] == "success"
