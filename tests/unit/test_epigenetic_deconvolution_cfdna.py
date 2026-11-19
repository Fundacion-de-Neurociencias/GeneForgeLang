"""Unit tests for Epigenetic Deconvolution and cfDNA Fragmentomics Contracts in GeneForgeLang."""

from geneforgelang.core.gftypes import (
    DecisionContract,
    DecisionStrategy,
    EpigeneticDeconvolutionContract,
    FragmentomicsModality,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_epigenetic_deconvolution_contract_instantiation_and_dict() -> None:
    """Test creating and serializing an EpigeneticDeconvolutionContract."""
    contract = EpigeneticDeconvolutionContract(
        deconvolution_id="CNS_Deconvolution_Run",
        target_tissue="central_nervous_system",
        cfdna_methylation_profile="patient_plasma_run_04",
        engine="pleiades-biodecision",
        modality=FragmentomicsModality.HIERARCHICAL_STACKED_ATTENTION,
        confidence_threshold=0.90,
        min_fragment_coverage=150000,
        sub_cell_types=["astrocytes", "cortical_neurons", "microglia", "oligodendrocytes"],
        calibration_method="temperature_scaling",
        max_ece=0.045,
    )

    data = contract.to_dict()
    assert data["deconvolution_id"] == "CNS_Deconvolution_Run"
    assert data["target_tissue"] == "central_nervous_system"
    assert data["cfdna_methylation_profile"] == "patient_plasma_run_04"
    assert data["engine"] == "pleiades-biodecision"
    assert data["modality"] == "hierarchical_stacked_attention"
    assert data["confidence_threshold"] == 0.90
    assert len(data["sub_cell_types"]) == 4
    assert contract.passes_gate(0.92, 200000) is True
    assert contract.passes_gate(0.85, 200000) is False  # below threshold
    assert contract.passes_gate(0.95, 50000) is False  # insufficient coverage


def test_decision_contract_with_epigenetic_and_cfdna_fields() -> None:
    """Test DecisionContract with target_tissue and cfdna_methylation_profile."""
    contract = DecisionContract(
        task_id="EpigeneticDeconvolutionGate",
        strategy=DecisionStrategy.SYSTEM_1_CALIBRATED,
        engine="pleiades-biodecision",
        target_tissue="central_nervous_system",
        cfdna_methylation_profile="patient_plasma_run_04",
        threshold=0.90,
    )

    data = contract.to_dict()
    assert data["target_tissue"] == "central_nervous_system"
    assert data["cfdna_methylation_profile"] == "patient_plasma_run_04"
    assert data["engine"] == "pleiades-biodecision"
    assert data["threshold"] == 0.90


def test_validator_accepts_epigenetic_decision_block() -> None:
    """Test validator accepts valid epigenetic decision block."""
    validator = EnhancedSemanticValidator()
    ast = {
        "decision": {
            "strategy": "SYSTEM_1_CALIBRATED",
            "engine": "pleiades-biodecision",
            "target_tissue": "central_nervous_system",
            "cfdna_methylation_profile": "patient_plasma_run_04",
            "threshold": 0.90,
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_accepts_pleiades_tools_and_strategies() -> None:
    """Test that pleiades tools and epigenetic_deconvolution strategies are accepted."""
    validator = EnhancedSemanticValidator()
    ast = {
        "experiment": {
            "tool": "pleiades-biodecision",
            "type": "analysis",
            "params": {"sample_id": "plasma_01"},
        },
        "analyze": {
            "strategy": "epigenetic_deconvolution",
        },
    }
    result = validator.validate_ast(ast)
    # Should not produce unknown tool or unknown strategy warnings
    assert not any("pleiades-biodecision" in w.message for w in result.warnings)
    assert not any("epigenetic_deconvolution" in w.message for w in result.warnings)


def test_validator_catches_invalid_epigenetic_decision_fields() -> None:
    """Test that validator catches empty or non-string epigenetic fields."""
    validator = EnhancedSemanticValidator()
    ast = {
        "decision": {
            "strategy": "SYSTEM_1_CALIBRATED",
            "engine": "pleiades-biodecision",
            "target_tissue": "",  # invalid empty string
            "cfdna_methylation_profile": 12345,  # invalid non-string
            "threshold": 0.90,
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("target_tissue must be a non-empty string" in e.message for e in result.errors)
    assert any("cfdna_methylation_profile must be a non-empty string" in e.message for e in result.errors)
