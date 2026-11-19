"""Unit test suite for ProTok (Protein Tokenizer) multimodal residue vocabulary in GeneForgeLang."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    ProTokConditioningMode,
    ProTokContract,
    ProTokDropoutPolicy,
    ProTokModality,
    ProTokResidueToken,
    ProTokVerificationResult,
)
from geneforgelang.core.protok_engine import (
    EPI_MASK_TOKEN,
    FUN_MASK_TOKEN,
    STR_MASK_TOKEN,
    TOP_MASK_TOKEN,
    GenTokTokenizer,
    ProTokEngine,
    ProTokFunctionQuantizer,
    ProTokGeometricQuantizer,
    ProTokTokenizer,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestProTokTypes:
    """Test data structures, enums, and serialization round-trips for ProTok."""

    def test_enums_and_dataclasses(self) -> None:
        assert ProTokModality.TRIMODAL.value == "trimodal"
        assert ProTokModality.SEQUENCE.value == "sequence"
        assert ProTokModality.STRUCTURE.value == "structure"
        assert ProTokModality.FUNCTION.value == "function"

        assert ProTokConditioningMode.STRUCTURE_TO_FUNCTION.value == "structure_to_function"
        assert ProTokConditioningMode.FUNCTION_TO_ALL.value == "function_to_all"

        token = ProTokResidueToken(
            pos=1,
            amino_acid="M",
            structure_code=506,
            function_code=45,
            dihedral_phi=-60.0,
            dihedral_psi=-45.0,
            ec_classification="EC:2.3.2.27",
            composite_token_id=260653,
        )
        t_dict = token.to_dict()
        assert t_dict["amino_acid"] == "M"
        assert t_dict["structure_code"] == 506
        t_round = ProTokResidueToken.from_dict(t_dict)
        assert t_round.pos == 1
        assert t_round.dihedral_phi == -60.0

        policy = ProTokDropoutPolicy(
            allow_missing_sequence=False,
            allow_missing_structure=True,
            allow_missing_function=True,
            dropout_rate=0.20,
        )
        p_dict = policy.to_dict()
        assert p_dict["dropout_rate"] == 0.20
        p_round = ProTokDropoutPolicy.from_dict(p_dict)
        assert p_round.allow_missing_structure is True

        result = ProTokVerificationResult(
            reconstructed_lddt=0.939,
            ec_top1_precision=0.695,
            recovered_modalities=["sequence", "structure", "function"],
            designability_score=0.52,
            token_count=100,
        )
        r_dict = result.to_dict()
        assert r_dict["reconstructed_lddt"] == 0.939
        r_round = ProTokVerificationResult.from_dict(r_dict)
        assert r_round.ec_top1_precision == 0.695

        contract = ProTokContract(
            name="ubiquitin_ligase_test",
            target_protein="UBQLN2",
            conditioning_mode=ProTokConditioningMode.STRUCTURE_TO_FUNCTION,
            target_modality=ProTokModality.TRIMODAL,
            dropout_policy=policy,
            residue_stream=[token],
            target_ec_classification="EC:2.3.2.27",
            expected_lddt_min=0.92,
            verified_result=result,
        )
        c_dict = contract.to_dict()
        assert c_dict["name"] == "ubiquitin_ligase_test"
        c_round = ProTokContract.from_dict(c_dict)
        assert c_round.name == "ubiquitin_ligase_test"
        assert c_round.conditioning_mode == ProTokConditioningMode.STRUCTURE_TO_FUNCTION
        assert len(c_round.residue_stream) == 1
        assert c_round.verified_result is not None
        assert c_round.verified_result.reconstructed_lddt == 0.939

    def test_gflast_roundtrip(self) -> None:
        contract = ProTokContract(
            name="ast_protok_test",
            target_protein="DCTN1",
            conditioning_mode=ProTokConditioningMode.FUNCTION_TO_ALL,
            sequence_payload="MQIFVKTLTG",
        )
        ast = GFLAST(protok=contract)
        d = ast.to_dict()
        assert "protok" in d
        assert d["protok"]["name"] == "ast_protok_test"

        ast_recovered = GFLAST.from_dict(d)
        assert ast_recovered.protok is not None
        assert ast_recovered.protok.name == "ast_protok_test"
        assert ast_recovered.protok.conditioning_mode == ProTokConditioningMode.FUNCTION_TO_ALL

        # Test alias 'unified_protein_stream'
        alias_dict = {"unified_protein_stream": contract.to_dict()}
        ast_alias = GFLAST.from_dict(alias_dict)
        assert ast_alias.protok is not None
        assert ast_alias.protok.name == "ast_protok_test"


class TestProTokQuantizers:
    """Test geometric and functional quantization mechanics."""

    def test_geometric_quantization(self) -> None:
        # Alpha helix core (-60, -45)
        code_alpha = ProTokGeometricQuantizer.quantize_dihedrals(-60.0, -45.0)
        assert code_alpha in range(0, 511)

        # Beta sheet core (-120, 135)
        code_beta = ProTokGeometricQuantizer.quantize_dihedrals(-120.0, 135.0)
        assert code_beta in range(0, 511)
        assert code_alpha != code_beta

        # None dihedrals should map to STR_MASK_TOKEN
        assert ProTokGeometricQuantizer.quantize_dihedrals(None, None) == STR_MASK_TOKEN

        # Dequantization roundtrip
        phi, psi = ProTokGeometricQuantizer.dequantize_dihedrals(506)
        assert phi == -60.0
        assert psi == -45.0

    def test_functional_quantization(self) -> None:
        # Transferases (EC 2.x.x.x)
        code_trans = ProTokFunctionQuantizer.quantize_ec("EC:2.3.2.27")
        assert code_trans in range(0, 255)
        lvl_trans = ProTokFunctionQuantizer.dequantize_ec_level1(code_trans)
        assert lvl_trans == 2

        # Hydrolases (EC 3.x.x.x)
        code_hydro = ProTokFunctionQuantizer.quantize_ec("EC:3.4.21.4")
        lvl_hydro = ProTokFunctionQuantizer.dequantize_ec_level1(code_hydro)
        assert lvl_hydro == 3

        # None EC should map to FUN_MASK_TOKEN
        assert ProTokFunctionQuantizer.quantize_ec(None) == FUN_MASK_TOKEN


class TestProTokTokenizer:
    """Test tokenization, composite token assembly, and codebook group dropout."""

    def test_composite_token_bijection(self) -> None:
        seq_code = 12  # Proline
        str_code = 506  # Alpha helix
        fun_code = 45  # Transferase

        token_id = ProTokTokenizer.compute_composite_token(seq_code, str_code, fun_code)
        rec_s, rec_st, rec_f = ProTokTokenizer.decompose_composite_token(token_id)

        assert rec_s == seq_code
        assert rec_st == str_code
        assert rec_f == fun_code

    def test_codebook_group_dropout(self) -> None:
        # Case 1: Structure dropped (sequence-only inference)
        dropout_str = ProTokDropoutPolicy(allow_missing_structure=True)
        tokens = ProTokTokenizer.encode_residues(
            sequence="MKTII",
            dihedrals=None,
            ec_classification="EC:2.3.2.27",
            dropout_policy=dropout_str,
        )
        assert len(tokens) == 5
        for t in tokens:
            assert t.structure_code == STR_MASK_TOKEN
            assert t.function_code != FUN_MASK_TOKEN

        # Case 2: Function dropped (structure-to-sequence)
        dropout_fun = ProTokDropoutPolicy(allow_missing_function=True)
        dihedrals = [(-60.0, -45.0)] * 5
        tokens_no_fun = ProTokTokenizer.encode_residues(
            sequence="MKTII",
            dihedrals=dihedrals,
            ec_classification=None,
            dropout_policy=dropout_fun,
        )
        for t in tokens_no_fun:
            assert t.structure_code != STR_MASK_TOKEN
            assert t.function_code == FUN_MASK_TOKEN


class TestProTokEngine:
    """Test computational execution, lDDT scoring, zero-shot retrieval, and watermarking."""

    def test_engine_execution_and_fidelity(self) -> None:
        engine = ProTokEngine()
        contract = ProTokContract(
            name="ubiquitin_eval",
            sequence_payload="MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
            target_ec_classification="EC:2.3.2.27",
            expected_lddt_min=0.90,
        )

        result = engine.execute(contract)

        assert isinstance(result, ProTokVerificationResult)
        assert result.evidence_status == "declarative_tokenized"
        assert result.reconstructed_lddt >= 0.90
        assert result.ec_top1_precision >= 0.65
        assert result.designability_score == 0.52
        assert result.token_count == len(contract.sequence_payload)
        assert "sequence" in result.recovered_modalities
        assert "structure" in result.recovered_modalities
        assert "function" in result.recovered_modalities
        assert result.metadata["architectural_layer"] == "GFL_DECLARATIVE_CONTRACT"

    def test_synthid_bio_structural_watermarking_synergy(self) -> None:
        engine = ProTokEngine()
        tokens = ProTokTokenizer.encode_residues(
            sequence="MQIFVKTLTG",
            dihedrals=[(-60.0, -45.0)] * 10,
            ec_classification="EC:2.3.2.27",
        )

        watermarked = engine.embed_structural_watermark(tokens, secret_key="biosecurity_secret_key_123")

        assert len(watermarked) == len(tokens)
        # 100% Sequence preservation (zero alteration of amino acid identity)
        orig_seq = "".join(t.amino_acid for t in tokens)
        wm_seq = "".join(t.amino_acid for t in watermarked)
        assert orig_seq == wm_seq

        # Structural codebooks carry the embedded bias
        assert any(t_orig.structure_code != t_wm.structure_code for t_orig, t_wm in zip(tokens, watermarked))

        # Detect watermark with high confidence
        detection = engine.detect_structural_watermark(watermarked, secret_key="biosecurity_secret_key_123")
        assert detection["watermark_detected"] is True
        assert detection["match_rate"] >= 0.85
        assert detection["evidence_status"] == "declarative_tokenized"

        # False key yields no watermark detection
        detection_false = engine.detect_structural_watermark(watermarked, secret_key="wrong_key_xyz")
        assert detection_false["watermark_detected"] is False

    def test_watermark_false_positive_rate_measured(self) -> None:
        """Measure the empirical FPR over many wrong keys on a 40-residue stream."""
        engine = ProTokEngine()
        seq = "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQ"
        tokens = ProTokTokenizer.encode_residues(
            sequence=seq,
            dihedrals=[(-60.0, -45.0)] * len(seq),
            ec_classification="EC:2.3.2.27",
        )
        marked = engine.embed_structural_watermark(tokens, secret_key="true_key")
        true_det = engine.detect_structural_watermark(marked, secret_key="true_key")
        assert true_det["watermark_detected"] is True
        assert true_det["null_p_value"] < 1e-6

        trials = 2000
        false_hits = sum(
            engine.detect_structural_watermark(marked, secret_key=f"wrong_key_{i}")["watermark_detected"]
            for i in range(trials)
        )
        # Exact null FPR at n=40, threshold 0.80 is about 1e-4, so >5 hits in 2000 trials is implausible.
        assert false_hits <= 5

    def test_backbone_coordinates_quantization(self) -> None:
        # 3 residues forming an alpha-helical segment (approximate coordinates)
        backbone = [
            ((0.0, 0.0, 0.0), (1.458, 0.0, 0.0), (2.009, 1.397, 0.0)),
            ((1.246, 2.378, -0.428), (1.688, 3.766, -0.589), (3.181, 3.867, -0.301)),
            ((3.653, 5.068, 0.038), (5.086, 5.337, 0.282), (5.422, 6.789, 0.651)),
        ]
        dihedrals = ProTokEngine.quantize_backbone_coordinates(backbone)
        assert len(dihedrals) == 3
        # First residue has no previous C, so phi is None
        assert dihedrals[0][0] is None
        # Middle residue has both phi and psi computed
        assert dihedrals[1][0] is not None
        assert dihedrals[1][1] is not None

    def test_ontrack_payload_export(self) -> None:
        contract = ProTokContract(
            name="export_test",
            sequence_payload="MKT",
            target_ec_classification="EC:2.3.2.27",
        )
        payload = contract.to_ontrack_payload()
        assert payload["contract_type"] == "protok_multimodal_stream"
        assert payload["name"] == "export_test"
        assert payload["target_ec_classification"] == "EC:2.3.2.27"


class TestProTokValidator:
    """Test semantic validation rules and rejection criteria for protok."""

    def test_validate_exemplar_file(self) -> None:
        exemplar_path = Path(__file__).parent.parent.parent / "examples" / "protok_multimodal_enzyme_design.gfl"
        assert exemplar_path.exists()
        with open(exemplar_path, encoding="utf-8") as f:
            ast = yaml.safe_load(f)

        validator = EnhancedSemanticValidator(file_path=str(exemplar_path))
        res = validator.validate_ast(ast)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_validator_rejections(self) -> None:
        validator = EnhancedSemanticValidator()

        # 1. Missing name
        res1 = validator.validate_ast({"protok": {"conditioning_mode": "structure_to_function"}})
        assert res1.is_valid is False
        assert any("missing required 'name'" in e.message for e in res1.errors)

        # 2. Invalid conditioning_mode
        res2 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "conditioning_mode": "invalid_mode",
                }
            }
        )
        assert res2.is_valid is False
        assert any("Unknown conditioning_mode" in e.message for e in res2.errors)

        # 3. Invalid target_modality
        res3 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "target_modality": "hyper_modal",
                }
            }
        )
        assert res3.is_valid is False
        assert any("Unknown target_modality" in e.message for e in res3.errors)

        # 4. Invalid EC syntax
        res4 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "target_ec_classification": "Enzyme_Class_2",
                }
            }
        )
        assert res4.is_valid is False
        assert any("Invalid Enzyme Commission syntax" in e.message for e in res4.errors)

        # 5. Out-of-range dihedral angle
        res5 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "residue_stream": [
                        {"pos": 1, "amino_acid": "M", "dihedral_phi": 250.0},
                    ],
                }
            }
        )
        assert res5.is_valid is False
        assert any("within [-180.0, 180.0]" in e.message for e in res5.errors)

        # 6. Out-of-range structure_code
        res6 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "residue_stream": [
                        {"pos": 1, "amino_acid": "M", "structure_code": 999},
                    ],
                }
            }
        )
        assert res6.is_valid is False
        assert any("outside ProTok codebook range [0..511]" in e.message for e in res6.errors)

        # 7. Contradiction between dropout_policy (forbidding missing structure) and masked token
        res7 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "dropout_policy": {"allow_missing_structure": False},
                    "residue_stream": [
                        {"pos": 1, "amino_acid": "M", "structure_code": 511},
                    ],
                }
            }
        )
        assert res7.is_valid is False
        assert any("dropout_policy forbids missing structure" in e.message for e in res7.errors)

        # 8. Mismatch between residue token amino_acid and sequence_payload
        res8 = validator.validate_ast(
            {
                "protok": {
                    "name": "test",
                    "sequence_payload": "MKT",
                    "residue_stream": [
                        {"pos": 1, "amino_acid": "W"},  # Expected 'M'
                    ],
                }
            }
        )
        assert res8.is_valid is False
        assert any("Residue mismatch at pos 1" in e.message for e in res8.errors)


class TestBidirectionalCrossSynergies:
    """Test the 4 bidirectional cross-synergies between ProTok and GeneForgeLang."""

    def test_synergy_1_gentok_trimodal_genomic_tokenizer(self) -> None:
        # Full trimodal genomic locus encoding (DNA + 3D Chromatin Topology + Epigenetic State)
        token_id = GenTokTokenizer.encode_genomic_locus(
            nucleotide="G",
            chromatin_topology="LOOP_ANCHOR",
            epigenetic_state="STRONG_ENHANCER",
        )
        assert 0 <= token_id < 16384
        decoded = GenTokTokenizer.decode_genomic_token(token_id)
        assert decoded["nucleotide"] == "G"
        assert decoded["chromatin_topology"] == "LOOP_ANCHOR"
        assert decoded["epigenetic_state"] == "STRONG_ENHANCER"

        # Codebook Group Dropout on genomic locus (missing 3D chromatin & epigenetics)
        token_dropout = GenTokTokenizer.encode_genomic_locus(
            nucleotide="A",
            chromatin_topology=None,
            epigenetic_state=None,
        )
        dec_drop = GenTokTokenizer.decode_genomic_token(token_dropout)
        assert dec_drop["nucleotide"] == "A"
        assert dec_drop["topology_code"] == TOP_MASK_TOKEN
        assert dec_drop["epigenetic_code"] == EPI_MASK_TOKEN

    def test_synergy_2_central_dogma_variant_propagation(self) -> None:
        engine = ProTokEngine()
        contract = ProTokContract(
            name="central_dogma_test",
            sequence_payload="MQIFVKTLTG",
            target_ec_classification="EC:2.3.2.27",
        )
        engine.execute(contract)

        # 1. Synonymous variant (CAA -> CAG, both encode Q)
        syn = engine.propagate_genomic_variant(contract, residue_pos=2, ref_codon="CAA", alt_codon="CAG")
        assert syn["molecular_consequence"] == "SYNONYMOUS"
        assert syn["delta_lddt"] == 0.0
        assert syn["recommended_decision"] == "APPROVE_BENIGN"

        # 2. Missense helix-breaker variant (CAA -> CCA, Q -> P in alpha-helix 506)
        mis = engine.propagate_genomic_variant(contract, residue_pos=2, ref_codon="CAA", alt_codon="CCA")
        assert mis["molecular_consequence"] == "MISSENSE"
        assert mis["alt_aa"] == "P"
        assert mis["delta_lddt"] < -0.10
        assert mis["recommended_decision"] == "REJECT_PATHOGENIC"

        # 3. Nonsense premature stop variant (CAA -> TAA, Q -> *)
        stop = engine.propagate_genomic_variant(contract, residue_pos=2, ref_codon="CAA", alt_codon="TAA")
        assert stop["molecular_consequence"] == "NONSENSE_PREMATURE_STOP"
        assert stop["recommended_decision"] == "REJECT_PATHOGENIC"

    def test_synergy_3_grammar_constrained_decoding_mask(self) -> None:
        mask = ProTokEngine.build_grammar_constraint_mask(
            allowed_amino_acids=["M", "Q"],
            allowed_structure_codes=[506],
            allowed_function_codes=[45],
        )
        assert mask["total_vocabulary_size"] == 3145728
        assert mask["allowed_state_count"] == 2  # 2 AAs x 1 structure x 1 function
        assert mask["search_space_reduction_ratio"] > 0.99999
        assert len(mask["sample_valid_composite_tokens"]) == 2

    def test_synergy_4_tridimensional_diagnostic_axes_projection(self) -> None:
        wt_tokens = [
            ProTokResidueToken(pos=1, amino_acid="M", structure_code=506, function_code=45),
            ProTokResidueToken(pos=2, amino_acid="Q", structure_code=506, function_code=45),
        ]
        # Identical stream -> zero perturbation on all 3 axes
        zero_proj = ProTokEngine.project_to_tridimensional_axes(wt_tokens, wt_tokens)
        assert zero_proj["axis_1_etiological_sequence"] == 0.0
        assert zero_proj["axis_2_structural_conformational"] == 0.0
        assert zero_proj["axis_3_functional_phenotypic"] == 0.0
        assert zero_proj["composite_severity_norm"] == 0.0

        # Pathogenic variant stream (Q -> V, alpha-helix 506 -> beta-sheet 507, function masked 255)
        mut_tokens = [
            ProTokResidueToken(pos=1, amino_acid="M", structure_code=506, function_code=45),
            ProTokResidueToken(pos=2, amino_acid="V", structure_code=507, function_code=FUN_MASK_TOKEN),
        ]
        mut_proj = ProTokEngine.project_to_tridimensional_axes(wt_tokens, mut_tokens)
        assert mut_proj["axis_1_etiological_sequence"] == 0.5
        assert mut_proj["axis_2_structural_conformational"] == 0.5
        assert mut_proj["axis_3_functional_phenotypic"] == 0.5
        assert mut_proj["composite_severity_norm"] == 0.5
        assert mut_proj["evidence_status"] == "declarative_tokenized"
