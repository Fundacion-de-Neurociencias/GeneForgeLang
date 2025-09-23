"""High-level integration tests for DataStagingManager with GFL service."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from gfl.staging import DataStagingManager
from gfl_service import app


class TestDataStagingIntegration:
    """High-level integration tests for complete data staging workflow."""

    def test_complete_workflow_with_data_staging(self):
        """Test complete workflow: GFL service receives request with manifest -> staging -> plugin execution."""

        # Mock the DataStagingManager to avoid actual downloads
        with patch("gfl.staging.DataStagingManager") as mock_manager_class:
            # Create a mock manager instance
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Mock the staging behavior
            mock_manager.staged_files = {
                "sample.sam": Path("/tmp/gfl_run_123/sample.sam"),
                "hg38.fasta": Path("/tmp/gfl_run_123/hg38.fasta"),
            }

            def mock_stage_files(params, manifest):
                # Simulate staging by updating file parameters
                staged_params = params.copy()
                for key, value in params.items():
                    if isinstance(value, str) and value in manifest:
                        staged_params[key] = f"/tmp/gfl_run_123/{value}"
                return staged_params

            mock_manager.stage_files.side_effect = mock_stage_files

            # Create test client
            client = TestClient(app)

            # Prepare test data
            gfl_ast = {
                "experiment": {
                    "tool": "samtools",
                    "type": "alignment",
                    "params": {
                        "input_file": "sample.sam",
                        "reference_file": "hg38.fasta",
                        "output_file": "aligned.bam",
                        "threads": 4,
                    },
                }
            }

            data_manifest = {
                "sample.sam": "https://storage.googleapis.com/bucket/sample.sam?signature=abc123",
                "hg38.fasta": "https://storage.googleapis.com/bucket/hg38.fasta?signature=def456",
            }

            # Execute the workflow
            response = client.post(
                "/api/v2/execute",
                json={"ast": gfl_ast, "context": {}, "data_manifest": data_manifest},
            )

            # Verify response
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is True
            assert "staged_files" in result["result"]
            assert "plugin_params" in result["result"]

            # Verify that files were staged
            staged_files = result["result"]["staged_files"]
            assert "sample.sam" in staged_files
            assert "hg38.fasta" in staged_files

            # Verify that parameters were updated with local paths
            plugin_params = result["result"]["plugin_params"]
            assert plugin_params["input_file"] == "/tmp/gfl_run_123/sample.sam"
            assert plugin_params["reference_file"] == "/tmp/gfl_run_123/hg38.fasta"
            assert plugin_params["output_file"] == "aligned.bam"  # Not in manifest
            assert plugin_params["threads"] == 4  # Not a file parameter

            # Verify that DataStagingManager was used correctly
            mock_manager_class.assert_called_once()
            mock_manager.stage_files.assert_called_once()
            mock_manager.cleanup.assert_called_once()

    def test_workflow_without_data_staging(self):
        """Test workflow execution without data manifest (no staging)."""

        client = TestClient(app)

        gfl_ast = {
            "experiment": {
                "tool": "samtools",
                "type": "alignment",
                "params": {
                    "input_file": "local_sample.sam",
                    "reference_file": "local_hg38.fasta",
                    "output_file": "aligned.bam",
                    "threads": 4,
                },
            }
        }

        # Execute without data manifest
        response = client.post(
            "/api/v2/execute", json={"ast": gfl_ast, "context": {}, "data_manifest": {}}
        )

        # Verify response
        assert response.status_code == 200
        result = response.json()

        assert result["success"] is True
        assert result["result"]["staged_files"] == []

        # Parameters should remain unchanged
        plugin_params = result["result"]["plugin_params"]
        assert plugin_params["input_file"] == "local_sample.sam"
        assert plugin_params["reference_file"] == "local_hg38.fasta"

    def test_workflow_with_staging_failure(self):
        """Test workflow execution when data staging fails."""

        with patch("gfl.staging.DataStagingManager") as mock_manager_class:
            # Create a mock manager that fails during staging
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.stage_files.side_effect = Exception("Download failed")

            client = TestClient(app)

            gfl_ast = {
                "experiment": {
                    "tool": "samtools",
                    "type": "alignment",
                    "params": {"input_file": "sample.sam", "threads": 4},
                }
            }

            data_manifest = {
                "sample.sam": "https://storage.googleapis.com/bucket/sample.sam?signature=abc123"
            }

            # Execute the workflow
            response = client.post(
                "/api/v2/execute",
                json={"ast": gfl_ast, "context": {}, "data_manifest": data_manifest},
            )

            # Should return error
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is False
            assert "Data staging failed" in result["message"]

    def test_multi_plugin_workflow(self):
        """Test workflow with multiple plugins that share staged files."""

        with patch("gfl.staging.DataStagingManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Mock staging to track calls
            staged_files = {}

            def mock_stage_files(params, manifest):
                staged_params = params.copy()
                for key, value in params.items():
                    if isinstance(value, str) and value in manifest:
                        local_path = f"/tmp/gfl_run_123/{value}"
                        staged_params[key] = local_path
                        staged_files[value] = local_path
                return staged_params

            mock_manager.stage_files.side_effect = mock_stage_files
            mock_manager.staged_files = staged_files

            client = TestClient(app)

            # GFL AST with multiple analysis steps
            gfl_ast = {
                "experiment": {
                    "tool": "samtools",
                    "type": "alignment",
                    "params": {
                        "input_file": "sample.sam",
                        "reference_file": "hg38.fasta",
                        "output_file": "aligned.bam",
                    },
                },
                "analyze": {
                    "strategy": "variant_calling",
                    "params": {
                        "input_bam": "aligned.bam",
                        "reference": "hg38.fasta",  # Should reuse staged file
                        "output_vcf": "variants.vcf",
                    },
                },
            }

            data_manifest = {
                "sample.sam": "https://storage.googleapis.com/bucket/sample.sam?signature=abc123",
                "hg38.fasta": "https://storage.googleapis.com/bucket/hg38.fasta?signature=def456",
            }

            # Execute the workflow
            response = client.post(
                "/api/v2/execute",
                json={"ast": gfl_ast, "context": {}, "data_manifest": data_manifest},
            )

            # Verify response
            assert response.status_code == 200
            result = response.json()

            assert result["success"] is True

            # Verify that both experiment and analyze parameters were processed
            plugin_params = result["result"]["plugin_params"]
            assert "input_file" in plugin_params
            assert "reference_file" in plugin_params
            assert "input_bam" in plugin_params
            assert "reference" in plugin_params

            # Both reference parameters should point to the same staged file
            assert plugin_params["reference_file"] == plugin_params["reference"]

    def test_health_check_with_staging(self):
        """Test that health check works independently of data staging."""

        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_plugin_listing_with_staging(self):
        """Test that plugin listing works independently of data staging."""

        client = TestClient(app)

        response = client.get("/api/v2/plugins")

        assert response.status_code == 200
        plugins = response.json()

        # Should return a list of plugins
        assert isinstance(plugins, list)
        assert len(plugins) > 0

        # Each plugin should have required fields
        for plugin in plugins:
            assert "name" in plugin
            assert "version" in plugin
            assert "description" in plugin
            assert "capabilities" in plugin
            assert "status" in plugin
