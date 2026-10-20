"""Unit tests for Omnii-1 multimodal foundation model, 5hmC epigenomics, and biosafe bacteriophage therapy contracts."""

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    AviModality,
    BacteriophageTherapyContract,
    BiodefenseSafetyGate,
    ConsensusModel,
    FragmentomicsModality,
    PhageCapsidArchitecture,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_5hmc_modality_and_consensus_model_registration() -> None:
    """Test 5hmC enum values in AviModality, FragmentomicsModality, and Omnii-1 in ConsensusModel."""
    assert AviModality.FIVE_HMC.value == "5hmC"
    assert FragmentomicsModality.HYDROXYMETHYLATION_5HMC.value == "5hmC_hydroxymethylation"
    assert ConsensusModel.OMNII_1.value == "omnii1"


def test_biodefense_safety_gate_evaluation() -> None:
    """Test BiodefenseSafetyGate passes safe phages and catches violations."""
    gate = BiodefenseSafetyGate(
        max_immunogenicity_score=0.15,
        prohibit_amr_transfer_genes=True,
        prohibit_toxin_homology=True,
        max_off_target_microbiome_lysis=0.01,
        verified_clearance=True,
    )

    data = gate.to_dict()
    assert data["prohibit_amr_transfer_genes"] is True
    assert data["prohibit_toxin_homology"] is True
    assert data["max_off_target_microbiome_lysis"] == 0.01

    # Case 1: Safe candidate meeting all criteria
    assert (
        gate.passes_safety_gate(
            immunogenicity=0.08,
            has_amr_genes=False,
            has_toxin_homology=False,
            off_target_lysis=0.002,
        )
        is True
    )

    # Case 2: AMR horizontal gene transfer risk
    assert (
        gate.passes_safety_gate(
            immunogenicity=0.08,
            has_amr_genes=True,
            has_toxin_homology=False,
            off_target_lysis=0.002,
        )
        is False
    )

    # Case 3: Bacterial toxin homology detected
    assert (
        gate.passes_safety_gate(
            immunogenicity=0.08,
            has_amr_genes=False,
            has_toxin_homology=True,
            off_target_lysis=0.002,
        )
        is False
    )

    # Case 4: Excessive off-target commensal microbiome lysis
    assert (
        gate.passes_safety_gate(
            immunogenicity=0.08,
            has_amr_genes=False,
            has_toxin_homology=False,
            off_target_lysis=0.05,
        )
        is False
    )


def test_bacteriophage_therapy_contract_roundtrip() -> None:
    """Test BacteriophageTherapyContract creation and dictionary serialization."""
    contract = BacteriophageTherapyContract(
        therapy_id="phage_pa01_test",
        target_pathogen="Pseudomonas_aeruginosa_PA01",
        model="omnii-1",
        modalities=["DNA_GENOME", "EPIGENOMIC_5HMC_EVASION"],
        capsid_architecture=PhageCapsidArchitecture.MYOVIRIDAE_T4,
        host_range_expansion=True,
        receptor_binding_fiber_ref="fiber_oprM",
        compassionate_use_approved=True,
        target_cfu_reduction_log10=6.5,
    )

    data = contract.to_dict()
    assert data["therapy_id"] == "phage_pa01_test"
    assert data["target_pathogen"] == "Pseudomonas_aeruginosa_PA01"
    assert data["model"] == "omnii-1"
    assert data["capsid_architecture"] == "myoviridae_t4"
    assert "EPIGENOMIC_5HMC_EVASION" in data["modalities"]

    restored = BacteriophageTherapyContract.from_dict(data)
    assert restored.therapy_id == contract.therapy_id
    assert restored.capsid_architecture == PhageCapsidArchitecture.MYOVIRIDAE_T4
    assert restored.compassionate_use_approved is True


def test_gfl_ast_roundtrip_with_bacteriophage_block() -> None:
    """Test GFLAST serialization and deserialization with bacteriophage block."""
    ast_dict = {
        "bacteriophage": {
            "therapy_id": "phage_mrsa_01",
            "target_pathogen": "Staphylococcus_aureus_MRSA",
            "model": "omnii-1",
            "capsid_architecture": "podoviridae_t7",
            "compassionate_use_approved": True,
        }
    }

    gfl_ast = GFLAST.from_dict(ast_dict)
    assert gfl_ast.bacteriophage is not None
    assert gfl_ast.bacteriophage.target_pathogen == "Staphylococcus_aureus_MRSA"
    assert gfl_ast.bacteriophage.capsid_architecture == PhageCapsidArchitecture.PODOVIRIDAE_T7

    out = gfl_ast.to_dict()
    assert out["bacteriophage"]["therapy_id"] == "phage_mrsa_01"


def test_validator_rejects_unsafe_bacteriophage_biodefense_violations() -> None:
    """Test EnhancedSemanticValidator flags disabling AMR prohibition or excessive microbiome lysis."""
    validator = EnhancedSemanticValidator()

    # Disabling AMR prohibition is a biodefense invariant violation
    ast_unsafe_amr = {
        "bacteriophage": {
            "target_pathogen": "Pseudomonas_aeruginosa",
            "biodefense_gate": {
                "prohibit_amr_transfer_genes": False,
            },
        }
    }
    res_amr = validator.validate_ast(ast_unsafe_amr)
    assert res_amr.is_valid is False
    assert any(
        "Synthetic bacteriophage cannot disable 'prohibit_amr_transfer_genes'" in e.message for e in res_amr.errors
    )

    # Excessive microbiome lysis (> 5%)
    ast_high_lysis = {
        "bacteriophage": {
            "target_pathogen": "Pseudomonas_aeruginosa",
            "biodefense_gate": {
                "max_off_target_microbiome_lysis": 0.25,
            },
        }
    }
    res_lysis = validator.validate_ast(ast_high_lysis)
    assert res_lysis.is_valid is False
    assert any("max_off_target_microbiome_lysis must be between 0.0 and 0.05" in e.message for e in res_lysis.errors)


def test_omnii1_bacteriophage_example_file_validates() -> None:
    """Test examples/omnii1_bacteriophage_therapy.gfl validates with 0 errors and 0 warnings."""
    example_path = Path(__file__).resolve().parent.parent.parent / "examples" / "omnii1_bacteriophage_therapy.gfl"
    assert example_path.exists(), f"Example file {example_path} does not exist"

    content = example_path.read_text(encoding="utf-8")
    ast = yaml.safe_load(content)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)

    assert result.is_valid is True, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
