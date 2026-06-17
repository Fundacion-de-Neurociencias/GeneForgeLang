from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Perturbation:
    kind: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PerturbationSet:
    perturbations: tuple[Perturbation, ...]
    composition_confidence: float = 1.0
    interaction_uncertainty: float = 0.0
    nonlinear_effect_risk: float = 0.0
    operator: str = "set"

    def __post_init__(self) -> None:
        for name in ("composition_confidence", "interaction_uncertainty", "nonlinear_effect_risk"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class CompositePerturbation:
    left: PerturbationSet
    right: PerturbationSet
    operator: str
    composition_confidence: float
    interaction_uncertainty: float
    nonlinear_effect_risk: float


class PerturbationAlgebra:
    def compose(self, left: PerturbationSet, right: PerturbationSet) -> PerturbationSet:
        return self._combine(left, right, "compose")

    def parallel(self, left: PerturbationSet, right: PerturbationSet) -> PerturbationSet:
        return self._combine(left, right, "parallel")

    def conditional(self, condition: str, perturbations: PerturbationSet) -> PerturbationSet:
        metadata = {"condition": condition}
        conditioned = tuple(
            Perturbation(p.kind, p.target, {**p.parameters, **metadata}) for p in perturbations.perturbations
        )
        return PerturbationSet(
            conditioned,
            composition_confidence=perturbations.composition_confidence * 0.95,
            interaction_uncertainty=min(1.0, perturbations.interaction_uncertainty + 0.05),
            nonlinear_effect_risk=perturbations.nonlinear_effect_risk,
            operator="conditional",
        )

    def repeat(self, perturbations: PerturbationSet, times: int) -> PerturbationSet:
        if times < 1:
            raise ValueError("times must be >= 1")
        repeated = perturbations.perturbations * times
        return PerturbationSet(
            repeated,
            composition_confidence=perturbations.composition_confidence**times,
            interaction_uncertainty=min(1.0, perturbations.interaction_uncertainty * times),
            nonlinear_effect_risk=min(1.0, perturbations.nonlinear_effect_risk * times),
            operator="repeat",
        )

    def _combine(self, left: PerturbationSet, right: PerturbationSet, operator: str) -> PerturbationSet:
        shared_targets = {p.target for p in left.perturbations} & {p.target for p in right.perturbations}
        risk_bump = 0.2 if shared_targets else 0.05
        uncertainty_bump = 0.15 if shared_targets else 0.05
        return PerturbationSet(
            left.perturbations + right.perturbations,
            composition_confidence=left.composition_confidence * right.composition_confidence,
            interaction_uncertainty=min(
                1.0,
                max(left.interaction_uncertainty, right.interaction_uncertainty) + uncertainty_bump,
            ),
            nonlinear_effect_risk=min(
                1.0,
                max(left.nonlinear_effect_risk, right.nonlinear_effect_risk) + risk_bump,
            ),
            operator=operator,
        )
