"""Unit tests for Prompteina text-conditioned protein design contracts in GeneForgeLang."""

from geneforgelang.core.gftypes import (
    NaturalLanguageConditioningContract,
    TextConditionedDesignContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_prompteina_contracts_instantiation_and_dict() -> None:
    """Test creating and serializing Prompteina design contracts."""
    prompt_contract = NaturalLanguageConditioningContract(
        prompt="Design an alpha-helical bundle that binds the hydrophobic cavity of GM2A",
        macro_topology="Three-helix bundle with amphipathic packing",
        interaction_site="Target the apical cavity around Thr108 and Leu115",
        negative_design="Avoid binding the lipid transfer gateway residues Lys88-Asp91",
        symmetry="C1",
        sequence_composition="High thermal stability, depleted in cysteines",
        guidance_scale=8.0,
        num_inference_steps=60,
    )

    data = prompt_contract.to_dict()
    assert data["macro_topology"] == "Three-helix bundle with amphipathic packing"
    assert data["interaction_site"] == "Target the apical cavity around Thr108 and Leu115"
    assert data["negative_design"] == "Avoid binding the lipid transfer gateway residues Lys88-Asp91"
    assert data["guidance_scale"] == 8.0
    assert data["num_inference_steps"] == 60

    design_contract = TextConditionedDesignContract(
        design_id="GM2ABinderDesign",
        target_pdb="targets/GM2A_human.pdb",
        prompt_conditioning=prompt_contract,
        target_protein_name="GM2A",
        min_affinity_nm=500.0,
        count=50,
    )

    design_data = design_contract.to_dict()
    assert design_data["design_id"] == "GM2ABinderDesign"
    assert design_data["target_protein_name"] == "GM2A"
    assert design_data["min_affinity_nm"] == 500.0
    assert design_data["model"] == "prompteina"
    assert design_data["prompt_conditioning"]["guidance_scale"] == 8.0


def test_validator_accepts_prompteina_in_design_block() -> None:
    """Test validator accepts design block with prompteina model and prompt_conditioning."""
    validator = EnhancedSemanticValidator()
    ast = {
        "design": {
            "entity": "ProteinSequence",
            "model": "prompteina",
            "objective": {
                "maximize": "binding_affinity",
            },
            "count": 20,
            "output": "gm2a_binders",
            "prompt_conditioning": {
                "macro_topology": "Three-helix bundle",
                "interaction_site": "GM2A hydrophobic pocket",
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
            },
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_accepts_prompteina_contract_object() -> None:
    """Test validator accepts NaturalLanguageConditioningContract object inside design."""
    validator = EnhancedSemanticValidator()
    prompt_contract = NaturalLanguageConditioningContract(
        prompt="De novo binder against GM2A",
        guidance_scale=9.0,
    )
    ast = {
        "design": {
            "entity": "ProteinSequence",
            "model": "Prompteina",
            "objective": {
                "maximize": "stability",
            },
            "count": 10,
            "output": "candidates",
            "prompt_conditioning": prompt_contract,
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_accepts_prompteina_tool_in_experiment() -> None:
    """Test validator accepts prompteina in experiment block."""
    validator = EnhancedSemanticValidator()
    ast = {
        "experiment": {
            "tool": "prompteina",
            "type": "design",
            "params": {
                "target_gene": "GM2A",
            },
        }
    }
    result = validator.validate_ast(ast)
    # Should not produce unknown tool warning
    assert not any("Unknown tool 'prompteina'" in w.message for w in result.warnings)


def test_validator_catches_invalid_prompt_conditioning_fields() -> None:
    """Test validator catches invalid guidance_scale and num_inference_steps."""
    validator = EnhancedSemanticValidator()
    ast = {
        "design": {
            "entity": "ProteinSequence",
            "model": "prompteina",
            "objective": {
                "maximize": "binding_affinity",
            },
            "count": 10,
            "output": "candidates",
            "prompt_conditioning": {
                "guidance_scale": -2.0,  # invalid negative
                "num_inference_steps": 0,  # invalid zero
            },
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("guidance_scale must be a positive number" in e.message for e in result.errors)
    assert any("num_inference_steps must be a positive integer" in e.message for e in result.errors)
