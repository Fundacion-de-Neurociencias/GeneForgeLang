#!/usr/bin/env python3
"""
Test script for GFL v1.3.0 Conformance Suite
This script validates all test cases in the conformance suite.
"""

import glob
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "gfl"))

from gfl.capability_system import get_engine_capabilities
from gfl.parser import parse_gfl
from gfl.semantic_validator import validate_with_engine_type


def test_conformance_suite():
    """Test the entire GFL v1.3.0 conformance suite."""

    print("🧬 GFL v1.3.0 Conformance Suite Test")
    print("=" * 50)

    # Test directories
    test_dirs = [
        "conformance_suite/v1.3.0/loci",
        "conformance_suite/v1.3.0/spatial_predicates",
        "conformance_suite/v1.3.0/simulate",
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    # Test with different engine types
    engine_types = ["basic", "standard", "advanced"]

    for engine_type in engine_types:
        print(f"\n🔧 Testing with {engine_type.upper()} engine:")
        print("-" * 30)

        for test_dir in test_dirs:
            if not os.path.exists(test_dir):
                print(f"❌ Test directory not found: {test_dir}")
                continue

            print(f"\n📁 Testing {test_dir}:")

            # Get all .gfl files in the directory
            gfl_files = glob.glob(os.path.join(test_dir, "*.gfl"))
            gfl_files.sort()  # Sort for consistent output

            for gfl_file in gfl_files:
                total_tests += 1
                test_name = os.path.basename(gfl_file)

                try:
                    # Read and parse the GFL file
                    with open(gfl_file, encoding="utf-8") as f:
                        gfl_content = f.read()

                    # Parse the GFL content
                    ast = parse_gfl(gfl_content)

                    if not ast:
                        print(f"  ❌ {test_name}: Parsing failed")
                        failed_tests += 1
                        continue

                    # Validate with the specified engine type
                    result = validate_with_engine_type(ast, engine_type, gfl_file)

                    # Check if this is expected to pass or fail
                    is_invalid_test = "invalid" in test_name.lower()
                    has_errors = len(result.errors) > 0
                    has_capability_warnings = len([w for w in result.warnings if hasattr(w, "feature")]) > 0

                    if is_invalid_test:
                        # Invalid tests should have errors
                        if has_errors:
                            print(f"  ✅ {test_name}: Correctly rejected (invalid test)")
                            passed_tests += 1
                        else:
                            print(f"  ❌ {test_name}: Should have been rejected but passed")
                            failed_tests += 1
                    else:
                        # Valid tests should not have errors
                        if not has_errors:
                            if has_capability_warnings and engine_type != "advanced":
                                print(f"  ⚠️  {test_name}: Passed with capability warnings")
                                passed_tests += 1
                            else:
                                print(f"  ✅ {test_name}: Passed validation")
                                passed_tests += 1
                        else:
                            print(f"  ❌ {test_name}: Failed validation")
                            for error in result.errors:
                                print(f"      Error: {error}")
                            failed_tests += 1

                    # Show capability warnings if any
                    if has_capability_warnings:
                        for warning in result.warnings:
                            if hasattr(warning, "feature"):
                                print(f"      Capability warning: {warning.feature.value}")

                except Exception as e:
                    print(f"  ❌ {test_name}: Exception - {e}")
                    failed_tests += 1

    # Summary
    print("\n📊 Test Summary:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    if total_tests > 0:
        print(f"  Success rate: {(passed_tests/total_tests)*100:.1f}%")
    else:
        print("  Success rate: 0.0%")

    if failed_tests == 0:
        print("\n🎉 All conformance tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Check implementation.")
        return False


def test_specific_features():
    """Test specific GFL v1.3.0 features."""

    print("\n🔬 Testing Specific Features:")
    print("-" * 30)

    # Test loci functionality
    print("\n1. Testing Loci Block:")
    loci_test = """
loci:
  - id: "TestLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    elements:
      - id: "TestElement"
        type: "promoter"
"""

    try:
        ast = parse_gfl(loci_test)
        result = validate_with_engine_type(ast, "advanced")
        if len(result.errors) == 0:
            print("  ✅ Loci block parsing and validation: PASSED")
        else:
            print("  ❌ Loci block validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Loci block test: Exception - {e}")

    # Test spatial predicates
    print("\n2. Testing Spatial Predicates:")
    spatial_test = """
loci:
  - id: "TestLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    elements:
      - id: "TestElement"
        type: "promoter"

rules:
  - id: "TestRule"
    description: "Test spatial predicate"
    if:
      - type: "is_within"
        element: "TestElement"
        locus: "TestLocus"
    then:
      - type: "set_activity"
        element: "TestElement"
        level: "active"
"""

    try:
        ast = parse_gfl(spatial_test)
        result = validate_with_engine_type(ast, "advanced")
        if len(result.errors) == 0:
            print("  ✅ Spatial predicates parsing and validation: PASSED")
        else:
            print("  ❌ Spatial predicates validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Spatial predicates test: Exception - {e}")

    # Test simulation
    print("\n3. Testing Simulation Block:")
    simulation_test = """
loci:
  - id: "TestLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    elements:
      - id: "TestElement"
        type: "promoter"

rules:
  - id: "TestRule"
    description: "Test rule"
    if:
      - type: "is_within"
        element: "TestElement"
        locus: "TestLocus"
    then:
      - type: "set_activity"
        element: "TestElement"
        level: "active"

simulate:
  name: "TestSimulation"
  description: "Test simulation"
  action:
    type: "move"
    element: "TestElement"
    destination: "chr1:2000000"
  query:
    - type: "get_activity"
      element: "TestElement"
"""

    try:
        ast = parse_gfl(simulation_test)
        result = validate_with_engine_type(ast, "advanced")
        if len(result.errors) == 0:
            print("  ✅ Simulation block parsing and validation: PASSED")
        else:
            print("  ❌ Simulation block validation: FAILED")
            for error in result.errors:
                print(f"      Error: {error}")
    except Exception as e:
        print(f"  ❌ Simulation block test: Exception - {e}")


def test_capability_warnings():
    """Test capability warnings for different engine types."""

    print("\n⚠️  Testing Capability Warnings:")
    print("-" * 30)

    # Test with spatial genomic features
    spatial_test = """
loci:
  - id: "TestLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000

rules:
  - id: "TestRule"
    description: "Test rule with spatial predicate"
    if:
      - type: "is_within"
        element: "TestElement"
        locus: "TestLocus"
    then:
      - type: "set_activity"
        element: "TestElement"
        level: "active"

simulate:
  name: "TestSimulation"
  description: "Test simulation"
  action:
    type: "move"
    element: "TestElement"
    destination: "chr1:2000000"
  query:
    - type: "get_activity"
      element: "TestElement"
"""

    engine_types = ["basic", "standard", "advanced"]

    for engine_type in engine_types:
        print(f"\n🔧 Testing with {engine_type} engine:")
        try:
            ast = parse_gfl(spatial_test)
            result = validate_with_engine_type(ast, engine_type)

            capability_warnings = [w for w in result.warnings if hasattr(w, "feature")]

            if capability_warnings:
                print(f"  ⚠️  {len(capability_warnings)} capability warnings:")
                for warning in capability_warnings:
                    print(f"      - {warning.feature.value}: {warning.message}")
            else:
                print("  ✅ No capability warnings (all features supported)")

        except Exception as e:
            print(f"  ❌ Exception: {e}")


if __name__ == "__main__":
    print("🧬 GFL v1.3.0 Conformance Suite Validation")
    print("=" * 50)

    # Run all tests
    success = test_conformance_suite()
    test_specific_features()
    test_capability_warnings()

    print("\n🎯 Final Result:")
    if success:
        print("✅ GFL v1.3.0 Conformance Suite: ALL TESTS PASSED")
        print("🚀 Ready for GeneForge engine implementation!")
    else:
        print("❌ GFL v1.3.0 Conformance Suite: SOME TESTS FAILED")
        print("🔧 Check implementation before proceeding")

    print("\n📚 Conformance Suite Features:")
    print("  - Loci block validation (8 test cases)")
    print("  - Spatial predicates validation (8 test cases)")
    print("  - Simulation block validation (8 test cases)")
    print("  - Capability-aware validation")
    print("  - Engine type compatibility testing")
    print("  - Comprehensive error handling")
