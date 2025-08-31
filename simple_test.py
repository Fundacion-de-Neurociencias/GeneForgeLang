#!/usr/bin/env python3
"""Simple test for GFL validator."""

import sys
import os

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfl.semantic_validator import EnhancedSemanticValidator

# Test AST with a simple design block
test_ast = {
    "design": {
        "entity": "ProteinSequence",
        "model": "ProteinGeneratorVAE",
        "objective": {
            "maximize": "stability"
        },
        "count": 10,
        "output": "test_output"
    }
}

# Create validator and validate
validator = EnhancedSemanticValidator()
result = validator.validate_ast(test_ast)

print("Validation successful:", result.is_valid)
if not result.is_valid:
    print("Errors found:")
    for error in result.errors:
        print(f"  - {error.message}")
else:
    print("No errors found!")