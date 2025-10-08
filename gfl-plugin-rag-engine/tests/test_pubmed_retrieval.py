"""
Test Suite: PubMed Retrieval
=============================

Tests for PubMed literature retrieval functionality.
Uses mocking to avoid real network calls during testing.
"""

import pytest
from unittest.mock import patch, MagicMock

try:
    from gfl_plugin_rag_engine import RAGEnginePlugin
except ImportError:
    pytest.skip("Plugin not installed", allow_module_level=True)


class TestPubMedRetrieval:
    """Test PubMed abstract retrieval with mocked API calls."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_retrieval_with_mock_entrez(
        self, mock_gfl, mock_entrez, mock_chromadb, mock_pubmed_search_results, mock_pubmed_response
    ):
        """Test successful PubMed retrieval with mocked Entrez."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock Entrez.esearch
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            mock_pubmed_search_results,  # First call: search results
            mock_pubmed_response,  # Second call: fetch results
        ]

        # Mock Entrez.efetch
        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()
        abstracts = plugin._fetch_pubmed_abstracts("TP53", "Lung Cancer")

        # Verify results
        assert len(abstracts) == 2
        assert abstracts[0]["pmid"] == "12345678"
        assert abstracts[0]["gene"] == "TP53"
        assert abstracts[0]["disease"] == "Lung Cancer"
        assert "TP53" in abstracts[0]["title"]
        assert len(abstracts[0]["abstract"]) > 0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_retrieval_handles_empty_results(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test handling of empty PubMed search results."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock empty search results
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": [], "Count": "0"}

        plugin = RAGEnginePlugin()
        abstracts = plugin._fetch_pubmed_abstracts("FAKEGENE", "FakeDisease")

        # Should return empty list
        assert isinstance(abstracts, list)
        assert len(abstracts) == 0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_retrieval_handles_network_error(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test handling of network errors during PubMed access."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock network error
        mock_entrez.esearch.side_effect = Exception("Network error")

        plugin = RAGEnginePlugin()
        abstracts = plugin._fetch_pubmed_abstracts("TP53", "Cancer")

        # Should handle error gracefully and return empty list
        assert isinstance(abstracts, list)
        assert len(abstracts) == 0

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_retrieval_handles_malformed_response(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test handling of malformed PubMed API responses."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Mock malformed response
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.side_effect = [
            {"IdList": ["12345"]},
            {
                "PubmedArticle": [
                    {
                        "MedlineCitation": {
                            # Missing required fields
                            "PMID": "12345"
                        }
                    }
                ]
            },
        ]

        mock_fetch_handle = MagicMock()
        mock_entrez.efetch.return_value = mock_fetch_handle

        plugin = RAGEnginePlugin()
        abstracts = plugin._fetch_pubmed_abstracts("TP53", "Cancer")

        # Should handle parsing errors and return what it can
        assert isinstance(abstracts, list)

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_retrieval_respects_max_results(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that max_results configuration is respected."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Create plugin with custom max_results
        plugin = RAGEnginePlugin(config={"max_results": 5})

        # Mock search
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle

        # Trigger search
        try:
            plugin._fetch_pubmed_abstracts("TP53", "Cancer")
        except:
            pass

        # Verify max_results was passed to esearch
        if mock_entrez.esearch.called:
            call_kwargs = mock_entrez.esearch.call_args[1]
            assert call_kwargs.get("retmax") == 5


class TestPubMedQueryConstruction:
    """Test PubMed query string construction."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_query_construction_with_gene_and_disease(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test query construction with both gene and disease."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Mock Entrez to capture query
        mock_search_handle = MagicMock()
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": []}

        plugin._fetch_pubmed_abstracts("BRCA1", "Breast Cancer")

        # Verify query was called with expected format
        assert mock_entrez.esearch.called
        call_kwargs = mock_entrez.esearch.call_args[1]
        query = call_kwargs.get("term", "")

        # Should contain gene and disease with appropriate PubMed tags
        assert "BRCA1" in query
        assert "Breast Cancer" in query


class TestAbstractIndexing:
    """Test indexing of abstracts into vector database."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_index_documents_with_valid_abstracts(
        self, mock_gfl, mock_entrez, mock_chromadb, mock_abstracts
    ):
        """Test indexing of valid abstracts."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Index abstracts
        plugin._index_documents(mock_abstracts)

        # Verify collection.add was called
        assert mock_collection.add.called

        # Verify correct structure
        call_kwargs = mock_collection.add.call_args[1]
        assert "documents" in call_kwargs
        assert "metadatas" in call_kwargs
        assert "ids" in call_kwargs

        # Verify data
        documents = call_kwargs["documents"]
        assert len(documents) == 2
        assert any("TP53" in doc for doc in documents)

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_index_documents_with_empty_list(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test indexing with empty abstract list."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Index empty list
        plugin._index_documents([])

        # Should not call collection.add
        assert not mock_collection.add.called

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_index_documents_handles_duplicate_pmids(
        self, mock_gfl, mock_entrez, mock_chromadb, mock_abstracts
    ):
        """Test handling of duplicate PMIDs during indexing."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.add.side_effect = Exception("Duplicate ID")
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Should handle error gracefully
        try:
            plugin._index_documents(mock_abstracts)
        except Exception as e:
            pytest.fail(f"Should not raise exception: {e}")


class TestKnowledgeBaseQuery:
    """Test querying of the knowledge base."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_query_knowledge_base_with_results(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test knowledge base query that returns results."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [
                [
                    "TP53 mutations are associated with lung cancer.",
                    "Studies show TP53 role in cancer development.",
                ]
            ],
            "metadatas": [
                [
                    {"pmid": "12345", "gene": "TP53", "title": "TP53 study"},
                    {"pmid": "67890", "gene": "TP53", "title": "Cancer research"},
                ]
            ],
            "distances": [[0.15, 0.22]],
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Query
        results = plugin._query_knowledge_base("TP53 lung cancer", n_results=5)

        # Verify results
        assert len(results) == 2
        assert all("document" in r for r in results)
        assert all("metadata" in r for r in results)
        assert all("distance" in r for r in results)

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_query_knowledge_base_empty_database(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test query on empty knowledge base."""
        # Mock empty ChromaDB
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

        plugin = RAGEnginePlugin()

        # Query
        results = plugin._query_knowledge_base("test query", n_results=5)

        # Should return empty list
        assert isinstance(results, list)
        assert len(results) == 0
