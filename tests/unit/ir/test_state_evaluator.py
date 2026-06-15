import pytest

from geneforgelang.ir.state_evaluator import StateEvaluator
from geneforgelang.ir.state import BiologicalState, Entity, EntityType, Relation, RelationType
from geneforgelang.ir.strategy import Objective


def _make_tp53_state():
    state = BiologicalState()
    state.add_entity(
        Entity(
            id="TP53",
            type=EntityType.GENE,
            attrs={
                "sequence": "ATCGATCG",
                "original_sequence": "ATCGATCG",
                "status": "wildtype",
            },
        )
    )
    state.add_entity(
        Entity(
            id="TP53_protein",
            type=EntityType.PROTEIN,
            attrs={"status": "functional"},
        )
    )
    state.add_relation(
        Relation(
            source="TP53", target="TP53_protein", type=RelationType.DERIVES_FROM
        )
    )
    return state


def test_evaluate_knockout_low_damage():
    state = _make_tp53_state()
    obj = Objective(description="Knockout TP53", target_entity="TP53")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    assert score == 0.0


def test_evaluate_knockout_with_mutation():
    state = _make_tp53_state()
    state.entities["TP53"].set_attr("sequence", "NNNNNNNN")
    obj = Objective(description="Knockout TP53", target_entity="TP53")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    assert score > 0.3


def test_evaluate_knockout_with_downstream_loss():
    state = _make_tp53_state()
    state.entities["TP53"].set_attr("status", "knocked_out")
    state.entities["TP53_protein"].set_attr("status", "loss_of_function")
    obj = Objective(description="Knockout TP53", target_entity="TP53")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    assert score >= 0.6


def test_evaluate_generic_change():
    state = _make_tp53_state()
    state.entities["TP53"].set_attr("sequence", "NNCGATCG")
    obj = Objective(description="Modify TP53", target_entity="TP53")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    assert 0.0 < score <= 1.0


def test_evaluate_no_target():
    state = _make_tp53_state()
    obj = Objective(description="Do something vague")
    ev = StateEvaluator()
    score = ev.evaluate(state, obj)
    assert score == 0.0
