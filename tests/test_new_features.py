"""
Comprehensive regression test suite for GeneForgeLang new features.

This module contains pytest test cases to validate the correct parsing and
semantic validation of the recently implemented design and optimize blocks.
These tests prevent future updates from breaking existing functionality.
"""

import pytest

from gfl.api import parse, validate


class TestNewFeaturesRegression:
    """Regression tests for new GFL features."""

    def test_valid_gfl_script_with_all_new_features(self):
        """Test that a valid GFL script using all new features parses and validates correctly."""

        gfl_script = """
        metadata:
          experiment_id: COMPREHENSIVE_TEST_001
          researcher: Dr. Test Suite
          project: feature_validation
          description: Comprehensive test of all new GFL features

        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
            target: ACE2_receptor
          constraints:
            - length(120, 150)
            - synthesizability > 0.7
          count: 25
          output: designed_sequences

        analyze:
          strategy: functional
          data: designed_sequences
          thresholds:
            binding_score: 0.8
            stability_score: 0.7
          operations:
            - type: sort
              params:
                by: binding_affinity
                order: descending

        optimize:
          search_space:
            temperature: range(25, 42)
            concentration: range(10, 100)
            duration: choice([6, 12, 24, 48])
            buffer_ph: range(6.5, 8.5)
          strategy:
            name: ActiveLearning
            uncertainty_metric: entropy
            initial_samples: 8
          objective:
            maximize: reaction_efficiency
          budget:
            max_experiments: 100
            max_time: 48h
            convergence_threshold: 0.01
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
                conc: ${concentration}
                time: ${duration}h
                ph: ${buffer_ph}
                target_gene: GFP
                replicates: 3
        """

        # Test parsing
        ast = parse(gfl_script)
        assert ast is not None, "Valid GFL script should parse successfully"

        # Verify all blocks are present
        assert "metadata" in ast, "Metadata block should be present"
        assert "design" in ast, "Design block should be present"
        assert "analyze" in ast, "Analyze block should be present"
        assert "optimize" in ast, "Optimize block should be present"

        # Test validation
        errors = validate(ast)
        assert not errors, f"Valid GFL script should validate without errors, got: {errors}"


class TestDesignBlockValidation:
    """Regression tests for design block validation."""

    def test_design_block_missing_objective_field(self):
        """Test that design block without objective field fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          # Missing objective field
          count: 10
          output: designed_proteins
        """

        ast = parse(gfl_script)
        assert ast is not None, "Script should parse even with missing fields"

        errors = validate(ast)
        assert len(errors) > 0, "Missing objective field should cause validation error"

        # Check that error mentions objective
        error_text = " ".join(str(error) for error in errors).lower()
        assert "objective" in error_text, "Error should mention missing objective field"

    def test_design_block_missing_entity_field(self):
        """Test that design block without entity field fails validation."""

        gfl_script = """
        design:
          # Missing entity field
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
          count: 10
          output: designed_proteins
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Missing entity field should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "entity" in error_text, "Error should mention missing entity field"

    def test_design_block_missing_model_field(self):
        """Test that design block without model field fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          # Missing model field
          objective:
            maximize: binding_affinity
          count: 10
          output: designed_proteins
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Missing model field should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "model" in error_text, "Error should mention missing model field"

    def test_design_block_invalid_count_negative(self):
        """Test that design block with negative count fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
          count: -1
          output: designed_proteins
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Negative count should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "count" in error_text, "Error should mention count field"

    def test_design_block_invalid_count_zero(self):
        """Test that design block with zero count fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
          count: 0
          output: designed_proteins
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Zero count should cause validation error"

    def test_design_block_conflicting_objectives(self):
        """Test that design block with both maximize and minimize fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
            minimize: toxicity
          count: 10
          output: designed_proteins
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Conflicting objectives should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "maximize" in error_text and "minimize" in error_text, \
            "Error should mention conflicting objectives"

    def test_design_block_invalid_output_identifier(self):
        """Test that design block with invalid output identifier fails validation."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
          count: 10
          output: 123invalid_identifier
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Invalid output identifier should cause validation error"


class TestOptimizeBlockValidation:
    """Regression tests for optimize block validation."""

    def test_optimize_block_missing_search_space(self):
        """Test that optimize block without search_space fails validation."""

        gfl_script = """
        optimize:
          # Missing search_space
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Missing search_space should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "search_space" in error_text, "Error should mention missing search_space"

    def test_optimize_block_missing_run_block(self):
        """Test that optimize block without run block fails validation."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          # Missing run block
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Missing run block should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "run" in error_text, "Error should mention missing run block"

    def test_optimize_block_undefined_parameter_injection(self):
        """Test parameter injection with undefined search space variable."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
            # learning_rate is not defined here
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
                rate: ${learning_rate}  # This parameter is not in search_space
        """

        ast = parse(gfl_script)

        # Basic parsing should succeed
        assert ast is not None, "Script should parse successfully"

        # Currently our validation doesn't enforce parameter matching between
        # search_space and injected parameters. This is a future enhancement.
        # For now, we just check that parameter injection syntax is recognized
        experiment_params = ast["optimize"]["run"]["experiment"]["params"]
        assert experiment_params["temp"] == "${temperature}"
        assert experiment_params["rate"] == "${learning_rate}"

    def test_optimize_block_invalid_search_space_syntax(self):
        """Test optimize block with invalid search space parameter syntax."""

        gfl_script = """
        optimize:
          search_space:
            temperature: invalid_syntax  # Should be range(...) or choice([...])
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Invalid search space syntax should cause validation error"

    def test_optimize_block_empty_search_space(self):
        """Test optimize block with empty search space."""

        gfl_script = """
        optimize:
          search_space: {}  # Empty search space
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Empty search space should cause validation error"

    def test_optimize_block_missing_strategy_name(self):
        """Test optimize block with strategy missing name field."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
          strategy:
            # Missing name field
            uncertainty_metric: entropy
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Missing strategy name should cause validation error"

        error_text = " ".join(str(error) for error in errors).lower()
        assert "name" in error_text, "Error should mention missing name field"

    def test_optimize_block_conflicting_objectives(self):
        """Test optimize block with conflicting objectives."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
            minimize: cost  # Conflicting with maximize
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Conflicting objectives should cause validation error"

    def test_optimize_block_empty_budget(self):
        """Test optimize block with empty budget."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget: {}  # Empty budget
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Empty budget should cause validation error"

    def test_optimize_block_invalid_budget_values(self):
        """Test optimize block with invalid budget values."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(25, 40)
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: -10  # Invalid negative value
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Invalid budget values should cause validation error"

    def test_optimize_block_invalid_range_syntax(self):
        """Test optimize block with invalid range syntax in search space."""

        gfl_script = """
        optimize:
          search_space:
            temperature: range(40, 25)  # min > max (invalid)
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temp: ${temperature}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Invalid range syntax should cause validation error"

    def test_optimize_block_empty_choice_syntax(self):
        """Test optimize block with empty choice syntax in search space."""

        gfl_script = """
        optimize:
          search_space:
            method: choice([])  # Empty choice array
          strategy:
            name: ActiveLearning
          objective:
            maximize: efficiency
          budget:
            max_experiments: 50
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                method: ${method}
        """

        ast = parse(gfl_script)
        errors = validate(ast)
        assert len(errors) > 0, "Empty choice array should cause validation error"


class TestParameterInjectionRegression:
    """Regression tests for parameter injection functionality."""

    def test_parameter_injection_basic_syntax(self):
        """Test that basic parameter injection syntax is parsed correctly."""

        gfl_script = """
        optimize:
          search_space:
            temp: range(20, 40)
            conc: range(1, 10)
          strategy:
            name: RandomSearch
          objective:
            maximize: yield
          budget:
            max_experiments: 10
          run:
            experiment:
              tool: PCR
              type: validation
              params:
                temperature: ${temp}
                concentration: ${conc}
                buffer: "PBS"
                replicates: 3
        """

        ast = parse(gfl_script)
        assert ast is not None, "Script with parameter injection should parse"

        # Verify parameter injection is preserved
        params = ast["optimize"]["run"]["experiment"]["params"]
        assert params["temperature"] == "${temp}", "Parameter injection should be preserved"
        assert params["concentration"] == "${conc}", "Parameter injection should be preserved"
        assert params["buffer"] == "PBS", "Non-injected parameters should be preserved"
        assert params["replicates"] == 3, "Non-injected parameters should be preserved"

        # Validation should pass
        errors = validate(ast)
        assert not errors, f"Parameter injection should validate correctly, got: {errors}"

    def test_parameter_injection_mixed_with_static_values(self):
        """Test parameter injection mixed with static parameter values."""

        gfl_script = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
            guide_rna: GGGCCGGGCGGGCTCCCAGA
            concentration: ${guide_concentration}  # Injected parameter
            temperature: 37.0                     # Static value
            duration: ${incubation_time}h          # Injected with unit
            replicates: 3                         # Static value
        """

        ast = parse(gfl_script)
        assert ast is not None, "Mixed parameter script should parse"

        params = ast["experiment"]["params"]
        assert params["concentration"] == "${guide_concentration}"
        assert params["temperature"] == 37.0
        assert params["duration"] == "${incubation_time}h"
        assert params["replicates"] == 3

    def test_parameter_injection_validation_skips_injected_params(self):
        """Test that parameter validation correctly skips injected parameters."""

        gfl_script = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            # These would normally fail type validation, but should be skipped
            # since they're parameter injections
            temperature: ${temp_param}      # Would fail if validated as string
            concentration: ${conc_param}    # Would fail if validated as string
            replicates: ${rep_param}        # Would fail if validated as string
            # This should still be validated normally
            target_gene: TP53
        """

        ast = parse(gfl_script)
        errors = validate(ast)

        # Should not have type validation errors for injected parameters
        type_errors = [e for e in errors if "should be" in str(e) and "got str" in str(e)]
        assert not type_errors, f"Parameter injection should skip type validation, got: {type_errors}"


class TestCombinedFeatureWorkflows:
    """Regression tests for combined feature workflows."""

    def test_design_feeding_optimize(self):
        """Test workflow where design output feeds into optimize block."""

        gfl_script = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
          count: 50
          output: candidate_proteins

        optimize:
          search_space:
            screening_threshold: range(0.1, 0.9)
            batch_size: choice([10, 20, 50])
          strategy:
            name: BayesianOptimization
          objective:
            maximize: hit_rate
          budget:
            max_experiments: 25
          run:
            analyze:
              strategy: functional
              data: candidate_proteins
              thresholds:
                binding_score: ${screening_threshold}
              operations:
                - type: filter
                  params:
                    top_n: ${batch_size}
        """

        ast = parse(gfl_script)
        assert ast is not None, "Combined workflow should parse"

        # Verify design output matches analyze input
        design_output = ast["design"]["output"]
        analyze_data = ast["optimize"]["run"]["analyze"]["data"]
        assert design_output == analyze_data, "Design output should feed into analysis"

        errors = validate(ast)
        assert not errors, f"Combined workflow should validate, got: {errors}"

    def test_multiple_optimize_blocks_invalid(self):
        """Test that multiple optimize blocks in one file are handled correctly."""

        gfl_script = """
        optimize:
          search_space:
            param1: range(1, 10)
          strategy:
            name: ActiveLearning
          objective:
            maximize: metric1
          budget:
            max_experiments: 20
          run:
            experiment:
              tool: PCR
              type: validation

        optimize:  # Second optimize block - should this be allowed?
          search_space:
            param2: range(5, 15)
          strategy:
            name: RandomSearch
          objective:
            maximize: metric2
          budget:
            max_experiments: 30
          run:
            experiment:
              tool: RNAseq
              type: sequencing
        """

        # This should parse (multiple top-level blocks of same type)
        ast = parse(gfl_script)
        assert ast is not None, "Multiple optimize blocks should parse"

        # However, validation behavior may vary - this tests current behavior
        errors = validate(ast)
        # We don't assert specific validation results here as the behavior
        # for multiple identical block types may be implementation-specific


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
