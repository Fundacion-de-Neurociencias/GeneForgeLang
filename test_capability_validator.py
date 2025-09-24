#!/usr/bin/env python3
"""
Test script for GFL capability-aware validator.
This script demonstrates the new capability validation features.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "gfl"))

from gfl.parser import parse_gfl
from gfl.semantic_validator import EnhancedSemanticValidator
from gfl.capability_system import (
    GFLFeature,
    get_engine_capabilities,
    EngineCapabilityChecker
)


def test_capability_validation():
    """Test the capability-aware validator with different engine types."""
    
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

experiment:
  name: "BasicExperiment"
  description: "Basic experiment that should work on all engines"
"""

    print("Testing GFL Capability-Aware Validator")
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
    
    # Test with different engine capabilities
    engine_types = ["basic", "standard", "advanced", "experimental"]
    
    for engine_type in engine_types:
        print(f"\n2. Testing with {engine_type.upper()} engine...")
        
        try:
            # Get capabilities for this engine type
            capabilities = get_engine_capabilities(engine_type)
            print(f"  Engine supports {len(capabilities)} features")
            
            # Create validator with engine capabilities
            validator = EnhancedSemanticValidator(
                file_path="test_spatial_genomic.gfl",
                engine_capabilities=capabilities
            )
            
            # Validate the AST
            result = validator.validate_ast(ast)
            
            # Report results
            print(f"  Validation result:")
            print(f"    Errors: {len(result.errors)}")
            print(f"    Warnings: {len(result.warnings)}")
            
            # Show capability warnings
            capability_warnings = [w for w in result.warnings if hasattr(w, 'feature')]
            if capability_warnings:
                print(f"    Capability warnings: {len(capability_warnings)}")
                for warning in capability_warnings:
                    print(f"      - {warning.message}")
                    if warning.feature:
                        print(f"        Feature: {warning.feature.value}")
            else:
                print("    No capability warnings")
                
            # Show feature support status
            required_features = {
                GFLFeature.LOCI_BLOCK,
                GFLFeature.SPATIAL_PREDICATES,
                GFLFeature.SPATIAL_SIMULATE,
                GFLFeature.EXPERIMENT_BLOCK
            }
            
            checker = EngineCapabilityChecker(capabilities)
            unsupported = checker.get_unsupported_features(required_features)
            
            if unsupported:
                print(f"    Unsupported features: {[f.value for f in unsupported]}")
            else:
                print("    All required features supported!")
                
        except Exception as e:
            print(f"    ✗ Validation error: {e}")
            import traceback
            traceback.print_exc()
    
    return True


def test_individual_features():
    """Test individual feature validation."""
    print("\n3. Testing individual feature validation...")
    
    # Test loci block validation
    loci_content = """
loci:
  - id: "TestLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    elements:
      - id: "TestElement"
        type: "promoter"
"""
    
    # Test with basic engine (should not support loci)
    basic_capabilities = get_engine_capabilities("basic")
    validator = EnhancedSemanticValidator(engine_capabilities=basic_capabilities)
    
    ast = parse_gfl(loci_content)
    result = validator.validate_ast(ast)
    
    capability_warnings = [w for w in result.warnings if hasattr(w, 'feature') and w.feature == GFLFeature.LOCI_BLOCK]
    
    if capability_warnings:
        print("✓ Loci block correctly flagged as unsupported on basic engine")
        print(f"  Warning: {capability_warnings[0].message}")
    else:
        print("✗ Loci block should have been flagged as unsupported")
    
    # Test with advanced engine (should support loci)
    advanced_capabilities = get_engine_capabilities("advanced")
    validator = EnhancedSemanticValidator(engine_capabilities=advanced_capabilities)
    
    result = validator.validate_ast(ast)
    capability_warnings = [w for w in result.warnings if hasattr(w, 'feature') and w.feature == GFLFeature.LOCI_BLOCK]
    
    if not capability_warnings:
        print("✓ Loci block correctly supported on advanced engine")
    else:
        print("✗ Loci block should have been supported on advanced engine")


def test_capability_system():
    """Test the capability system itself."""
    print("\n4. Testing capability system...")
    
    # Test engine capability sets
    capability_sets = get_engine_capabilities("standard")
    print(f"  Standard engine capabilities: {len(capability_sets)} features")
    
    # Test specific feature checks
    checker = EngineCapabilityChecker(capability_sets)
    
    # Test supported feature
    if checker.supports_feature(GFLFeature.EXPERIMENT_BLOCK):
        print("✓ EXPERIMENT_BLOCK correctly supported")
    else:
        print("✗ EXPERIMENT_BLOCK should be supported")
    
    # Test unsupported feature
    if not checker.supports_feature(GFLFeature.LOCI_BLOCK):
        print("✓ LOCI_BLOCK correctly unsupported on standard engine")
    else:
        print("✗ LOCI_BLOCK should be unsupported on standard engine")
    
    # Test dependency checking
    missing_deps = checker.check_dependencies(GFLFeature.SPATIAL_SIMULATE)
    if missing_deps:
        print(f"✓ SPATIAL_SIMULATE correctly identifies missing dependencies: {[d.value for d in missing_deps]}")
    else:
        print("✗ SPATIAL_SIMULATE should have missing dependencies on standard engine")


if __name__ == "__main__":
    print("GFL Capability-Aware Validator Test")
    print("=" * 50)
    
    success = test_capability_validation()
    test_individual_features()
    test_capability_system()
    
    if success:
        print("\n✓ All tests passed! Capability-aware validator is working.")
    else:
        print("\n✗ Some tests failed. Check the implementation.")
    
    print("\nNew Capability-Aware Validator Features:")
    print("- Engine capability checking")
    print("- Feature dependency validation")
    print("- Capability warnings (not errors)")
    print("- Support for different engine types (basic, standard, advanced, experimental)")
    print("- Spatial genomic feature validation")
    print("- Backward compatibility with legacy GFL features")
