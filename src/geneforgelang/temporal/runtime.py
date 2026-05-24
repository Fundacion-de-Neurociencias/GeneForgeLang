from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from geneforgelang.temporal.constraints import TemporalConstraintEngine, TemporalValidationResult
from geneforgelang.temporal.ir import TemporalPerturbationIR
from geneforgelang.temporal.operators import TemporalPerturbationComposition


@dataclass(frozen=True)
class TemporalRegimeAssessment:
    stable: bool
    confidence: float
    rationale: str


@runtime_checkable
class TemporalCapabilityProvider(Protocol):
    name: str
    version: str

    def simulate_temporal_regime(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        raise NotImplementedError

    def evaluate_dissociation_schedule(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        raise NotImplementedError

    def estimate_rebound_topology(self, temporal_ir: TemporalPerturbationIR) -> TemporalRegimeAssessment:
        raise NotImplementedError

    def assess_temporal_stability(self, composition: TemporalPerturbationComposition) -> TemporalRegimeAssessment:
        raise NotImplementedError


class CrossScaleTemporalCompiler:
    _forward = (
        "phenotype",
        "pathway_timing",
        "receptor_occupancy_dynamics",
        "molecular_perturbation_schedule",
    )

    def compile(self, source_scale: str, target_scale: str) -> tuple[str, ...]:
        if source_scale not in self._forward or target_scale not in self._forward:
            raise ValueError("unknown temporal biological scale")
        source_index = self._forward.index(source_scale)
        target_index = self._forward.index(target_scale)
        if source_index <= target_index:
            return self._forward[source_index : target_index + 1]
        return tuple(reversed(self._forward[target_index : source_index + 1]))


@dataclass
class TemporalExecutionRuntime:
    constraint_engine: TemporalConstraintEngine = field(default_factory=TemporalConstraintEngine)
    providers: dict[str, TemporalCapabilityProvider] = field(default_factory=dict)
    compiler: CrossScaleTemporalCompiler = field(default_factory=CrossScaleTemporalCompiler)

    def register_provider(self, provider: TemporalCapabilityProvider) -> None:
        if not isinstance(provider, TemporalCapabilityProvider):
            raise TypeError("provider does not implement TemporalCapabilityProvider")
        self.providers[provider.name] = provider

    def validate(self, temporal_ir: TemporalPerturbationIR) -> TemporalValidationResult:
        return self.constraint_engine.validate_ir(temporal_ir)

    def validate_composition(self, composition: TemporalPerturbationComposition) -> TemporalValidationResult:
        return self.constraint_engine.validate_composition(composition)
