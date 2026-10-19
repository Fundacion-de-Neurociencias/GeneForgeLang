"""Unit tests for Regulatory Genomics Dual-Head Contracts (BPNet & AtacWorks) in GeneForgeLang."""

import pytest
from geneforgelang.core.gftypes import (
    GFLAST,
    CountHeadContract,
    EpistemicLevel,
    ProfileHeadContract,
    ProfileLossMetric,
    ProfileResolution,
    RegulatoryProfileContract,
    RegulatoryTrackContract,
    SignalModality,
    StrandMode,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_multinomial_nll_mit_lecture_example() -> None:
    """Test Multinomial profile loss reproduces the exact MIT 6.874 Lecture 7 example.

    In MIT 6.874 with observed counts (0, 100, 0):
    - Profile P1 (0.1, 0.8, 0.1) has NLL loss ~ 22.3
    - Profile P2 (0.4, 0.2, 0.4) has NLL loss ~ 160.9
    Both predictions have identical predicted/observed totals, proving that reducing to a scalar loses spatial signal.
    """
    observed = [0, 100, 0]
    p1 = [0.1, 0.8, 0.1]
    p2 = [0.4, 0.2, 0.4]

    loss1 = RegulatoryProfileContract.compute_multinomial_nll(observed, p1)
    loss2 = RegulatoryProfileContract.compute_multinomial_nll(observed, p2)

    assert pytest.approx(loss1, rel=1e-3) == 22.314
    assert pytest.approx(loss2, rel=1e-3) == 160.944
    assert loss2 > loss1 * 7.0


def test_jensen_shannon_divergence_computation() -> None:
    """Test Jensen-Shannon Divergence metric properties: symmetric and bounded in [0, 1]."""
    p = [0.1, 0.8, 0.1]
    q = [0.4, 0.2, 0.4]

    jsd_pq = RegulatoryProfileContract.compute_jsd(p, q)
    jsd_qp = RegulatoryProfileContract.compute_jsd(q, p)

    # Symmetry
    assert pytest.approx(jsd_pq, rel=1e-6) == jsd_qp
    # Bounded in [0, 1]
    assert 0.0 <= jsd_pq <= 1.0
    # Identical distributions have JSD = 0
    assert pytest.approx(RegulatoryProfileContract.compute_jsd(p, p), abs=1e-9) == 0.0


def test_regulatory_profile_contract_serialization_and_ast() -> None:
    """Test serialization, deserialization, and GFLAST conversion."""
    count_head = CountHeadContract(
        expected_total_counts=100.0,
        tolerance_fold=1.4,
        dispersion=0.08,
        loss_model="negative_binomial",
    )
    profile_head = ProfileHeadContract(
        resolution=ProfileResolution.BASE_PAIR,
        loss_metric=ProfileLossMetric.MULTINOMIAL_NLL,
        max_jsd_threshold=0.18,
        strand_mode=StrandMode.STRANDED_PLUS_MINUS,
    )
    contract = RegulatoryProfileContract(
        profile_id="OCT4_Enhancer_Profile",
        target_factor="OCT4",
        locus="chr1:15432000-15433000",
        cell_type="H1_hESC",
        modality=SignalModality.DE_NOVO_SEQUENCE_DIRECT,
        count_head=count_head,
        profile_head=profile_head,
        epistemic_level=EpistemicLevel.PREDICTIVE_GUIDANCE,
        orthogonal_validation_required=True,
        orthogonal_validation_confirmed=False,
        source_model="BPNet",
    )

    data = contract.to_dict()
    assert data["profile_id"] == "OCT4_Enhancer_Profile"
    assert data["target_factor"] == "OCT4"
    assert data["count_head"]["expected_total_counts"] == 100.0
    assert data["profile_head"]["resolution"] == "base_pair"
    assert data["profile_head"]["strand_mode"] == "stranded_plus_minus"

    # Test AST parsing
    ast_dict = {"regulatory_profile": data}
    ast = GFLAST.from_dict(ast_dict)
    assert ast.regulatory_profile is not None
    assert ast.regulatory_profile.profile_id == "OCT4_Enhancer_Profile"
    assert ast.regulatory_profile.count_head.tolerance_fold == 1.4


def test_validator_accepts_valid_regulatory_profile_block() -> None:
    """Test validator accepts valid regulatory_profile block."""
    validator = EnhancedSemanticValidator()
    ast = {
        "regulatory_profile": {
            "profile_id": "CTCF_Insulator_Track",
            "target_factor": "CTCF",
            "locus": "chr7:27142000-27143000",
            "cell_type": "K562",
            "modality": "de_novo_sequence_direct",
            "count_head": {
                "expected_total_counts": 250.0,
                "tolerance_fold": 1.5,
            },
            "profile_head": {
                "resolution": "base_pair",
                "loss_metric": "multinomial_nll",
                "max_jsd_threshold": 0.20,
            },
            "epistemic_level": "predictive_guidance",
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_enforces_epistemic_barrier() -> None:
    """Test validator rejects VALIDATED_MECHANISM without confirmed orthogonal empirical validation."""
    validator = EnhancedSemanticValidator()
    ast = {
        "regulatory_profile": {
            "target_factor": "SOX2",
            "locus": "chr3:18171000-18172000",
            "epistemic_level": "VALIDATED_MECHANISM",
            "orthogonal_validation_confirmed": False,  # Missing orthogonal validation
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("EPISTEMIC BARRIER VIOLATION" in e.message for e in result.errors)


def test_validator_catches_invalid_locus_and_thresholds() -> None:
    """Test validator flags malformed locus strings and out-of-range thresholds."""
    validator = EnhancedSemanticValidator()
    ast = {
        "regulatory_profile": {
            "target_factor": "NANOG",
            "locus": "chr12:invalid_coords",  # malformed
            "count_head": {
                "expected_total_counts": -10.0,  # negative counts
                "tolerance_fold": 0.5,  # must be >= 1.0
            },
            "profile_head": {
                "max_jsd_threshold": 1.5,  # must be <= 1.0
            },
        }
    }
    result = validator.validate_ast(ast)
    assert result.is_valid is False
    assert any("Invalid genomic locus format" in e.message for e in result.errors)
    assert any("expected_total_counts must be a non-negative number" in e.message for e in result.errors)
    assert any("tolerance_fold must be >= 1.0" in e.message for e in result.errors)
    assert any("max_jsd_threshold must be between 0.0 and 1.0" in e.message for e in result.errors)


def test_atacworks_denoised_track_contract() -> None:
    """Test RegulatoryTrackContract for AtacWorks signal enhancement modality."""
    track = RegulatoryTrackContract(
        track_id="AtacWorks_LowCoverage_Denoised",
        modality=SignalModality.SIGNAL_DENOISED_ENRICHED,
        source_measurement="5k_cell_atac_sparse_run",
        denoiser_model="AtacWorks-v2",
        peak_classification_threshold=0.65,
        min_snr=3.2,
    )
    data = track.to_dict()
    assert data["track_id"] == "AtacWorks_LowCoverage_Denoised"
    assert data["modality"] == "signal_denoised_enriched"
    assert data["source_measurement"] == "5k_cell_atac_sparse_run"
    assert data["denoiser_model"] == "AtacWorks-v2"
    assert data["peak_classification_threshold"] == 0.65
