"""Tests for the DataStagingManager functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from gfl.staging import DataStagingManager


class TestDataStagingManager:
    """Test cases for DataStagingManager."""

    def test_initialization(self):
        """Test DataStagingManager initialization."""
        manager = DataStagingManager()
        
        assert manager.temp_dir.exists()
        assert manager.temp_dir.name.startswith("gfl_run_")
        assert isinstance(manager.staged_files, dict)
        assert len(manager.staged_files) == 0
        
        # Cleanup
        manager.cleanup()

    def test_stage_files_basic(self):
        """Test basic file staging functionality."""
        manager = DataStagingManager()
        
        # Create mock data manifest
        data_manifest = {
            "sample.sam": "https://example.com/sample.sam",
            "reference.fasta": "https://example.com/reference.fasta",
            "config.json": "https://example.com/config.json"
        }
        
        # Create plugin parameters
        plugin_params = {
            "input_file": "sample.sam",
            "reference": "reference.fasta",
            "output_file": "result.bam",
            "threads": 4
        }
        
        # Mock the download function to create files instead of downloading
        with patch.object(manager, '_download_file_from_signed_url') as mock_download:
            def create_mock_file(signed_url, destination):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(f"Mock content for {destination.name}")
            
            mock_download.side_effect = create_mock_file
            
            # Stage files
            staged_params = manager.stage_files(plugin_params, data_manifest)
            
            # Verify that file parameters were updated with local paths
            assert staged_params["input_file"] == str(manager.temp_dir / "sample.sam")
            assert staged_params["reference"] == str(manager.temp_dir / "reference.fasta")
            assert staged_params["output_file"] == "result.bam"  # Not in manifest
            assert staged_params["threads"] == 4  # Not a file parameter
            
            # Verify files were created
            assert (manager.temp_dir / "sample.sam").exists()
            assert (manager.temp_dir / "reference.fasta").exists()
            
            # Verify staged_files tracking
            assert "sample.sam" in manager.staged_files
            assert "reference.fasta" in manager.staged_files
        
        # Cleanup
        manager.cleanup()

    def test_stage_files_no_manifest(self):
        """Test staging with empty manifest."""
        manager = DataStagingManager()
        
        plugin_params = {
            "input_file": "sample.sam",
            "threads": 4
        }
        
        result = manager.stage_files(plugin_params, {})
        
        # Parameters should remain unchanged
        assert result == plugin_params
        assert len(manager.staged_files) == 0
        
        # Cleanup
        manager.cleanup()

    def test_stage_files_no_matching_files(self):
        """Test staging with no matching files in manifest."""
        manager = DataStagingManager()
        
        plugin_params = {
            "input_file": "nonexistent.sam",
            "threads": 4
        }
        
        data_manifest = {
            "other.sam": "https://example.com/other.sam"
        }
        
        result = manager.stage_files(plugin_params, data_manifest)
        
        # Parameters should remain unchanged
        assert result == plugin_params
        assert len(manager.staged_files) == 0
        
        # Cleanup
        manager.cleanup()

    def test_stage_files_mixed_types(self):
        """Test staging with mixed parameter types."""
        manager = DataStagingManager()
        
        mixed_params = {
            "file_param": "test.txt",
            "int_param": 42,
            "float_param": 3.14,
            "bool_param": True,
            "none_param": None,
            "list_param": ["item1", "item2"]
        }
        
        data_manifest = {"test.txt": "https://example.com/test.txt"}
        
        # Mock download to create file
        with patch.object(manager, '_download_file_from_signed_url') as mock_download:
            def create_mock_file(signed_url, destination):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("Mock content")
            
            mock_download.side_effect = create_mock_file
            
            result = manager.stage_files(mixed_params, data_manifest)
            
            # Only file parameter should be modified
            assert result["file_param"] == str(manager.temp_dir / "test.txt")
            assert result["int_param"] == 42
            assert result["float_param"] == 3.14
            assert result["bool_param"] is True
            assert result["none_param"] is None
            assert result["list_param"] == ["item1", "item2"]
        
        # Cleanup
        manager.cleanup()

    def test_download_file_success(self):
        """Test successful file download."""
        manager = DataStagingManager()
        
        # Mock requests.get to return successful response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b"test content"]
            mock_get.return_value.__enter__.return_value = mock_response
            
            destination = manager.temp_dir / "test.txt"
            manager._download_file_from_signed_url("https://example.com/test.txt", destination)
            
            assert destination.exists()
            assert destination.read_text() == "test content"
        
        # Cleanup
        manager.cleanup()

    def test_download_file_failure(self):
        """Test file download failure."""
        manager = DataStagingManager()
        
        # Mock requests.get to raise an exception
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Download failed")
            
            destination = manager.temp_dir / "test.txt"
            
            with pytest.raises(Exception, match="Download failed"):
                manager._download_file_from_signed_url("https://example.com/test.txt", destination)
            
            assert not destination.exists()
        
        # Cleanup
        manager.cleanup()

    def test_cleanup(self):
        """Test cleanup functionality."""
        manager = DataStagingManager()
        temp_dir = manager.temp_dir
        
        # Create some test files
        (temp_dir / "test1.txt").write_text("content1")
        (temp_dir / "test2.txt").write_text("content2")
        (temp_dir / "subdir" / "test3.txt").write_text("content3")
        
        # Verify files exist
        assert temp_dir.exists()
        assert (temp_dir / "test1.txt").exists()
        assert (temp_dir / "subdir" / "test3.txt").exists()
        
        # Cleanup
        manager.cleanup()
        
        # Verify directory is removed
        assert not temp_dir.exists()

    def test_cleanup_nonexistent_directory(self):
        """Test cleanup when directory doesn't exist."""
        manager = DataStagingManager()
        temp_dir = manager.temp_dir
        
        # Remove directory manually
        import shutil
        shutil.rmtree(temp_dir)
        
        # Cleanup should not raise exception
        manager.cleanup()
        
        # Should not raise any exception
        assert True

    def test_stage_files_download_failure(self):
        """Test staging when download fails."""
        manager = DataStagingManager()
        
        plugin_params = {
            "input_file": "sample.sam",
            "threads": 4
        }
        
        data_manifest = {
            "sample.sam": "https://example.com/sample.sam"
        }
        
        # Mock download to fail
        with patch.object(manager, '_download_file_from_signed_url') as mock_download:
            mock_download.side_effect = Exception("Download failed")
            
            # Should not raise exception, but keep original parameter
            result = manager.stage_files(plugin_params, data_manifest)
            
            # Original parameter should be preserved
            assert result["input_file"] == "sample.sam"
            assert result["threads"] == 4
            assert len(manager.staged_files) == 0
        
        # Cleanup
        manager.cleanup()


class TestDataStagingIntegration:
    """Integration tests for DataStagingManager with GFL service."""

    def test_gfl_service_integration(self):
        """Test DataStagingManager integration with GFL service."""
        from gfl_service import ExecuteRequest
        
        # Create a mock AST with file parameters
        ast = {
            "experiment": {
                "tool": "samtools",
                "type": "alignment",
                "params": {
                    "input_file": "sample.sam",
                    "reference_file": "hg38.fasta",
                    "output_file": "aligned.bam",
                    "threads": 4
                }
            }
        }
        
        # Create data manifest
        data_manifest = {
            "sample.sam": "https://storage.googleapis.com/bucket/sample.sam?signature=abc123",
            "hg38.fasta": "https://storage.googleapis.com/bucket/hg38.fasta?signature=def456"
        }
        
        # Create execute request
        request = ExecuteRequest(
            ast=ast,
            context={},
            data_manifest=data_manifest
        )
        
        # Test that the request structure is correct
        assert "experiment" in request.ast
        assert "params" in request.ast["experiment"]
        assert "sample.sam" in request.data_manifest
        assert "hg38.fasta" in request.data_manifest
