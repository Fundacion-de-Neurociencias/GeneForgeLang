from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ConstraintKind:
    REACHABILITY = "reachability"
    MONOTONICITY = "monotonicity"
    BOUNDED_UNCERTAINTY = "bounded_uncertainty"
    TOPOLOGICAL_INTEGRITY = "topological_integrity"
    IDENTIFIABILITY = "identifiability"


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
        seen: set[str] = set()
        frontier = [constraint_id]
        while frontier:
            current = frontier.pop()
            for relation in self.relations:
                if (
                    relation.source == current
                    and relation.relation == ConstraintRelationType.PROPAGATES_TO
                    and relation.target not in seen
                ):
                    seen.add(relation.target)
                    frontier.append(relation.target)
        return tuple(seen)


class ConstraintPropagationEngine:
    def __init__(self, graph: ConstraintGraph | None = None):
        self.graph = graph or ConstraintGraph()

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
                downstream = self.graph.downstream_of(constraint.id)
                violations.append(
                    ConstraintViolation(
                        constraint_id=violation.constraint_id,
                        target=violation.target,
                        code=violation.code,
                        message=violation.message,
                        severity=violation.severity,
                        downstream=downstream,
                    )
                )
                violations.extend(self._propagate_violation(violation, downstream))
        mean_score = sum(scores) / len(scores) if scores else 1.0
        return ConstraintSatisfaction(
            satisfied=not any(item.severity == "error" for item in violations),
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
            )
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
        )

    def _propagate_violation(
        self,
        violation: ConstraintViolation,
        downstream: tuple[str, ...],
    ) -> tuple[ConstraintViolation, ...]:
        return tuple(
            ConstraintViolation(
                constraint_id=constraint_id,
                target=self.graph.constraints[constraint_id].target,
                code="propagated_constraint_violation",
                message=f"Upstream violation {violation.constraint_id} propagates to {constraint_id}",
                severity="warning",
            )
            for constraint_id in downstream
            if constraint_id in self.graph.constraints
        )
