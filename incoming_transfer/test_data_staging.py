#!/usr/bin/env python3
"""
Test script for the DataStagingManager functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the GeneForge directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from geneforge_app.execution_components.data_staging_manager import DataStagingManager


def test_data_staging():
    """Test the DataStagingManager functionality."""
    print("=== DataStagingManager Test ===")
    
    # Create a DataStagingManager instance
    manager = DataStagingManager()
    print(f"Created temporary directory: {manager.temp_dir}")
    
    # Create some mock data manifest (in a real scenario, these would be signed URLs)
    data_manifest = {
        "sample.sam": "https://example.com/sample.sam",
        "reference.fasta": "https://example.com/reference.fasta",
        "config.json": "https://example.com/config.json"
    }
    
    # Create some plugin parameters
    plugin_params = {
        "input_file": "sample.sam",
        "reference": "reference.fasta",
        "output_file": "result.bam",
        "config": "config.json",
        "threads": 4  # This should remain unchanged
    }
    
    print("Original plugin parameters:")
    for key, value in plugin_params.items():
        print(f"  {key}: {value}")
    print()
    
    # In a real implementation, we would download files from the signed URLs
    # For this test, we'll create mock files
    print("Creating mock files...")
    mock_files = ["sample.sam", "reference.fasta", "config.json"]
    for filename in mock_files:
        mock_file_path = manager.temp_dir / filename
        mock_file_path.write_text(f"Mock content for {filename}")
        print(f"  Created mock file: {mock_file_path}")
    print()
    
    # Stage the files
    print("Staging files...")
    staged_params = manager.stage_files(plugin_params, data_manifest)
    
    print("Staged parameters:")
    for key, value in staged_params.items():
        print(f"  {key}: {value}")
    print()
    
    # Verify that file parameters were updated with local paths
    expected_updates = ["input_file", "reference", "config"]
    for param in expected_updates:
        if param in staged_params:
            param_value = staged_params[param]
            if isinstance(param_value, str) and str(manager.temp_dir) in param_value:
                print(f"✓ {param} correctly updated to local path: {param_value}")
            else:
                print(f"✗ {param} not correctly updated. Value: {param_value}")
        else:
            print(f"✗ {param} missing from staged parameters")
    
    # Verify that non-file parameters remain unchanged
    if staged_params.get("threads") == 4:
        print("✓ Non-file parameter 'threads' remains unchanged")
    else:
        print("✗ Non-file parameter 'threads' was incorrectly modified")
    
    if staged_params.get("output_file") == "result.bam":
        print("✓ Non-referenced file parameter 'output_file' remains unchanged")
    else:
        print("✗ Non-referenced file parameter 'output_file' was incorrectly modified")
    
    print()
    
    # Test cleanup
    print("Cleaning up...")
    manager.cleanup()
    
    if not manager.temp_dir.exists():
        print("✓ Temporary directory cleaned up successfully")
    else:
        print("✗ Temporary directory cleanup failed")
    
    print("\n=== Test Complete ===")


def test_edge_cases():
    """Test edge cases for the DataStagingManager."""
    print("\n=== Edge Cases Test ===")
    
    manager = DataStagingManager()
    
    # Test with empty parameters
    print("Testing with empty parameters...")
    empty_params = {}
    empty_manifest = {}
    result = manager.stage_files(empty_params, empty_manifest)
    assert result == {}
    print("✓ Empty parameters handled correctly")
    
    # Test with no matching files in manifest
    print("Testing with no matching files...")
    no_match_params = {"input": "nonexistent.txt"}
    no_match_manifest = {"other.txt": "https://example.com/other.txt"}
    result = manager.stage_files(no_match_params, no_match_manifest)
    assert result == no_match_params
    print("✓ Non-matching parameters handled correctly")
    
    # Test with mixed parameter types
    print("Testing with mixed parameter types...")
    mixed_params = {
        "file_param": "test.txt",
        "int_param": 42,
        "float_param": 3.14,
        "bool_param": True,
        "none_param": None,
        "list_param": ["item1", "item2"]
    }
    mixed_manifest = {"test.txt": "https://example.com/test.txt"}
    # Create mock file
    (manager.temp_dir / "test.txt").write_text("Mock content")
    result = manager.stage_files(mixed_params, mixed_manifest)
    
    # Check that only the file parameter was modified
    assert result["int_param"] == 42
    assert result["float_param"] == 3.14
    assert result["bool_param"] == True
    assert result["none_param"] is None
    assert result["list_param"] == ["item1", "item2"]
    print("✓ Mixed parameter types handled correctly")
    
    manager.cleanup()
    print("✓ Edge cases test completed")


if __name__ == "__main__":
    test_data_staging()
    test_edge_cases()
    print("\nAll tests completed successfully!")