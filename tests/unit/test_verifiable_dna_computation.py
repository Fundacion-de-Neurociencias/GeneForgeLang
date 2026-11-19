"""Unit tests for FineDNA-inspired verifiable DNA computation and sequence localization contracts."""

from __future__ import annotations

import pytest

from geneforgelang.core.gftypes import (
    CoordinateSystem,
    DNAComputationContract,
    DNAComputationType,
    GFLAST,
    RLVRTaskDomain,
    SequenceLocalizationContract,
    SequenceLocalizationMode,
    StrandOrientation,
    VerifiableRewardContract,
)


class TestSequenceLocalizationContract:
    def test_exact_forward_localization(self) -> None:
        contract = SequenceLocalizationContract(
            contract_id="loc_test_exact_01",
            target_sequence="ATGCGATCGATCGATCGATCG",
            query_pattern="CGATCG",
            mode=SequenceLocalizationMode.EXACT_MATCH,
            coordinate_system=CoordinateSystem.ONE_BASED_CLOSED,
            strand_orientation=StrandOrientation.FORWARD,
        )
        matches = contract.find_matches()
        assert len(matches) == 4
        assert (4, 9, "+") in matches
        assert (8, 13, "+") in matches
        assert (12, 17, "+") in matches
        assert (16, 21, "+") in matches
        assert contract.verify_coordinates(4, 9, "+") is True
        assert contract.verify_coordinates(4, 10, "+") is False

    def test_zero_based_coordinate_system(self) -> None:
        contract = SequenceLocalizationContract(
            contract_id="loc_test_0based",
            target_sequence="ATGCGATCG",
            query_pattern="CGATCG",
            mode=SequenceLocalizationMode.EXACT_MATCH,
            coordinate_system=CoordinateSystem.ZERO_BASED_HALF_OPEN,
            strand_orientation=StrandOrientation.FORWARD,
        )
        matches = contract.find_matches()
        assert len(matches) == 1
        assert matches[0] == (3, 9, "+")
        assert contract.verify_coordinates(3, 9, "+") is True

    def test_iupac_degenerate_localization(self) -> None:
        contract = SequenceLocalizationContract(
            contract_id="loc_test_iupac",
            target_sequence="AAAGTCGGGATCTTT",
            query_pattern="AGYCG",
            mode=SequenceLocalizationMode.IUPAC_PATTERN,
            coordinate_system=CoordinateSystem.ONE_BASED_CLOSED,
            strand_orientation=StrandOrientation.FORWARD,
        )
        matches = contract.find_matches()
        assert len(matches) == 1
        assert matches[0] == (3, 7, "+")
        assert contract.verify_coordinates(3, 7, "+") is True

    def test_reverse_complement_localization(self) -> None:
        contract = SequenceLocalizationContract(
            contract_id="loc_test_both_strands",
            target_sequence="CCCCCTAGCTTTTT",
            query_pattern="AAGCTA",
            mode=SequenceLocalizationMode.EXACT_MATCH,
            coordinate_system=CoordinateSystem.ONE_BASED_CLOSED,
            strand_orientation=StrandOrientation.DUAL_STRAND,
        )
        matches = contract.find_matches()
        assert len(matches) == 1
        start, end, strand = matches[0]
        assert strand == "-"
        assert contract.verify_coordinates(start, end, "-") is True

    def test_serialization(self) -> None:
        contract = SequenceLocalizationContract(
            contract_id="loc_ser_01",
            target_sequence="ATGCATGC",
            query_pattern="ATGC",
            mode=SequenceLocalizationMode.EXACT_MATCH,
        )
        d = contract.to_dict()
        assert d["contract_id"] == "loc_ser_01"
        reconstituted = SequenceLocalizationContract.from_dict(d)
        assert reconstituted.contract_id == contract.contract_id
        assert reconstituted.query_pattern == contract.query_pattern
        assert reconstituted.mode == contract.mode


class TestDNAComputationContract:
    def test_transcription(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_tx_01",
            computation_type=DNAComputationType.TRANSCRIPTION,
            input_dna="ATGCTA",
        )
        result = contract.execute_computation()
        assert result == "AUGCUA"

    def test_reverse_complement(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_rc_01",
            computation_type=DNAComputationType.REVERSE_COMPLEMENT,
            input_dna="ATGCAT",
        )
        result = contract.execute_computation()
        assert result == "ATGCAT"

    def test_translation_forward_frames(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_trans_f1",
            computation_type=DNAComputationType.TRANSLATION,
            input_dna="ATGTTTTAA",
            reading_frame=1,
        )
        assert contract.execute_computation() == "MF*"

        contract_f2 = DNAComputationContract(
            contract_id="comp_trans_f2",
            computation_type=DNAComputationType.TRANSLATION,
            input_dna="AATGTTTTAA",
            reading_frame=2,
        )
        assert contract_f2.execute_computation() == "MF*"

    def test_translation_reverse_frame(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_trans_r1",
            computation_type=DNAComputationType.TRANSLATION,
            input_dna="TTAAAACAT",
            reading_frame=-1,
        )
        assert contract.execute_computation() == "MF*"

    def test_gc_skew(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_gc_01",
            computation_type=DNAComputationType.GC_SKEW_WINDOW,
            input_dna="GGGCC",
        )
        result = contract.execute_computation()
        assert isinstance(result, list)
        assert round(result[0], 2) == 0.20

    def test_orf_detection(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_orf_01",
            computation_type=DNAComputationType.ORF_DETECTION,
            input_dna="AAATGAAACCCTAGCC",
            orf_min_len_nt=9,
        )
        orfs = contract.execute_computation()
        assert len(orfs) >= 1
        assert orfs[0]["start"] == 3
        assert orfs[0]["end"] == 14
        assert orfs[0]["strand"] == "+"
        assert orfs[0]["orf_sequence"] == "ATGAAACCCTAG"

    def test_restriction_digest(self) -> None:
        contract = DNAComputationContract(
            contract_id="comp_digest_01",
            computation_type=DNAComputationType.RESTRICTION_DIGEST,
            input_dna="AAAAAGAATTCTTTTT",
            restriction_enzyme="EcoRI",
        )
        frags = contract.execute_computation()
        assert len(frags) == 2
        assert frags[0] == "AAAAAG"
        assert frags[1] == "AATTCTTTTT"


class TestVerifiableRewardContract:
    def test_ground_truth_reward_evaluation(self) -> None:
        contract = VerifiableRewardContract(
            task_id="rlvr_test_01",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
            ground_truth_reference="45-98:+",
        )
        reward, verified = contract.evaluate_reward("45-98:+")
        assert reward == 1.0
        assert verified is True

        reward, verified = contract.evaluate_reward("45-99:+")
        assert reward == 0.0
        assert verified is False

    def test_localization_linked_reward(self) -> None:
        loc = SequenceLocalizationContract(
            contract_id="loc_inner",
            target_sequence="NNNNNATGCGATCGNNNNN",
            query_pattern="ATGCGATCG",
            coordinate_system=CoordinateSystem.ONE_BASED_CLOSED,
        )
        contract = VerifiableRewardContract(
            task_id="rlvr_loc_eval",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
            localization_contract=loc,
        )
        reward, verified = contract.evaluate_reward("6-14:+")
        assert reward == 1.0
        assert verified is True

        reward, verified = contract.evaluate_reward("5-14:+")
        assert reward == 0.0
        assert verified is False

    def test_computation_linked_reward(self) -> None:
        comp = DNAComputationContract(
            contract_id="comp_inner",
            computation_type=DNAComputationType.TRANSLATION,
            input_dna="ATGCGATGA",
            reading_frame=1,
        )
        contract = VerifiableRewardContract(
            task_id="rlvr_comp_eval",
            domain=RLVRTaskDomain.DNA_COMPUTATION,
            computation_contract=comp,
        )
        reward, verified = contract.evaluate_reward("MR*")
        assert reward == 1.0
        assert verified is True

    def test_cryptographic_verification_proof(self) -> None:
        contract = VerifiableRewardContract(
            task_id="rlvr_proof_task",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
        )
        proof = contract.generate_verification_proof("10-25:+")
        assert isinstance(proof, str)
        assert len(proof) == 64


class TestGFLASTVerifiableDNAIntegration:
    def test_gflast_verifiable_dna_roundtrip(self) -> None:
        reward_contract = VerifiableRewardContract(
            task_id="ast_rlvr_01",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
            ground_truth_reference="10-50:+",
        )
        ast = GFLAST(verifiable_dna=reward_contract)
        assert ast.verifiable_dna is not None

        d = ast.to_dict()
        assert "verifiable_dna" in d
        assert d["verifiable_dna"]["task_id"] == "ast_rlvr_01"

        reconstructed = GFLAST.from_dict(d)
        assert reconstructed.verifiable_dna is not None
        assert reconstructed.verifiable_dna.task_id == "ast_rlvr_01"
        assert reconstructed.verifiable_dna.domain == RLVRTaskDomain.SEQUENCE_LOCALIZATION


class TestVerifiableDNASemanticValidation:
    def test_semantic_validator_verifiable_dna_success(self) -> None:
        from geneforgelang.core.validator import EnhancedSemanticValidator

        validator = EnhancedSemanticValidator()
        ast = {
            "verifiable_dna": {
                "task_id": "test_rlvr_01",
                "domain": "sequence_localization",
                "localization_contract": {
                    "query_pattern": "ATGC",
                },
                "computation_contract": {
                    "input_dna": "ATGCATGC",
                },
            }
        }
        result = validator.validate_ast(ast)
        assert result.is_valid is True

    def test_semantic_validator_missing_task_id(self) -> None:
        from geneforgelang.core.validator import EnhancedSemanticValidator

        validator = EnhancedSemanticValidator()
        ast = {
            "verifiable_dna": {
                "domain": "sequence_localization",
            }
        }
        result = validator.validate_ast(ast)
        assert result.is_valid is False
        assert any("task_id" in e.message for e in result.errors)

    def test_validate_exemplar_file(self) -> None:
        import yaml
        from pathlib import Path
        from geneforgelang.core.validator import EnhancedSemanticValidator

        example_path = Path("examples/features/verifiable_dna_computation.gfl")
        assert example_path.exists(), f"Exemplar file {example_path} not found"
        with open(example_path, "r", encoding="utf-8") as f:
            ast = yaml.safe_load(f)

        validator = EnhancedSemanticValidator()
        result = validator.validate_ast(ast)
        assert result.is_valid is True, f"Validation failed: {[e.message for e in result.errors]}"
