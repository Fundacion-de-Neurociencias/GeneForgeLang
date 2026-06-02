#!/usr/bin/env python3
"""
Test the design block JSON schema validation.
"""

from geneforgelang.core.api import parse
from geneforgelang.utils.schema_validator import comprehensive_validate


def test_design_schema_validation():
    """Test that design block validates against the JSON schema."""

    print("Testing design block JSON schema validation...")

    # Test valid design block
    valid_design = """
    design:
      entity: ProteinSequence
      model: ProteinGeneratorVAE
      objective:
        maximize: binding_affinity
      count: 10
      output: proteins
    """

    print("\n1. Testing valid design block...")
    ast = parse(valid_design)
    result = comprehensive_validate(ast)

    if result.errors:
        print("❌ Validation errors for valid design:")
        for error in result.errors:
            print(f"  - {error.message}")
        raise AssertionError("Valid design block should not have validation errors")
    else:
        print("✓ Valid design block passes schema validation")

    # Test invalid entity
    invalid_entity = """
    design:
      entity: InvalidEntity
      model: ProteinGeneratorVAE
      objective:
        maximize: binding_affinity
      count: 10
      output: proteins
    """

    print("\n2. Testing invalid entity...")
    ast = parse(invalid_entity)
    result = comprehensive_validate(ast)

    # Should have validation errors or warnings
    if not result.errors and not result.warnings:
        print("❌ Should have validation issues for invalid entity")
        raise AssertionError("Invalid entity should have validation issues")
    else:
        print("✓ Invalid entity properly flagged")

    # Test missing required fields
    missing_count = """
    design:
      entity: ProteinSequence
      model: ProteinGeneratorVAE
      objective:
        maximize: binding_affinity
      output: proteins
    """

    print("\n3. Testing missing required field...")
    ast = parse(missing_count)
    result = comprehensive_validate(ast)

    if not result.errors:
        print("❌ Should have errors for missing count field")
        raise AssertionError("Missing count field should have validation errors")
    else:
        print("✓ Missing count field properly detected")

    # Test conflicting objectives
    conflicting_objectives = """
    design:
      entity: ProteinSequence
      model: ProteinGeneratorVAE
      objective:
        maximize: binding_affinity
        minimize: toxicity
      count: 10
      output: proteins
    """

    print("\n4. Testing conflicting objectives...")
    ast = parse(conflicting_objectives)
    result = comprehensive_validate(ast)

    if not result.errors:
        print("❌ Should have errors for conflicting objectives")
        raise AssertionError("Conflicting objectives should have validation errors")
    else:
        print("✓ Conflicting objectives properly detected")

    print("\n🎉 All schema validation tests passed!")


if __name__ == "__main__":
    success = test_design_schema_validation()
    exit(0 if success else 1)
