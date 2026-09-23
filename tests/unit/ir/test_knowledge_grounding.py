import pytest

from geneforgelang.ir.knowledge_grounding import KnowledgeBase
from geneforgelang.ir.state import BiologicalState, Entity, EntityType


def test_query_known_entity():
    kb = KnowledgeBase()
    result = kb.query("TP53")
    assert result["function"] == "tumor_suppressor"
    assert "MDM2" in result["interactors"]


def test_query_unknown_entity():
    kb = KnowledgeBase()
    assert kb.query("UNKNOWN_GENE") == {}


def test_enrich_state():
    state = BiologicalState()
    state.add_entity(Entity(id="TP53", type=EntityType.GENE))
    state.add_entity(Entity(id="X", type=EntityType.GENE))
    kb = KnowledgeBase()
    enriched = kb.enrich_state(state)
    assert enriched.get_entity("TP53").get_attr("knowledge") is not None
    assert enriched.get_entity("X").get_attr("knowledge") is None


def test_suggest_constraints():
    kb = KnowledgeBase()
    constraints = kb.suggest_constraints("TP53")
    assert "knockout_may_be_lethal" in constraints


def test_is_viable_edit_knockout_essential():
    kb = KnowledgeBase()
    assert not kb.is_viable_edit("TP53", "knockout")
    assert kb.is_viable_edit("KRAS", "knockout")


def test_is_viable_edit_non_essential():
    kb = KnowledgeBase()
    assert kb.is_viable_edit("TP53", "substitute A to G")
