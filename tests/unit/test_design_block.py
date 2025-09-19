"""Unit tests for the GFL design block functionality.

Tests cover:
- Design block parsing and validation
- Type definitions and conversions
- Error handling for malformed design blocks
- Design-specific constraints and objectives
"""

import pytest

from gfl.api import parse, validate
from gfl.types import Design


class TestDesignBlockParsing:
    """Test design block parsing functionality."""

    def test_parse_minimal_design(self):
        """Test parsing a minimal design block."""
        gfl_text = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
            target: ACE2_receptor
          count: 10
          output: designed_candidates
        """
        ast = parse(gfl_text)

        assert ast is not None
        assert "design" in ast

        design = ast["design"]
        assert design["entity"] == "ProteinSequence"
        assert design["model"] == "ProteinGeneratorVAE"
        assert design["objective"]["maximize"] == "binding_affinity"
        assert design["objective"]["target"] == "ACE2_receptor"
        assert design["count"] == 10
        assert design["output"] == "designed_candidates"

    def test_parse_design_with_constraints(self):
        """Test parsing design block with constraints."""
        gfl_text = """
        design:
          entity: DNASequence
          model: DNADesignerGAN
          objective:
            minimize: toxicity
          constraints:
            - length(50, 100)
            - gc_content(0.4, 0.6)
            - has_start_codon
          count: 5
          output: dna_designs
        """
        ast = parse(gfl_text)

        assert ast is not None
        design = ast["design"]
        assert design["entity"] == "DNASequence"
        assert design["model"] == "DNADesignerGAN"
        assert "minimize" in design["objective"]
        assert len(design["constraints"]) == 3
        assert "length(50, 100)" in design["constraints"]

    def test_parse_design_with_maximize_objective(self):
        """Test parsing design block with maximize objective."""
        gfl_text = """
        design:
          entity: SmallMolecule
          model: MoleculeTransformer
          objective:
            maximize: solubility
          count: 20
          output: molecules
        """
        ast = parse(gfl_text)

        design = ast["design"]
        assert design["objective"]["maximize"] == "solubility"
        assert "minimize" not in design["objective"]

    def test_parse_design_with_minimize_objective(self):
        """Test parsing design block with minimize objective."""
        gfl_text = """
        design:
          entity: Peptide
          model: SequenceOptimizer
          objective:
            minimize: aggregation
          count: 15
          output: peptides
        """
        ast = parse(gfl_text)

        design = ast["design"]
        assert design["objective"]["minimize"] == "aggregation"
        assert "maximize" not in design["objective"]


class TestDesignBlockValidation:
    """Test design block validation functionality."""

    def test_valid_design_block_passes(self):
        """Test that a valid design block passes validation."""
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert not errors

    def test_missing_required_fields(self):
        """Test validation errors for missing required fields."""
        # Missing entity
        ast = {
            "design": {
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("entity" in error.lower() for error in errors)

        # Missing model
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("model" in error.lower() for error in errors)

        # Missing objective
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("objective" in error.lower() for error in errors)

        # Missing count
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("count" in error.lower() for error in errors)

        # Missing output
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("output" in error.lower() for error in errors)

    def test_invalid_entity_type(self):
        """Test validation of invalid entity types."""
        ast = {
            "design": {
                "entity": "InvalidEntity",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        # Should have warnings but not necessarily errors (extensibility)

    def test_invalid_model_type(self):
        """Test validation of invalid model types."""
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "UnknownModel",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        # Should have warnings for unknown model

    def test_objective_validation(self):
        """Test objective field validation."""
        # Empty objective
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Both maximize and minimize
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity", "minimize": "toxicity"},
                "count": 10,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

    def test_count_validation(self):
        """Test count field validation."""
        # Negative count
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": -5,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Zero count
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 0,
                "output": "designed_proteins",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

    def test_output_validation(self):
        """Test output identifier validation."""
        # Invalid identifier
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "123invalid",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Valid identifiers should pass
        valid_outputs = ["designed_proteins", "_output", "output_var_1", "camelCaseOutput"]
        for output in valid_outputs:
            ast = {
                "design": {
                    "entity": "ProteinSequence",
                    "model": "ProteinGeneratorVAE",
                    "objective": {"maximize": "binding_affinity"},
                    "count": 10,
                    "output": output,
                }
            }
            errors = validate(ast)
            # Should not have errors specifically about the output identifier
            output_errors = [e for e in errors if "output" in e.lower() and "identifier" in e.lower()]
            assert len(output_errors) == 0

    def test_constraints_validation(self):
        """Test constraints field validation."""
        # Invalid constraints type
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
                "constraints": "not_a_list",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0

        # Non-string constraint items
        ast = {
            "design": {
                "entity": "ProteinSequence",
                "model": "ProteinGeneratorVAE",
                "objective": {"maximize": "binding_affinity"},
                "count": 10,
                "output": "designed_proteins",
                "constraints": [123, "valid_constraint"],
            }
        }
        errors = validate(ast)
        assert len(errors) > 0


class TestDesignTypeDefinitions:
    """Test Design type definitions and conversions."""

    def test_design_type_creation(self):
        """Test creating Design type instances."""
        design = Design(
            entity="ProteinSequence",
            model="ProteinGeneratorVAE",
            objective={"maximize": "binding_affinity"},
            count=10,
            output="designed_proteins",
        )

        assert design.entity == "ProteinSequence"
        assert design.model == "ProteinGeneratorVAE"
        assert design.objective == {"maximize": "binding_affinity"}
        assert design.count == 10
        assert design.output == "designed_proteins"
        assert design.constraints is None

    def test_design_with_constraints(self):
        """Test Design with constraints."""
        constraints = ["length(100, 200)", "has_motif('RGD')"]
        design = Design(
            entity="Peptide",
            model="SequenceOptimizer",
            objective={"minimize": "toxicity"},
            count=5,
            output="peptide_designs",
            constraints=constraints,
        )

        assert design.constraints == constraints

    def test_design_to_dict(self):
        """Test Design to_dict conversion."""
        design = Design(
            entity="DNASequence",
            model="DNADesignerGAN",
            objective={"maximize": "stability"},
            count=15,
            output="dna_sequences",
        )

        result = design.to_dict()
        expected = {
            "entity": "DNASequence",
            "model": "DNADesignerGAN",
            "objective": {"maximize": "stability"},
            "count": 15,
            "output": "dna_sequences",
        }

        assert result == expected

    def test_design_to_dict_with_constraints(self):
        """Test Design to_dict with constraints."""
        constraints = ["gc_content(0.4, 0.6)", "no_repeats"]
        design = Design(
            entity="DNASequence",
            model="DNADesignerGAN",
            objective={"maximize": "stability"},
            count=15,
            output="dna_sequences",
            constraints=constraints,
        )

        result = design.to_dict()
        assert result["constraints"] == constraints


class TestDesignBlockIntegration:
    """Test design block integration with other blocks."""

    def test_design_with_analyze_workflow(self):
        """Test design block followed by analysis."""
        gfl_text = """
        design:
          entity: ProteinSequence
          model: ProteinGeneratorVAE
          objective:
            maximize: binding_affinity
            target: ACE2_receptor
          count: 10
          output: designed_candidates

        analyze:
          strategy: functional
          data: designed_candidates
          thresholds:
            binding_score: 0.8
        """
        ast = parse(gfl_text)

        assert ast is not None
        assert "design" in ast
        assert "analyze" in ast

        # Analyze block should reference the design output
        assert ast["analyze"]["data"] == "designed_candidates"

        errors = validate(ast)
        # Should be valid
        assert not errors

    def test_design_with_multiple_blocks(self):
        """Test design block in complex workflow."""
        gfl_text = """
        metadata:
          experiment_id: DESIGN_001
          researcher: Dr. Smith

        design:
          entity: SmallMolecule
          model: MoleculeTransformer
          objective:
            maximize: activity
            minimize: toxicity
          count: 50
          output: candidate_molecules

        analyze:
          strategy: comparative
          data: candidate_molecules
        """
        ast = parse(gfl_text)

        assert "metadata" in ast
        assert "design" in ast
        assert "analyze" in ast

        # This should fail validation due to conflicting objective
        errors = validate(ast)
        assert len(errors) > 0
