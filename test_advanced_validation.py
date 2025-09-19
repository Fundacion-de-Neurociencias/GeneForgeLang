#!/usr/bin/env python3
"""Test script for advanced GFL syntax validation."""

import os
import sys

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfl.api import parse, validate
from gfl.semantic_validator import EnhancedSemanticValidator


def test_advanced_syntax():
    """Test the advanced AI workflow syntax validation."""
    print("Testing advanced GFL syntax validation...")

    # Read the test GFL file
    with open("test_advanced_syntax.gfl") as f:
        gfl_content = f.read()

    # Parse the GFL content
    ast = parse(gfl_content)

    if ast is None:
        print("ERROR: Failed to parse GFL content")
        return False

    print("Parsed AST successfully")

    # Validate the AST with enhanced validation
    result = validate(ast, enhanced=True)

    print(f"Validation result: {'Valid' if result.is_valid else 'Invalid'}")

    if not result.is_valid:
        print(f"Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"  - {error}")
        return False
    else:
        print("All validations passed!")
        return True


if __name__ == "__main__":
    success = test_advanced_syntax()
    sys.exit(0 if success else 1)
