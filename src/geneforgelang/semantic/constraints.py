from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ConstraintKind:
    REACHABILITY = "reachability"
    MONOTONICITY = "monotonicity"
    BOUNDED_UNCERTAINTY = "bounded_uncertainty"
    TOPOLOGICAL_INTEGRITY = "topological_integrity"
    IDENTIFIABILITY = "identifiability"
    EPISTEMIC_CONSISTENCY = "epistemic_consistency"
    CROSS_SCALE_COMPATIBILITY = "cross_scale_compatibility"


class ConstraintRelationType:
    REQUIRES = "requires"
    INHIBITS = "inhibits"
    PROPAGATES_TO = "propagates_to"


@dataclass(frozen=True)
class SemanticConstraint:
    id: str
    target: str
    kind: str
    threshold: float = 1.0
    dependencies: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConstraintRelation:
    source: str
    target: str
    relation: str = ConstraintRelationType.PROPAGATES_TO
    weight: float = 1.0


@dataclass(frozen=True)
class ConstraintObservation:
    target: str
    values: dict[str, float | bool]


@dataclass(frozen=True)
class ConstraintViolation:
    constraint_id: str
    target: str
    code: str
    message: str
    severity: str = "error"
    downstream: tuple[str, ...] = ()
    influence: float = 1.0
    recoverable: bool = False


@dataclass(frozen=True)
class ConstraintSatisfaction:
    satisfied: bool
    score: float
    violations: tuple[ConstraintViolation, ...] = ()


@dataclass
class ConstraintGraph:
    constraints: dict[str, SemanticConstraint] = field(default_factory=dict)
    relations: list[ConstraintRelation] = field(default_factory=list)

    def add_constraint(self, constraint: SemanticConstraint) -> None:
        self.constraints[constraint.id] = constraint

    def add_relation(self, relation: ConstraintRelation) -> None:
        if relation.source not in self.constraints:
            raise ValueError(f"Unknown source constraint: {relation.source}")
        if relation.target not in self.constraints:
            raise ValueError(f"Unknown target constraint: {relation.target}")
        self.relations.append(relation)

    def downstream_of(self, constraint_id: str) -> tuple[str, ...]:
        return tuple(item[0] for item in self.downstream_paths(constraint_id))

    def downstream_paths(
        self,
        constraint_id: str,
        max_depth: int | None = None,
    ) -> tuple[tuple[str, int, float], ...]:
        seen: set[str] = set()
        frontier = [(constraint_id, 0, 1.0)]
        downstream: list[tuple[str, int, float]] = []
        while frontier:
            current, depth, influence = frontier.pop()
            if max_depth is not None and depth >= max_depth:
                continue
            for relation in self.relations:
                if (
                    relation.source == current
                    and relation.relation == ConstraintRelationType.PROPAGATES_TO
                    and relation.target not in seen
                ):
                    seen.add(relation.target)
                    propagated_influence = influence * relation.weight
                    downstream.append((relation.target, depth + 1, propagated_influence))
                    frontier.append((relation.target, depth + 1, propagated_influence))
        return tuple(downstream)


@dataclass(frozen=True)
class PropagationPolicy:
    propagation_decay: float = 0.65
    influence_threshold: float = 0.1
    max_depth: int = 4
    confidence_attenuation: float = 0.2
    stability_hysteresis: float = 0.05

    def __post_init__(self) -> None:
        for field_name in (
            "propagation_decay",
            "influence_threshold",
            "confidence_attenuation",
            "stability_hysteresis",
        ):
            value = getattr(self, field_name)
            if not 0 <= value <= 1:
                raise ValueError(f"{field_name} must be in [0, 1]")
        if self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")


class ConstraintSeverity:
    HARD = "hard"
    SOFT = "soft"
    RECOVERABLE = "recoverable"


class ConstraintPropagationEngine:
    def __init__(
        self,
        graph: ConstraintGraph | None = None,
        policy: PropagationPolicy | None = None,
    ):
        self.graph = graph or ConstraintGraph()
        self.policy = policy or PropagationPolicy()

    def evaluate(
        self,
        observations: dict[str, ConstraintObservation],
    ) -> ConstraintSatisfaction:
        violations: list[ConstraintViolation] = []
        scores: list[float] = []
        for constraint in self.graph.constraints.values():
            observation = observations.get(constraint.target)
            score, violation = self._evaluate_constraint(constraint, observation)
            scores.append(score)
            if violation is not None:
                downstream = tuple(
                    target
                    for target, _depth, influence in self.graph.downstream_paths(
                        constraint.id,
                        max_depth=self.policy.max_depth,
                    )
                    if influence * self.policy.propagation_decay >= self.policy.influence_threshold
                )
                violations.append(
                    ConstraintViolation(
                        constraint_id=violation.constraint_id,
                        target=violation.target,
                        code=violation.code,
                        message=violation.message,
                        severity=violation.severity,
                        downstream=downstream,
                        influence=violation.influence,
                        recoverable=violation.recoverable,
                    )
                )
                violations.extend(self._propagate_violation(violation, downstream))
        mean_score = sum(scores) / len(scores) if scores else 1.0
        return ConstraintSatisfaction(
            satisfied=not violations,
            score=mean_score,
            violations=tuple(violations),
        )

    def _evaluate_constraint(
        self,
        constraint: SemanticConstraint,
        observation: ConstraintObservation | None,
    ) -> tuple[float, ConstraintViolation | None]:
        if observation is None:
            return 0.0, ConstraintViolation(
                constraint.id,
                constraint.target,
                "missing_observation",
                f"No observation available for constraint target {constraint.target}",
            )
        if constraint.kind == ConstraintKind.REACHABILITY:
            return self._minimum_value(constraint, observation, "reachability")
        if constraint.kind == ConstraintKind.IDENTIFIABILITY:
            return self._minimum_value(constraint, observation, "identifiability")
        if constraint.kind == ConstraintKind.BOUNDED_UNCERTAINTY:
            return self._maximum_value(constraint, observation, "uncertainty")
        if constraint.kind == ConstraintKind.TOPOLOGICAL_INTEGRITY:
            intact = bool(observation.values.get("topology_intact", False))
            if intact:
                return 1.0, None
            return 0.0, ConstraintViolation(
                constraint.id,
                constraint.target,
                "topological_rupture",
                f"Topology ruptured for {constraint.target}",
                severity=ConstraintSeverity.HARD,
            )
        if constraint.kind == ConstraintKind.MONOTONICITY:
            previous = float(observation.values.get("previous", 0.0))
            current = float(observation.values.get("current", 0.0))
            if current >= previous:
                return 1.0, None
            return 0.0, ConstraintViolation(
                constraint.id,
                constraint.target,
                "monotonicity_violation",
                f"Current value {current} is below previous value {previous}",
                severity=ConstraintSeverity.RECOVERABLE,
                recoverable=True,
            )
        if constraint.kind == ConstraintKind.EPISTEMIC_CONSISTENCY:
            consistent = bool(observation.values.get("epistemic_consistent", False))
            if consistent:
                return 1.0, None
            return 0.0, ConstraintViolation(
                constraint.id,
                constraint.target,
                "epistemic_inconsistency",
                f"Epistemic state is inconsistent for {constraint.target}",
                severity=ConstraintSeverity.RECOVERABLE,
                recoverable=True,
            )
        if constraint.kind == ConstraintKind.CROSS_SCALE_COMPATIBILITY:
            return self._minimum_value(constraint, observation, "scale_compatibility")
        return 0.0, ConstraintViolation(
            constraint.id,
            constraint.target,
            "unknown_constraint_kind",
            f"Unknown constraint kind: {constraint.kind}",
        )

    def _minimum_value(
        self,
        constraint: SemanticConstraint,
        observation: ConstraintObservation,
        key: str,
    ) -> tuple[float, ConstraintViolation | None]:
        value = float(observation.values.get(key, 0.0))
        if value >= constraint.threshold:
            return min(1.0, value), None
        return value, ConstraintViolation(
            constraint.id,
            constraint.target,
            f"{key}_below_threshold",
            f"{key}={value} below threshold {constraint.threshold}",
            severity=ConstraintSeverity.SOFT if value > 0 else ConstraintSeverity.HARD,
            influence=max(0.0, constraint.threshold - value),
            recoverable=value > 0,
        )

    def _maximum_value(
        self,
        constraint: SemanticConstraint,
        observation: ConstraintObservation,
        key: str,
    ) -> tuple[float, ConstraintViolation | None]:
        value = float(observation.values.get(key, 1.0))
        if value <= constraint.threshold:
            return max(0.0, 1.0 - value), None
        return max(0.0, 1.0 - value), ConstraintViolation(
            constraint.id,
            constraint.target,
            f"{key}_above_threshold",
            f"{key}={value} above threshold {constraint.threshold}",
            severity=ConstraintSeverity.SOFT,
            influence=min(1.0, value - constraint.threshold),
            recoverable=True,
        )

    def _propagate_violation(
        self,
        violation: ConstraintViolation,
        downstream: tuple[str, ...],
    ) -> tuple[ConstraintViolation, ...]:
        propagated: list[ConstraintViolation] = []
        for constraint_id in downstream:
            if constraint_id not in self.graph.constraints:
                continue
            influence = violation.influence * self.policy.propagation_decay
            if influence < self.policy.influence_threshold:
                continue
            propagated.append(
                ConstraintViolation(
                    constraint_id=constraint_id,
                    target=self.graph.constraints[constraint_id].target,
                    code="propagated_constraint_violation",
                    message=f"Upstream violation {violation.constraint_id} propagates to {constraint_id}",
                    severity="warning",
                    influence=influence,
                    recoverable=violation.recoverable,
                )
            )
        return tuple(propagated)


@dataclass(frozen=True)
class SemanticConvergenceReport:
    convergence_reached: bool
    oscillation_detected: bool
    unstable_attractor: bool
    contradiction_loop: bool
    fixed_point_confidence: float
    iterations: int
    history: tuple[tuple[str, ...], ...]


class SemanticConvergenceEngine:
    def __init__(
        self,
        propagation: ConstraintPropagationEngine,
        max_iterations: int = 8,
        fixed_point_tolerance: float = 0.0,
    ):
        self.propagation = propagation
        self.max_iterations = max_iterations
        self.fixed_point_tolerance = fixed_point_tolerance

    def converge(
        self,
        observations: dict[str, ConstraintObservation],
    ) -> SemanticConvergenceReport:
        history: list[tuple[str, ...]] = []
        previous_signature: tuple[str, ...] | None = None
        seen: set[tuple[str, ...]] = set()
        for iteration in range(1, self.max_iterations + 1):
            satisfaction = self.propagation.evaluate(observations)
            signature = tuple(sorted(item.code + ":" + item.target for item in satisfaction.violations))
            history.append(signature)
            if signature == previous_signature:
                return SemanticConvergenceReport(
                    convergence_reached=True,
                    oscillation_detected=False,
                    unstable_attractor=False,
                    contradiction_loop=False,
                    fixed_point_confidence=satisfaction.score,
                    iterations=iteration,
                    history=tuple(history),
                )
            if signature in seen:
                return SemanticConvergenceReport(
                    convergence_reached=False,
                    oscillation_detected=True,
                    unstable_attractor=True,
                    contradiction_loop=any("epistemic_inconsistency" in item for item in signature),
                    fixed_point_confidence=0.0,
                    iterations=iteration,
                    history=tuple(history),
                )
            seen.add(signature)
            previous_signature = signature
        return SemanticConvergenceReport(
            convergence_reached=False,
            oscillation_detected=False,
            unstable_attractor=True,
            contradiction_loop=False,
            fixed_point_confidence=0.0,
            iterations=self.max_iterations,
            history=tuple(history),
        )
