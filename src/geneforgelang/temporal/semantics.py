from __future__ import annotations

import re

from geneforgelang.temporal.ir import (
    ActivationProfile,
    CausalTimingConstraint,
    DissociationMode,
    DwellRegime,
    ReboundExpectation,
    TemporalPerturbationIR,
)


def parse_temporal_program(source: str) -> TemporalPerturbationIR:
    entity_match = re.search(r"^\s*entity\s+([A-Za-z_][\w]*)", source, re.MULTILINE)
    perturbation_match = re.search(r"^\s*perturbation\s+([A-Za-z_][\w]*)\s*:", source, re.MULTILINE)
    if entity_match is None or perturbation_match is None:
        raise ValueError("temporal program requires entity and perturbation declarations")

    target = entity_match.group(1)
    perturbation_type = perturbation_match.group(1)
    activation_profile = ActivationProfile.GATED if re.search(r"\bactivate\b", source) else ActivationProfile.IMMEDIATE
    dwell_regime = _extract_call_value(source, "dwell", default=DwellRegime.TRANSIENT)
    dissociation_mode = _extract_call_value(source, "dissociate", default=DissociationMode.PASSIVE)
    rebound_expectation = _extract_call_value(source, "rebound", default=ReboundExpectation.UNKNOWN)
    constraints = _extract_gate_constraints(source)
    return TemporalPerturbationIR(
        perturbation_type=perturbation_type,
        target=target,
        activation_profile=activation_profile,
        dwell_regime=dwell_regime,
        dissociation_mode=dissociation_mode,
        rebound_expectation=rebound_expectation,
        causal_timing_constraints=constraints,
    )


def _extract_call_value(source: str, operator: str, default: str) -> str:
    match = re.search(rf"\b{operator}\(([^)]+)\)", source)
    if match is None:
        return default
    return match.group(1).strip().strip("\"'")


def _extract_gate_constraints(source: str) -> tuple[CausalTimingConstraint, ...]:
    constraints: list[CausalTimingConstraint] = []
    for match in re.finditer(r"\bgate\(([^,)]+),\s*temporal_constraint=([^)]+)\)", source):
        signal = match.group(1).strip().strip("\"'")
        relation = match.group(2).strip().strip("\"'")
        constraints.append(CausalTimingConstraint(relation=relation, during=signal))
    return tuple(constraints)
