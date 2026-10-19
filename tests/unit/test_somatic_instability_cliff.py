"""Unit tests for Microsatellite Somatic Instability and Toxicity Cliff Gating contracts in GeneForgeLang."""

import pytest
from geneforgelang.core.gftypes import (
    GFLAST,
    SomaticDriftModel,
    SomaticDriftSimulationContract,
    SomaticInstabilityContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_somatic_instability_contract_instantiation_and_dict() -> None:
    """Test creating and serializing SomaticInstabilityContract."""
    sim = SomaticDriftSimulationContract(
        time_horizon_years=65.0,
        toxicity_cliff_threshold=150,
        stochastic_drift_rate_per_year=2.3,
        stochastic_dispersion=0.25,
        drift_model=SomaticDriftModel.STOCHASTIC_EXPANSION,
    )
    contract = SomaticInstabilityContract(
        target_gene="HTT",
        locus="chr4:3074877-3074933",
        repeat_unit="CAG",
        germline_repeat_count=42,
        cell_type="striatal_projection_neuron",
        modifiers={"msh3_genotype": "risk_variant_rs1805355", "mlh1_expression": 1.15},
        simulation=sim,
        protocol_name="HuntingtonSomaticInstabilitySimulator",
    )

    data = contract.to_dict()
    assert data["target_gene"] == "HTT"
    assert data["germline_repeat_count"] == 42
    assert data["germline_cag_repeat"] == 42
    assert data["simulation"]["toxicity_cliff_threshold"] == 150
    assert data["simulation"]["toxicity_cliff_cag"] == 150
    assert data["simulation"]["time_horizon_years"] == 65.0
    assert data["modifiers"]["mlh1_expression"] == 1.15


def test_somatic_drift_analytical_distribution_and_gating() -> None:
    """Test analytical projection of repeat tract drift and cliff exceedance probability."""
    # Case 1: High drift with modifiers reaching catastrophe cliff
    sim = SomaticDriftSimulationContract(
        time_horizon_years=65.0,
        toxicity_cliff_threshold=150,
        stochastic_drift_rate_per_year=2.3,
        stochastic_dispersion=0.25,
    )
    contract_severe = SomaticInstabilityContract(
        target_gene="HTT",
        germline_repeat_count=42,
        modifiers={"msh3_genotype": "risk_variant_rs1805355", "mlh1_expression": 1.15},
        simulation=sim,
    )
    stats_severe = contract_severe.calculate_projected_distribution()
    # E[CAG] = 42 + (2.3 * 1.15 * 1.25 * 65) = 42 + 214.9 = ~256.9 > 150
    assert stats_severe["mean_projected_repeat"] > 150.0
    assert stats_severe["cliff_exceedance_probability"] > 0.99
    assert contract_severe.evaluate_neurodegeneration_state(threshold=0.85) == "CLIFF_COLLAPSE_IMMINENT"

    # Case 2: Early stage / young age far below catastrophe cliff
    sim_young = SomaticDriftSimulationContract(
        time_horizon_years=15.0,
        toxicity_cliff_threshold=150,
        stochastic_drift_rate_per_year=1.0,
        stochastic_dispersion=0.1,
    )
    contract_young = SomaticInstabilityContract(
        target_gene="HTT",
        germline_repeat_count=40,
        modifiers={},
        simulation=sim_young,
    )
    stats_young = contract_young.calculate_projected_distribution()
    # E[CAG] = 40 + (1.0 * 15) = 55 << 150
    assert stats_young["mean_projected_repeat"] < 70.0
    assert stats_young["cliff_exceedance_probability"] < 0.01
    assert contract_young.evaluate_neurodegeneration_state(threshold=0.85) == "SUB_THRESHOLD_LATENT"


def test_validator_accepts_protocol_somatic_instability_and_decision() -> None:
    """Test validator accepts protocol block matching Neurodiagnoses Huntington simulator specification."""
    validator = EnhancedSemanticValidator()
    ast = {
        "protocol": {
            "name": "HuntingtonSomaticInstabilitySimulator",
            "target_gene": "HTT",
            "locus": "chr4:3074877-3074933",
            "germline_cag_repeat": 42,
            "cell_type": "striatal_projection_neuron",
            "modifiers": {
                "msh3_genotype": "risk_variant_rs1805355",
                "mlh1_expression": 1.15,
            },
            "SomaticDrift": {
                "time_horizon_years": 65,
                "toxicity_cliff_cag": 150,
                "stochastic_drift_rate_per_year": 2.3,
            },
            "decision": {
                "task_id": "NeurodegenerationTippingPoint",
                "strategy": "SYSTEM_1_CALIBRATED",
                "engine": "biodecision-4b",
                "threshold": 0.85,
                "allowed_space": [
                    "SUB_THRESHOLD_LATENT",
                    "CLIFF_COLLAPSE_IMMINENT",
                ],
            },
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0

    # Also test GFLAST parsing
    gfl_ast = GFLAST.from_dict(ast)
    assert gfl_ast.protocol is not None
    assert gfl_ast.protocol.target_gene == "HTT"
    assert gfl_ast.protocol.germline_repeat_count == 42
    assert gfl_ast.protocol.simulation.toxicity_cliff_threshold == 150


def test_validator_catches_invalid_somatic_cliff_threshold() -> None:
    """Test validator flags toxicity cliff less than or equal to germline repeat count."""
    validator = EnhancedSemanticValidator()
    ast = {
        "somatic_instability": {
            "target_gene": "HTT",
            "germline_cag_repeat": 45,
            "simulation": {
                "time_horizon_years": 50,
                "toxicity_cliff_threshold": 35,  # Invalid: cliff (35) <= germline (45)
            },
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("must be strictly greater than germline repeat count" in e.message for e in result.errors)


def test_validator_catches_invalid_locus_format() -> None:
    """Test validator flags invalid genomic locus syntax in somatic instability block."""
    validator = EnhancedSemanticValidator()
    ast = {
        "protocol": {
            "target_gene": "HTT",
            "locus": "chr4_invalid_coords",
            "germline_cag_repeat": 42,
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("Invalid genomic locus format" in e.message for e in result.errors)


def test_examples_somatic_repeat_expansion_gate_validates() -> None:
    """Test examples/somatic_repeat_expansion_gate.gfl passes EnhancedSemanticValidator cleanly."""
    from pathlib import Path

    import yaml

    example_path = Path(__file__).resolve().parent.parent.parent / "examples" / "somatic_repeat_expansion_gate.gfl"
    assert example_path.exists(), f"Example file {example_path} does not exist"

    content = example_path.read_text(encoding="utf-8")
    ast = yaml.safe_load(content)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)

    assert result.is_valid is True, f"Validation failed: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
