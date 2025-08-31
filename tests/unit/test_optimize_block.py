"""Unit tests for the GFL optimize block functionality.

Tests cover:
- Optimize block parsing and validation
- Type definitions and conversions
- Search space parameter validation
- Strategy configuration validation
- Objective and budget validation
- Nested experiment block validation
- Parameter injection syntax validation
"""

import pytest

from gfl.api import parse, validate
from gfl.types import Optimize


class TestOptimizeBlockParsing:
    """Test optimize block parsing functionality."""

    def test_parse_basic_optimize_block(self):
        """Test parsing a basic optimize block."""
        gfl_text = """
        optimize:
          search_space:
            promoter_strength: range(0.1, 1.0)
            terminator_efficiency: choice([0.8, 0.9, 0.95, 0.99])
          strategy:
            name: ActiveLearning
            uncertainty_metric: entropy
          objective:
            maximize: gene_expression_level
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: SyntheticCircuitSimulator
              type: gene_editing
              params:
                promoter: ${promoter_strength}
                terminator: ${terminator_efficiency}
        """
        ast = parse(gfl_text)

        assert ast is not None
        assert "optimize" in ast

        optimize = ast["optimize"]
        assert optimize["search_space"]["promoter_strength"] == "range(0.1, 1.0)"
        assert optimize["search_space"]["terminator_efficiency"] == "choice([0.8, 0.9, 0.95, 0.99])"
        assert optimize["strategy"]["name"] == "ActiveLearning"
        assert optimize["strategy"]["uncertainty_metric"] == "entropy"
        assert optimize["objective"]["maximize"] == "gene_expression_level"
        assert optimize["budget"]["max_experiments"] == 50
        assert "experiment" in optimize["run"]

    def test_parse_optimize_with_minimize_objective(self):
        """Test parsing optimize block with minimize objective."""
        gfl_text = """
        optimize:
          search_space:
            temperature: range(20, 40)
            ph: range(6.0, 8.0)
          strategy:
            name: BayesianOptimization
          objective:
            minimize: cost
          budget:
            max_experiments: 30
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
                buffer_ph: ${ph}
        """
        ast = parse(gfl_text)

        assert ast is not None
        optimize = ast["optimize"]
        assert optimize["objective"]["minimize"] == "cost"
        assert "maximize" not in optimize["objective"]

    def test_parse_optimize_with_multiple_budget_constraints(self):
        """Test parsing optimize block with multiple budget constraints."""
        gfl_text = """
        optimize:
          search_space:
            dose: range(1, 100)
          strategy:
            name: GeneticAlgorithm
          objective:
            maximize: efficacy
          budget:
            max_experiments: 100
            max_time: 24h
            max_cost: 5000
            convergence_threshold: 0.01
          run:
            experiment:
              tool: flow_cytometry
              type: screening
              params:
                concentration: ${dose}
        """
        ast = parse(gfl_text)

        optimize = ast["optimize"]
        budget = optimize["budget"]
        assert budget["max_experiments"] == 100
        assert budget["max_time"] == "24h"
        assert budget["max_cost"] == 5000
        assert budget["convergence_threshold"] == 0.01

    def test_parse_optimize_with_analyze_run_block(self):
        """Test parsing optimize block with analyze in run block."""
        gfl_text = """
        optimize:
          search_space:
            threshold: range(0.1, 0.9)
          strategy:
            name: RandomSearch
          objective:
            maximize: precision
          budget:
            max_experiments: 20
          run:
            analyze:
              strategy: differential
              data: experiment_data
              thresholds:
                p_value: ${threshold}
        """
        ast = parse(gfl_text)

        optimize = ast["optimize"]
        assert "analyze" in optimize["run"]
        assert optimize["run"]["analyze"]["strategy"] == "differential"


class TestOptimizeBlockValidation:
    """Test optimize block validation functionality."""

    def test_valid_optimize_block_passes(self):
        """Test that a valid optimize block passes validation."""
        ast = {
            "optimize": {
                "search_space": {
                    "parameter1": "range(0, 10)",
                    "parameter2": "choice([a, b, c])"
                },
                "strategy": {
                    "name": "ActiveLearning"
                },
                "objective": {
                    "maximize": "efficiency"
                },
                "budget": {
                    "max_experiments": 50
                },
                "run": {
                    "experiment": {
                        "tool": "CRISPR_cas9",
                        "type": "gene_editing",
                        "params": {
                            "param1": "${parameter1}",
                            "param2": "${parameter2}"
                        }
                    }
                }
            }
        }
        errors = validate(ast)
        assert not errors

    def test_missing_required_fields(self):
        """Test validation errors for missing required fields."""
        # Missing search_space
        ast = {
            "optimize": {
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("search_space" in error.lower() for error in errors)

        # Missing strategy
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("strategy" in error.lower() for error in errors)

        # Missing objective
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("objective" in error.lower() for error in errors)

        # Missing budget
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("budget" in error.lower() for error in errors)

        # Missing run
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("run" in error.lower() for error in errors)

    def test_search_space_validation(self):
        """Test search space parameter validation."""
        # Empty search space
        ast = {
            "optimize": {
                "search_space": {},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid parameter name
        ast = {
            "optimize": {
                "search_space": {"123invalid": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid parameter definition type
        ast = {
            "optimize": {
                "search_space": {"param": 123},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid syntax
        ast = {
            "optimize": {
                "search_space": {"param": "invalid_syntax"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

    def test_range_syntax_validation(self):
        """Test range() syntax validation."""
        # Valid range
        ast = {
            "optimize": {
                "search_space": {"param": "range(0.1, 1.0)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        # Should not have range-specific errors
        range_errors = [e for e in errors if "range" in e.lower()]
        assert len(range_errors) == 0

        # Invalid range - min >= max
        ast["optimize"]["search_space"]["param"] = "range(1.0, 0.1)"
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid range - wrong number of arguments
        ast["optimize"]["search_space"]["param"] = "range(1.0)"
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid range - non-numeric values
        ast["optimize"]["search_space"]["param"] = "range(a, b)"
        errors = validate(ast)
        assert len(errors) > 0

    def test_choice_syntax_validation(self):
        """Test choice() syntax validation."""
        # Valid choice
        ast = {
            "optimize": {
                "search_space": {"param": "choice([0.8, 0.9, 0.95])"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        # Should not have choice-specific errors
        choice_errors = [e for e in errors if "choice" in e.lower()]
        assert len(choice_errors) == 0

        # Empty choice should warn
        ast["optimize"]["search_space"]["param"] = "choice([])"
        errors = validate(ast)
        assert len(errors) > 0

    def test_strategy_validation(self):
        """Test strategy field validation."""
        # Missing name field
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"uncertainty_metric": "entropy"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)

        # Invalid strategy name type
        ast["optimize"]["strategy"] = {"name": 123}
        errors = validate(ast)
        assert len(errors) > 0

        # Unknown strategy name (should be warning)
        ast["optimize"]["strategy"] = {"name": "UnknownStrategy"}
        errors = validate(ast)
        # This might be warnings, not errors

    def test_objective_validation(self):
        """Test objective field validation."""
        # Empty objective
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {},
                "budget": {"max_experiments": 50},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Both maximize and minimize
        ast["optimize"]["objective"] = {
            "maximize": "efficiency",
            "minimize": "cost"
        }
        errors = validate(ast)
        assert len(errors) > 0

    def test_budget_validation(self):
        """Test budget field validation."""
        # Empty budget
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {},
                "run": {"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Invalid budget values
        ast["optimize"]["budget"] = {"max_experiments": -5}
        errors = validate(ast)
        assert len(errors) > 0

        ast["optimize"]["budget"] = {"max_cost": "invalid"}
        errors = validate(ast)
        assert len(errors) > 0

    def test_run_block_validation(self):
        """Test run block validation."""
        # Missing nested block
        ast = {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 50},
                "run": {}
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Multiple nested blocks
        ast["optimize"]["run"] = {
            "experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"},
            "analyze": {"strategy": "differential"}
        }
        errors = validate(ast)
        assert len(errors) > 0


class TestOptimizeTypeDefinitions:
    """Test Optimize type definitions and conversions."""

    def test_optimize_type_creation(self):
        """Test creating Optimize type instances."""
        optimize = Optimize(
            search_space={"param1": "range(0, 10)", "param2": "choice([a, b])"},
            strategy={"name": "ActiveLearning"},
            objective={"maximize": "efficiency"},
            budget={"max_experiments": 50},
            run={"experiment": {"tool": "CRISPR_cas9", "type": "gene_editing"}}
        )

        assert optimize.search_space["param1"] == "range(0, 10)"
        assert optimize.strategy["name"] == "ActiveLearning"
        assert optimize.objective["maximize"] == "efficiency"
        assert optimize.budget["max_experiments"] == 50
        assert "experiment" in optimize.run

    def test_optimize_to_dict(self):
        """Test Optimize to_dict conversion."""
        optimize = Optimize(
            search_space={"temperature": "range(20, 40)"},
            strategy={"name": "BayesianOptimization"},
            objective={"minimize": "cost"},
            budget={"max_experiments": 30, "max_time": "24h"},
            run={"experiment": {"tool": "PCR", "type": "validation"}}
        )

        result = optimize.to_dict()
        expected = {
            "search_space": {"temperature": "range(20, 40)"},
            "strategy": {"name": "BayesianOptimization"},
            "objective": {"minimize": "cost"},
            "budget": {"max_experiments": 30, "max_time": "24h"},
            "run": {"experiment": {"tool": "PCR", "type": "validation"}}
        }

        assert result == expected


class TestOptimizeBlockIntegration:
    """Test optimize block integration with other components."""

    def test_optimize_with_metadata_workflow(self):
        """Test optimize block with metadata."""
        gfl_text = """
        metadata:
          experiment_id: OPTIM_001
          researcher: Dr. Jane Smith
          project: parameter_optimization

        optimize:
          search_space:
            concentration: range(10, 100)
            temperature: range(25, 45)
          strategy:
            name: ActiveLearning
            uncertainty_metric: entropy
          objective:
            maximize: yield
          budget:
            max_experiments: 75
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                conc: ${concentration}
                temp: ${temperature}
                replicates: 3
        """
        ast = parse(gfl_text)

        assert ast is not None
        assert "metadata" in ast
        assert "optimize" in ast

        errors = validate(ast)
        # Should be valid
        assert not errors

    def test_complex_optimize_workflow(self):
        """Test complex optimize workflow with nested structures."""
        gfl_text = """
        optimize:
          search_space:
            promoter_strength: range(0.1, 2.0)
            enhancer_position: choice([upstream, downstream, intergenic])
            copy_number: range(1, 10)
          strategy:
            name: BayesianOptimization
            acquisition_function: expected_improvement
          objective:
            maximize: gene_expression_level
            target: target_protein
          budget:
            max_experiments: 100
            max_time: 72h
            convergence_threshold: 0.005
          run:
            experiment:
              tool: SyntheticCircuitSimulator
              type: gene_editing
              strategy: activation
              params:
                promoter: ${promoter_strength}
                enhancer: ${enhancer_position}
                copies: ${copy_number}
                target_gene: GFP
                replicates: 5
        """
        ast = parse(gfl_text)

        assert "optimize" in ast
        optimize = ast["optimize"]

        # Check complex structures
        assert len(optimize["search_space"]) == 3
        assert "acquisition_function" in optimize["strategy"]
        assert optimize["objective"]["target"] == "target_protein"
        assert len(optimize["budget"]) == 3
        assert optimize["run"]["experiment"]["strategy"] == "activation"

        errors = validate(ast)
        # Should be valid
        assert not errors


class TestParameterInjectionSyntax:
    """Test parameter injection syntax validation."""

    def test_valid_parameter_injection(self):
        """Test valid ${parameter} syntax."""
        gfl_text = """
        optimize:
          search_space:
            temp: range(20, 40)
            ph: range(6.0, 8.0)
          strategy:
            name: RandomSearch
          objective:
            maximize: activity
          budget:
            max_experiments: 25
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temperature: ${temp}
                buffer_ph: ${ph}
                primer_conc: 0.5
        """
        ast = parse(gfl_text)

        assert ast is not None
        params = ast["optimize"]["run"]["experiment"]["params"]
        assert params["temperature"] == "${temp}"
        assert params["buffer_ph"] == "${ph}"
        assert params["primer_conc"] == 0.5

        errors = validate(ast)
        # Basic validation should pass
        assert not errors

    def test_parameter_reference_validation(self):
        """Test that parameter references match search space."""
        # This would be implemented in a more sophisticated parameter injection validator
        # For now, we just test that the basic structure is parsed correctly
        gfl_text = """
        optimize:
          search_space:
            param1: range(0, 10)
          strategy:
            name: ActiveLearning
          objective:
            maximize: result
          budget:
            max_experiments: 10
          run:
            experiment:
              tool: CRISPR_cas9
              type: gene_editing
              params:
                value: ${param1}
                other_param: ${undefined_param}  # This should eventually be flagged
        """
        ast = parse(gfl_text)
        assert ast is not None

        # Basic parsing should work
        params = ast["optimize"]["run"]["experiment"]["params"]
        assert params["value"] == "${param1}"
        assert params["other_param"] == "${undefined_param}"
