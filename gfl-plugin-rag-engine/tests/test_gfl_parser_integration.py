"""
Test Suite: GFL Parser Integration
===================================

Tests for the integration with the official GFL parser.
Ensures correct parsing and extraction of hypothesis blocks.
"""

import pytest
from unittest.mock import patch, MagicMock

try:
    from gfl_plugin_rag_engine import RAGEnginePlugin
except ImportError:
    pytest.skip("Plugin not installed", allow_module_level=True)


class TestHypothesisParsing:
    """Test parsing of GFL hypothesis blocks."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_parses_valid_hypothesis_file(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl
    ):
        """Test parsing of a valid GFL file with multiple hypotheses."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock GFL parser to return 3 hypotheses
        mock_gfl.return_value = {
            "hypothesis": [
                {
                    "id": "H_TP53_LungCancer",
                    "description": "Test TP53 association",
                    "if": [
                        {"entity_is": {"gene": "TP53"}},
                        {"entity_is": {"disease": "Lung Cancer"}},
                    ],
                    "then": [{"relationship_is": "association"}],
                },
                {
                    "id": "H_BRCA1_BreastCancer",
                    "description": "Test BRCA1 role",
                    "if": [
                        {"entity_is": {"gene": "BRCA1"}},
                        {"entity_is": {"disease": "Breast Cancer"}},
                    ],
                    "then": [{"relationship_is": "causal"}],
                },
                {
                    "id": "H_CFTR_CysticFibrosis",
                    "description": "CFTR variants",
                    "if": [
                        {"entity_is": {"gene": "CFTR"}},
                        {"entity_is": {"disease": "Cystic Fibrosis"}},
                    ],
                    "then": [{"relationship_is": "causal"}],
                },
            ]
        }

        plugin = RAGEnginePlugin()
        hypotheses = plugin._parse_gfl_hypotheses(str(valid_hypothesis_gfl))

        # Verify correct number of hypotheses extracted
        assert len(hypotheses) == 3

        # Verify hypothesis structure
        for hyp in hypotheses:
            assert "id" in hyp
            assert "gene" in hyp
            assert "disease" in hyp
            assert "description" in hyp

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_extracts_gene_disease_pairs(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl
    ):
        """Test extraction of gene-disease pairs from hypotheses."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser with specific hypothesis
        mock_gfl.return_value = {
            "hypothesis": [
                {
                    "id": "H_Test",
                    "if": [
                        {"entity_is": {"gene": "TP53"}},
                        {"entity_is": {"disease": "Lung Cancer"}},
                    ],
                }
            ]
        }

        plugin = RAGEnginePlugin()
        hypotheses = plugin._parse_gfl_hypotheses(str(valid_hypothesis_gfl))

        # Verify gene-disease extraction
        assert len(hypotheses) == 1
        assert hypotheses[0]["gene"] == "TP53"
        assert hypotheses[0]["disease"] == "Lung Cancer"

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_handles_empty_file(self, mock_gfl, mock_entrez, mock_chromadb, empty_gfl):
        """Test handling of empty GFL file."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser to return empty dict
        mock_gfl.return_value = {}

        plugin = RAGEnginePlugin()
        hypotheses = plugin._parse_gfl_hypotheses(str(empty_gfl))

        # Should return empty list without crashing
        assert isinstance(hypotheses, list)
        assert len(hypotheses) == 0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_handles_file_with_no_hypotheses(
        self, mock_gfl, mock_entrez, mock_chromadb, gfl_without_hypotheses
    ):
        """Test handling of valid GFL file without hypothesis blocks."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser to return GFL without hypotheses
        mock_gfl.return_value = {
            "loci": [
                {"id": "BRCA1_locus", "chromosome": "chr17", "start": 43044295, "end": 43125483}
            ]
        }

        plugin = RAGEnginePlugin()
        hypotheses = plugin._parse_gfl_hypotheses(str(gfl_without_hypotheses))

        # Should return empty list
        assert isinstance(hypotheses, list)
        assert len(hypotheses) == 0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_handles_single_hypothesis(self, mock_gfl, mock_entrez, mock_chromadb, temp_dir):
        """Test handling of GFL file with single hypothesis (not a list)."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock parser returning single hypothesis (not list)
        mock_gfl.return_value = {
            "hypothesis": {
                "id": "H_Single",
                "if": [{"entity_is": {"gene": "MYC"}}, {"entity_is": {"disease": "Neuroblastoma"}}],
            }
        }

        # Create temp file
        gfl_file = temp_dir / "single_hyp.gfl"
        gfl_file.write_text("hypothesis:\n  id: H_Single")

        plugin = RAGEnginePlugin()
        hypotheses = plugin._parse_gfl_hypotheses(str(gfl_file))

        # Should convert single hypothesis to list
        assert isinstance(hypotheses, list)
        assert len(hypotheses) == 1
        assert hypotheses[0]["gene"] == "MYC"
        assert hypotheses[0]["disease"] == "Neuroblastoma"


class TestHypothesisExtraction:
    """Test hypothesis data extraction from AST nodes."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_extract_hypothesis_with_entity_is(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test extraction when using entity_is predicate."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Test hypothesis node
        hyp_node = {
            "id": "H_Test",
            "description": "Test description",
            "if": [{"entity_is": {"gene": "BRCA1"}}, {"entity_is": {"disease": "Breast Cancer"}}],
        }

        result = plugin._extract_hypothesis_data(hyp_node)

        assert result is not None
        assert result["gene"] == "BRCA1"
        assert result["disease"] == "Breast Cancer"
        assert result["id"] == "H_Test"
        assert result["description"] == "Test description"

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_extract_hypothesis_with_direct_keys(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test extraction when using direct gene/disease keys."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Test hypothesis node with direct keys
        hyp_node = {"id": "H_Direct", "if": [{"gene": "CFTR"}, {"disease": "Cystic Fibrosis"}]}

        result = plugin._extract_hypothesis_data(hyp_node)

        assert result is not None
        assert result["gene"] == "CFTR"
        assert result["disease"] == "Cystic Fibrosis"

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_extract_hypothesis_missing_entities(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test extraction when gene or disease is missing."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Hypothesis with no gene/disease
        hyp_node = {"id": "H_Invalid", "if": [{"other_predicate": "value"}]}

        result = plugin._extract_hypothesis_data(hyp_node)

        # Should return None for invalid hypothesis
        assert result is None

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_extract_hypothesis_with_only_gene(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test extraction when only gene is present."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Hypothesis with only gene
        hyp_node = {"id": "H_GeneOnly", "if": [{"entity_is": {"gene": "TP53"}}]}

        result = plugin._extract_hypothesis_data(hyp_node)

        # Should still extract (disease can be None)
        assert result is not None
        assert result["gene"] == "TP53"
        assert result["disease"] is None
