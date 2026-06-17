from __future__ import annotations

from dataclasses import dataclass, field

from geneforgelang.temporal.ir import DissociationMode, DwellRegime, TemporalPerturbationIR
from geneforgelang.temporal.operators import TemporalPerturbationComposition


@dataclass(frozen=True)
class TemporalConstraintViolation:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class TemporalValidationResult:
    valid: bool
    violations: tuple[TemporalConstraintViolation, ...] = ()


@dataclass
class TemporalConstraintEngine:
    instability_threshold: float = 0.5
    _known_dwell_regimes: set[str] = field(
        default_factory=lambda: {
            DwellRegime.BRIEF,
            DwellRegime.TRANSIENT,
            DwellRegime.SUSTAINED,
            DwellRegime.OSCILLATORY,
        }
    )
    _known_dissociation_modes: set[str] = field(
        default_factory=lambda: {
            DissociationMode.PASSIVE,
            DissociationMode.FACILITATED,
            DissociationMode.SWITCHABLE,
            DissociationMode.COMPETITIVE,
            DissociationMode.DECAY_MODULATED,
        }
    )

    def validate_ir(self, temporal_ir: TemporalPerturbationIR) -> TemporalValidationResult:
        violations: list[TemporalConstraintViolation] = []
        if temporal_ir.dwell_regime not in self._known_dwell_regimes:
            violations.append(
                TemporalConstraintViolation(
                    "impossible_temporal_topology",
                    f"Unknown dwell regime: {temporal_ir.dwell_regime}",
                )
            )
        if temporal_ir.dissociation_mode not in self._known_dissociation_modes:
            violations.append(
                TemporalConstraintViolation(
                    "incompatible_dissociation_semantics",
                    f"Unknown dissociation mode: {temporal_ir.dissociation_mode}",
                )
            )
        if (
            temporal_ir.dwell_regime == DwellRegime.BRIEF
            and temporal_ir.dissociation_mode == DissociationMode.PASSIVE
            and temporal_ir.rebound_expectation == "strong"
        ):
            violations.append(
                TemporalConstraintViolation(
                    "causal_timing_contradiction",
                    "Strong rebound after brief passive dwell requires explicit coupling evidence",
                )
            )
        return TemporalValidationResult(valid=not violations, violations=tuple(violations))

    def validate_composition(self, composition: TemporalPerturbationComposition) -> TemporalValidationResult:
        violations: list[TemporalConstraintViolation] = []
        if composition.temporal_stability < self.instability_threshold:
            violations.append(
                TemporalConstraintViolation(
                    "unstable_temporal_composition",
                    f"Temporal stability {composition.temporal_stability} is below threshold",
                )
            )
        targets = [item.target for item in composition.perturbations if item.target is not None]
        if composition.operator == "concurrent" and len(targets) != len(set(targets)):
            violations.append(
                TemporalConstraintViolation(
                    "antagonistic_timing",
                    "Concurrent temporal perturbations target the same entity",
                    severity="warning",
                )
            )
        for perturbation in composition.perturbations:
            violations.extend(self.validate_ir(perturbation).violations)
        return TemporalValidationResult(
            valid=not any(item.severity == "error" for item in violations),
            violations=tuple(violations),
        )
