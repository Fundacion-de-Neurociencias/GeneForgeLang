#!/usr/bin/env python3
"""Test script to verify workflow execution works correctly."""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_workflow():
    """Test workflow execution."""
    print("Testing workflow execution...")

    try:
        # Import the auto-registration module and register plugins
        from gfl.plugins.auto_register import _register_genesis_plugins

        _register_genesis_plugins()
        print("Plugins registered successfully")

        # Import the execution engine
        from gfl.execution_engine import execute_gfl_ast, validate_execution_requirements

        print("Execution engine imported successfully")

        # Create a simple AST for testing
        test_ast = {
            "design": {
                "entity": "DNASequence",
                "model": "ontarget_scorer",
                "objective": {"maximize": "efficiency"},
                "count": 5,
                "output": "test_sequences",
                "constraints": [],
            }
        }

        print("Validating execution requirements...")
        errors = validate_execution_requirements(test_ast)
        if errors:
            print(f"Validation errors: {errors}")
        else:
            print("✓ Validation passed")

            # Try to execute the workflow
            print("Executing workflow...")
            result = execute_gfl_ast(test_ast)
            print(f"✓ Workflow executed successfully: {result}")

    except Exception as e:
        print(f"Error during workflow test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_workflow()
