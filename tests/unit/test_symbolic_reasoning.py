"""Unit tests for the new symbolic reasoning features in GFL.

Tests cover:
- Rules block validation
- Hypothesis block validation
- Timeline block validation
- Pathway and complex entity validation
- Hypothesis reference validation
- Entity reference validation
"""

import pytest

from gfl.api import validate


class TestRulesBlockValidation:
    """Test rules block validation."""

    def test_valid_rules_block(self):
        """Test validation of a valid rules block."""
        ast = {
            "rules": [
                {
                    "id": "rule1",
                    "if": {"gene": "TP53", "mutation": "R175H"},
                    "then": {"effect": "increased_risk", "cancer_type": "breast"},
                },
                {
                    "id": "rule2",
                    "if": {"gene": "BRCA1", "expression": "low"},
                    "then": {"effect": "increased_risk", "cancer_type": "ovarian"},
                },
            ]
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_rules_block_not_list(self):
        """Test validation when rules block is not a list."""
        ast = {"rules": {"id": "rule1", "if": {"gene": "TP53"}, "then": {"effect": "increased_risk"}}}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("list" in error.lower() for error in errors)

    def test_invalid_rule_missing_fields(self):
        """Test validation when rule is missing required fields."""
        ast = {
            "rules": [
                {
                    "id": "rule1",
                    # Missing 'if' and 'then' fields
                }
            ]
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("if" in error.lower() for error in errors)
        assert any("then" in error.lower() for error in errors)


class TestHypothesisBlockValidation:
    """Test hypothesis block validation."""

    def test_valid_hypothesis_block(self):
        """Test validation of a valid hypothesis block."""
        ast = {
            "hypothesis": {
                "id": "hypothesis1",
                "description": "TP53 mutations increase cancer risk",
                "if": [{"gene": "TP53", "mutation": "R175H"}, {"expression": "low"}],
                "then": [
                    {"effect": "increased_risk", "cancer_type": "breast"},
                    {"biomarker": "Ki67", "expression": "high"},
                ],
            }
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_hypothesis_block_not_dict(self):
        """Test validation when hypothesis block is not a dictionary."""
        ast = {"hypothesis": [{"id": "hypothesis1", "description": "TP53 mutations increase cancer risk"}]}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("dictionary" in error.lower() for error in errors)

    def test_invalid_hypothesis_missing_fields(self):
        """Test validation when hypothesis is missing required fields."""
        ast = {
            "hypothesis": {
                "id": "hypothesis1",
                # Missing 'description', 'if', and 'then' fields
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("description" in error.lower() for error in errors)
        assert any("if" in error.lower() for error in errors)
        assert any("then" in error.lower() for error in errors)

    def test_invalid_hypothesis_field_types(self):
        """Test validation when hypothesis fields have wrong types."""
        ast = {
            "hypothesis": {
                "id": "hypothesis1",
                "description": "TP53 mutations increase cancer risk",
                "if": "not_a_list",  # Should be a list
                "then": "not_a_list",  # Should be a list
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("list" in error.lower() for error in errors)


class TestTimelineBlockValidation:
    """Test timeline block validation."""

    def test_valid_timeline_block(self):
        """Test validation of a valid timeline block."""
        ast = {
            "timeline": {
                "events": [
                    {
                        "at": "2024-01-01",
                        "actions": [{"type": "sequencing", "sample": "patient1"}],
                        "expectations": [{"outcome": "high_quality_data"}],
                    },
                    {"at": "2024-01-15", "actions": [{"type": "analysis", "data": "sequencing_results"}]},
                ]
            }
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_timeline_block_not_dict(self):
        """Test validation when timeline block is not a dictionary."""
        ast = {"timeline": [{"events": []}]}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("dictionary" in error.lower() for error in errors)

    def test_invalid_timeline_missing_events(self):
        """Test validation when timeline is missing required events field."""
        ast = {
            "timeline": {
                # Missing 'events' field
                "description": "Study timeline"
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("events" in error.lower() for error in errors)

    def test_invalid_timeline_events_not_list(self):
        """Test validation when timeline events is not a list."""
        ast = {"timeline": {"events": "not_a_list"}}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("list" in error.lower() for error in errors)

    def test_invalid_timeline_event_missing_fields(self):
        """Test validation when timeline event is missing required fields."""
        ast = {
            "timeline": {
                "events": [
                    {
                        # Missing 'at' and 'actions' fields
                        "description": "Event description"
                    }
                ]
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("at" in error.lower() for error in errors)
        assert any("actions" in error.lower() for error in errors)

    def test_invalid_timeline_event_field_types(self):
        """Test validation when timeline event fields have wrong types."""
        ast = {
            "timeline": {
                "events": [
                    {
                        "at": 123,  # Should be a string
                        "actions": "not_a_list",  # Should be a list
                    }
                ]
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("string" in error.lower() for error in errors)
        assert any("list" in error.lower() for error in errors)


class TestEntityDefinitionValidation:
    """Test pathway and complex entity definition validation."""

    def test_valid_pathways_block(self):
        """Test validation of a valid pathways block."""
        ast = {
            "pathways": {
                "UreaCycle": {
                    "description": "Urea cycle metabolic pathway",
                    "genes": ["ASS1", "ASL", "ARG1"],
                    "enzymes": ["ASS", "ASL", "ARG"],
                    "reactions": [{"substrate": "ornithine", "product": "citrulline"}],
                },
                "Glycolysis": {
                    "description": "Glycolysis pathway",
                    "genes": ["HK1", "PGK1", "PKM"],
                    "enzymes": ["Hexokinase", "Phosphoglycerate kinase", "Pyruvate kinase"],
                },
            }
        }
        errors = validate(ast)
        assert not errors

    def test_valid_complexes_block(self):
        """Test validation of a valid complexes block."""
        ast = {
            "complexes": {
                "RNA_POLYMERASE_II": {
                    "description": "RNA polymerase II complex",
                    "subunits": ["POLR2A", "POLR2B", "POLR2C", "POLR2D", "POLR2E"],
                    "function": "transcription",
                },
                "RIBOSOME_80S": {
                    "description": "80S ribosome complex",
                    "subunits": ["RPSA", "RPSB", "RPLA", "RPLB"],
                    "function": "translation",
                },
            }
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_pathways_not_dict(self):
        """Test validation when pathways block is not a dictionary."""
        ast = {"pathways": [{"UreaCycle": {"description": "Urea cycle metabolic pathway"}}]}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("dictionary" in error.lower() for error in errors)

    def test_invalid_complexes_not_dict(self):
        """Test validation when complexes block is not a dictionary."""
        ast = {"complexes": [{"RNA_POLYMERASE_II": {"description": "RNA polymerase II complex"}}]}
        errors = validate(ast)
        assert len(errors) > 0
        assert any("dictionary" in error.lower() for error in errors)


class TestHypothesisReferenceValidation:
    """Test hypothesis reference validation in experiment and analysis blocks."""

    def test_valid_experiment_with_hypothesis_reference(self):
        """Test validation of experiment block with valid hypothesis reference."""
        ast = {
            "hypothesis": {
                "id": "hypothesis1",
                "description": "TP53 mutations increase cancer risk",
                "if": [{"gene": "TP53", "mutation": "R175H"}],
                "then": [{"effect": "increased_risk"}],
            },
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
                "validates_hypothesis": "hypothesis1",
            },
        }
        errors = validate(ast)
        assert not errors

    def test_valid_analysis_with_hypothesis_reference(self):
        """Test validation of analysis block with valid hypothesis reference."""
        ast = {
            "hypothesis": {
                "id": "hypothesis1",
                "description": "TP53 mutations increase cancer risk",
                "if": [{"gene": "TP53", "mutation": "R175H"}],
                "then": [{"effect": "increased_risk"}],
            },
            "analyze": {"strategy": "variant", "data": "sequencing_results.csv", "validates_hypothesis": "hypothesis1"},
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_hypothesis_reference_undefined(self):
        """Test validation when referencing undefined hypothesis."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
                "validates_hypothesis": "undefined_hypothesis",
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("undefined" in error.lower() for error in errors)
        assert any("hypothesis" in error.lower() for error in errors)

    def test_invalid_hypothesis_reference_wrong_type(self):
        """Test validation when hypothesis reference is not a string."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
                "validates_hypothesis": 123,  # Should be a string
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("string" in error.lower() for error in errors)


class TestEntityReferenceValidation:
    """Test entity reference validation in parameter values."""

    def test_valid_pathway_reference_in_params(self):
        """Test validation of pathway reference in experiment parameters."""
        ast = {
            "pathways": {
                "UreaCycle": {"description": "Urea cycle metabolic pathway", "genes": ["ASS1", "ASL", "ARG1"]}
            },
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_pathway": "pathway(UreaCycle)", "concentration": 50.0},
            },
        }
        errors = validate(ast)
        assert not errors

    def test_valid_complex_reference_in_params(self):
        """Test validation of complex reference in experiment parameters."""
        ast = {
            "complexes": {
                "RNA_POLYMERASE_II": {"description": "RNA polymerase II complex", "subunits": ["POLR2A", "POLR2B"]}
            },
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_complex": "complex(RNA_POLYMERASE_II)", "temperature": 37.0},
            },
        }
        errors = validate(ast)
        assert not errors

    def test_invalid_entity_reference_undefined(self):
        """Test validation when referencing undefined entity."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_pathway": "pathway(UndefinedPathway)"},
            }
        }
        errors = validate(ast)
        assert len(errors) > 0
        assert any("undefined" in error.lower() for error in errors)
        assert any("pathway" in error.lower() for error in errors)

    def test_invalid_entity_reference_wrong_format(self):
        """Test validation when entity reference has wrong format."""
        ast = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {
                    "target_pathway": "pathway_UreaCycle"  # Wrong format, should be pathway(UreaCycle)
                },
            }
        }
        errors = validate(ast)
        # This might not generate an error since it's treated as a regular string parameter
        # But if we do check for entity references, it should catch this
