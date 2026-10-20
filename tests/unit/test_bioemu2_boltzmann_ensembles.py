"""Unit tests for BioEmu2 Boltzmann Conformational Ensembles and Thermodynamic Free Energy Operators in GeneForgeLang."""

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    BoltzmannEnsembleContract,
    CrypticPocketContract,
    EnsembleGenerator,
    SolvationModel,
    ThermodynamicBindingContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_boltzmann_ensemble_contract_instantiation_and_weight() -> None:
    """Test creating BoltzmannEnsembleContract and computing Boltzmann probability weights."""
    contract = BoltzmannEnsembleContract(
        target="MAPT_HUMAN",
        sample_size=1000,
        generator=EnsembleGenerator.BIOEMU_2,
        temperature_kelvin=310.15,
        solvation=SolvationModel.EXPLICIT_EQUIVALENT,
        ensemble_id="TauEnsemble_01",
        max_energy_cutoff_kcal_mol=15.0,
    )

    data = contract.to_dict()
    assert data["target"] == "MAPT_HUMAN"
    assert data["sample_size"] == 1000
    assert data["generator"] == "bioemu2"
    assert data["temperature_kelvin"] == 310.15
    assert data["solvation"] == "explicit_equivalent"
    assert data["ensemble_id"] == "TauEnsemble_01"

    # Ground state: Delta G = 0 -> weight = 1.0
    w_ground = contract.compute_boltzmann_weight(0.0)
    assert pytest.approx(w_ground, 1e-4) == 1.0

    # Thermally accessible state: Delta G = 1.0 kcal/mol at 310.15 K (k_B * T ~ 0.6163)
    # exp(-1.0 / 0.6163) ~ 0.197
    w_1kcal = contract.compute_boltzmann_weight(1.0)
    assert 0.18 < w_1kcal < 0.22

    # High energy barrier: Delta G = 20.0 kcal/mol -> negligible weight
    w_high = contract.compute_boltzmann_weight(20.0)
    assert w_high < 1e-10


def test_cryptic_pocket_contract_druggability_evaluation() -> None:
    """Test CrypticPocketContract instantiation and thermodynamic druggability gate."""
    pocket = CrypticPocketContract(
        pocket_id="tau_phf6_cleft",
        target_ensemble="TauEnsemble_01",
        residues=[306, 307, 308, 309, 310, 311],
        probe_radius_angstrom=1.4,
        min_boltzmann_weight=0.05,
        max_delta_g_relative_kcal_mol=2.5,
        target_pathogen_domain="tau_phf6_hexapeptide",
    )

    data = pocket.to_dict()
    assert data["pocket_id"] == "tau_phf6_cleft"
    assert data["residues"] == [306, 307, 308, 309, 310, 311]
    assert data["min_boltzmann_weight"] == 0.05
    assert data["max_delta_g_relative_kcal_mol"] == 2.5

    # Case 1: Druggable open cryptic state (8% population, Delta G = 1.8 kcal/mol)
    assert pocket.evaluates_druggability(observed_boltzmann_weight=0.08, observed_delta_g=1.8) is True

    # Case 2: Too rare / transient (< 5% occupancy)
    assert pocket.evaluates_druggability(observed_boltzmann_weight=0.02, observed_delta_g=1.8) is False

    # Case 3: Too costly in energy (> 2.5 kcal/mol penalty)
    assert pocket.evaluates_druggability(observed_boltzmann_weight=0.10, observed_delta_g=3.2) is False


def test_thermodynamic_binding_contract_allosteric_stabilization() -> None:
    """Test ThermodynamicBindingContract allosteric state selection."""
    binding = ThermodynamicBindingContract(
        binder_id="vhh_stabilizer_v1",
        target_ensemble="GPCR_Ensemble",
        stabilized_state_condition="tm6_displacement >= 10.0",
        min_target_fraction=0.80,
        max_delta_delta_g_kcal_mol=-2.5,
    )

    data = binding.to_dict()
    assert data["binder_id"] == "vhh_stabilizer_v1"
    assert data["min_target_fraction"] == 0.80
    assert data["max_delta_delta_g_kcal_mol"] == -2.5

    # Favorable binding: 88% active fraction shift, Delta Delta G = -3.2 kcal/mol
    assert (
        binding.satisfies_allosteric_stabilization(observed_active_fraction=0.88, observed_delta_delta_g=-3.2) is True
    )

    # Unfavorable: does not shift enough fraction or insufficient stabilization
    assert (
        binding.satisfies_allosteric_stabilization(observed_active_fraction=0.70, observed_delta_delta_g=-3.2) is False
    )
    assert (
        binding.satisfies_allosteric_stabilization(observed_active_fraction=0.88, observed_delta_delta_g=-1.5) is False
    )


def test_gfl_ast_roundtrip_with_boltzmann_blocks() -> None:
    """Test GFLAST serialization and deserialization with ensemble contracts."""
    ast_dict = {
        "ensemble": {
            "target": "TDP43_HUMAN",
            "sample_size": 2000,
            "generator": "bioemu2",
            "temperature_kelvin": 310.15,
            "solvation": "explicit_equivalent",
        },
        "cryptic_pocket": {
            "pocket_id": "rrm_cryptic_loop",
            "target_ensemble": "TDP43_Ensemble",
            "residues": [106, 107, 108],
            "min_boltzmann_weight": 0.10,
            "max_delta_g_relative_kcal_mol": 2.0,
        },
        "thermodynamic_binding": {
            "binder_id": "vhh_tdp43_01",
            "target_ensemble": "TDP43_Ensemble",
            "stabilized_state_condition": "pocket_accessible == True",
            "min_target_fraction": 0.85,
            "max_delta_delta_g_kcal_mol": -2.2,
        },
    }

    gfl_ast = GFLAST.from_dict(ast_dict)
    assert gfl_ast.ensemble is not None
    assert gfl_ast.ensemble.target == "TDP43_HUMAN"
    assert gfl_ast.ensemble.sample_size == 2000
    assert gfl_ast.cryptic_pocket is not None
    assert gfl_ast.cryptic_pocket.residues == [106, 107, 108]
    assert gfl_ast.thermodynamic_binding is not None
    assert gfl_ast.thermodynamic_binding.binder_id == "vhh_tdp43_01"

    out = gfl_ast.to_dict()
    assert out["ensemble"]["target"] == "TDP43_HUMAN"
    assert out["cryptic_pocket"]["pocket_id"] == "rrm_cryptic_loop"
    assert out["thermodynamic_binding"]["min_target_fraction"] == 0.85


def test_validator_rejects_invalid_ensemble_parameters() -> None:
    """Test EnhancedSemanticValidator flags invalid sample size, temperature, or empty targets."""
    validator = EnhancedSemanticValidator()

    # Invalid negative sample size and non-positive temperature
    ast = {
        "ensemble": {
            "target": "MAPT",
            "sample_size": -50,
            "temperature_kelvin": -10.0,
        }
    }
    res = validator.validate_ast(ast)
    assert res.is_valid is False
    assert any("sample_size must be a positive integer" in e.message for e in res.errors)
    assert any("temperature_kelvin must be positive" in e.message for e in res.errors)


def test_validator_rejects_invalid_cryptic_pocket_parameters() -> None:
    """Test EnhancedSemanticValidator flags invalid residue list or impossible Boltzmann weight."""
    validator = EnhancedSemanticValidator()

    ast = {
        "cryptic_pocket": {
            "pocket_id": "test_pocket",
            "target_ensemble": "TestEnsemble",
            "residues": [-5, "invalid"],
            "min_boltzmann_weight": 1.5,  # Weight > 1.0 impossible
        }
    }
    res = validator.validate_ast(ast)
    assert res.is_valid is False
    assert any("Residue index must be a positive integer" in e.message for e in res.errors)
    assert any("min_boltzmann_weight must be in range (0.0, 1.0]" in e.message for e in res.errors)


def test_bioemu2_cryptic_pocket_example_file_validates() -> None:
    """Test that examples/bioemu2_cryptic_pocket_ensemble.gfl validates cleanly with 0 errors and 0 warnings."""
    example_path = Path(__file__).resolve().parent.parent.parent / "examples" / "bioemu2_cryptic_pocket_ensemble.gfl"
    assert example_path.exists(), f"Example file {example_path} does not exist"

    content = example_path.read_text(encoding="utf-8")
    ast = yaml.safe_load(content)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)

    assert result.is_valid is True, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
