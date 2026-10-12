"""Unit tests for BioDecision-4B System 1 calibrated gating in GeneForgeLang.
=============================================================================
Tests cover:
- DecisionContract, DecisionOutcome, DecisionStrategy, DecisionMode types
- GFLAST integration (to_dict and from_dict with decision blocks)
- Softmax temperature scaling and ECE calculation mathematical correctness
- BioDecisionPlugin single forward pass execution, latency gating, and calibration
- EnhancedSemanticValidator support for decision blocks and biodecision-4b tools
"""

import math

import pytest
from geneforgelang.core.gftypes import (
    GFLAST,
    DecisionContract,
    DecisionMode,
    DecisionOption,
    DecisionOutcome,
    DecisionStrategy,
)
from geneforgelang.core.validator import EnhancedSemanticValidator
from geneforgelang.plugins.biodecision_plugin import (
    BioDecisionPlugin,
    compute_ece,
    softmax,
)


class TestBioDecisionTypesAndContracts:
    """Test data structures, contracts, and GFLAST serialization."""

    def test_decision_strategy_and_mode_enums(self):
        """Verify enum values for strategies and modes."""
        assert DecisionStrategy.SYSTEM_1_CALIBRATED.value == "system_1_calibrated"
        assert DecisionStrategy.SYSTEM_1_FAST.value == "system_1_fast"
        assert DecisionStrategy.BIODECISION_SINGLE_FORWARD.value == "biodecision_single_forward"

        assert DecisionMode.CHOICE.value == "choice"
        assert DecisionMode.BINARY.value == "binary"
        assert DecisionMode.SCORE.value == "score"

    def test_decision_contract_defaults_and_synchronization(self):
        """Verify DecisionContract __post_init__ harmonizes options and thresholds."""
        contract = DecisionContract(
            task_id="endpoint_gating",
            allowed_space=["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"],
            threshold=0.88,
        )

        # allowed_space and allowed_options should be synced
        assert contract.allowed_options == ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
        assert contract.allowed_space == ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
        assert contract.confidence_threshold == 0.88
        assert contract.threshold == 0.88
        assert contract.engine == "biodecision-4b"
        assert contract.latency_budget_ms == 50.0
        assert contract.calibration_error_max == 0.08
        assert contract.strategy == DecisionStrategy.SYSTEM_1_CALIBRATED
        assert contract.mode == DecisionMode.CHOICE

        # Test reverse sync: allowed_options provided, allowed_space empty
        contract2 = DecisionContract(
            task_id="legacy_task",
            allowed_options=["PASS", "FAIL"],
            confidence_threshold=0.90,
        )
        assert contract2.allowed_space == ["PASS", "FAIL"]
        assert contract2.threshold == 0.90

    def test_decision_contract_budget_and_calibration_methods(self):
        """Verify budget and calibration error checking methods."""
        contract = DecisionContract(
            task_id="trial_gate",
            allowed_space=["YES", "NO"],
            latency_budget_ms=50.0,
            calibration_error_max=0.08,
        )

        assert contract.is_within_budget(42.5) is True
        assert contract.is_within_budget(50.0) is True
        assert contract.is_within_budget(55.2) is False

        assert contract.passes_calibration(0.068) is True
        assert contract.passes_calibration(0.08) is True
        assert contract.passes_calibration(0.095) is False

    def test_decision_outcome_threshold_and_ambiguity(self):
        """Verify DecisionOutcome passes_threshold logic."""
        opt1 = DecisionOption(option_id="SUPPORTED", label="SUPPORTED", calibrated_probability=0.89)
        opt2 = DecisionOption(option_id="CONTRADICTED", label="CONTRADICTED", calibrated_probability=0.11)

        outcome = DecisionOutcome(
            selected_option_id="SUPPORTED",
            confidence=0.89,
            is_ambiguous=False,
            options_evaluated=[opt1, opt2],
            latency_ms=41.2,
            ece=0.068,
            mode="choice",
        )

        assert outcome.passes_threshold(0.85) is True
        assert outcome.passes_threshold(0.90) is False

        # Ambiguous outcome should fail threshold
        outcome_ambiguous = DecisionOutcome(
            selected_option_id="SUPPORTED",
            confidence=0.89,
            is_ambiguous=True,
            options_evaluated=[opt1, opt2],
        )
        assert outcome_ambiguous.passes_threshold(0.85) is False

    def test_gflast_roundtrip_with_decision_block(self):
        """Verify GFLAST from_dict and to_dict preserve decision blocks."""
        ast_dict = {
            "decision": {
                "task_id": "ClinicalTrialEndpointGating",
                "strategy": "system_1_calibrated",
                "engine": "biodecision-4b",
                "latency_budget_ms": 50.0,
                "calibration_error_max": 0.08,
                "allowed_space": ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"],
                "threshold": 0.85,
                "mode": "choice",
            }
        }

        ast = GFLAST.from_dict(ast_dict)
        assert ast.decision is not None
        assert isinstance(ast.decision, DecisionContract)
        assert ast.decision.task_id == "ClinicalTrialEndpointGating"
        assert ast.decision.engine == "biodecision-4b"
        assert ast.decision.threshold == 0.85
        assert ast.decision.allowed_space == ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]

        serialized = ast.to_dict()
        assert "decision" in serialized
        assert serialized["decision"]["engine"] == "biodecision-4b"
        assert serialized["decision"]["threshold"] == 0.85


class TestBioDecisionMathematics:
    """Test softmax temperature scaling and ECE computation."""

    def test_softmax_properties(self):
        """Verify softmax sums to 1.0 and responds to temperature."""
        logits = [2.0, 1.0, 0.1]
        probs = softmax(logits, temperature=1.0)
        assert math.isclose(sum(probs), 1.0, rel_tol=1e-6)
        assert probs[0] > probs[1] > probs[2]

        # Higher temperature smooths distribution
        probs_high_t = softmax(logits, temperature=10.0)
        assert probs_high_t[0] < probs[0]

        # Lower temperature sharpens distribution
        probs_low_t = softmax(logits, temperature=0.2)
        assert probs_low_t[0] > probs[0]

        # Edge cases
        assert softmax([]) == []
        with pytest.raises(ValueError):
            softmax(logits, temperature=-1.0)

    def test_compute_ece(self):
        """Verify Expected Calibration Error calculation."""
        # Perfectly calibrated example
        confidences = [0.8] * 10
        accuracies = [True] * 8 + [False] * 2  # 80% accuracy matching 80% confidence
        ece = compute_ece(confidences, accuracies, num_bins=5)
        assert math.isclose(ece, 0.0, abs_tol=1e-5)

        # Under-confident example
        accuracies_perfect = [True] * 10
        ece_miscalibrated = compute_ece(confidences, accuracies_perfect, num_bins=5)
        assert ece_miscalibrated > 0.15

        # Empty handling
        assert compute_ece([], []) == 0.0

        with pytest.raises(ValueError):
            compute_ece([0.5], [True, False])


class TestBioDecisionPluginExecution:
    """Test BioDecisionPlugin inference, gating, and process methods."""

    def test_plugin_metadata(self):
        """Verify plugin metadata conforms to GFL standards."""
        plugin = BioDecisionPlugin()
        assert plugin.name == "biodecision-4b"
        assert plugin.version == "1.0.0"

    def test_single_forward_pass_evaluation(self):
        """Test evaluation of ClinicalTrialEndpointGating contract."""
        plugin = BioDecisionPlugin()
        contract = DecisionContract(
            task_id="ClinicalTrialEndpointGating",
            strategy=DecisionStrategy.SYSTEM_1_CALIBRATED,
            engine="biodecision-4b",
            latency_budget_ms=50.0,
            calibration_error_max=0.08,
            allowed_space=["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"],
            threshold=0.85,
        )

        outcome = plugin.evaluate_decision(
            contract=contract,
            query="Primary endpoint PFS achieved with hazard ratio 0.65",
            evidence="In randomized Phase 3 trial, median PFS was significantly prolonged (HR 0.65, p=0.001)",
        )

        assert outcome.selected_option_id in contract.allowed_space
        assert 0.0 <= outcome.confidence <= 1.0
        assert len(outcome.options_evaluated) == 3
        assert outcome.ece == 0.068
        assert contract.passes_calibration(outcome.ece) is True
        assert contract.is_within_budget(outcome.latency_ms) is True

    def test_custom_logits_and_ambiguity_gating(self):
        """Test ambiguity detection when logits are tied or margins are small."""
        plugin = BioDecisionPlugin()
        contract = DecisionContract(
            task_id="binary_safety_gate",
            allowed_space=["PASS", "FAIL"],
            threshold=0.85,
        )

        # Clear winner: large margin
        clear_outcome = plugin.evaluate_decision(
            contract=contract,
            custom_logits=[4.0, 0.0],
            min_margin=0.10,
        )
        assert clear_outcome.selected_option_id == "PASS"
        assert clear_outcome.is_ambiguous is False
        assert clear_outcome.passes_threshold(0.85) is True

        # Tied logits: margin is 0.0 -> ambiguous
        tied_outcome = plugin.evaluate_decision(
            contract=contract,
            custom_logits=[2.0, 2.0],
            min_margin=0.10,
        )
        assert tied_outcome.is_ambiguous is True
        assert tied_outcome.passes_threshold(0.85) is False

    def test_plugin_process_dictionary_interface(self):
        """Test plugin process() with structured dictionary payload."""
        plugin = BioDecisionPlugin()
        payload = {
            "query": "Does candidate inhibit CDK4/6?",
            "evidence": "Biochemical IC50 is 4.2 nM against CDK4 and 1.8 nM against CDK6",
            "decision": {
                "task_id": "target_inhibition_gate",
                "allowed_space": ["SUPPORTED", "CONTRADICTED"],
                "threshold": 0.85,
                "latency_budget_ms": 50.0,
                "calibration_error_max": 0.08,
            },
        }

        res = plugin.process(payload)
        assert res["success"] is True
        assert "outcome" in res
        assert res["outcome"]["selected_option_id"] in ["SUPPORTED", "CONTRADICTED"]
        assert res["is_within_budget"] is True
        assert res["passes_calibration"] is True


class TestSemanticValidationWithDecisionBlock:
    """Test AST validation of decision blocks and biodecision-4b tools."""

    def test_validate_valid_decision_block(self):
        """Verify validator accepts valid decision block."""
        validator = EnhancedSemanticValidator()
        ast = {
            "decision": {
                "strategy": "SYSTEM_1_CALIBRATED",
                "engine": "biodecision-4b",
                "latency_budget_ms": 50,
                "calibration_error_max": 0.08,
                "allowed_space": ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"],
                "threshold": 0.85,
            }
        }
        result = validator.validate_ast(ast)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_decision_with_contract_instance(self):
        """Verify validator accepts DecisionContract object directly."""
        validator = EnhancedSemanticValidator()
        contract = DecisionContract(
            task_id="endpoint_gate",
            strategy=DecisionStrategy.BIODECISION_SINGLE_FORWARD,
            allowed_space=["YES", "NO"],
            threshold=0.80,
        )
        result = validator.validate_ast({"decision": contract})
        assert result.is_valid is True

    def test_validate_invalid_decision_fields(self):
        """Verify validator flags invalid decision parameters."""
        validator = EnhancedSemanticValidator()

        # Empty allowed space
        bad_ast_1 = {
            "decision": {
                "allowed_space": [],
                "latency_budget_ms": 50,
            }
        }
        res_1 = validator.validate_ast(bad_ast_1)
        assert res_1.is_valid is False
        assert any("allowed_space" in e.message for e in res_1.errors)

        # Negative latency budget
        bad_ast_2 = {
            "decision": {
                "allowed_space": ["A", "B"],
                "latency_budget_ms": -10,
            }
        }
        res_2 = validator.validate_ast(bad_ast_2)
        assert res_2.is_valid is False
        assert any("latency_budget_ms" in e.message for e in res_2.errors)

        # Invalid threshold > 1.0
        bad_ast_3 = {
            "decision": {
                "allowed_space": ["A", "B"],
                "threshold": 1.5,
            }
        }
        res_3 = validator.validate_ast(bad_ast_3)
        assert res_3.is_valid is False
        assert any("threshold" in e.message for e in res_3.errors)

    def test_validate_biodecision_tool_in_experiment(self):
        """Verify biodecision-4b is a recognized tool in experiment block."""
        validator = EnhancedSemanticValidator()
        ast = {
            "experiment": {
                "tool": "biodecision-4b",
                "type": "analysis",
                "params": {
                    "sequence": "ATCG",
                },
            }
        }
        result = validator.validate_ast(ast)
        # Should not raise unknown tool warning
        assert not any("Unknown tool 'biodecision-4b'" in w.message for w in result.warnings)
