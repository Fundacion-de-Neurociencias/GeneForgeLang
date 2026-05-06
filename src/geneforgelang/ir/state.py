from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class EntityType:
    GENE = "GENE"
    TRANSCRIPT = "TRANSCRIPT"
    PROTEIN = "PROTEIN"
    CELL = "CELL"
    METABOLITE = "METABOLITE"
    COMPLEX = "COMPLEX"
    UNKNOWN = "UNKNOWN"


class RelationType:
    REGULATES = "REGULATES"
    DERIVES_FROM = "DERIVES_FROM"
    CAUSES = "CAUSES"
    INHIBITS = "INHIBITS"
    BINDS = "BINDS"
    PART_OF = "PART_OF"


@dataclass
class Entity:
    id: str
    type: str
    attrs: Dict[str, Any] = field(default_factory=dict)

    def get_attr(self, key: str, default: Any = None) -> Any:
        return self.attrs.get(key, default)

    def set_attr(self, key: str, value: Any) -> None:
        self.attrs[key] = value

    def copy(self) -> Entity:
        return Entity(id=self.id, type=self.type, attrs=deepcopy(self.attrs))

    def __repr__(self) -> str:
        return f"Entity(id={self.id!r}, type={self.type!r})"


@dataclass
class Relation:
    source: str
    target: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> Relation:
        return Relation(
            source=self.source,
            target=self.target,
            type=self.type,
            metadata=deepcopy(self.metadata),
        )

    def __repr__(self) -> str:
        return f"Relation({self.source} -{self.type}-> {self.target})"


@dataclass
class BiologicalState:
    entities: Dict[str, Entity] = field(default_factory=dict)
    relations: List[Relation] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: str) -> None:
        self.entities.pop(entity_id, None)
        self.relations = [
            r for r in self.relations
            if r.source != entity_id and r.target != entity_id
        ]

    def add_relation(self, relation: Relation) -> None:
        self.relations.append(relation)

    def get_downstream_entities(self, entity_id: str, visited: set[str] | None = None) -> list[str]:
        """Return all entity IDs causally downstream of *entity_id* (transitive closure)."""
        if visited is None:
            visited = set()
        if entity_id in visited:
            return []
        visited.add(entity_id)
        downstream: list[str] = []
        for rel in self.relations:
            if rel.source == entity_id and rel.type in (
                RelationType.REGULATES,
                RelationType.CAUSES,
                RelationType.DERIVES_FROM,
            ):
                downstream.append(rel.target)
                downstream.extend(self.get_downstream_entities(rel.target, visited))
        return downstream

    def break_relation(self, source: str, target: str, rel_type: str) -> None:
        """Mark a relation as inactive (e.g. after a knockout)."""
        for rel in self.relations:
            if rel.source == source and rel.target == target and rel.type == rel_type:
                rel.metadata["active"] = False

    def activate_relation(self, source: str, target: str, rel_type: str) -> None:
        """Mark a relation as active."""
        for rel in self.relations:
            if rel.source == source and rel.target == target and rel.type == rel_type:
                rel.metadata["active"] = True

    def propagate_mutation_effects(
        self, mutated_entity_id: str, visited: set[str] | None = None
    ) -> None:
        """Propagate mutation effects along DERIVES_FROM and REGULATES edges.

        Recursively walks the causal graph so that a gene mutation can
        cascade:  GENE → TRANSCRIPT → PROTEIN → regulated targets.
        """
        if visited is None:
            visited = set()
        if mutated_entity_id in visited:
            return
        visited.add(mutated_entity_id)

        entity = self.get_entity(mutated_entity_id)
        if entity is None:
            return

        # Layer 1: propagate along DERIVES_FROM (gene → transcript → protein)
        for rel in self.relations:
            if (
                rel.source == mutated_entity_id
                and rel.type == RelationType.DERIVES_FROM
                and rel.metadata.get("active", True)
            ):
                child = self.get_entity(rel.target)
                if child is None:
                    continue
                if entity.type == "GENE" and child.type == "TRANSCRIPT":
                    child.set_attr("status", "affected")
                    self.propagate_mutation_effects(child.id, visited)
                elif entity.type in ("GENE", "TRANSCRIPT") and child.type == "PROTEIN":
                    child.set_attr("status", "loss_of_function")
                    self._propagate_regulatory_loss(child.id)
                    self.propagate_mutation_effects(child.id, visited)

        # If the mutated entity itself is a protein and its function is lost,
        # deregulate its targets.
        if entity.type == "PROTEIN" and entity.get_attr("status") == "loss_of_function":
            self._propagate_regulatory_loss(entity.id)

    def _propagate_regulatory_loss(self, source_id: str) -> None:
        for rel in self.relations:
            if (
                rel.source == source_id
                and rel.type == RelationType.REGULATES
                and rel.metadata.get("active", True)
            ):
                target = self.get_entity(rel.target)
                if target is not None:
                    target.set_attr("status", "deregulated")

    def fork(self) -> BiologicalState:
        """Return a deep, independent copy of this state."""
        return BiologicalState(
            entities={eid: e.copy() for eid, e in self.entities.items()},
            relations=[r.copy() for r in self.relations],
            properties=deepcopy(self.properties),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BiologicalState):
            return NotImplemented
        return (
            self.entities == other.entities
            and self.relations == other.relations
            and self.properties == other.properties
        )
