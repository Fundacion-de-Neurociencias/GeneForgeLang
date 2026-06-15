import pytest

from geneforgelang.ir.state import BiologicalState, Entity, EntityType, Relation, RelationType


def test_entity_creation():
    e = Entity(id="TP53", type=EntityType.GENE, attrs={"sequence": "ATCG"})
    assert e.id == "TP53"
    assert e.type == "GENE"
    assert e.get_attr("sequence") == "ATCG"


def test_state_fork_immutability():
    e = Entity(id="TP53", type=EntityType.GENE, attrs={"sequence": "ATCG"})
    state = BiologicalState(entities={"TP53": e})
    state2 = state.fork()
    state2.entities["TP53"].set_attr("sequence", "GGGG")
    assert state.get_entity("TP53").get_attr("sequence") == "ATCG"
    assert state2.get_entity("TP53").get_attr("sequence") == "GGGG"


def test_state_add_remove_entity():
    state = BiologicalState()
    e = Entity(id="BRCA1", type=EntityType.GENE)
    state.add_entity(e)
    assert state.get_entity("BRCA1") is not None
    state.remove_entity("BRCA1")
    assert state.get_entity("BRCA1") is None


def test_state_remove_entity_cleans_relations():
    state = BiologicalState()
    e1 = Entity(id="A", type=EntityType.GENE)
    e2 = Entity(id="B", type=EntityType.PROTEIN)
    state.add_entity(e1)
    state.add_entity(e2)
    state.add_relation(Relation(source="A", target="B", type=RelationType.REGULATES))
    state.remove_entity("A")
    assert len(state.relations) == 0


def test_state_equality():
    e1 = Entity(id="A", type=EntityType.GENE, attrs={"x": 1})
    s1 = BiologicalState(entities={"A": e1})
    s2 = BiologicalState(entities={"A": e1.copy()})
    assert s1 == s2
