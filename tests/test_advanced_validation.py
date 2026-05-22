#!/usr/bin/env python3
"""Test script for advanced GFL syntax validation."""

import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geneforgelang.core.api import parse, validate


def test_advanced_syntax():
    """Test the advanced AI workflow syntax validation."""
    print("Testing advanced GFL syntax validation...")

    # Read the test GFL file
    test_file = Path(__file__).parent / "test_advanced_syntax.gfl"
    with open(test_file) as f:
        gfl_content = f.read()

    # Parse the GFL content
    ast = parse(gfl_content)

    if ast is None:
        print("ERROR: Failed to parse GFL content")
        raise AssertionError("Failed to parse GFL content")

    print("Parsed AST successfully")

    # Validate the AST with enhanced validation
    result = validate(ast, enhanced=True)

    print(f"Validation result: {'Valid' if result is not None else 'Invalid'}")

    if not result or result is None:
        print(f"Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"  - {error}")
        raise AssertionError("Advanced syntax validation failed")
    else:
        print("All validations passed!")

if __name__ == "__main__":
    success = test_advanced_syntax()
    sys.exit(0 if success else 1)
