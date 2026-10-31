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
    FUN_MASK_TOKEN,
    STR_MASK_TOKEN,
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
