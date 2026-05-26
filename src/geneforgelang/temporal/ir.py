from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, cast


class ActivationProfile:
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    PULSED = "pulsed"
    GATED = "gated"
    RAMPED = "ramped"


class DwellRegime:
    BRIEF = "brief"
    TRANSIENT = "transient"
    SUSTAINED = "sustained"
    OSCILLATORY = "oscillatory"


class DissociationMode:
    PASSIVE = "passive"
    FACILITATED = "facilitated"
    SWITCHABLE = "switchable"
    COMPETITIVE = "competitive"
    DECAY_MODULATED = "decay_modulated"


class ReboundExpectation:
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    STRONG = "strong"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TemporalUncertainty:
    activation: float = 0.0
    dwell: float = 0.0
    dissociation: float = 0.0
    rebound: float = 0.0
    method: str = "semantic_prior"

    def __post_init__(self) -> None:
        for name in ("activation", "dwell", "dissociation", "rebound"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} uncertainty must be in [0, 1]")


@dataclass(frozen=True)
class CausalTimingConstraint:
    relation: str
    before: str | None = None
    after: str | None = None
    during: str | None = None
    window: str | None = None
    required: bool = True


@dataclass(frozen=True)
class TemporalPerturbationIR:
    perturbation_type: str
    activation_profile: str
    dwell_regime: str
    dissociation_mode: str
    rebound_expectation: str = ReboundExpectation.UNKNOWN
    temporal_uncertainty: TemporalUncertainty = field(default_factory=TemporalUncertainty)
    causal_timing_constraints: tuple[CausalTimingConstraint, ...] = ()
    target: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], asdict(self))
