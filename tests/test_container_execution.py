#!/usr/bin/env python3
"""
Test script to verify container-based plugin execution
"""

import unittest
from unittest.mock import Mock, patch

from gfl.container_executor import ContainerExecutionError, ContainerExecutor
from gfl.execution_engine import ExecutionError, GFLExecutionEngine
from gfl.plugins.plugin_registry import plugin_registry


class TestContainerExecution(unittest.TestCase):
    """Test container-based plugin execution functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = GFLExecutionEngine()

    def test_container_executor_initialization(self):
        """Test that ContainerExecutor initializes correctly."""
        executor = ContainerExecutor()
        # Either docker is available or not, but the executor should initialize
        self.assertIsInstance(executor, ContainerExecutor)

    @patch("gfl.plugins.plugin_registry.plugin_registry.get_container_image")
    def test_execution_engine_checks_for_container_image(self, mock_get_container_image):
        """Test that execution engine checks for container images."""
        # Mock that no container image is available
        mock_get_container_image.return_value = None

        # Mock the generator to avoid actual execution
        with patch.object(plugin_registry, "get_generator") as mock_get_generator:
            mock_generator = Mock()
            mock_generator.generate.return_value = {"sequences": ["ACGT"]}
            mock_get_generator.return_value = mock_generator

            # Execute a design block
            design_block = {"model": "TestGenerator", "count": 5, "entity": "DNASequence"}

            result = self.engine.execute_design_block(design_block)

            # Verify that get_container_image was called
            mock_get_container_image.assert_called_once_with("TestGenerator")
            # Verify that the local generator was called
            mock_generator.generate.assert_called_once()
            # Verify the result
            self.assertEqual(result, {"sequences": ["ACGT"]})

    @patch("gfl.plugins.plugin_registry.plugin_registry.get_container_image")
    def test_execution_engine_falls_back_to_local_when_container_unavailable(self, mock_get_container_image):
        """Test that execution engine falls back to local execution when container is unavailable."""
        # Mock that a container image is available but Docker is not
        mock_get_container_image.return_value = "biocontainers/samtools:v1.15.1_cv4"

        # Mock the container executor to simulate Docker not being available
        with patch.object(self.engine.container_executor, "is_container_execution_available") as mock_is_available:
            mock_is_available.return_value = False

            # Mock the generator to avoid actual execution
            with patch.object(plugin_registry, "get_generator") as mock_get_generator:
                mock_generator = Mock()
                mock_generator.generate.return_value = {"sequences": ["TGCA"]}
                mock_get_generator.return_value = mock_generator

                # Execute a design block
                design_block = {"model": "TestGenerator", "count": 3, "entity": "RNASequence"}

                result = self.engine.execute_design_block(design_block)

                # Verify that get_container_image was called
                mock_get_container_image.assert_called_once_with("TestGenerator")
                # Verify that container availability was checked
                mock_is_available.assert_called_once()
                # Verify that the local generator was called (fallback)
                mock_generator.generate.assert_called_once()
                # Verify the result
                self.assertEqual(result, {"sequences": ["TGCA"]})

    def test_plugin_registry_container_image_storage(self):
        """Test that plugin registry can store and retrieve container images."""
        # Test that we can add a container image
        plugin_registry._container_images["test_plugin"] = "test/image:latest"

        # Test that we can retrieve it
        image = plugin_registry.get_container_image("test_plugin")
        self.assertEqual(image, "test/image:latest")

        # Test that non-existent plugins return None
        image = plugin_registry.get_container_image("nonexistent_plugin")
        self.assertIsNone(image)


if __name__ == "__main__":
    unittest.main()
