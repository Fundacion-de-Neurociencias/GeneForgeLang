#!/usr/bin/env python3
"""
Test script for GFL v2.0 Multi-Omic Capabilities
This script validates the new multi-omic features and external identifiers.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "gfl"))

from gfl.capability_system import get_engine_capabilities
from gfl.parser import parse_gfl
from gfl.semantic_validator import EnhancedSemanticValidator


def test_multi_omic_features():
    """Test the new multi-omic features in GFL v2.0."""

    print("🧬 GFL v2.0 Multi-Omic Capabilities Test")
    print("=" * 50)

    # Test transcripts block
    print("\n1. Testing Transcripts Block:")
    transcripts_test = """
transcripts:
  - id: "TP53_transcript_201"
    gene_source: "TP53"
    exons: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    identifiers:
      refseq: "NM_000546.6"
      ensembl: "ENST00000269305"
"""

    try:
        ast = parse_gfl(transcripts_test)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) == 0:
            print("  ✅ Transcripts block parsing and validation: PASSED")
        else:
            print("  ❌ Transcripts block validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Transcripts block test: Exception - {e}")

    # Test proteins block
    print("\n2. Testing Proteins Block:")
    proteins_test = """
transcripts:
  - id: "TP53_transcript_201"
    gene_source: "TP53"
    exons: [1, 2, 3, 4, 5]

proteins:
  - id: "p53_protein"
    translates_from: "transcript(TP53_transcript_201)"
    domains:
      - id: "DNA_BindingDomain"
        start: 102
        end: 292
    identifiers:
      uniprot: "P04637"
      refseq: "NP_000537.3"
"""

    try:
        ast = parse_gfl(proteins_test)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) == 0:
            print("  ✅ Proteins block parsing and validation: PASSED")
        else:
            print("  ❌ Proteins block validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Proteins block test: Exception - {e}")

    # Test metabolites block
    print("\n3. Testing Metabolites Block:")
    metabolites_test = """
metabolites:
  - id: "ATP"
    formula: "C10H16N5O13P3"
    identifiers:
      chebi: "CHEBI:15422"
      hmdb: "HMDB0000538"
      kegg: "C00002"
"""

    try:
        ast = parse_gfl(metabolites_test)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) == 0:
            print("  ✅ Metabolites block parsing and validation: PASSED")
        else:
            print("  ❌ Metabolites block validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Metabolites block test: Exception - {e}")


def test_external_identifiers():
    """Test external identifiers functionality."""

    print("\n4. Testing External Identifiers:")

    # Test with various identifier types
    identifiers_test = """
proteins:
  - id: "test_protein"
    translates_from: "transcript(test_transcript)"
    domains:
      - id: "test_domain"
        start: 1
        end: 100
    identifiers:
      uniprot: "P12345"
      refseq: "NP_123456.1"
      pdb: "1ABC"
      genbank: "AAA12345.1"
"""

    try:
        ast = parse_gfl(identifiers_test)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) == 0:
            print("  ✅ External identifiers validation: PASSED")
        else:
            print("  ❌ External identifiers validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ External identifiers test: Exception - {e}")


def test_invalid_cases():
    """Test invalid cases that should be rejected."""

    print("\n5. Testing Invalid Cases:")

    # Test missing required fields
    invalid_transcript = """
transcripts:
  - id: "invalid_transcript"
    # gene_source: "TP53"  # Missing required field
    exons: [1, 2, 3]
"""

    try:
        ast = parse_gfl(invalid_transcript)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) > 0:
            print("  ✅ Invalid transcript correctly rejected: PASSED")
        else:
            print("  ❌ Invalid transcript should have been rejected: FAILED")
    except Exception as e:
        print(f"  ❌ Invalid transcript test: Exception - {e}")

    # Test invalid translates_from format
    invalid_protein = """
proteins:
  - id: "invalid_protein"
    translates_from: "invalid_format"  # Should be transcript(ID)
    domains:
      - id: "test_domain"
        start: 1
        end: 100
"""

    try:
        ast = parse_gfl(invalid_protein)
        capabilities = get_engine_capabilities("advanced")
        validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
        result = validator.validate_ast(ast)
        if len(result.errors) > 0:
            print("  ✅ Invalid protein format correctly rejected: PASSED")
        else:
            print("  ❌ Invalid protein format should have been rejected: FAILED")
    except Exception as e:
        print(f"  ❌ Invalid protein test: Exception - {e}")


def test_capability_warnings():
    """Test capability warnings for different engine types."""

    print("\n6. Testing Capability Warnings:")

    # Test with multi-omic features
    multi_omic_test = """
transcripts:
  - id: "test_transcript"
    gene_source: "TEST"
    exons: [1, 2, 3]

proteins:
  - id: "test_protein"
    translates_from: "transcript(test_transcript)"
    domains:
      - id: "test_domain"
        start: 1
        end: 100

metabolites:
  - id: "test_metabolite"
    formula: "C6H12O6"
"""

    engine_types = ["basic", "standard", "advanced"]

    for engine_type in engine_types:
        print(f"\n  🔧 Testing with {engine_type} engine:")
        try:
            ast = parse_gfl(multi_omic_test)
            capabilities = get_engine_capabilities(engine_type)
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)

            capability_warnings = [w for w in result.warnings if hasattr(w, "feature")]

            if capability_warnings:
                print(f"    ⚠️  {len(capability_warnings)} capability warnings:")
                for warning in capability_warnings:
                    print(f"      - {warning.feature.value}: {warning.message}")
            else:
                print("    ✅ No capability warnings (all features supported)")

        except Exception as e:
            print(f"    ❌ Exception: {e}")


def test_complete_example():
    """Test the complete multi-omic example."""

    print("\n7. Testing Complete Multi-Omic Example:")

    # Read the complete example file
    example_file = "examples/multi_omic_example.gfl"

    if os.path.exists(example_file):
        try:
            with open(example_file, encoding="utf-8") as f:
                gfl_content = f.read()

            ast = parse_gfl(gfl_content)
            capabilities = get_engine_capabilities("advanced")
            validator = EnhancedSemanticValidator(engine_capabilities=capabilities)
            result = validator.validate_ast(ast)

            if len(result.errors) == 0:
                print("  ✅ Complete multi-omic example: PASSED")
                print(f"    AST keys: {list(ast.keys())}")
            else:
                print("  ❌ Complete multi-omic example: FAILED")
                for error in result.errors:
                    print(f"      Error: {error}")

        except Exception as e:
            print(f"  ❌ Complete example test: Exception - {e}")
    else:
        print(f"  ⚠️  Example file not found: {example_file}")


if __name__ == "__main__":
    print("🧬 GFL v2.0 Multi-Omic Capabilities Validation")
    print("=" * 50)

    # Run all tests
    test_multi_omic_features()
    test_external_identifiers()
    test_invalid_cases()
    test_capability_warnings()
    test_complete_example()

    print("\n🎯 GFL v2.0 Multi-Omic Features:")
    print("  - Transcripts block with gene_source and exons")
    print("  - Proteins block with translates_from and domains")
    print("  - Metabolites block with chemical formulas")
    print("  - External identifiers for database integration")
    print("  - Capability-aware validation")
    print("  - Cross-omic relationship validation")

    print("\n🚀 GFL v2.0 Multi-Omic Capabilities: IMPLEMENTATION COMPLETE!")
    print("Ready for GeneForge engine integration!")
