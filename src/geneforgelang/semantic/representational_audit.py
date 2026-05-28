from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from geneforgelang.semantic.adversarial_generator import (
    OperationTrace,
    RepresentationalAdversarialGenerator,
    flatten_trace_states,
)
from geneforgelang.semantic.lattice import EpistemicState
from geneforgelang.semantic.semantic_equivalence import canonical_key, semantic_equivalent
from geneforgelang.semantic.state_space import SemanticStateSpaceAudit


@dataclass(frozen=True)
class RepresentationalAuditReport:
    rsi: float
    fpcr: float
    illegal_collapses: list[dict[str, Any]]
    monotonicity_breaches: list[dict[str, Any]]
    canonicalization_failures: list[dict[str, Any]]
    freeze_decision: str


def run_representational_audit(
    config_path: str | Path,
    output_path: str | Path = "representational_audit_report.json",
) -> RepresentationalAuditReport:
    config = _load_config(Path(config_path))
    generator = RepresentationalAdversarialGenerator(seed=int(config["seed"]))

    tier_a_states = generator.tier_a_states(bool(config.get("tier_a", {}).get("enabled", True)))
    tier_b = generator.tier_b_operation_traces(
        sequence_lengths=tuple(config.get("tier_b", {}).get("sequence_lengths", ())),
        samples=int(config.get("tier_b", {}).get("samples", 0)),
    )
    tier_c = generator.tier_c_mutations(int(config.get("tier_c", {}).get("mutations", 0)))

    observed_states = tuple(tier_a_states) + flatten_trace_states(tier_b) + flatten_trace_states(tier_c)
    traces = tuple(tier_b) + tuple(tier_c)

    canonicalization_failures = _canonicalization_failures(observed_states)
    illegal_collapses = _illegal_collapses(observed_states)
    monotonicity_breaches = _monotonicity_breaches(traces)

    total_observations = max(1, len(observed_states))
    rsi = 1.0 - (len(illegal_collapses) / total_observations)
    fpcr = len(illegal_collapses) / max(1, len(_collision_groups(observed_states)))

    thresholds = config.get("thresholds", {})
    freeze_decision = (
        "PASS"
        if rsi >= float(thresholds.get("min_rsi", 1.0))
        and len(illegal_collapses) <= int(thresholds.get("max_illegal_collapses", 0))
        and not monotonicity_breaches
        and not canonicalization_failures
        else "FAIL"
    )

    report = RepresentationalAuditReport(
        rsi=rsi,
        fpcr=fpcr,
        illegal_collapses=illegal_collapses,
        monotonicity_breaches=monotonicity_breaches,
        canonicalization_failures=canonicalization_failures,
        freeze_decision=freeze_decision,
    )
    Path(output_path).write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return report


def _load_config(path: Path) -> Mapping[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("representational audit config must be a JSON object")
    return data


def _canonicalization_failures(states: tuple[EpistemicState, ...]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for state in states:
        key = canonical_key(state)
        if len(key) != 5 or any(not item for item in key):
            failures.append({"state": _state_dict(state), "canonical_key": list(key)})
    return failures


def _illegal_collapses(states: tuple[EpistemicState, ...]) -> list[dict[str, Any]]:
    collapses: list[dict[str, Any]] = []
    groups = _collision_groups(states)
    for key, grouped_states in groups.items():
        unique = tuple(dict.fromkeys(grouped_states))
        for index, left in enumerate(unique):
            for right in unique[index + 1 :]:
                if not semantic_equivalent(left, right):
                    collapses.append(
                        {
                            "canonical_key": list(key),
                            "left": _state_dict(left),
                            "right": _state_dict(right),
                        }
                    )
    return collapses


def _collision_groups(states: tuple[EpistemicState, ...]) -> dict[tuple[str, str, str, str, str], list[EpistemicState]]:
    groups: dict[tuple[str, str, str, str, str], list[EpistemicState]] = {}
    for state in states:
        groups.setdefault(canonical_key(state), []).append(state)
    return {key: value for key, value in groups.items() if len(value) > 1}


def _monotonicity_breaches(traces: tuple[OperationTrace, ...]) -> list[dict[str, Any]]:
    breaches: list[dict[str, Any]] = []
    valid_states = SemanticStateSpaceAudit().valid_states
    for trace in traces:
        if trace.operation.endswith("meet"):
            _append_meet_breach(trace, breaches)
        elif trace.operation.endswith("join"):
            _append_join_breach(trace, breaches)

        if trace.result not in valid_states and all(operand in valid_states for operand in trace.operands):
            breaches.append(
                {
                    "operation": trace.operation,
                    "kind": "valid_operands_to_invalid_result",
                    "result": _state_dict(trace.result),
                }
            )
    return breaches


def _append_meet_breach(trace: OperationTrace, breaches: list[dict[str, Any]]) -> None:
    result = trace.result
    for operand in trace.operands:
        if result.join(operand) != operand:
            breaches.append(
                {
                    "operation": trace.operation,
                    "kind": "meet_result_exceeds_operand",
                    "operand": _state_dict(operand),
                    "result": _state_dict(result),
                }
            )


def _append_join_breach(trace: OperationTrace, breaches: list[dict[str, Any]]) -> None:
    result = trace.result
    for operand in trace.operands:
        if result.meet(operand) != operand:
            breaches.append(
                {
                    "operation": trace.operation,
                    "kind": "join_result_below_operand",
                    "operand": _state_dict(operand),
                    "result": _state_dict(result),
                }
            )


def _state_dict(state: EpistemicState) -> dict[str, str]:
    return {
        "truth_support": state.truth_support.name,
        "temporal_stability": state.temporal_stability.name,
        "observational_resolution": state.observational_resolution.name,
        "ecological_scope": state.ecological_scope.name,
        "contradiction_load": state.contradiction_load.name,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run Phase 5.6 representational stress audit.")
    parser.add_argument("config", help="Path to generative audit_config.json.")
    parser.add_argument(
        "--output",
        default="representational_audit_report.json",
        help="Path for representational_audit_report.json.",
    )
    args = parser.parse_args()
    report = run_representational_audit(args.config, args.output)
    return 0 if report.freeze_decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
