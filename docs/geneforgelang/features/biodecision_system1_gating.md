# Feature Specification: BioDecision-4B & System 1 Fast Calibrated Gating

## Overview
This specification details the formal integration of **BioDecision-4B** (single forward pass calibrated decision engine based on Qwen3.5-4B + LoRA Tev1 recipe) into GeneForgeLang (GFL).

Traditional Large Language Model calls for scientific gating suffer from two fundamental problems:
1. **High Latency and Token Overhead**: Generating verbal reasoning traces takes seconds per candidate, creating severe bottlenecks in high-throughput biological screening.
2. **Uncalibrated Heuristics**: Autoregressive verbal outputs do not provide rigorous mathematical probabilities, making it impossible to define deterministic gating thresholds.

BioDecision-4B resolves this by operating as a biological **System 1 reflex**:
- Reads query, evidence, and allowed answer candidates in a **single forward pass** (~40 ms).
- Outputs mathematically calibrated probabilities with Expected Calibration Error $ECE \le 0.08$ (empirically $0.068$ on HaluBench/PubMedQA).
- Enables deterministic branching and escalation.

---

## GFL Declarative Grammar

GFL introduces the `decision` block as a first-class language structure:

```yaml
decision:
  task_id: "ClinicalTrialEndpointGating"
  strategy: "system_1_calibrated"
  engine: "biodecision-4b"
  latency_budget_ms: 50.0
  calibration_error_max: 0.08
  allowed_space:
    - "SUPPORTED"
    - "CONTRADICTED"
    - "INSUFFICIENT_EVIDENCE"
  threshold: 0.85
  mode: "choice"
  fallback_strategy: "ESCALATE_TO_SYSTEM2"
```

### Parameters
- `task_id` (string): Unique identifier for the decision contract.
- `strategy` (`DecisionStrategy`): Gating strategy (`SYSTEM_1_CALIBRATED`, `SYSTEM_1_FAST`, `BIODECISION_SINGLE_FORWARD`).
- `engine` (string): Underlying engine, defaults to `"biodecision-4b"`.
- `latency_budget_ms` (float): Maximum latency budget in milliseconds (default: `50.0`).
- `calibration_error_max` (float): Upper bound on acceptable Empirical Calibration Error (default: `0.08`).
- `allowed_space` (list of strings): Discrete allowable response categories.
- `threshold` (float): Minimum confidence required to accept the top prediction (default: `0.85`).
- `mode` (`DecisionMode`): Operating mode (`choice`, `binary`, or `score`).
- `fallback_strategy` (string): Escalation path when confidence falls below `threshold` or outcome is ambiguous (default: `"ESCALATE_TO_SYSTEM2"`).

---

## Python API & Types

Available from `geneforgelang.core.gftypes`:
- `DecisionContract`: Dataclass holding the contract configuration with `.is_within_budget(ms)` and `.passes_calibration(ece)` methods.
- `DecisionOutcome`: Dataclass containing the outcome (`selected_option_id`, `confidence`, `is_ambiguous`, `ece`, `latency_ms`) with `.passes_threshold(tau)`.
- `DecisionStrategy`: Enumeration of decision strategies.
- `DecisionMode`: Enumeration of decision modes (`CHOICE`, `BINARY`, `SCORE`).

Plugin implementation available from `geneforgelang.plugins.biodecision_plugin`:
- `BioDecisionPlugin`: Plugin conforming to `BaseGFLPlugin` implementing single forward pass inference and temperature scaling.
- `compute_ece(confidences, accuracies, num_bins)`: Expected Calibration Error computation.
- `softmax(logits, temperature)`: Temperature-scaled softmax.

---

## Testing & Verification
All contracts, mathematical calibration routines, plugin inference paths, and semantic validations are tested under:
`tests/unit/test_biodecision_system1_gating.py`
