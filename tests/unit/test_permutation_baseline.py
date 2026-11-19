"""Unit tests for the Phylo-style Permutation Baseline Gate and sequence signal auditing."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

from geneforgelang.core.gftypes import (
    GFLAST,
    PermutationControlMode,
    RLVRTaskDomain,
    SequencePermutationBaselineContract,
    VerifiableRewardContract,
)
from geneforgelang.core.permutation_baseline import (
    PermutationBaselineAuditor,
    deterministic_shuffle,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestDeterministicShuffle:
    """Tests for composition-preserving and 2-mer-preserving deterministic shuffles."""

    def test_uniform_shuffle_preserves_composition_and_is_seeded(self) -> None:
        seq = "MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ"
        s1 = deterministic_shuffle(seq, PermutationControlMode.UNIFORM_SHUFFLE, seed=42)
        s2 = deterministic_shuffle(seq, PermutationControlMode.UNIFORM_SHUFFLE, seed=42)
        s3 = deterministic_shuffle(seq, PermutationControlMode.UNIFORM_SHUFFLE, seed=99)

        assert s1 == s2
        assert s1 != seq
        assert s1 != s3
        assert Counter(s1) == Counter(seq)

    def test_dipeptide_shuffle_preserves_exact_2mer_transitions(self) -> None:
        seq = "MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ"
        shuffled = deterministic_shuffle(seq, PermutationControlMode.DIPEPTIDE_SHUFFLE, seed=42)

        assert len(shuffled) == len(seq)
        assert shuffled[0] == seq[0]
        assert shuffled[-1] == seq[-1]
        assert Counter(shuffled) == Counter(seq)

        orig_2mers = Counter(seq[i : i + 2] for i in range(len(seq) - 1))
        shuf_2mers = Counter(shuffled[i : i + 2] for i in range(len(shuffled) - 1))
        assert shuf_2mers == orig_2mers

    def test_dinucleotide_shuffle_preserves_exact_2mer_transitions(self) -> None:
        dna = "ATGCGATCGATCGTAGCTAGCTAGCATCGATCG"
        shuffled = deterministic_shuffle(dna, PermutationControlMode.DINUCLEOTIDE_SHUFFLE, seed=7)

        assert len(shuffled) == len(dna)
        assert shuffled[0] == dna[0]
        assert shuffled[-1] == dna[-1]
        orig_2mers = Counter(dna[i : i + 2] for i in range(len(dna) - 1))
        shuf_2mers = Counter(shuffled[i : i + 2] for i in range(len(shuffled) - 1))
        assert shuf_2mers == orig_2mers


class TestPermutationBaselineAuditor:
    """Tests for native vs. shuffled continuation gap auditing."""

    def test_auditor_passes_when_model_exhibits_real_sequence_signal(self) -> None:
        contract = SequencePermutationBaselineContract(
            contract_id="audit_fable_01",
            sequence_type="protein",
            reference_prefix="MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ",
            target_suffix="GKSFEVLKDR",
            control_mode=PermutationControlMode.DIPEPTIDE_SHUFFLE,
            seed=42,
            min_permutation_gap=0.20,
            model_id="claude-fable-5.2",
        )

        # Native prediction gets 8/10 residues right (0.80); shuffled control gets 1/10 (0.10)
        res = PermutationBaselineAuditor.audit_predictions(
            contract,
            native_prediction="GKSFEVLKAA",
            shuffled_prediction="GAAAAAAAAA",
        )

        assert res.native_accuracy == 0.8
        assert res.shuffled_accuracy == 0.1
        assert res.permutation_gap == 0.7
        assert res.passes_gate is True
        assert res.evidence_status == "PERMUTATION_CONTROL_VERIFIED"
        assert len(res.verification_hash) == 64
        assert len(res.shuffled_prefix) == len(contract.reference_prefix)

    def test_auditor_fails_when_gap_is_near_zero(self) -> None:
        contract = SequencePermutationBaselineContract(
            contract_id="audit_zero_gap_01",
            sequence_type="protein",
            reference_prefix="MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ",
            target_suffix="GKSFEVLKDR",
            control_mode=PermutationControlMode.UNIFORM_SHUFFLE,
            seed=42,
            min_permutation_gap=0.15,
            model_id="untrained-baseline",
        )

        res = PermutationBaselineAuditor.audit_predictions(
            contract,
            native_prediction="AAAAAAAAAA",
            shuffled_prediction="AAAAAAAAAA",
        )

        assert res.native_accuracy == 0.0
        assert res.shuffled_accuracy == 0.0
        assert res.permutation_gap == 0.0
        assert res.passes_gate is False
        assert res.evidence_status == "INSUFFICIENT_SEQUENCE_SIGNAL"


class TestPermutationBaselineTypesAndAST:
    """Tests for GFL AST and VerifiableRewardContract serialization roundtrips."""

    def test_contract_and_verifiable_reward_roundtrip(self) -> None:
        pb = SequencePermutationBaselineContract(
            contract_id="pb_01",
            sequence_type="protein",
            reference_prefix="MKKLLVLSLV",
            target_suffix="GKSFE",
            control_mode=PermutationControlMode.DIPEPTIDE_SHUFFLE,
            seed=11,
            min_permutation_gap=0.25,
            model_id="claude-fable-5.2",
        )
        vrc = VerifiableRewardContract(
            task_id="rlvr_pb_01",
            domain=RLVRTaskDomain.PERMUTATION_BASELINE_GAP,
            ground_truth_reference="GKSFE",
            permutation_baseline=pb,
        )

        d = vrc.to_dict()
        assert d["permutation_baseline"]["contract_id"] == "pb_01"
        rec = VerifiableRewardContract.from_dict(d)
        assert rec.domain == RLVRTaskDomain.PERMUTATION_BASELINE_GAP
        assert rec.permutation_baseline is not None
        assert rec.permutation_baseline.control_mode == PermutationControlMode.DIPEPTIDE_SHUFFLE

    def test_gflast_roundtrip_and_alias(self) -> None:
        pb = SequencePermutationBaselineContract(
            contract_id="ast_pb_01",
            sequence_type="dna",
            reference_prefix="ATGCGATCG",
            target_suffix="TTAA",
        )
        ast = GFLAST(permutation_baseline=pb)
        d = ast.to_dict()
        assert "permutation_baseline" in d

        rec1 = GFLAST.from_dict(d)
        assert rec1.permutation_baseline is not None
        assert rec1.permutation_baseline.contract_id == "ast_pb_01"

        rec2 = GFLAST.from_dict({"sequence_signal_audit": d["permutation_baseline"]})
        assert rec2.permutation_baseline is not None
        assert rec2.permutation_baseline.contract_id == "ast_pb_01"


class TestPermutationBaselineValidator:
    """Tests for EnhancedSemanticValidator rules on permutation_baseline blocks."""

    def test_validate_official_exemplar(self) -> None:
        exemplar_path = Path(__file__).parents[2] / "examples" / "features" / "phylo_permutation_baseline_audit.gfl"
        assert exemplar_path.exists()

        with open(exemplar_path, encoding="utf-8") as f:
            ast_data = yaml.safe_load(f.read())

        res = EnhancedSemanticValidator().validate_ast(ast_data)
        assert res.is_valid, f"Unexpected validation errors: {[e.message for e in res.errors]}"

    def test_validator_rejects_invalid_characters_and_params(self) -> None:
        bad_ast = {
            "permutation_baseline": {
                "contract_id": "bad_01",
                "sequence_type": "dna",
                "reference_prefix": "ATGCGZ123",
                "target_suffix": "TTAA",
                "control_mode": "magic_shuffle",
                "min_permutation_gap": 1.5,
                "seed": -3,
            }
        }
        res = EnhancedSemanticValidator().validate_ast(bad_ast)
        assert not res.is_valid
        messages = " | ".join(e.message for e in res.errors)
        assert "Invalid dna characters" in messages
        assert "Invalid control_mode" in messages
        assert "min_permutation_gap" in messages
        assert "seed" in messages
