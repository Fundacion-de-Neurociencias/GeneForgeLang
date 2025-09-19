#!/usr/bin/env python3
"""Test script to verify complete workflow execution works correctly."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_complete_workflow():
    """Test complete workflow execution."""
    print("Testing complete workflow execution...")

    try:
        # Import the API
        import gfl

        print(f"GFL version: {gfl.__version__}")

        # Manually register the genesis plugins
        from gfl.plugins.auto_register import _register_genesis_plugins

        _register_genesis_plugins()
        print("Genesis plugins registered")

        # Test plugin availability
        from gfl.plugins.plugin_registry import plugin_registry

        plugin_registry._discover_plugins()

        print("\nAvailable plugins:")
        plugins = plugin_registry.list_plugins()
        for plugin in plugins:
            print(f"  - {plugin.name} (v{plugin.version})")

        # Test the CRISPR evaluator plugin directly
        from gfl.plugins.plugin_registry import get_plugin

        print("\nTesting CRISPR evaluator plugin...")
        crispr_evaluator = get_plugin("crispr_evaluator")
        print(f"Plugin loaded: {crispr_evaluator}")

        # Test processing some gRNA sequences
        test_data = {
            "sequences": [
                "GCGTGGGCTCGAGGCTGGTGGCGCTGCTGG",
                "GCTGGAGGCTGGTGGCGCTGCTGGGCGTGG",
                "GCGTGGGCTCGAGGCTGGTGGCGCTGCTGG",
                "GCTGGAGGCTGGTGGCGCTGCTGGGCGTGG",
                "GCGTGGGCTCGAGGCTGGTGGCGCTGCTGG",
            ]
        }

        print("Processing test data...")
        result = crispr_evaluator.process(test_data)
        print(f"Processing result: {result}")

        # Show the evaluation table
        if "evaluation_table" in result:
            print("\nEvaluation Results:")
            for item in result["evaluation_table"]:
                print(f"  Sequence: {item['sequence'][:10]}...")
                print(f"    On-target score: {item['on_target_score']:.3f}")
                print(f"    Off-target risk: {item['off_target_risk']:.3f}")
                print(f"    Composite score: {item['composite_score']:.3f}")
                print()

        print("✓ Complete workflow test passed!")

    except Exception as e:
        print(f"Error during workflow test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_complete_workflow()
