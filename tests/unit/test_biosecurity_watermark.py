"""Unit tests for BiosecurityWatermarkContract, SynthID Bio, and WatermarkEngine.

Grounded in Google DeepMind's SynthID Bio framework (Nature, September 2026;
Stutz, Cowen-Rivers, Kohli et al.; `google-deepmind/synthidbio`) and expanded
across the Central Dogma (Proteins, mRNA, and Coding DNA).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    BiosecurityWatermarkContract,
    WatermarkAlgorithm,
    WatermarkDetectionPolicy,
    WatermarkModality,
    WatermarkProvenance,
    WatermarkVerificationResult,
    WatermarkViabilityGuardrails,
)
from geneforgelang.core.validator import EnhancedSemanticValidator
from geneforgelang.core.watermark_engine import (
    SynonymousCodonWatermarker,
    SynthIDProteinWatermarker,
    WatermarkEngine,
    calculate_cai,
    translate_dna,
)


def test_biosecurity_watermark_enums_and_dataclasses() -> None:
    """Verify all enums and dataclasses instantiate with expected defaults."""
    assert str(WatermarkModality.PROTEIN) == "protein"
    assert str(WatermarkModality.CODING_DNA) == "coding_dna"
    assert str(WatermarkModality.MRNA) == "mrna"
    assert str(WatermarkModality.MULTIMODAL) == "multimodal"

    assert str(WatermarkAlgorithm.SYNTHID_GVALUE) == "synthid_gvalue"
    assert str(WatermarkAlgorithm.SYNONYMOUS_CODON_HMAC) == "synonymous_codon_hmac"

    prov = WatermarkProvenance()
    assert prov.institution == "Fundacion de Neurociencias"
    assert prov.lab_id == "INVESTIGO_NEUROIA"
    assert prov.generator_engine == "GeneForge-Rosalind"

    guard = WatermarkViabilityGuardrails()
    assert guard.max_delta_delta_g == 0.50
    assert guard.min_cai_score == 0.80
    assert guard.preserve_amino_acid_sequence is True
    assert guard.avoid_splice_motifs is True

    policy = WatermarkDetectionPolicy()
    assert policy.min_z_score == 4.50
    assert policy.green_list_fraction == 0.50
    assert policy.context_kmer_size == 3


def test_biosecurity_watermark_contract_roundtrip() -> None:
    """Test serialization and deserialization roundtrip of BiosecurityWatermarkContract."""
    contract = BiosecurityWatermarkContract(
        name="test_watermark_protocol",
        target_modality=WatermarkModality.PROTEIN,
        algorithm=WatermarkAlgorithm.SYNTHID_GVALUE,
        provenance=WatermarkProvenance(
            institution="Fundacion de Neurociencias",
            lab_id="INVESTIGO_TREM2",
            timestamp="2026-10-25T11:00:00Z",
        ),
        viability_guardrails=WatermarkViabilityGuardrails(
            max_delta_delta_g=0.40,
            min_cai_score=0.85,
        ),
        detection_policy=WatermarkDetectionPolicy(
            min_z_score=4.80,
            green_list_fraction=0.50,
        ),
        security_key_ref="test_key_seed",
    )

    data = contract.to_dict()
    assert data["name"] == "test_watermark_protocol"
    assert data["target_modality"] == "protein"
    assert data["algorithm"] == "synthid_gvalue"
    assert data["provenance"]["lab_id"] == "INVESTIGO_TREM2"
    assert data["detection_policy"]["min_z_score"] == 4.80

    reconstructed = BiosecurityWatermarkContract.from_dict(data)
    assert reconstructed.name == contract.name
    assert reconstructed.target_modality == WatermarkModality.PROTEIN
    assert reconstructed.provenance.lab_id == "INVESTIGO_TREM2"
    assert reconstructed.detection_policy.min_z_score == 4.80


def test_gfl_ast_roundtrip_with_biosecurity_watermark() -> None:
    """Test integration of biosecurity_watermark into GFLAST serialization."""
    ast = GFLAST()
    ast.biosecurity_watermark = BiosecurityWatermarkContract(
        name="ast_level_watermark",
        target_modality=WatermarkModality.CODING_DNA,
        algorithm=WatermarkAlgorithm.SYNONYMOUS_CODON_HMAC,
    )

    d = ast.to_dict()
    assert "biosecurity_watermark" in d
    assert d["biosecurity_watermark"]["name"] == "ast_level_watermark"
    assert d["biosecurity_watermark"]["target_modality"] == "coding_dna"

    loaded_ast = GFLAST.from_dict(d)
    assert loaded_ast.biosecurity_watermark is not None
    assert loaded_ast.biosecurity_watermark.name == "ast_level_watermark"
    assert loaded_ast.biosecurity_watermark.target_modality == WatermarkModality.CODING_DNA


def test_synthid_protein_watermarking_embedding_and_detection() -> None:
    """Test DeepMind SynthID Bio protein sequence watermarking and g-value detection."""
    watermarker = SynthIDProteinWatermarker(key="deepmind_synthid_test_key_2026", kmer_size=3, gamma=0.50)

    # Standard therapeutic nanobody sequence (115 amino acids)
    nanobody = (
        "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGR"
        "FTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDYDYWGQGTLVTVSS"
    )

    # 1. Unwatermarked sequence should yield g-value around 0.50 and low z-score
    g_raw, z_raw, p_raw = watermarker.detect(nanobody)
    assert abs(g_raw - 0.50) < 0.20
    assert z_raw < 3.0  # Not detected as watermarked

    # 2. Embed watermark with conservative viability constraint
    watermarked_nb = watermarker.embed(nanobody, strength=1.0, preserve_viability=True)
    assert len(watermarked_nb) == len(nanobody)

    # 3. Watermarked sequence must show strong statistical signature
    g_wm, z_wm, p_wm = watermarker.detect(watermarked_nb)
    assert g_wm > g_raw
    assert g_wm >= 0.70
    assert z_wm >= 4.0
    assert p_wm < 1e-4


def test_synonymous_codon_watermarking_exact_phenotypic_invariance() -> None:
    """Verify coding DNA watermarking achieves 100% amino acid identity (zero mutation)."""
    codon_wm = SynonymousCodonWatermarker(key="fneurociencias_codon_key_2026")

    # Coding DNA sequence (90 codons = 270 bp)
    dna = (
        "ATGCAGGTGCAGCTGGTGGAGTCTGGGGGAGGCTTGGTACAGCCTGGGGGGTCCCTGAGACTCTCCTGTGCAGCCTCT"
        "GGATTCACCTTTAGCAGCTATGCCATGAGCTGGGTCCGCCAGGCTCCAGGGAAGGGGCTGGAGTGGGTCTCAGCTATT"
        "AGTGGTAGTGGTGGTAGCACATACTACGCAGACTCCGTGAAGGGCCGGTTCACCATCTCCAGAGACAATTCCAAGAAC"
        "ACGCTGTATCTGCAAATGAACAGCCTGAGAGCCGAGGACACGGCC"
    )

    original_protein = translate_dna(dna)
    original_cai = calculate_cai(dna)
    assert len(original_protein) > 50

    # Embed synonymous watermark
    watermarked_dna = codon_wm.embed(dna, min_cai=0.80)
    watermarked_protein = translate_dna(watermarked_dna)

    # STRICT INVARIANT: 100% Amino acid identity must be preserved!
    assert (
        watermarked_protein == original_protein
    ), f"Phenotype modified! Original: {original_protein}\nWatermarked: {watermarked_protein}"

    # CAI must remain favorable for human host expression
    wm_cai = calculate_cai(watermarked_dna)
    assert wm_cai >= 0.75

    # Watermark detector should confirm presence
    g, z, p, detected_cai = codon_wm.detect(watermarked_dna)
    assert g >= 0.70
    assert z >= 3.0
    assert p < 0.01


def test_mrna_watermarking_and_ribo_detection() -> None:
    """Verify mRNA watermarking preserves translation and operates with uracil bases."""
    codon_wm = SynonymousCodonWatermarker(key="mrna_therapeutic_key_2026")

    mrna = (
        "AUGCAAGUGCAACUGGUGGAGUCUGGGGGAGGCUUGGUACAGCCUGGGGGGUCCCUGAGACUCUCCUGUGCAGCCUCU"
        "GGAUUCACCUUUAGCAGCUAUGCCAUGAGCUGGGUC"
    )

    orig_aa = translate_dna(mrna)
    wm_mrna = codon_wm.embed(mrna)

    assert "U" in wm_mrna
    assert "T" not in wm_mrna
    assert translate_dna(wm_mrna) == orig_aa

    g, z, p, cai = codon_wm.detect(wm_mrna)
    assert g >= 0.70
    assert z >= 2.0


def test_watermark_engine_high_level_orchestration() -> None:
    """Test high-level WatermarkEngine watermarking and verification workflow."""
    contract = BiosecurityWatermarkContract(
        name="high_level_nanobody_test",
        target_modality=WatermarkModality.PROTEIN,
        algorithm=WatermarkAlgorithm.SYNTHID_GVALUE,
        security_key_ref="hl_key_123",
        detection_policy=WatermarkDetectionPolicy(min_z_score=4.0),
    )

    protein = "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDYDYWGQGTLVTVSS"
    watermarked_seq, result = WatermarkEngine.watermark(contract, protein)

    assert result.is_watermarked is True
    assert result.z_score >= 4.0
    assert result.confidence_level == "CONFIRMED_AI_ORIGIN"

    # Verify call on watermarked sequence
    verify_res = WatermarkEngine.verify(contract, watermarked_seq)
    assert verify_res.is_watermarked is True
    assert verify_res.confidence_level == "CONFIRMED_AI_ORIGIN"

    # Verify call on unwatermarked raw sequence
    raw_res = WatermarkEngine.verify(contract, protein)
    assert raw_res.is_watermarked is False


def test_validator_rejects_invalid_watermark_parameters() -> None:
    """Test that EnhancedSemanticValidator rejects invalid parameters in biosecurity_watermark."""
    validator = EnhancedSemanticValidator()

    # Missing name
    invalid_doc_no_name = {
        "biosecurity_watermark": {
            "target_modality": "protein",
        }
    }
    res = validator.validate_ast(invalid_doc_no_name)
    assert not res.is_valid
    assert any("missing required 'name'" in err.message for err in res.errors)

    # Invalid modality
    invalid_doc_modality = {
        "biosecurity_watermark": {
            "name": "wm1",
            "target_modality": "unknown_quantum_biological_modality",
        }
    }
    res2 = validator.validate_ast(invalid_doc_modality)
    assert not res2.is_valid
    assert any("Unknown target_modality" in err.message for err in res2.errors)

    # Invalid min_z_score (must be positive)
    invalid_doc_z = {
        "biosecurity_watermark": {
            "name": "wm2",
            "target_modality": "protein",
            "detection_policy": {
                "min_z_score": -1.5,
            },
        }
    }
    res3 = validator.validate_ast(invalid_doc_z)
    assert not res3.is_valid
    assert any("min_z_score must be a positive float" in err.message for err in res3.errors)


def test_exemplar_biosecurity_watermark_file_validates() -> None:
    """Verify that the exemplar GFL biosecurity watermarking file parses and validates with 0 errors."""
    exemplar_path = (
        Path(__file__).parent.parent.parent / "examples" / "biosecurity_watermarked_therapeutic_nanobody.gfl"
    )
    assert exemplar_path.exists(), f"Exemplar file not found at {exemplar_path}"

    with open(exemplar_path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(doc)

    assert result.is_valid, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
