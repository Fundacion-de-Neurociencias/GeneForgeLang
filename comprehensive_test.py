#!/usr/bin/env python3
"""Comprehensive test for all new GFL features."""

import os
import sys

# Add the current directory to the path so we can import gfl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfl.semantic_validator import EnhancedSemanticValidator


def test_active_learning_optimize():
    """Test optimize block with Active Learning strategy."""
    print("Testing optimize block with Active Learning strategy...")

    test_ast = {
        "optimize_active_learning": {
            "search_space": {"learning_rate": "range(0.001, 0.1)", "batch_size": "choice([32, 64, 128])"},
            "strategy": {
                "name": "ActiveLearning",
                "active_learning": {
                    "acquisition_function": "expected_improvement",
                    "initial_experiments": 10,
                    "max_uncertainty": 0.8,
                    "convergence_threshold": 0.01,
                },
            },
            "objective": {"maximize": "accuracy"},
            "budget": {"max_experiments": 100},
            "surrogate_model": "GaussianProcess",
            "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}},
        }
    }

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(test_ast)

    print(f"  Valid: {result.is_valid}")
    if not result.is_valid:
        for error in result.errors:
            print(f"    Error: {error.message}")
    return result.is_valid


def test_inverse_design():
    """Test design block with inverse design."""
    print("Testing design block with inverse design...")

    test_ast = {
        "design_inverse": {
            "design_type": "inverse_design",
            "entity": "ProteinSequence",
            "model": "ProteinGeneratorVAE",
            "objective": {"maximize": "stability"},
            "count": 50,
            "output": "designed_proteins",
            "inverse_design": {
                "target_properties": {"stability": 0.9, "binding_affinity": 0.8},
                "foundation_model": "ESM2",
            },
        }
    }

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(test_ast)

    print(f"  Valid: {result.is_valid}")
    if not result.is_valid:
        for error in result.errors:
            print(f"    Error: {error.message}")
    return result.is_valid


def test_refine_data():
    """Test refine_data block."""
    print("Testing refine_data block...")

    test_ast = {
        "refine_data": {
            "refinement_config": {"refinement_type": "noise_reduction", "noise_level": 0.1, "target_resolution": "high"}
        }
    }

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(test_ast)

    print(f"  Valid: {result.is_valid}")
    if not result.is_valid:
        for error in result.errors:
            print(f"    Error: {error.message}")
    return result.is_valid


def test_guided_discovery():
    """Test guided_discovery block."""
    print("Testing guided_discovery block...")

    test_ast = {
        "guided_discovery": {
            "design_params": {
                "entity": "SmallMolecule",
                "model": "MoleculeTransformer",
                "objective": {"maximize": "binding_affinity"},
                "count": 20,
                "output": "candidate_molecules",
                "candidates_per_cycle": 5,
            },
            "active_learning_params": {
                "search_space": {"concentration": "range(0.1, 1.0)"},
                "strategy": {
                    "name": "ActiveLearning",
                    "active_learning": {
                        "acquisition_function": "upper_confidence_bound",
                        "initial_experiments": 5,
                        "max_uncertainty": 0.7,
                        "convergence_threshold": 0.02,
                    },
                },
                "objective": {"maximize": "expression_level"},
                "budget": {"max_experiments": 50},
                "surrogate_model": "RandomForest",
                "run": {"experiment": {"tool": "CRISPR_base_editor", "type": "gene_editing"}},
                "experiments_per_cycle": 3,
            },
            "budget": {"max_cycles": 10},
            "output": "discovered_compounds",
        }
    }

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(test_ast)

    print(f"  Valid: {result.is_valid}")
    if not result.is_valid:
        for error in result.errors:
            print(f"    Error: {error.message}")
    return result.is_valid


def main():
    """Run all tests."""
    print("Running comprehensive tests for new GFL features...\n")

    tests = [test_active_learning_optimize, test_inverse_design, test_refine_data, test_guided_discovery]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ERROR: {e}\n")

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("All tests passed! 🎉")
        return True
    else:
        print("Some tests failed. 😞")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
