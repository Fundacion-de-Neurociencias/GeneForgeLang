#!/usr/bin/env python3
"""
Test the design block implementation with a real GFL file.
"""
import os
from geneforgelang.core.api import parse, validate


def test_real_gfl_file():
    """Test parsing and validating a real GFL file with design block."""

    print("Testing real GFL file with design block...")
    gfl_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "features", "example_protein_design.gfl")

    # Read the GFL file
    with open(gfl_file_path) as f:
        gfl_content = f.read()
    print(f"GFL content ({len(gfl_content)} characters):")
    print("-" * 40)
    print(gfl_content)
    print("-" * 40)

    # Parse the file
    print("\n1. Parsing GFL file...")
    ast = parse(gfl_content)

    if ast is None:
        print("❌ Failed to parse GFL file")
        raise AssertionError("Failed to parse GFL file")

    print("✓ Successfully parsed GFL file")

    # Check structure
    print("\n2. Checking AST structure...")
    required_blocks = ["metadata", "design", "analyze"]

    for block in required_blocks:
        if block in ast:
            print(f"✓ Found {block} block")
        else:
            print(f"❌ Missing {block} block")
            raise AssertionError(f"Missing {block} block")

    # Check design block details
    print("\n3. Validating design block structure...")
    design = ast["design"]

    required_design_fields = ["entity", "model", "objective", "constraints", "count", "output"]
    for field in required_design_fields:
        if field in design:
            print(f"✓ Found design.{field}: {design[field]}")
        else:
            print(f"❌ Missing design.{field}")
            raise AssertionError(f"Missing design.{field}")

    # Validate the AST
    print("\n4. Running semantic validation...")
    errors = validate(ast)

    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        raise AssertionError("Validation errors found")
    else:
        print("✓ No validation errors")

    print("\n🎉 All tests passed! Design block implementation works correctly with GFL files.")

if __name__ == "__main__":
    success = test_real_gfl_file()
    exit(0 if success else 1)
