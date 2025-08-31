"""Test configuration and fixtures for the GeneForgeLang test suite.

This module provides common test fixtures, utilities, and configuration
for unit, integration, and performance tests.
"""

from pathlib import Path
from typing import Any, Dict

import pytest

from gfl.api import parse, validate


@pytest.fixture
def examples_dir() -> Path:
    """Path to the examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory."""
    test_dir = Path(__file__).parent
    data_dir = test_dir / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def valid_experiment_ast() -> Dict[str, Any]:
    """Valid experiment AST for testing."""
    return {
        "experiment": {
            "tool": "CRISPR_cas9",
            "type": "gene_editing",
            "params": {
                "target_gene": "TP53",
                "guide_rna": "GGGCCGGGCGGGCTCCCAGACATGCGTAT",
                "vector": "pCRISPR-Cas9",
            },
        }
    }


@pytest.fixture
def valid_analysis_ast() -> Dict[str, Any]:
    """Valid analysis AST for testing."""
    return {
        "analyze": {
            "strategy": "differential",
            "data": "experiment_results.csv",
            "thresholds": {"p_value": 0.05, "fold_change": 2.0},
            "filters": ["remove_low_counts", "normalize"],
        }
    }


@pytest.fixture
def valid_simulation_ast() -> Dict[str, Any]:
    """Valid simulation AST for testing."""
    return {"simulate": True, "metadata": {"confidence": 0.95}}


@pytest.fixture
def valid_design_ast() -> Dict[str, Any]:
    """Valid design AST for testing."""
    return {
        "design": {
            "entity": "ProteinSequence",
            "model": "ProteinGeneratorVAE",
            "objective": {
                "maximize": "binding_affinity",
                "target": "ACE2_receptor"
            },
            "constraints": [
                "length(120, 150)",
                "has_motif('E_box')",
                "synthesizability > 0.7"
            ],
            "count": 10,
            "output": "designed_candidates"
        }
    }


@pytest.fixture
def complex_ast() -> Dict[str, Any]:
    """Complex AST with multiple blocks for testing."""
    return {
        "experiment": {
            "tool": "CRISPR_cas9",
            "type": "gene_editing",
            "params": {
                "target_gene": "BRCA1",
                "concentration": 50.0,
                "temperature": 37.0,
                "replicates": 3,
            },
        },
        "analyze": {
            "strategy": "variant",
            "thresholds": {"quality_score": 30},
            "operations": [{"type": "filter", "params": {"min_depth": 10}}],
        },
        "simulate": True,
        "metadata": {"experiment_id": "EXP001", "date": "2024-01-01"},
    }


@pytest.fixture
def complex_design_ast() -> Dict[str, Any]:
    """Complex AST with design and analysis blocks for testing."""
    return {
        "design": {
            "entity": "SmallMolecule",
            "model": "MoleculeTransformer",
            "objective": {
                "maximize": "activity"
            },
            "constraints": [
                "molecular_weight < 500",
                "logP < 5",
                "rotatable_bonds < 10"
            ],
            "count": 100,
            "output": "candidate_molecules"
        },
        "analyze": {
            "strategy": "comparative",
            "data": "candidate_molecules",
            "thresholds": {
                "activity_score": 0.7,
                "toxicity_score": 0.3
            }
        },
        "metadata": {
            "experiment_id": "DESIGN_001",
            "researcher": "Dr. Smith",
            "project": "drug_discovery"
        }
    }


@pytest.fixture
def invalid_ast_missing_tool() -> Dict[str, Any]:
    """Invalid AST missing required tool field."""
    return {
        "experiment": {
            "type": "gene_editing",
            "params": {"target_gene": "TP53"},
        }
    }


@pytest.fixture
def invalid_ast_unknown_strategy() -> Dict[str, Any]:
    """Invalid AST with unknown analysis strategy."""
    return {
        "analyze": {
            "strategy": "unknown_strategy",
            "data": "results.csv",
        }
    }


class GFLTestUtils:
    """Utility class for common test operations."""

    @staticmethod
    def parse_and_validate(gfl_text: str) -> tuple[Dict[str, Any], list[str]]:
        """Parse GFL text and return AST and validation errors."""
        ast = parse(gfl_text)
        errors = validate(ast)
        return ast, errors

    @staticmethod
    def assert_valid_gfl(gfl_text: str) -> Dict[str, Any]:
        """Assert that GFL text is valid and return the AST."""
        ast, errors = GFLTestUtils.parse_and_validate(gfl_text)
        assert not errors, f"Expected valid GFL but got errors: {errors}"
        assert isinstance(ast, dict), f"Expected dict AST, got {type(ast)}"
        return ast

    @staticmethod
    def assert_invalid_gfl(gfl_text: str) -> list[str]:
        """Assert that GFL text is invalid and return the errors."""
        ast, errors = GFLTestUtils.parse_and_validate(gfl_text)
        assert errors, "Expected validation errors but got none"
        return errors


@pytest.fixture
def gfl_utils() -> GFLTestUtils:
    """Test utilities fixture."""
    return GFLTestUtils()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "plugin: Plugin system tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Add slow marker for tests that take more time
        if "test_large" in item.name or "test_performance" in item.name:
            item.add_marker(pytest.mark.slow)
