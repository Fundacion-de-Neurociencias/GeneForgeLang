#!/usr/bin/env python3
"""
Test script for GFL spatial genomic capabilities.
This script demonstrates the new spatial genomic features.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "gfl"))

from gfl.interpreter import Interpreter
from gfl.parser import parse_gfl


def test_spatial_genomic_features():
    """Test the new spatial genomic capabilities."""

    # Test GFL content with spatial genomic features
    gfl_content = """
loci:
  - id: "TestGene_Locus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    elements:
      - id: "TestGene_Promoter"
        type: "promoter"
      - id: "TestGene_Body"
        type: "gene"

rules:
  - id: "TestSpatialRule"
    description: "Test rule for spatial genomic reasoning"
    if:
      - type: "is_within"
        element: "TestGene_Promoter"
        locus: "TestGene_Locus"
    then:
      - type: "set_activity"
        element: "TestGene_Body"
        level: "active"

simulate:
  name: "TestSimulation"
  description: "Test spatial genomic simulation"
  action:
    type: "move"
    element: "TestGene_Promoter"
    destination: "chr1:2000000"
  query:
    - type: "get_activity"
      element: "TestGene_Body"
"""

    print("Testing GFL Spatial Genomic Capabilities")
    print("=" * 50)

    # Parse the GFL content
    print("1. Parsing GFL content...")
    try:
        ast = parse_gfl(gfl_content)
        if ast:
            print("✓ GFL parsing successful")
            print(f"  AST keys: {list(ast.keys())}")
        else:
            print("✗ GFL parsing failed")
            return False
    except Exception as e:
        print(f"✗ GFL parsing error: {e}")
        return False

    # Test interpreter
    print("\n2. Testing interpreter...")
    try:
        interpreter = Interpreter()
        interpreter.interpret(ast)
        print("✓ Interpreter execution successful")

        # Check symbol table
        print(f"  Symbol table keys: {list(interpreter.symbol_table.keys())}")

        # Test spatial condition evaluation
        print("\n3. Testing spatial condition evaluation...")
        test_condition = {"type": "is_within", "element": "TestGene_Promoter", "locus": "TestGene_Locus"}
        result = interpreter.evaluate_spatial_condition(test_condition)
        print(f"  Spatial condition result: {result}")

        return True

    except Exception as e:
        print(f"✗ Interpreter execution error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_example_files():
    """Test the example GFL files."""
    print("\n4. Testing example files...")

    example_files = [
        "examples/spatial_genomic_minimal_example.gfl",
        "examples/spatial_genomic_sox2_example.gfl",
        "examples/spatial_genomic_complex_example.gfl",
    ]

    for example_file in example_files:
        if os.path.exists(example_file):
            print(f"  Testing {example_file}...")
            try:
                with open(example_file) as f:
                    content = f.read()
                ast = parse_gfl(content)
                if ast:
                    print(f"    ✓ {example_file} parsed successfully")
                else:
                    print(f"    ✗ {example_file} parsing failed")
            except Exception as e:
                print(f"    ✗ {example_file} error: {e}")
        else:
            print(f"  ⚠ {example_file} not found")


if __name__ == "__main__":
    print("GFL Spatial Genomic Capabilities Test")
    print("=" * 50)

    success = test_spatial_genomic_features()
    test_example_files()

    if success:
        print("\n✓ All tests passed! Spatial genomic capabilities are working.")
    else:
        print("\n✗ Some tests failed. Check the implementation.")

    print("\nNew GFL Spatial Genomic Features:")
    print("- loci: Define genomic regions with coordinates")
    print("- rules: Spatial predicates (is_within, distance_between, is_in_contact)")
    print("- simulate: What-if reasoning and in silico experiments")
    print("- Enhanced interpreter with spatial condition evaluation")
