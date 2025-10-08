"""
Test Suite: Plugin Interface
=============================

Tests for the RAGEnginePlugin interface, initialization, and basic functionality.
Ensures the plugin adheres to the standard GFL plugin contract.
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the plugin
try:
    from gfl_plugin_rag_engine import RAGEnginePlugin
except ImportError:
    pytest.skip("Plugin not installed", allow_module_level=True)


class TestPluginInstantiation:
    """Test plugin instantiation and initialization."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_plugin_instantiation(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that RAGEnginePlugin can be instantiated without errors."""
        # Mock ChromaDB client
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Instantiate plugin
        plugin = RAGEnginePlugin()

        # Verify basic attributes
        assert plugin.name == "gfl-plugin-rag-engine"
        assert plugin.version == "1.0.0"
        assert hasattr(plugin, "config")
        assert hasattr(plugin, "email")
        assert hasattr(plugin, "db_path")

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_plugin_instantiation_with_config(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test plugin initialization with custom configuration."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        # Custom configuration
        config = {"email": "custom@test.com", "db_path": "/custom/path", "max_results": 20}

        # Instantiate with config
        plugin = RAGEnginePlugin(config=config)

        # Verify config was applied
        assert plugin.email == "custom@test.com"
        assert plugin.db_path == "/custom/path"
        assert plugin.max_results == 20
        assert plugin.config == config

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_plugin_has_required_methods(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that plugin has all required methods."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Check required methods exist
        assert hasattr(plugin, "run")
        assert callable(plugin.run)
        assert hasattr(plugin, "validate_input")
        assert callable(plugin.validate_input)
        assert hasattr(plugin, "get_metadata")
        assert callable(plugin.get_metadata)


class TestRunMethodSignature:
    """Test the run method signature and parameters."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_run_method_signature(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that run method accepts expected parameters."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Check method signature
        import inspect

        sig = inspect.signature(plugin.run)
        params = list(sig.parameters.keys())

        assert "input_gfl" in params
        assert "output_report" in params
        assert "params" in params

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_run_returns_dict(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl, temp_dir
    ):
        """Test that run method returns a dictionary with status."""
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

        # Mock GFL parser
        mock_gfl.return_value = {
            "hypothesis": [
                {
                    "id": "H_Test",
                    "if": [{"entity_is": {"gene": "TP53"}}, {"entity_is": {"disease": "Cancer"}}],
                    "description": "Test",
                }
            ]
        }

        # Mock Entrez
        mock_search_handle = MagicMock()
        mock_search_handle.read.return_value = {"IdList": []}
        mock_entrez.esearch.return_value = mock_search_handle
        mock_entrez.read.return_value = {"IdList": []}

        plugin = RAGEnginePlugin()
        output = temp_dir / "output.json"

        # Run plugin
        result = plugin.run(str(valid_hypothesis_gfl), str(output))

        # Verify result structure
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ["success", "error", "warning"]
        assert "plugin" in result


class TestInputValidation:
    """Test input validation functionality."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_validate_input_with_valid_file(
        self, mock_gfl, mock_entrez, mock_chromadb, valid_hypothesis_gfl
    ):
        """Test input validation with a valid file."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Validate existing file
        assert plugin.validate_input(str(valid_hypothesis_gfl)) is True

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_validate_input_with_nonexistent_file(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test input validation with non-existent file."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Validate non-existent file
        assert plugin.validate_input("/nonexistent/file.gfl") is False

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_validate_input_with_empty_path(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test input validation with empty path."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()

        # Validate empty path
        assert plugin.validate_input("") is False
        assert plugin.validate_input(None) is False


class TestPluginMetadata:
    """Test plugin metadata functionality."""

    @patch("gfl_plugin_rag_engine.plugin.chromadb")
    @patch("gfl_plugin_rag_engine.plugin.Entrez")
    @patch("gfl_plugin_rag_engine.plugin.gfl_parse")
    def test_get_metadata(self, mock_gfl, mock_entrez, mock_chromadb):
        """Test that get_metadata returns proper structure."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        plugin = RAGEnginePlugin()
        metadata = plugin.get_metadata()

        # Verify metadata structure
        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert "version" in metadata
        assert "description" in metadata
        assert "capabilities" in metadata
        assert isinstance(metadata["capabilities"], list)

        # Verify content
        assert metadata["name"] == "gfl-plugin-rag-engine"
        assert metadata["version"] == "1.0.0"
        assert len(metadata["capabilities"]) > 0
