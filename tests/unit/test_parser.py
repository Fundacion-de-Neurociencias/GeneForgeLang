"""Unit tests for the GFL parser module.

Tests cover:
- Basic YAML parsing functionality
- AST structure validation
- Error handling for malformed input
- Edge cases and boundary conditions
"""

import pytest

from gfl.api import parse
from gfl.yaml_lang.parser import YamlParseError


class TestBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_minimal_experiment(self, gfl_utils):
        """Test parsing a minimal experiment block."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        assert "experiment" in ast
        exp = ast["experiment"]
        assert exp["tool"] == "CRISPR_cas9"
        assert exp["type"] == "gene_editing"
        assert exp["params"]["target_gene"] == "TP53"

    def test_parse_minimal_analysis(self, gfl_utils):
        """Test parsing a minimal analysis block."""
        gfl_text = """
        analyze:
          strategy: differential
          data: results.csv
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        assert "analyze" in ast
        analyze = ast["analyze"]
        assert analyze["strategy"] == "differential"
        assert analyze["data"] == "results.csv"

    def test_parse_simulation_block(self, gfl_utils):
        """Test parsing a simulation block."""
        gfl_text = """
        simulate: true
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)
        assert "simulate" in ast
        assert ast["simulate"] is True

    def test_parse_complex_experiment(self, gfl_utils):
        """Test parsing a complex experiment with all parameters."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          strategy: knockout
          params:
            target_gene: BRCA1
            guide_rna: GGGCCGGGCGGGCTCCCAGACATGCGTAT
            vector: pCRISPR-Cas9
            concentration: 50.0
            temperature: 37.0
            duration: "24h"
            replicates: 3
            custom_param: "custom_value"
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        exp = ast["experiment"]
        params = exp["params"]

        assert exp["strategy"] == "knockout"
        assert params["target_gene"] == "BRCA1"
        assert params["concentration"] == 50.0
        assert params["temperature"] == 37.0
        assert params["duration"] == "24h"
        assert params["replicates"] == 3
        assert params["custom_param"] == "custom_value"

    def test_parse_multiple_blocks(self, gfl_utils):
        """Test parsing GFL with multiple top-level blocks."""
        gfl_text = """
        experiment:
          tool: RNAseq
          type: sequencing
          params:
            sample_type: tissue

        analyze:
          strategy: pathway
          thresholds:
            p_value: 0.01
            fold_change: 1.5
          filters:
            - remove_low_counts
            - normalize

        simulate: false

        metadata:
          experiment_id: EXP001
          researcher: Dr. Smith
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        assert "experiment" in ast
        assert "analyze" in ast
        assert "simulate" in ast
        assert "metadata" in ast

        assert ast["experiment"]["tool"] == "RNAseq"
        assert ast["analyze"]["strategy"] == "pathway"
        assert ast["simulate"] is False
        assert ast["metadata"]["experiment_id"] == "EXP001"


class TestParsingEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_empty_document(self):
        """Test parsing an empty document."""
        with pytest.raises((YamlParseError, ValueError)):
            parse("")

    def test_parse_whitespace_only(self):
        """Test parsing a document with only whitespace."""
        result = parse("   \n  \n  ")
        assert result is None or result == {}

    def test_parse_comments_only(self):
        """Test parsing a document with only comments."""
        gfl_text = """
        # This is a comment
        # Another comment
        """
        result = parse(gfl_text)
        assert result is None or result == {}

    def test_parse_with_yaml_references(self, gfl_utils):
        """Test parsing with YAML anchors and references."""
        gfl_text = """
        defaults: &defaults
          concentration: 25.0
          temperature: 37.0

        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
            <<: *defaults
            replicates: 3
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        params = ast["experiment"]["params"]
        assert params["concentration"] == 25.0
        assert params["temperature"] == 37.0
        assert params["replicates"] == 3

    def test_parse_with_multiline_strings(self, gfl_utils):
        """Test parsing with multiline string values."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            description: |
              This is a multi-line description
              of the experiment protocol.
              It spans multiple lines.
            target_gene: TP53
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        description = ast["experiment"]["params"]["description"]
        assert "multi-line description" in description
        assert "multiple lines" in description

    def test_parse_unicode_content(self, gfl_utils):
        """Test parsing with Unicode characters."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53
            researcher: "José María"
            notes: "Étude génétique avancée"
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        params = ast["experiment"]["params"]
        assert params["researcher"] == "José María"
        assert params["notes"] == "Étude génétique avancée"


class TestParsingErrors:
    """Test error handling for malformed input."""

    def test_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
            invalid_indentation: value
        """
        with pytest.raises(Exception):  # Should raise YAML parsing error
            parse(gfl_text)

    def test_duplicate_keys(self):
        """Test handling of duplicate keys."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          tool: CRISPR_cas12
          type: gene_editing
        """
        # YAML allows duplicate keys (last one wins)
        ast = parse(gfl_text)
        assert ast["experiment"]["tool"] == "CRISPR_cas12"

    def test_malformed_list(self):
        """Test handling of malformed list syntax."""
        gfl_text = """
        analyze:
          strategy: differential
          filters:
            - filter1
            - filter2
            invalid_item
        """
        with pytest.raises(Exception):
            parse(gfl_text)

    def test_unquoted_special_characters(self):
        """Test handling of unquoted special characters."""
        gfl_text = """
        experiment:
          tool: CRISPR:cas9  # Colon without quotes
          type: gene_editing
        """
        with pytest.raises(Exception):
            parse(gfl_text)


class TestParsingPerformance:
    """Test parsing performance with larger inputs."""

    @pytest.mark.slow
    def test_parse_large_parameter_set(self, gfl_utils):
        """Test parsing with a large number of parameters."""
        params = {}
        for i in range(1000):
            params[f"param_{i}"] = f"value_{i}"

        import yaml

        large_gfl = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": params,
            }
        }

        gfl_text = yaml.dump(large_gfl)
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        assert len(ast["experiment"]["params"]) == 1000
        assert ast["experiment"]["params"]["param_500"] == "value_500"

    @pytest.mark.slow
    def test_parse_deeply_nested_structure(self, gfl_utils):
        """Test parsing with deeply nested structures."""
        gfl_text = """
        analyze:
          strategy: pathway
          operations:
            - type: filter
              params:
                conditions:
                  - field: expression
                    operator: greater_than
                    value: 2.0
                    metadata:
                      confidence: 0.95
                      source: reference_database
            - type: normalize
              params:
                method: quantile
                options:
                  robust: true
                  remove_zeros: false
        """
        ast = gfl_utils.assert_valid_gfl(gfl_text)

        operations = ast["analyze"]["operations"]
        assert len(operations) == 2

        filter_op = operations[0]
        condition = filter_op["params"]["conditions"][0]
        assert condition["metadata"]["confidence"] == 0.95


@pytest.mark.integration
class TestParsingIntegration:
    """Integration tests for parsing with other components."""

    def test_parse_and_validate_workflow(self, gfl_utils):
        """Test parsing followed by validation."""
        gfl_text = """
        experiment:
          tool: CRISPR_cas9
          type: gene_editing
          params:
            target_gene: TP53

        analyze:
          strategy: variant
          data: experiment_output
        """

        ast, errors = gfl_utils.parse_and_validate(gfl_text)
        assert not errors
        assert "experiment" in ast
        assert "analyze" in ast

    def test_parse_all_example_files(self, examples_dir):
        """Test parsing all files in the examples directory."""
        gfl_files = list(examples_dir.glob("*.gfl")) if examples_dir.exists() else []

        if not gfl_files:
            pytest.skip("No .gfl files found in examples directory")

        for gfl_file in gfl_files:
            try:
                content = gfl_file.read_text(encoding="utf-8")
                ast = parse(content)
                assert isinstance(ast, (dict, type(None)))
            except Exception as e:
                pytest.fail(f"Failed to parse {gfl_file}: {e}")
