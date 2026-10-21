"""Unit tests for Virtual Cell Perturbation Modeling and Open Atlas Ground Truth in GeneForgeLang."""

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    CellAtlasReference,
    PerturbationReadout,
    PerturbationType,
    VirtualCellPerturbationContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_perturbation_enums_and_readout_evaluation() -> None:
    """Test PerturbationType, CellAtlasReference, and PerturbationReadout threshold evaluation."""
    assert PerturbationType.CRISPR_INHIBITION.value == "crispr_inhibition"
    assert CellAtlasReference.TABULA_SAPIENS.value == "tabula_sapiens"
    assert CellAtlasReference.ZEBRAHUB.value == "zebrahub"

    readout = PerturbationReadout(
        max_transcriptome_cosine_distance=0.15,
        min_survival_probability=0.85,
        mitochondrial_potential_retention=0.90,
        off_target_pathway_disruption=0.05,
    )

    data = readout.to_dict()
    assert data["max_transcriptome_cosine_distance"] == 0.15
    assert data["min_survival_probability"] == 0.85

    # Case 1: Healthy in silico transition meeting all phenotypic criteria
    assert (
        readout.satisfies_phenotype_gate(
            observed_cosine_distance=0.10,
            observed_survival=0.92,
            observed_mito_retention=0.94,
            observed_off_target=0.02,
        )
        is True
    )

    # Case 2: Excessive transcriptomic distortion (> 0.15)
    assert (
        readout.satisfies_phenotype_gate(
            observed_cosine_distance=0.22,
            observed_survival=0.92,
            observed_mito_retention=0.94,
            observed_off_target=0.02,
        )
        is False
    )

    # Case 3: Viability drop below 85%
    assert (
        readout.satisfies_phenotype_gate(
            observed_cosine_distance=0.10,
            observed_survival=0.75,
            observed_mito_retention=0.94,
            observed_off_target=0.02,
        )
        is False
    )


def test_virtual_cell_contract_roundtrip() -> None:
    """Test VirtualCellPerturbationContract serialization and deserialization."""
    contract = VirtualCellPerturbationContract(
        simulation_id="sim_mapt_knockdown",
        cell_type="human_cortical_neuron",
        target_gene_or_compound="MAPT",
        perturbation_type=PerturbationType.CRISPR_INHIBITION,
        atlas_ref=CellAtlasReference.TABULA_SAPIENS,
        dose_or_fold_change=0.20,
        tissue_context="cerebral_cortex",
        engine="virtual-cell-foundation-1",
        wet_lab_clearance=True,
    )

    data = contract.to_dict()
    assert data["simulation_id"] == "sim_mapt_knockdown"
    assert data["cell_type"] == "human_cortical_neuron"
    assert data["target_gene_or_compound"] == "MAPT"
    assert data["perturbation_type"] == "crispr_inhibition"
    assert data["atlas_ref"] == "tabula_sapiens"
    assert data["tissue_context"] == "cerebral_cortex"

    restored = VirtualCellPerturbationContract.from_dict(data)
    assert restored.simulation_id == contract.simulation_id
    assert restored.perturbation_type == PerturbationType.CRISPR_INHIBITION
    assert restored.atlas_ref == CellAtlasReference.TABULA_SAPIENS
    assert restored.wet_lab_clearance is True


def test_gfl_ast_roundtrip_with_virtual_cell_block() -> None:
    """Test GFLAST serialization with virtual_cell block."""
    ast_dict = {
        "virtual_cell": {
            "simulation_id": "sim_snca_gcase",
            "cell_type": "midbrain_dopaminergic_neuron",
            "target_gene_or_compound": "GBA1_activator",
            "perturbation_type": "small_molecule_inhibition",
            "atlas_ref": "cellxgene",
        }
    }

    gfl_ast = GFLAST.from_dict(ast_dict)
    assert gfl_ast.virtual_cell is not None
    assert gfl_ast.virtual_cell.simulation_id == "sim_snca_gcase"
    assert gfl_ast.virtual_cell.cell_type == "midbrain_dopaminergic_neuron"
    assert gfl_ast.virtual_cell.atlas_ref == CellAtlasReference.CELLXGENE

    out = gfl_ast.to_dict()
    assert out["virtual_cell"]["target_gene_or_compound"] == "GBA1_activator"


def test_validator_rejects_invalid_virtual_cell_parameters() -> None:
    """Test EnhancedSemanticValidator flags invalid survival probabilities or negative cosine distances."""
    validator = EnhancedSemanticValidator()

    # Invalid survival probability > 1.0 and negative cosine distance
    ast = {
        "virtual_cell": {
            "cell_type": "human_astrocyte",
            "target_gene_or_compound": "APOE4",
            "readout": {
                "min_survival_probability": 1.5,
                "max_transcriptome_cosine_distance": -0.5,
            },
        }
    }
    res = validator.validate_ast(ast)
    assert res.is_valid is False
    assert any("min_survival_probability must be between 0.0 and 1.0" in e.message for e in res.errors)
    assert any("max_transcriptome_cosine_distance must be non-negative" in e.message for e in res.errors)


def test_virtual_cell_perturbation_example_file_validates() -> None:
    """Test examples/virtual_cell_perturbation_screening.gfl validates cleanly with 0 errors and 0 warnings."""
    example_path = (
        Path(__file__).resolve().parent.parent.parent / "examples" / "virtual_cell_perturbation_screening.gfl"
    )
    assert example_path.exists(), f"Example file {example_path} does not exist"

    content = example_path.read_text(encoding="utf-8")
    ast = yaml.safe_load(content)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)

    assert result.is_valid is True, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
