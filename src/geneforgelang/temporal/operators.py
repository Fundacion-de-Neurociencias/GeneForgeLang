from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from geneforgelang.temporal.ir import (
    ActivationProfile,
    CausalTimingConstraint,
    DissociationMode,
    DwellRegime,
    ReboundExpectation,
    TemporalPerturbationIR,
    TemporalUncertainty,
)


def activation(entity: str, profile: str = ActivationProfile.IMMEDIATE, **parameters: Any) -> TemporalPerturbationIR:
    return activate(entity, profile=profile, **parameters)


def activate(entity: str, profile: str = ActivationProfile.IMMEDIATE, **parameters: Any) -> TemporalPerturbationIR:
    return TemporalPerturbationIR(
        perturbation_type="activation",
        target=entity,
        activation_profile=profile,
        dwell_regime=parameters.pop("dwell_regime", DwellRegime.TRANSIENT),
        dissociation_mode=parameters.pop("dissociation_mode", DissociationMode.PASSIVE),
        rebound_expectation=parameters.pop("rebound_expectation", ReboundExpectation.UNKNOWN),
        parameters=parameters,
    )


def dwell(entity: str, duration: str = DwellRegime.TRANSIENT, **parameters: Any) -> TemporalPerturbationIR:
    return TemporalPerturbationIR(
        perturbation_type="dwell",
        target=entity,
        activation_profile=parameters.pop("activation_profile", ActivationProfile.GATED),
        dwell_regime=duration,
        dissociation_mode=parameters.pop("dissociation_mode", DissociationMode.PASSIVE),
        rebound_expectation=parameters.pop("rebound_expectation", ReboundExpectation.UNKNOWN),
        parameters=parameters,
    )


def dissociate(entity: str, mode: str = DissociationMode.FACILITATED, **parameters: Any) -> TemporalPerturbationIR:
    return TemporalPerturbationIR(
        perturbation_type="dissociation",
        target=entity,
        activation_profile=parameters.pop("activation_profile", ActivationProfile.GATED),
        dwell_regime=parameters.pop("dwell_regime", DwellRegime.TRANSIENT),
        dissociation_mode=mode,
        rebound_expectation=parameters.pop("rebound_expectation", ReboundExpectation.UNKNOWN),
        parameters=parameters,
    )


def pulse(entity: str, cadence: str, **parameters: Any) -> TemporalPerturbationIR:
    parameters = {**parameters, "cadence": cadence}
    return TemporalPerturbationIR(
        perturbation_type="pulse",
        target=entity,
        activation_profile=ActivationProfile.PULSED,
        dwell_regime=parameters.pop("dwell_regime", DwellRegime.OSCILLATORY),
        dissociation_mode=parameters.pop("dissociation_mode", DissociationMode.PASSIVE),
        rebound_expectation=parameters.pop("rebound_expectation", ReboundExpectation.UNKNOWN),
        parameters=parameters,
    )


def gate(signal: str, temporal_constraint: CausalTimingConstraint | str, **parameters: Any) -> TemporalPerturbationIR:
    constraint = (
        temporal_constraint
        if isinstance(temporal_constraint, CausalTimingConstraint)
        else CausalTimingConstraint(relation=str(temporal_constraint), during=signal)
    )
    return TemporalPerturbationIR(
        perturbation_type="gate",
        target=signal,
        activation_profile=ActivationProfile.GATED,
        dwell_regime=parameters.pop("dwell_regime", DwellRegime.TRANSIENT),
        dissociation_mode=parameters.pop("dissociation_mode", DissociationMode.PASSIVE),
        rebound_expectation=parameters.pop("rebound_expectation", ReboundExpectation.UNKNOWN),
        causal_timing_constraints=(constraint,),
        parameters=parameters,
    )


def facilitated_dissociation(
    entity: str,
    competitive_displacement: bool = False,
    timed_release: str | None = None,
    decay_modulation: str | None = None,
    switchable_occupancy: bool = False,
) -> TemporalPerturbationIR:
    return TemporalPerturbationIR(
        perturbation_type="facilitated_dissociation",
        target=entity,
        activation_profile=ActivationProfile.GATED,
        dwell_regime=DwellRegime.TRANSIENT,
        dissociation_mode=DissociationMode.FACILITATED,
        rebound_expectation=ReboundExpectation.UNKNOWN,
        temporal_uncertainty=TemporalUncertainty(dissociation=0.2, rebound=0.2),
        parameters={
            "competitive_displacement": competitive_displacement,
            "timed_release": timed_release,
            "decay_modulation": decay_modulation,
            "switchable_occupancy": switchable_occupancy,
        },
    )


@dataclass(frozen=True)
class TemporalPerturbationComposition:
    operator: str
    perturbations: tuple[TemporalPerturbationIR, ...]
    delayed_by: str | None = None
    coupling: str | None = None
    temporal_stability: float = 1.0
    antagonistic_pairs: tuple[tuple[str, str], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.perturbations:
            raise ValueError("temporal composition requires at least one perturbation")
        if not 0 <= self.temporal_stability <= 1:
            raise ValueError("temporal_stability must be in [0, 1]")


def sequential(*perturbations: TemporalPerturbationIR) -> TemporalPerturbationComposition:
    return TemporalPerturbationComposition("sequential", tuple(perturbations), temporal_stability=0.9)


def concurrent(*perturbations: TemporalPerturbationIR) -> TemporalPerturbationComposition:
    return TemporalPerturbationComposition("concurrent", tuple(perturbations), temporal_stability=0.75)


def delayed_activation(perturbation: TemporalPerturbationIR, delayed_by: str) -> TemporalPerturbationComposition:
    return TemporalPerturbationComposition(
        "delayed_activation",
        (perturbation,),
        delayed_by=delayed_by,
        temporal_stability=0.8,
    )


def rebound_coupling(first: TemporalPerturbationIR, second: TemporalPerturbationIR) -> TemporalPerturbationComposition:
    return TemporalPerturbationComposition(
        "rebound_coupling",
        (first, second),
        coupling="rebound",
        temporal_stability=0.7,
    )
