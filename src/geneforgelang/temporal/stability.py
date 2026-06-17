from __future__ import annotations

from dataclasses import dataclass, field

from geneforgelang.temporal.constraints import TemporalConstraintEngine
from geneforgelang.temporal.ir import (
    ActivationProfile,
    DissociationMode,
    DwellRegime,
    ReboundExpectation,
    TemporalPerturbationIR,
)
from geneforgelang.temporal.operators import TemporalPerturbationComposition


@dataclass(frozen=True)
class TemporalStressProfile:
    name: str
    activation_shift: str | None = None
    dwell_shift: str | None = None
    dissociation_shift: str | None = None
    rebound_shift: str | None = None
    severity: float = 0.1

    def __post_init__(self) -> None:
        if not 0 <= self.severity <= 1:
            raise ValueError("stress profile severity must be in [0, 1]")


@dataclass(frozen=True)
class TemporalStabilityInvariant:
    name: str
    field: str
    expected: str


@dataclass(frozen=True)
class TemporalStressOutcome:
    profile: TemporalStressProfile
    stable: bool
    sensitivity: float
    violations: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemporalStabilityReport:
    stable: bool
    stability_score: float
    outcomes: tuple[TemporalStressOutcome, ...]
    invariant_failures: tuple[str, ...] = ()

    @property
    def max_sensitivity(self) -> float:
        if not self.outcomes:
            return 0.0
        return max(outcome.sensitivity for outcome in self.outcomes)


class TemporalStabilityTester:
    def __init__(self, constraint_engine: TemporalConstraintEngine | None = None):
        self.constraint_engine = constraint_engine or TemporalConstraintEngine()

    def test_ir(
        self,
        temporal_ir: TemporalPerturbationIR,
        profiles: tuple[TemporalStressProfile, ...] | None = None,
        invariants: tuple[TemporalStabilityInvariant, ...] = (),
    ) -> TemporalStabilityReport:
        stress_profiles = profiles or default_stress_profiles()
        outcomes = tuple(self._evaluate_profile(temporal_ir, profile, invariants) for profile in stress_profiles)
        invariant_failures = tuple(
            failure for outcome in outcomes for failure in outcome.violations if failure.startswith("invariant:")
        )
        score = self._score(outcomes)
        return TemporalStabilityReport(
            stable=score >= self.constraint_engine.instability_threshold and not invariant_failures,
            stability_score=score,
            outcomes=outcomes,
            invariant_failures=invariant_failures,
        )

    def test_composition(
        self,
        composition: TemporalPerturbationComposition,
        profiles: tuple[TemporalStressProfile, ...] | None = None,
        invariants: tuple[TemporalStabilityInvariant, ...] = (),
    ) -> TemporalStabilityReport:
        reports = tuple(
            self.test_ir(perturbation, profiles=profiles, invariants=invariants)
            for perturbation in composition.perturbations
        )
        outcomes = tuple(outcome for report in reports for outcome in report.outcomes)
        invariant_failures = tuple(failure for report in reports for failure in report.invariant_failures)
        composition_penalty = 1.0 - composition.temporal_stability
        score = max(0.0, self._score(outcomes) - composition_penalty)
        return TemporalStabilityReport(
            stable=score >= self.constraint_engine.instability_threshold and not invariant_failures,
            stability_score=score,
            outcomes=outcomes,
            invariant_failures=invariant_failures,
        )

    def _evaluate_profile(
        self,
        temporal_ir: TemporalPerturbationIR,
        profile: TemporalStressProfile,
        invariants: tuple[TemporalStabilityInvariant, ...],
    ) -> TemporalStressOutcome:
        stressed = TemporalPerturbationIR(
            perturbation_type=temporal_ir.perturbation_type,
            target=temporal_ir.target,
            activation_profile=profile.activation_shift or temporal_ir.activation_profile,
            dwell_regime=profile.dwell_shift or temporal_ir.dwell_regime,
            dissociation_mode=profile.dissociation_shift or temporal_ir.dissociation_mode,
            rebound_expectation=profile.rebound_shift or temporal_ir.rebound_expectation,
            temporal_uncertainty=temporal_ir.temporal_uncertainty,
            causal_timing_constraints=temporal_ir.causal_timing_constraints,
            parameters=temporal_ir.parameters,
        )
        validation = self.constraint_engine.validate_ir(stressed)
        invariant_failures = self._check_invariants(stressed, invariants)
        sensitivity = profile.severity + 0.2 * len(validation.violations) + 0.3 * len(invariant_failures)
        violations = tuple(item.code for item in validation.violations) + invariant_failures
        return TemporalStressOutcome(
            profile=profile,
            stable=validation.valid and not invariant_failures,
            sensitivity=min(1.0, sensitivity),
            violations=violations,
        )

    def _check_invariants(
        self,
        temporal_ir: TemporalPerturbationIR,
        invariants: tuple[TemporalStabilityInvariant, ...],
    ) -> tuple[str, ...]:
        failures: list[str] = []
        for invariant in invariants:
            actual = getattr(temporal_ir, invariant.field)
            if actual != invariant.expected:
                failures.append(f"invariant:{invariant.name}")
        return tuple(failures)

    @staticmethod
    def _score(outcomes: tuple[TemporalStressOutcome, ...]) -> float:
        if not outcomes:
            return 1.0
        mean_sensitivity = sum(outcome.sensitivity for outcome in outcomes) / len(outcomes)
        hard_failure_penalty = 0.2 * sum(1 for outcome in outcomes if not outcome.stable)
        return max(0.0, 1.0 - mean_sensitivity - hard_failure_penalty)


def default_stress_profiles() -> tuple[TemporalStressProfile, ...]:
    return (
        TemporalStressProfile(
            name="delayed_activation",
            activation_shift=ActivationProfile.DELAYED,
            severity=0.15,
        ),
        TemporalStressProfile(
            name="dwell_extension",
            dwell_shift=DwellRegime.SUSTAINED,
            severity=0.2,
        ),
        TemporalStressProfile(
            name="passive_release",
            dissociation_shift=DissociationMode.PASSIVE,
            severity=0.2,
        ),
        TemporalStressProfile(
            name="rebound_amplification",
            rebound_shift=ReboundExpectation.STRONG,
            severity=0.25,
        ),
    )
