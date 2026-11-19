"""Unit tests for FineDNA sovereign biological reasoning and RLVR compiler engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from geneforgelang.core.errors import ErrorCodes
from geneforgelang.core.finedna_engine import (
    FineDNAClientHarness,
    FineDNARLVREnvironment,
    FineDNARLVRExporter,
)
from geneforgelang.core.gftypes import (
    GFLAST,
    FineDNAContract,
    FineDNAInferenceConfig,
    FineDNATaskType,
    RLVREnvironmentTrace,
    RLVRTaskDomain,
    SequenceLocalizationContract,
    SequenceLocalizationMode,
    VerifiableRewardContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestFineDNADataTypes:
    """Tests for FineDNA enums, dataclasses, and GFL AST integration."""

    def test_finedna_task_types(self) -> None:
        assert FineDNATaskType.GFL_CODE_SYNTHESIS.value == "gfl_code_synthesis"
        assert FineDNATaskType.SEQUENCE_LOCALIZATION.value == "sequence_localization"
        assert FineDNATaskType.CRISPR_CIRCUIT_DESIGN.value == "crispr_circuit_design"
        assert FineDNATaskType.VARIANT_EFFECT_REASONING.value == "variant_effect_reasoning"
        assert FineDNATaskType.ENZYME_MUTAGENESIS.value == "enzyme_mutagenesis"
        assert FineDNATaskType.RLVR_BENCHMARK_TASK.value == "rlvr_benchmark_task"

    def test_inference_config_serialization(self) -> None:
        cfg = FineDNAInferenceConfig(
            endpoint_url="http://127.0.0.1:8000/v1",
            model_name="FineDNA-14B",
            temperature=0.15,
            max_tokens=2048,
            air_gapped=True,
            timeout_seconds=45.0,
        )
        d = cfg.to_dict()
        assert d["endpoint_url"] == "http://127.0.0.1:8000/v1"
        assert d["air_gapped"] is True

        reconstituted = FineDNAInferenceConfig.from_dict(d)
        assert reconstituted.endpoint_url == cfg.endpoint_url
        assert reconstituted.temperature == cfg.temperature
        assert reconstituted.air_gapped == cfg.air_gapped
        assert reconstituted.timeout_seconds == cfg.timeout_seconds

    def test_trace_serialization(self) -> None:
        trace = RLVREnvironmentTrace(
            iteration_count=2,
            successful=True,
            reward_score=1.0,
            verification_proof="abcdef0123456789",
            error_history=["Iteration 1 syntax error"],
            final_gfl_code="verifiable_dna:\n  task_id: test",
        )
        d = trace.to_dict()
        assert d["iteration_count"] == 2
        assert d["successful"] is True
        assert len(d["error_history"]) == 1

        rec = RLVREnvironmentTrace.from_dict(d)
        assert rec.iteration_count == 2
        assert rec.verification_proof == "abcdef0123456789"
        assert rec.successful is True

    def test_contract_roundtrip(self) -> None:
        vrc = VerifiableRewardContract(
            task_id="vrc_trem2",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
            ground_truth_reference="10-25:+",
            reward_success=1.0,
        )
        contract = FineDNAContract(
            contract_id="contract_test_01",
            task_type=FineDNATaskType.CRISPR_CIRCUIT_DESIGN,
            prompt="Design repair template for TREM2 R47H",
            target_locus="chr6:41126000-41131000",
            verifiable_reward_contract=vrc,
            generated_gfl="verifiable_dna:\n  task_id: test\n",
        )
        d = contract.to_dict()
        assert d["contract_id"] == "contract_test_01"
        assert d["task_type"] == "crispr_circuit_design"
        assert d["target_locus"] == "chr6:41126000-41131000"
        assert d["verifiable_reward_contract"] is not None

        rec = FineDNAContract.from_dict(d)
        assert rec.contract_id == contract.contract_id
        assert rec.task_type == FineDNATaskType.CRISPR_CIRCUIT_DESIGN
        assert rec.target_locus == contract.target_locus
        assert rec.verifiable_reward_contract is not None
        assert rec.verifiable_reward_contract.task_id == "vrc_trem2"

    def test_gflast_roundtrip_with_aliases(self) -> None:
        contract = FineDNAContract(
            contract_id="ast_test_fd",
            task_type=FineDNATaskType.GFL_CODE_SYNTHESIS,
            prompt="Synthesize pathway",
        )
        ast = GFLAST(finedna=contract)
        d = ast.to_dict()
        assert "finedna" in d
        assert d["finedna"]["contract_id"] == "ast_test_fd"

        # Roundtrip via canonical name
        rec1 = GFLAST.from_dict(d)
        assert rec1.finedna is not None
        assert rec1.finedna.contract_id == "ast_test_fd"

        # Roundtrip via alias finedna_circuit
        alias_data = {"finedna_circuit": d["finedna"]}
        rec2 = GFLAST.from_dict(alias_data)
        assert rec2.finedna is not None
        assert rec2.finedna.contract_id == "ast_test_fd"


class TestFineDNAClientHarness:
    """Tests for endpoint sanitization, air-gapped security, and prompt generation."""

    def test_sanitize_valid_local_endpoints(self) -> None:
        assert FineDNAClientHarness.sanitize_endpoint("http://localhost:8000/v1", air_gapped=True)
        assert FineDNAClientHarness.sanitize_endpoint("http://127.0.0.1:11434", air_gapped=True)
        assert FineDNAClientHarness.sanitize_endpoint("http://10.48.3.222:8000/v1", air_gapped=True)
        assert FineDNAClientHarness.sanitize_endpoint("http://192.168.1.100:8000/v1", air_gapped=True)
        assert FineDNAClientHarness.sanitize_endpoint("http://172.20.0.10:8000", air_gapped=True)

    def test_sanitize_rejects_external_when_air_gapped(self) -> None:
        with pytest.raises(ValueError, match="Air-gapped sovereign inference violation"):
            FineDNAClientHarness.sanitize_endpoint("https://api.openai.com/v1", air_gapped=True)

        with pytest.raises(ValueError, match="Air-gapped sovereign inference violation"):
            FineDNAClientHarness.sanitize_endpoint("https://api.anthropic.com/v1", air_gapped=True)

    def test_sanitize_allows_external_when_air_gapped_disabled(self) -> None:
        endpoint = FineDNAClientHarness.sanitize_endpoint("https://api.openai.com/v1", air_gapped=False)
        assert endpoint == "https://api.openai.com/v1"

    def test_generate_chatml_prompt(self) -> None:
        contract = FineDNAContract(
            contract_id="prompt_test",
            task_type=FineDNATaskType.SEQUENCE_LOCALIZATION,
            prompt="Find EcoRI motif",
            target_locus="chr17:41196312-41277500",
        )
        msgs = FineDNAClientHarness.generate_chatml_prompt(contract)
        assert len(msgs) == 2
        assert "FineDNA-14B" in msgs[0]["content"]
        assert "chr17:41196312-41277500" in msgs[1]["content"]
        assert "sequence_localization" in msgs[1]["content"]

    def test_offline_deterministic_fallback(self) -> None:
        contract = FineDNAContract(
            contract_id="offline_test",
            task_type=FineDNATaskType.CRISPR_CIRCUIT_DESIGN,
            prompt="Generate HDR construct",
        )
        output = FineDNAClientHarness.offline_deterministic_fallback(contract)
        assert "crispr_hdr:" in output
        assert "verifiable_dna:" in output

    def test_run_inference_offline_resilience(self) -> None:
        contract = FineDNAContract(
            contract_id="resilience_test",
            task_type=FineDNATaskType.GFL_CODE_SYNTHESIS,
            prompt="Synthesize protocol",
            inference_config=FineDNAInferenceConfig(
                endpoint_url="http://127.0.0.1:59999/v1",  # Unused port
                timeout_seconds=0.1,
            ),
        )
        result = FineDNAClientHarness.run_inference(contract)
        assert isinstance(result, str)
        assert len(result) > 0


class TestFineDNARLVREnvironment:
    """Tests for closed-loop RLVR interactive compilation and self-correction."""

    def test_rlvr_environment_convergence_and_proof(self) -> None:
        loc = SequenceLocalizationContract(
            contract_id="loc_sub",
            target_sequence="NNNNNATGCGATCGATCGNNNNN",
            query_pattern="ATGCGATCGATCG",
            mode=SequenceLocalizationMode.EXACT_MATCH,
        )
        vrc = VerifiableRewardContract(
            task_id="vrc_proof_test",
            domain=RLVRTaskDomain.SEQUENCE_LOCALIZATION,
            ground_truth_reference="6-18:+",
            reward_success=1.0,
            localization_contract=loc,
        )
        contract = FineDNAContract(
            contract_id="rlvr_eval_01",
            task_type=FineDNATaskType.SEQUENCE_LOCALIZATION,
            prompt="Localize query pattern",
            verifiable_reward_contract=vrc,
        )

        env = FineDNARLVREnvironment()
        trace = env.evaluate_and_correct(contract, max_iterations=2)

        assert trace.successful is True
        assert trace.reward_score == 1.0
        assert len(trace.verification_proof) == 64  # SHA-256 hex string
        assert "verifiable_dna:" in trace.final_gfl_code

    def test_rlvr_code_fence_stripping(self) -> None:
        fenced_code = "```gfl\nverifiable_dna:\n  task_id: fenced_task\n```"
        cleaned = FineDNARLVREnvironment._extract_clean_gfl(fenced_code)
        assert cleaned == "verifiable_dna:\n  task_id: fenced_task"

    def test_rlvr_self_correction_recovers_from_syntax_error(self) -> None:
        contract = FineDNAContract(
            contract_id="correction_test",
            task_type=FineDNATaskType.SEQUENCE_LOCALIZATION,
            prompt="Localize motif",
            generated_gfl="INVALID: : : SYNTAX {[[",
        )
        env = FineDNARLVREnvironment()
        trace = env.evaluate_and_correct(contract, max_iterations=3)
        assert trace.iteration_count >= 2
        assert len(trace.error_history) >= 1
        assert trace.successful is True
        assert trace.reward_score == 1.0


class TestFineDNARLVRExporter:
    """Tests for exporting FineDNA-compatible 100k RL task datasets."""

    def test_export_dataset_jsonl(self, tmp_path: Path) -> None:
        c1 = FineDNAContract(
            contract_id="task_001",
            task_type=FineDNATaskType.SEQUENCE_LOCALIZATION,
            prompt="Localize motif in exon 2",
            target_locus="chr6:41126000-41131000",
        )
        c2 = FineDNAContract(
            contract_id="task_002",
            task_type=FineDNATaskType.CRISPR_CIRCUIT_DESIGN,
            prompt="Synthesize prime editing guide",
        )

        out_file = tmp_path / "finedna_rlvr_benchmark.jsonl"
        count = FineDNARLVRExporter.export_dataset([c1, c2], str(out_file))

        assert count == 2
        assert out_file.exists()

        with open(out_file, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 2

        rec1 = json.loads(lines[0])
        assert rec1["task_id"] == "task_001"
        assert rec1["environment_evaluator"] == "gfl_deterministic_reward_oracle"
        assert rec1["air_gapped_requirement"] is True


class TestFineDNASemanticValidation:
    """Tests for EnhancedSemanticValidator integration with FineDNA contracts."""

    def test_validate_official_exemplar_file(self) -> None:
        exemplar_path = Path(__file__).parents[2] / "examples" / "features" / "finedna_sovereign_circuit_synthesis.gfl"
        assert exemplar_path.exists(), f"Exemplar {exemplar_path} missing"

        with open(exemplar_path, encoding="utf-8") as f:
            content = f.read()

        ast_data = yaml.safe_load(content)
        validator = EnhancedSemanticValidator()
        result = validator.validate_ast(ast_data)
        assert result.is_valid, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_missing_contract_id(self) -> None:
        invalid_block = {
            "finedna": {
                "task_type": "crispr_circuit_design",
                "prompt": "Test prompt",
            }
        }
        validator = EnhancedSemanticValidator()
        res = validator.validate_ast(invalid_block)
        assert not res.is_valid
        assert any("contract_id" in e.message for e in res.errors)

    def test_validator_rejects_invalid_task_type(self) -> None:
        invalid_block = {
            "finedna": {
                "contract_id": "test_id",
                "task_type": "invalid_magic_task",
                "prompt": "Test prompt",
            }
        }
        validator = EnhancedSemanticValidator()
        res = validator.validate_ast(invalid_block)
        assert not res.is_valid
        assert any("Invalid task_type" in e.message for e in res.errors)

    def test_validator_rejects_external_url_when_air_gapped(self) -> None:
        invalid_block = {
            "finedna": {
                "contract_id": "leak_test",
                "task_type": "gfl_code_synthesis",
                "prompt": "Private patient sequence analysis",
                "inference_config": {
                    "endpoint_url": "https://api.openai.com/v1",
                    "air_gapped": True,
                },
            }
        }
        validator = EnhancedSemanticValidator()
        res = validator.validate_ast(invalid_block)
        assert not res.is_valid
        assert any("Air-gapped sovereign inference violation" in e.message for e in res.errors)
        assert any(e.code == ErrorCodes.SECURITY_UNSAFE_OPERATION for e in res.errors)
