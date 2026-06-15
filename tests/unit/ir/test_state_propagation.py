import pytest

from geneforgelang.ir.instruction import Substitute
from geneforgelang.ir.state import BiologicalState, Entity, EntityType, Relation, RelationType


def _make_state_with_derived():
    state = BiologicalState()
    state.add_entity(
        Entity(
            id="TP53",
            type=EntityType.GENE,
            attrs={"sequence": "ATCG", "status": "wildtype"},
        )
    )
    state.add_entity(
        Entity(
            id="TP53_transcript",
            type=EntityType.TRANSCRIPT,
            attrs={"status": "intact"},
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
        Relation(source="TP53", target="TP53_transcript", type=RelationType.DERIVES_FROM)
    )
    state.add_relation(
        Relation(
            source="TP53_transcript", target="TP53_protein", type=RelationType.DERIVES_FROM
        )
    )
    return state


def test_substitute_propagates_to_transcript_and_protein():
    state = _make_state_with_derived()
    inst = Substitute(gene_id="TP53", position=0, ref="A", alt="G")
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53_transcript").get_attr("status") == "affected"
    assert new_state.get_entity("TP53_protein").get_attr("status") == "loss_of_function"


def test_propagate_regulatory_loss():
    state = BiologicalState()
    state.add_entity(
        Entity(id="MDM2", type=EntityType.PROTEIN, attrs={"status": "functional"})
    )
    state.add_entity(
        Entity(id="TP53", type=EntityType.GENE, attrs={"status": "wildtype"})
    )
    state.add_relation(
        Relation(
            source="MDM2",
            target="TP53",
            type=RelationType.REGULATES,
            metadata={"active": True},
        )
    )
    state.entities["MDM2"].set_attr("status", "loss_of_function")
    state.propagate_mutation_effects("MDM2")
    assert state.get_entity("TP53").get_attr("status") == "deregulated"


def test_break_relation_prevents_propagation():
    state = _make_state_with_derived()
    state.break_relation("TP53", "TP53_transcript", RelationType.DERIVES_FROM)
    inst = Substitute(gene_id="TP53", position=0, ref="A", alt="G")
    new_state = inst.apply(state)
    # Broken relation → transcript stays intact
    assert new_state.get_entity("TP53_transcript").get_attr("status") == "intact"


def test_downstream_entities():
    state = _make_state_with_derived()
    downstream = state.get_downstream_entities("TP53")
    assert "TP53_transcript" in downstream
    assert "TP53_protein" in downstream
