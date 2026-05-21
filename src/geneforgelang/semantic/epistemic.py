from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from geneforgelang.semantic.provenance import ProvenanceGraph


class MutableEntity(Protocol):
    def set_attr(self, key: str, value: Any) -> None:
        raise NotImplementedError


class CausalState(Protocol):
    def get_downstream_entities(self, entity_id: str) -> list[str]:
        raise NotImplementedError

    def get_entity(self, entity_id: str) -> MutableEntity | None:
        raise NotImplementedError


class ObservationStatus:
    OBSERVED_PRESENT = "observed_present"
    OBSERVED_ABSENT = "observed_absent"
    NOT_OBSERVED = "not_observed"
    NOT_OBSERVABLE = "not_observable"


@dataclass(frozen=True)
class ObservabilityAssessment:
    target: str
    status: str
    visibility: float
    reachability: float
    identifiability: float
    perturbability: float
    resolution: str | None = None


@dataclass
class BiologicalObservabilityFramework:
    def assess(
        self,
        target: str,
        observed: bool | None,
        observable: bool = True,
        resolution: str | None = None,
    ) -> ObservabilityAssessment:
        if not observable:
            status = ObservationStatus.NOT_OBSERVABLE
            visibility = 0.0
        elif observed is True:
            status = ObservationStatus.OBSERVED_PRESENT
            visibility = 1.0
        elif observed is False:
            status = ObservationStatus.OBSERVED_ABSENT
            visibility = 1.0
        else:
            status = ObservationStatus.NOT_OBSERVED
            visibility = 0.25
        return ObservabilityAssessment(
            target=target,
            status=status,
            visibility=visibility,
            reachability=visibility,
            identifiability=visibility,
            perturbability=visibility,
            resolution=resolution,
        )


@dataclass(frozen=True)
class EvidenceView:
    source: str
    claim: str
    confidence: float
    uncertainty_kind: str = "epistemic"
    calibration: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConsensusEstimate:
    claim: str
    confidence: float
    sources: tuple[str, ...]
    conflict_score: float
    view_uncertainties: dict[str, str]
    contradiction_edges: tuple[tuple[str, str], ...] = ()
    consensus_instability: float = 0.0


class MultiViewEvidenceTriangulator:
    contradiction_threshold = 0.35

    def estimate(self, views: list[EvidenceView]) -> ConsensusEstimate:
        if not views:
            raise ValueError("at least one evidence view is required")
        weighted = [view.confidence * view.calibration for view in views]
        confidence = max(0.0, min(1.0, sum(weighted) / len(weighted)))
        conflict_score = max(weighted) - min(weighted) if len(weighted) > 1 else 0.0
        contradiction_edges = self._contradictions(views)
        return ConsensusEstimate(
            claim=views[0].claim,
            confidence=confidence,
            sources=tuple(view.source for view in views),
            conflict_score=conflict_score,
            view_uncertainties={view.source: view.uncertainty_kind for view in views},
            contradiction_edges=contradiction_edges,
            consensus_instability=max(conflict_score, min(1.0, len(contradiction_edges) * 0.25)),
        )

    def _contradictions(self, views: list[EvidenceView]) -> tuple[tuple[str, str], ...]:
        edges: list[tuple[str, str]] = []
        for index, left in enumerate(views):
            for right in views[index + 1 :]:
                left_score = left.confidence * left.calibration
                right_score = right.confidence * right.calibration
                polarity_conflict = left.metadata.get("polarity") != right.metadata.get("polarity")
                both_have_polarity = "polarity" in left.metadata and "polarity" in right.metadata
                if abs(left_score - right_score) >= self.contradiction_threshold or (
                    both_have_polarity and polarity_conflict
                ):
                    edges.append((left.source, right.source))
        return tuple(edges)


@dataclass(frozen=True)
class InvalidationRecord:
    target: str
    reason: str
    downstream: tuple[str, ...]


class CausalInvalidationEngine:
    def invalidate(self, state: CausalState, entity_id: str, reason: str) -> InvalidationRecord:
        downstream = tuple(state.get_downstream_entities(entity_id))
        for target_id in (entity_id,) + downstream:
            entity = state.get_entity(target_id)
            if entity is not None:
                entity.set_attr("epistemic_status", "invalidated")
                entity.set_attr("invalidation_reason", reason)
        return InvalidationRecord(target=entity_id, reason=reason, downstream=downstream)


@dataclass(frozen=True)
class CompressibilityEstimate:
    target: str
    semantic_compressibility: float
    causal_compressibility: float
    representation_stability: float
    scale_dependent: bool


@dataclass(frozen=True)
class CompressibilityProfile:
    target: str
    molecular: float
    pathway: float
    cellular: float
    tissue: float
    organism: float
    temporal: float
    intervention_stability: float
    causal_entropy: float
    observability_dependence: float

    @property
    def representation_stability(self) -> float:
        values = (
            self.molecular,
            self.pathway,
            self.cellular,
            self.tissue,
            self.organism,
            self.temporal,
            self.intervention_stability,
        )
        return sum(values) / len(values)


class CompressibilityEngine:
    def estimate(
        self,
        target: str,
        evidence_count: int,
        conflict_score: float,
        scale_count: int = 1,
    ) -> CompressibilityEstimate:
        evidence_factor = min(1.0, evidence_count / 5)
        stability = max(0.0, 1.0 - conflict_score)
        scale_penalty = 0.1 * max(0, scale_count - 1)
        semantic = max(0.0, min(1.0, evidence_factor * stability - scale_penalty))
        causal = max(0.0, min(1.0, stability - scale_penalty))
        return CompressibilityEstimate(
            target=target,
            semantic_compressibility=semantic,
            causal_compressibility=causal,
            representation_stability=stability,
            scale_dependent=scale_count > 1,
        )

    def profile(
        self,
        target: str,
        evidence_count: int,
        conflict_score: float,
        observability_dependence: float = 0.5,
    ) -> CompressibilityProfile:
        evidence_factor = min(1.0, evidence_count / 5)
        stability = max(0.0, 1.0 - conflict_score)
        temporal = max(0.0, stability - 0.15)
        intervention_stability = max(0.0, stability - observability_dependence * 0.2)
        causal_entropy = min(1.0, conflict_score + observability_dependence * 0.3)
        return CompressibilityProfile(
            target=target,
            molecular=evidence_factor * stability,
            pathway=max(0.0, evidence_factor * stability - 0.1),
            cellular=max(0.0, evidence_factor * stability - 0.2),
            tissue=max(0.0, evidence_factor * stability - 0.35),
            organism=max(0.0, evidence_factor * stability - 0.45),
            temporal=temporal,
            intervention_stability=intervention_stability,
            causal_entropy=causal_entropy,
            observability_dependence=observability_dependence,
        )


class EpistemicStatus:
    HYPOTHESIS = "hypothesis"
    SUPPORTED = "supported"
    CONFLICTED = "conflicted"
    RETRACTED = "retracted"
    REVALIDATED = "revalidated"


@dataclass(frozen=True)
class EpistemicTransition:
    claim: str
    from_status: str
    to_status: str
    reason: str


@dataclass
class BeliefState:
    beliefs: dict[str, ConsensusEstimate] = field(default_factory=dict)
    invalidations: list[InvalidationRecord] = field(default_factory=list)
    statuses: dict[str, str] = field(default_factory=dict)
    transitions: list[EpistemicTransition] = field(default_factory=list)

    def accumulate(self, estimate: ConsensusEstimate) -> None:
        self.beliefs[estimate.claim] = estimate
        target = (
            EpistemicStatus.CONFLICTED
            if estimate.contradiction_edges
            or estimate.consensus_instability >= MultiViewEvidenceTriangulator.contradiction_threshold
            else EpistemicStatus.SUPPORTED
        )
        self.transition(estimate.claim, target, "evidence accumulated")

    def confidence(self, claim: str) -> float | None:
        estimate = self.beliefs.get(claim)
        return None if estimate is None else estimate.confidence

    def mark_invalidated(self, record: InvalidationRecord) -> None:
        self.invalidations.append(record)
        self.transition(record.target, EpistemicStatus.RETRACTED, record.reason)

    def transition(self, claim: str, to_status: str, reason: str) -> None:
        from_status = self.statuses.get(claim, EpistemicStatus.HYPOTHESIS)
        self.statuses[claim] = to_status
        self.transitions.append(
            EpistemicTransition(
                claim=claim,
                from_status=from_status,
                to_status=to_status,
                reason=reason,
            )
        )


@dataclass
class EpistemicRuntime:
    belief_state: BeliefState = field(default_factory=BeliefState)
    observability: BiologicalObservabilityFramework = field(default_factory=BiologicalObservabilityFramework)
    triangulator: MultiViewEvidenceTriangulator = field(default_factory=MultiViewEvidenceTriangulator)
    invalidation: CausalInvalidationEngine = field(default_factory=CausalInvalidationEngine)
    compressibility: CompressibilityEngine = field(default_factory=CompressibilityEngine)
    provenance: ProvenanceGraph = field(default_factory=ProvenanceGraph)

    def ingest_evidence(self, views: list[EvidenceView]) -> ConsensusEstimate:
        estimate = self.triangulator.estimate(views)
        self.belief_state.accumulate(estimate)
        self.provenance.record_inference(
            claim=estimate.claim,
            sources=estimate.sources,
            engine_name="multi_view_triangulator",
            engine_version="semantic-core",
            confidence=estimate.confidence,
        )
        return estimate

    def invalidate(self, state: CausalState, entity_id: str, reason: str) -> InvalidationRecord:
        record = self.invalidation.invalidate(state, entity_id, reason)
        self.belief_state.mark_invalidated(record)
        return record
