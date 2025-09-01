#!/usr/bin/env python3
"""Test script for IO Contracts validation."""

import sys
import os

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfl.api import parse, validate
from gfl.semantic_validator import EnhancedSemanticValidator

def test_io_contracts():
    """Test IO Contracts validation."""
    print("Testing IO Contracts validation...")
    
    # Read the test GFL file
    with open("test_io_contracts.gfl", "r") as f:
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
    
    # Check for specific contract-related errors
    contract_errors = [error for error in result.errors if "contract" in error.message.lower()]
    if contract_errors:
        print(f"Found {len(contract_errors)} contract-related errors:")
        for error in contract_errors:
            print(f"  - {error}")
    
    return True

def test_simple_io_contracts():
    """Test simple IO Contracts validation."""
    print("\nTesting simple IO Contracts validation...")
    
    # Simple valid case
    test_ast = {
        "experiment": {
            "tool": "sequence_aligner",
            "type": "sequencing",
            "contract": {
                "inputs": {
                    "raw_sequences": {
                        "type": "FASTQ",
                        "attributes": {"layout": "paired-end"}
                    }
                },
                "outputs": {
                    "aligned_reads": {
                        "type": "BAM",
                        "attributes": {"sorted": True}
                    }
                }
            }
        },
        "analyze": {
            "strategy": "variant",
            "contract": {
                "inputs": {
                    "aligned_reads": {
                        "type": "BAM",
                        "attributes": {"sorted": True, "indexed": True}
                    }
                },
                "outputs": {
                    "variants": {"type": "VCF"}
                }
            }
        }
    }
    
    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(test_ast)
    
    print(f"Simple validation result: {'Valid' if result.is_valid else 'Invalid'}")
    
    if not result.is_valid:
        print(f"Found {len(result.errors)} errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    return result.is_valid

if __name__ == "__main__":
    success1 = test_io_contracts()
    success2 = test_simple_io_contracts()
    sys.exit(0 if success1 and success2 else 1)