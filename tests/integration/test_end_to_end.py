"""Integration tests for end-to-end GFL workflows.

Tests cover:
- Complete parse -> validate -> infer workflows
- Integration between different components
- Real-world usage scenarios
- Performance with realistic data
"""

import pytest

from gfl.api import parse, validate, infer
from gfl.models.dummy import DummyGeneModel


class TestBasicWorkflows:
    """Test basic end-to-end workflows."""

    def test_simple_experiment_workflow(self, gfl_utils):
        """Test complete workflow for simple experiment."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
            guide_rna: GGGCCGGGCGGGCTCCCAGACATGCGTAT
            concentration: 50.0
        """

        # Parse
        ast = parse(gfl_text)
        assert isinstance(ast, dict)
        assert "experiment" in ast

        # Validate
        errors = validate(ast)
        assert not errors, f"Validation failed: {errors}"

        # Infer
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)
        assert "label" in result
        assert "confidence" in result

    def test_analysis_workflow(self, gfl_utils):
        """Test complete workflow for analysis."""
        gfl_text = """
        analyze:
          strategy: differential
          data: experiment_results.csv
          thresholds:
            p_value: 0.05
            fold_change: 2.0
          filters:
            - remove_low_counts
            - normalize
          operations:
            - type: sort
              field: p_value
              order: ascending
        """

        ast, errors = gfl_utils.parse_and_validate(gfl_text)
        assert not errors
        assert ast["analyze"]["strategy"] == "differential"

        # Should be able to run inference even on analysis-only AST
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)

    def test_multi_block_workflow(self, gfl_utils):
        """Test workflow with multiple blocks."""
        gfl_text = """
        experiment:
          tool: RNAseq
          type: sequencing
          params:
            sample_type: tissue
            read_length: 150
            paired_end: true

        analyze:
          strategy: pathway
          data: sequencing_output
          thresholds:
            fdr: 0.01
            pathway_score: 0.7

        simulate: false

        metadata:
          experiment_id: RNA001
          researcher: Dr. Smith
          date: "2024-01-01"
        """

        ast = gfl_utils.assert_valid_gfl(gfl_text)

        # All blocks should be present
        assert "experiment" in ast
        assert "analyze" in ast
        assert "simulate" in ast
        assert "metadata" in ast

        # Run inference
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)


class TestErrorHandling:
    """Test error handling in integrated workflows."""

    def test_parse_error_handling(self):
        """Test handling of parse errors in workflow."""
        invalid_gfl = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
            invalid_indentation: value
        """

        with pytest.raises(Exception):
            parse(invalid_gfl)

    def test_validation_error_handling(self, gfl_utils):
        """Test handling of validation errors in workflow."""
        gfl_text = """
        experiment:
          type: gene_editing
          # Missing required 'tool' field
          params:
            target_gene: TP53
        """

        ast, errors = gfl_utils.parse_and_validate(gfl_text)
        assert errors  # Should have validation errors

        # Should still be able to run inference with invalid AST
        # (implementation dependent)
        model = DummyGeneModel()
        try:
            result = infer(model, ast)
            # If no exception, result should be dict
            assert isinstance(result, dict)
        except Exception:
            # Exception is acceptable for invalid AST
            pass

    def test_inference_error_handling(self, valid_experiment_ast):
        """Test handling of inference errors."""

        class FaultyModel:
            def predict(self, features):
                raise ValueError("Model prediction failed")

        errors = validate(valid_experiment_ast)
        assert not errors

        model = FaultyModel()
        with pytest.raises(ValueError):
            infer(model, valid_experiment_ast)


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    def test_crispr_knockout_experiment(self, gfl_utils):
        """Test CRISPR knockout experiment scenario."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          strategy: knockout
          params:
            target_gene: BRCA1
            guide_rna: GGGCCGGGCGGGCTCCCAGACATGCGTAT
            vector: pCRISPR-Cas9
            concentration: 75.0
            temperature: 37.0
            duration: "48h"
            replicates: 3
            cell_line: HEK293T
            transfection_method: lipofection

        analyze:
          strategy: variant
          data: sequencing_results
          thresholds:
            quality_score: 30
            coverage: 100
          filters:
            - remove_duplicates
            - quality_filter
          operations:
            - type: variant_calling
              params:
                caller: gatk
                reference: hg38
            - type: annotation
              params:
                database: ensembl

        metadata:
          experiment_id: CRISPR_KO_001
          project: cancer_research
          approval_id: IRB2024001
          date: "2024-01-15"
        """

        ast = gfl_utils.assert_valid_gfl(gfl_text)

        # Verify experiment details
        exp = ast["experiment"]
        assert exp["strategy"] == "knockout"
        assert exp["params"]["target_gene"] == "BRCA1"
        assert exp["params"]["replicates"] == 3

        # Verify analysis details
        analyze = ast["analyze"]
        assert analyze["strategy"] == "variant"
        assert len(analyze["operations"]) == 2

        # Run inference
        model = DummyGeneModel()
        result = infer(model, ast)
        assert "label" in result

    def test_rnaseq_differential_analysis(self, gfl_utils):
        """Test RNA-seq differential expression analysis scenario."""
        gfl_text = """
        experiment:
          tool: RNAseq
          type: sequencing
          params:
            sample_type: tissue
            read_length: 150
            paired_end: true
            stranded: true
            library_prep: polyA
            platform: illumina
            samples:
              - control_1
              - control_2
              - control_3
              - treated_1
              - treated_2
              - treated_3

        analyze:
          strategy: differential
          data: count_matrix.tsv
          thresholds:
            p_value: 0.05
            adjusted_p_value: 0.1
            fold_change: 1.5
            min_counts: 10
          filters:
            - remove_low_counts
            - normalize_library_size
            - log_transform
          operations:
            - type: differential_expression
              params:
                method: deseq2
                design: "~ condition"
                contrast: ["condition", "treated", "control"]
            - type: pathway_analysis
              params:
                database: kegg
                method: gsea

        metadata:
          study: cancer_treatment_response
          tissue_type: liver
          treatment: drug_x
          duration: "7d"
        """

        ast = gfl_utils.assert_valid_gfl(gfl_text)

        # Verify complex structure
        exp_params = ast["experiment"]["params"]
        assert exp_params["paired_end"] is True
        assert len(exp_params["samples"]) == 6

        analyze = ast["analyze"]
        assert len(analyze["filters"]) == 3
        assert len(analyze["operations"]) == 2

        # Should handle complex analysis
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)

    def test_simulation_scenario(self, gfl_utils):
        """Test simulation-based workflow."""
        gfl_text = """
        simulate: true

        experiment:
          tool: variant_simulator
          type: simulation
          params:
            population: european
            sample_size: 1000
            variant_types:
              - snv
              - indel
              - cnv
            mutation_rate: 1e-8
            selection_coefficient: 0.01

        analyze:
          strategy: variant
          data: simulated_variants
          thresholds:
            allele_frequency: 0.01
            effect_size: 0.1

        metadata:
          simulation_id: SIM_001
          purpose: method_validation
        """

        ast = gfl_utils.assert_valid_gfl(gfl_text)
        assert ast["simulate"] is True

        # Should work with simulation data
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)


class TestComponentIntegration:
    """Test integration between different GFL components."""

    def test_parser_validator_integration(self):
        """Test integration between parser and validator."""
        # Test that parser output is compatible with validator
        test_cases = [
            """
            experiment:
              tool: CRISPR_cas9
              type: gene_editing
              params:
                target_gene: TP53
            """,
            """
            analyze:
              strategy: differential
              data: results.csv
            """,
            """
            simulate: true
            """,
        ]

        for gfl_text in test_cases:
            ast = parse(gfl_text)
            errors = validate(ast)
            # Should not fail due to format incompatibility
            assert isinstance(errors, list)

    def test_validator_inference_integration(self, valid_experiment_ast):
        """Test integration between validator and inference engine."""
        # Valid AST should work with inference
        errors = validate(valid_experiment_ast)
        assert not errors

        model = DummyGeneModel()
        result = infer(model, valid_experiment_ast)
        assert isinstance(result, dict)

    def test_full_pipeline_integration(self, gfl_utils):
        """Test full pipeline integration."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
            concentration: 50.0

        analyze:
          strategy: variant
          data: experiment_output
        """

        # Full pipeline: parse -> validate -> infer
        ast = parse(gfl_text)
        assert isinstance(ast, dict)

        errors = validate(ast)
        assert not errors

        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict)
        assert "label" in result


@pytest.mark.performance
class TestPerformanceIntegration:
    """Test performance of integrated workflows."""

    @pytest.mark.slow
    def test_large_experiment_workflow(self, gfl_utils):
        """Test workflow with large experiment parameters."""
        import time

        # Create large parameter set
        large_params = {f"param_{i}": f"value_{i}" for i in range(100)}

        import yaml

        large_gfl_dict = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53", **large_params},
            }
        }

        gfl_text = yaml.dump(large_gfl_dict)

        start_time = time.time()

        # Full workflow
        ast = parse(gfl_text)
        errors = validate(ast)
        assert not errors

        model = DummyGeneModel()
        result = infer(model, ast)

        end_time = time.time()

        # Should complete in reasonable time
        assert end_time - start_time < 10.0  # Less than 10 seconds
        assert isinstance(result, dict)

    @pytest.mark.slow
    def test_multiple_workflows_performance(self, gfl_utils):
        """Test performance of running multiple workflows."""
        import time

        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
        """

        model = DummyGeneModel()

        start_time = time.time()

        # Run workflow multiple times
        for i in range(50):
            ast = parse(gfl_text)
            errors = validate(ast)
            assert not errors
            result = infer(model, ast)
            assert isinstance(result, dict)

        end_time = time.time()

        # Should handle multiple workflows efficiently
        assert end_time - start_time < 30.0  # Less than 30 seconds for 50 runs


class TestExampleFiles:
    """Test integration with example files."""

    def test_parse_all_examples(self, examples_dir):
        """Test parsing all example files."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        gfl_files = list(examples_dir.glob("*.gfl"))
        if not gfl_files:
            pytest.skip("No .gfl files found in examples")

        model = DummyGeneModel()

        for gfl_file in gfl_files:
            try:
                content = gfl_file.read_text(encoding="utf-8")

                # Full workflow on example
                ast = parse(content)
                assert isinstance(ast, (dict, type(None)))

                if ast:
                    errors = validate(ast)
                    # Examples should be valid
                    if errors:
                        pytest.fail(
                            f"Example {gfl_file.name} has validation errors: {errors}"
                        )

                    # Try inference
                    result = infer(model, ast)
                    assert isinstance(result, dict)

            except Exception as e:
                pytest.fail(f"Failed to process example {gfl_file.name}: {e}")

    def test_roundtrip_examples(self, examples_dir):
        """Test roundtrip conversion of example files."""
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")

        gfl_files = list(examples_dir.glob("*.gfl"))
        if not gfl_files:
            pytest.skip("No .gfl files found in examples")

        for gfl_file in gfl_files[:5]:  # Test first 5 files only
            try:
                content = gfl_file.read_text(encoding="utf-8")

                # Parse and validate
                ast = parse(content)
                if not ast:
                    continue

                errors = validate(ast)
                if errors:
                    continue  # Skip invalid examples for roundtrip test

                # If we have typed AST support, test roundtrip
                try:
                    from gfl.types import GFLAST

                    typed_ast = GFLAST.from_dict(ast)
                    reconstructed_dict = typed_ast.to_dict()

                    # Key fields should be preserved
                    if "experiment" in ast:
                        assert "experiment" in reconstructed_dict
                        assert (
                            ast["experiment"]["tool"]
                            == reconstructed_dict["experiment"]["tool"]
                        )

                except ImportError:
                    # Skip if typed AST not available
                    pass

            except Exception as e:
                pytest.fail(f"Roundtrip test failed for {gfl_file.name}: {e}")
