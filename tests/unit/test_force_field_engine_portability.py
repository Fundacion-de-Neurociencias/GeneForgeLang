"""Unit tests for Force Field Engine Portability and Inter-Engine Energy Consistency (Miletić et al.)."""

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    ForceFieldEngineContract,
    ForceFieldFamily,
    InterEngineEnergyTolerance,
    SimulationEngine,
    WaterModel,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_force_field_engine_enums_and_tolerance_evaluation() -> None:
    """Test ForceFieldFamily, SimulationEngine, WaterModel, and InterEngineEnergyTolerance."""
    assert ForceFieldFamily.AMBER_FF19SB.value == "amber_ff19sb"
    assert SimulationEngine.GROMACS.value == "gromacs"
    assert SimulationEngine.AMBER.value == "amber"
    assert WaterModel.OPC.value == "opc"

    tol = InterEngineEnergyTolerance(
        max_potential_energy_delta_kj_mol=1e-6,
        max_force_delta_kj_mol_nm=1e-4,
        audit_improper_dihedral_ordering=True,
        audit_cmap_residue_spec=True,
        electrostatic_14_scale=0.8333333,
        vdw_14_scale=0.5,
    )

    data = tol.to_dict()
    assert data["max_potential_energy_delta_kj_mol"] == 1e-6
    assert data["max_force_delta_kj_mol_nm"] == 1e-4
    assert data["audit_improper_dihedral_ordering"] is True
    assert data["audit_cmap_residue_spec"] is True

    # Case 1: Bitwise equivalence meeting strict physical standards
    assert (
        tol.satisfies_inter_engine_portability(
            observed_energy_delta=5e-7,
            observed_force_delta=2e-5,
            improper_ordering_valid=True,
            cmap_spec_valid=True,
        )
        is True
    )

    # Case 2: Potential energy discrepancy exceeds tolerance (> 1e-6 kJ/mol)
    assert (
        tol.satisfies_inter_engine_portability(
            observed_energy_delta=5e-5,
            observed_force_delta=2e-5,
            improper_ordering_valid=True,
            cmap_spec_valid=True,
        )
        is False
    )

    # Case 3: Improper dihedral atom sequence mismatch causing chiral inversion risk
    assert (
        tol.satisfies_inter_engine_portability(
            observed_energy_delta=5e-7,
            observed_force_delta=2e-5,
            improper_ordering_valid=False,
            cmap_spec_valid=True,
        )
        is False
    )

    # Case 4: CMAP grid missing residue-specific amino acid parameters
    assert (
        tol.satisfies_inter_engine_portability(
            observed_energy_delta=5e-7,
            observed_force_delta=2e-5,
            improper_ordering_valid=True,
            cmap_spec_valid=False,
        )
        is False
    )


def test_force_field_engine_contract_roundtrip() -> None:
    """Test ForceFieldEngineContract creation and dictionary roundtrip."""
    contract = ForceFieldEngineContract(
        contract_id="contract_ff19sb_opc",
        force_field=ForceFieldFamily.AMBER_FF19SB,
        primary_engine=SimulationEngine.GROMACS,
        reference_engine=SimulationEngine.AMBER,
        water_model=WaterModel.OPC,
        target_structure_ref="PDB:1UBQ",
        verified_portability=True,
    )

    data = contract.to_dict()
    assert data["contract_id"] == "contract_ff19sb_opc"
    assert data["force_field"] == "amber_ff19sb"
    assert data["primary_engine"] == "gromacs"
    assert data["reference_engine"] == "amber"
    assert data["water_model"] == "opc"
    assert data["target_structure_ref"] == "PDB:1UBQ"

    restored = ForceFieldEngineContract.from_dict(data)
    assert restored.contract_id == contract.contract_id
    assert restored.force_field == ForceFieldFamily.AMBER_FF19SB
    assert restored.primary_engine == SimulationEngine.GROMACS
    assert restored.water_model == WaterModel.OPC
    assert restored.verified_portability is True


def test_gfl_ast_roundtrip_with_force_field_engine_block() -> None:
    """Test GFLAST serialization with force_field_engine block."""
    ast_dict = {
        "force_field_engine": {
            "contract_id": "ffe_01",
            "force_field": "amber_ff14sb",
            "primary_engine": "gromacs",
            "reference_engine": "amber",
            "water_model": "tip3p",
        }
    }

    gfl_ast = GFLAST.from_dict(ast_dict)
    assert gfl_ast.force_field_engine is not None
    assert gfl_ast.force_field_engine.contract_id == "ffe_01"
    assert gfl_ast.force_field_engine.force_field == ForceFieldFamily.AMBER_FF14SB
    assert gfl_ast.force_field_engine.primary_engine == SimulationEngine.GROMACS

    out = gfl_ast.to_dict()
    assert out["force_field_engine"]["contract_id"] == "ffe_01"


def test_validator_rejects_invalid_force_field_engine_parameters() -> None:
    """Test EnhancedSemanticValidator flags non-positive tolerances or invalid 1-4 scaling factors."""
    validator = EnhancedSemanticValidator()

    # Invalid non-positive energy tolerance and invalid 1-4 scaling > 1.0
    ast = {
        "force_field_engine": {
            "contract_id": "invalid_ffe",
            "energy_tolerance": {
                "max_potential_energy_delta_kj_mol": -1e-6,
                "electrostatic_14_scale": 1.5,
                "vdw_14_scale": -0.2,
            },
        }
    }
    res = validator.validate_ast(ast)
    assert res.is_valid is False
    assert any("max_potential_energy_delta_kj_mol must be a positive number" in e.message for e in res.errors)
    assert any("electrostatic_14_scale must be in range (0.0, 1.0]" in e.message for e in res.errors)
    assert any("vdw_14_scale must be in range (0.0, 1.0]" in e.message for e in res.errors)


def test_force_field_engine_consistency_example_file_validates() -> None:
    """Test examples/force_field_engine_consistency.gfl validates cleanly with 0 errors and 0 warnings."""
    example_path = Path(__file__).resolve().parent.parent.parent / "examples" / "force_field_engine_consistency.gfl"
    assert example_path.exists(), f"Example file {example_path} does not exist"

    content = example_path.read_text(encoding="utf-8")
    ast = yaml.safe_load(content)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)

    assert result.is_valid is True, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
