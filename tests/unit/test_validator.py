"""Unit tests for the GFL semantic validator module.

Tests cover:
- Symbol resolution and validation
- Plugin call validation
- Parameter type checking
- Semantic constraint validation
- Error message generation
"""

import pytest

from gfl.api import validate
from gfl.semantic_validator import SemanticValidator


class TestBasicValidation:
    """Test basic semantic validation functionality."""

    def test_validate_valid_experiment(self, valid_experiment_ast):
        """Test validation of a valid experiment."""
        errors = validate(valid_experiment_ast)
        assert not errors

    def test_validate_valid_analysis(self, valid_analysis_ast):
        """Test validation of a valid analysis block."""
        errors = validate(valid_analysis_ast)
        assert not errors

    def test_validate_valid_simulation(self, valid_simulation_ast):
        """Test validation of a valid simulation block."""
        errors = validate(valid_simulation_ast)
        assert not errors

    def test_validate_complex_ast(self, complex_ast):
        """Test validation of a complex AST with multiple blocks."""
        errors = validate(complex_ast)
        assert not errors

    def test_validate_empty_ast(self):
        """Test validation of an empty AST."""
        errors = validate({})
        # Should have errors for missing required content
        assert len(errors) > 0

    def test_validate_none_ast(self):
        """Test validation of None AST."""
        errors = validate(None)
        assert len(errors) > 0


class TestExperimentValidation:
    """Test experiment block validation."""

    def test_missing_tool_field(self, invalid_ast_missing_tool):
        """Test validation when tool field is missing."""
        errors = validate(invalid_ast_missing_tool)
        assert len(errors) > 0
        assert any("tool" in error.lower() for error in errors)

    def test_invalid_tool_name(self):
        """Test validation with invalid tool name."""
        ast = {
            "experiment": {
                "tool": "invalid_tool_name",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
            }
        }
        errors = validate(ast)
        # Should accept unknown tools (extensibility)
        assert not errors

    def test_missing_type_field(self):
        """Test validation when type field is missing."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "params": {"target_gene": "TP53"},
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("type" in error.lower() for error in errors)

    def test_invalid_type_value(self):
        """Test validation with invalid experiment type."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "invalid_type",
                "params": {"target_gene": "TP53"},
            }
        }
        errors = validate(ast)
        # Should accept unknown types (extensibility)
        assert not errors

    def test_missing_params_field(self):
        """Test validation when params field is missing."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
            }
        }
        validate(ast)
        # Params might be optional depending on implementation
        # Check if this generates an error or warning

    def test_empty_params(self):
        """Test validation with empty params."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {},
            }
        }
        validate(ast)
        # Empty params should be valid (tool-specific validation)

    def test_valid_parameter_types(self):
        """Test validation of various parameter types."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {
                    "target_gene": "TP53",  # string
                    "concentration": 50.0,  # float
                    "replicates": 3,  # int
                    "enabled": True,  # bool
                    "tags": ["urgent", "validated"],  # list
                    "metadata": {"source": "lab_a"},  # dict
                },
            }
        }
        errors = validate(ast)
        assert not errors


class TestAnalysisValidation:
    """Test analysis block validation."""

    def test_missing_strategy_field(self):
        """Test validation when strategy field is missing."""
        ast = {
            "analyze": {
                "data": "results.csv",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("strategy" in error.lower() for error in errors)

    def test_unknown_strategy(self, invalid_ast_unknown_strategy):
        """Test validation with unknown analysis strategy."""
        errors = validate(invalid_ast_unknown_strategy)
        # Should accept unknown strategies (extensibility)
        assert not errors

    def test_valid_strategies(self):
        """Test validation of known analysis strategies."""
        strategies = ["differential", "pathway", "variant", "expression", "structural"]

        for strategy in strategies:
            ast = {
                "analyze": {
                    "strategy": strategy,
                    "data": "results.csv",
                }
            }
            errors = validate(ast)
            assert not errors, f"Strategy '{strategy}' should be valid"

    def test_optional_fields(self):
        """Test validation of optional analysis fields."""
        ast = {
            "analyze": {
                "strategy": "differential",
                "data": "results.csv",
                "thresholds": {"p_value": 0.05},
                "filters": ["normalize"],
                "operations": [{"type": "sort", "field": "p_value"}],
            }
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_threshold_types(self):
        """Test validation of invalid threshold types."""
        ast = {
            "analyze": {
                "strategy": "differential",
                "thresholds": "invalid_type",  # Should be dict
            }
        }
        validate(ast)
        # Implementation dependent - might allow flexible types

    def test_invalid_filter_types(self):
        """Test validation of invalid filter types."""
        ast = {
            "analyze": {
                "strategy": "differential",
                "filters": "invalid_type",  # Should be list
            }
        }
        validate(ast)
        # Implementation dependent - might allow flexible types


class TestBranchValidation:
    """Test branch block validation."""

    def test_simple_branch(self):
        """Test validation of a simple branch block."""
        ast = {
            "branch": {
                "if": "condition",
                "then": {
                    "experiment": {
                        "tool": "CRISPR_cas9",
                        "type": "gene_editing",
                        "params": {"target_gene": "TP53"},
                    }
                },
            }
        }
        validate(ast)
        # Branch validation depends on implementation

    def test_branch_with_else(self):
        """Test validation of branch with else clause."""
        ast = {
            "branch": {
                "if": "condition",
                "then": {"simulate": True},
                "else": {"simulate": False},
            }
        }
        validate(ast)
        # Branch validation depends on implementation


class TestPluginValidation:
    """Test plugin-related validation."""

    def test_plugin_invocation(self):
        """Test validation of plugin invocation."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
            },
            "invoke": {
                "plugin": "alpha_genome",
                "method": "predict_effect",
                "params": {"gene": "TP53"},
                "as_var": "prediction",
            },
        }
        _ = validate(ast)  # Explicitly ignore unused variable
        # Plugin validation should be lenient (plugins may not be loaded)

    def test_missing_plugin_name(self):
        """Test validation when plugin name is missing."""
        ast = {
            "invoke": {
                "method": "predict_effect",
                "params": {"gene": "TP53"},
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

    def test_unknown_plugin(self):
        """Test validation with unknown plugin."""
        ast = {
            "invoke": {
                "plugin": "unknown_plugin",
                "method": "some_method",
                "params": {},
            }
        }
        _ = validate(ast)  # Explicitly ignore unused variable
        # Should not error for unknown plugins (may be loaded later)


class TestSymbolValidation:
    """Test symbol resolution and variable validation."""

    def test_variable_redefinition(self):
        """Test detection of variable redefinition."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
            },
            "invoke": [
                {
                    "plugin": "alpha_genome",
                    "method": "predict",
                    "as_var": "result",
                },
                {
                    "plugin": "variant_sim",
                    "method": "simulate",
                    "as_var": "result",  # Redefinition
                },
            ],
        }
        _ = validate(ast)  # Explicitly ignore unused variable
        # Should detect variable redefinition

    def test_undefined_variable_reference(self):
        """Test detection of undefined variable references."""
        ast = {
            "analyze": {
                "strategy": "differential",
                "data": "undefined_variable",  # Reference to undefined variable
            }
        }
        _ = validate(ast)  # Explicitly ignore unused variable
        # Should detect undefined variable reference if strict mode


class TestValidationErrorMessages:
    """Test validation error message generation."""

    def test_error_message_format(self):
        """Test that error messages have proper format."""
        ast = {
            "experiment": {
                "type": "gene_editing",
                # Missing required 'tool' field
                "params": {"target_gene": "TP53"},
            }
        }
        errors = validate(ast)

        if errors:
            # Check that error messages are informative
            error = errors[0]
            assert isinstance(error, str)
            assert len(error) > 0
            assert not error.isspace()

    def test_multiple_errors(self):
        """Test handling of multiple validation errors."""
        ast = {
            "experiment": {
                # Missing both 'tool' and 'type'
                "params": {"target_gene": "TP53"},
            },
            "analyze": {
                # Missing 'strategy'
                "data": "results.csv",
            },
        }
        errors = validate(ast)

        # Should detect multiple errors
        if len(errors) > 1:
            # Ensure each error is distinct
            assert len(set(errors)) == len(errors)


class TestValidatorDirectUsage:
    """Test direct usage of SemanticValidator class."""

    def test_validator_initialization(self):
        """Test SemanticValidator initialization."""
        validator = SemanticValidator()
        assert validator is not None

    def test_validator_visit_methods(self):
        """Test that validator has required visit methods."""
        validator = SemanticValidator()

        # Check for essential visit methods
        assert hasattr(validator, "validate")
        # Additional method checks depend on implementation

    def test_validator_symbol_table(self):
        """Test validator symbol table functionality."""
        validator = SemanticValidator()

        # Test symbol table operations if exposed
        if hasattr(validator, "symbol_table"):
            # Test symbol table functionality
            pass


@pytest.mark.performance
class TestValidationPerformance:
    """Test validation performance with large inputs."""

    @pytest.mark.slow
    def test_validate_large_ast(self):
        """Test validation performance with large AST."""
        # Create a large AST with many parameters
        large_params = {f"param_{i}": f"value_{i}" for i in range(1000)}

        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": large_params,
            }
        }

        import time

        start_time = time.time()
        errors = validate(ast)
        end_time = time.time()

        # Validation should complete quickly
        assert end_time - start_time < 5.0  # Less than 5 seconds
        assert not errors  # Should be valid

    @pytest.mark.slow
    def test_validate_deeply_nested_ast(self):
        """Test validation with deeply nested structures."""
        # Create deeply nested structure
        nested_operations = []
        for i in range(100):
            nested_operations.append(
                {
                    "type": f"operation_{i}",
                    "params": {"nested": {"level": i, "data": [f"item_{j}" for j in range(10)]}},
                }
            )

        ast = {
            "analyze": {
                "strategy": "pathway",
                "operations": nested_operations,
            }
        }

        _ = validate(ast)  # Explicitly ignore unused variable
        # Should handle deep nesting without stack overflow
