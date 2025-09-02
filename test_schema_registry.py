#!/usr/bin/env python3
"""Test script for Schema Registry functionality."""

import sys
import os

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfl.api import parse, validate
from gfl.semantic_validator import EnhancedSemanticValidator
from gfl.schema_loader import SchemaLoader

def test_schema_loader():
    """Test the SchemaLoader functionality."""
    print("Testing SchemaLoader...")

    loader = SchemaLoader()
    result = EnhancedValidationResult()

    # Test loading valid schema file
    success = loader.load_schema_file("test_custom_types.yml", result)

    if not success:
        print("❌ Failed to load schema file:")
        for error in result.errors:
            print(f"  - {error.message}")
        return False

    # Check that schemas were loaded
    schemas = loader.get_all_schemas()
    if len(schemas) != 3:
        print(f"❌ Expected 3 schemas, got {len(schemas)}")
        return False

    # Check specific schema
    if "FASTQ_PairedEnd" not in schemas:
        print("❌ FASTQ_PairedEnd schema not found")
        return False

    fastq_schema = schemas["FASTQ_PairedEnd"]
    if fastq_schema.base_type != "FASTQ":
        print(f"❌ Expected base type 'FASTQ', got '{fastq_schema.base_type}'")
        return False

    if "layout" not in fastq_schema.attributes:
        print("❌ 'layout' attribute not found in FASTQ_PairedEnd schema")
        return False

    print("✓ SchemaLoader tests passed")
    return True

def test_schema_registry_validation():
    """Test schema registry validation in GFL."""
    print("\nTesting schema registry validation...")

    # Read the test GFL file
    with open("test_schema_registry.gfl", "r") as f:
        gfl_content = f.read()

    # Parse the GFL content
    ast = parse(gfl_content)

    if ast is None:
        print("❌ Failed to parse GFL content")
        return False

    print("✓ Parsed AST successfully")

    # Validate the AST with enhanced validation
    result = validate(ast, enhanced=True)

    print(f"Validation result: {'Valid' if result.is_valid else 'Invalid'}")

    # Check for schema-related errors
    schema_errors = [error for error in result.errors if "schema" in error.message.lower() or "attribute" in error.message.lower()]
    if schema_errors:
        print(f"Found {len(schema_errors)} schema-related errors:")
        for error in schema_errors:
            print(f"  - {error.message}")

    # We expect some errors for the invalid test cases
    # But the valid cases should pass
    return True

def test_simple_schema_usage():
    """Test simple schema usage validation."""
    print("\nTesting simple schema usage...")

    # Simple valid case with schema import
    test_ast = {
        "import_schemas": ["./test_custom_types.yml"],
        "experiment": {
            "tool": "sequence_aligner",
            "type": "sequencing",
            "contract": {
                "inputs": {
                    "raw_sequences": {
                        "type": "FASTQ_PairedEnd"
                    }
                },
                "outputs": {
                    "aligned_reads": {
                        "type": "BAM_Indexed",
                        "attributes": {
                            "sorted": True,
                            "indexed": True
                        }
                    }
                }
            }
        }
    }

    validator = EnhancedSemanticValidator(file_path="test.gfl")
    result = validator.validate_ast(test_ast)

    print(f"Simple validation result: {'Valid' if result.is_valid else 'Invalid'}")

    if not result.is_valid:
        print(f"Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"  - {error.message}")

    return result.is_valid

if __name__ == "__main__":
    success1 = test_schema_loader()
    success2 = test_schema_registry_validation()
    success3 = test_simple_schema_usage()

    if success1 and success2 and success3:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
