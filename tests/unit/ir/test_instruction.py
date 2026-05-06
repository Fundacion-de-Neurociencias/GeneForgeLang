import pytest

from geneforgelang.ir.instruction import (
    Substitute,
    Insert,
    Delete,
    Invert,
    EntityNotFoundError,
    ReferenceMismatchError,
    InvalidSequenceError,
)
from geneforgelang.ir.state import BiologicalState, Entity, EntityType


def _make_tp53():
    return BiologicalState(
        entities={
            "TP53": Entity(
                id="TP53",
                type=EntityType.GENE,
                attrs={"sequence": "ATCGATCG", "status": "wildtype"},
            )
        }
    )


def test_substitute_success():
    state = _make_tp53()
    inst = Substitute(gene_id="TP53", position=0, ref="A", alt="G")
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53").get_attr("sequence") == "GTCGATCG"
    assert state.get_entity("TP53").get_attr("sequence") == "ATCGATCG"


def test_substitute_reference_mismatch():
    state = _make_tp53()
    inst = Substitute(gene_id="TP53", position=0, ref="T", alt="G")
    with pytest.raises(ReferenceMismatchError):
        inst.apply(state)


def test_substitute_entity_not_found():
    state = _make_tp53()
    inst = Substitute(gene_id="KRAS", position=0, ref="A", alt="G")
    with pytest.raises(EntityNotFoundError):
        inst.apply(state)


def test_insert_success():
    state = _make_tp53()
    inst = Insert(gene_id="TP53", position=2, sequence="GG")
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53").get_attr("sequence") == "ATGGCGATCG"


def test_delete_success():
    state = _make_tp53()
    inst = Delete(gene_id="TP53", start=1, end=3)
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53").get_attr("sequence") == "AGATCG"


def test_invert_success():
    state = _make_tp53()
    # seq = "ATCGATCG"
    # segment[1:3] = "TC"
    # complement = AG, reverse = GA
    inst = Invert(gene_id="TP53", start=1, end=3)
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53").get_attr("sequence") == "AGAGATCG"


def test_invert_full_segment():
    state = _make_tp53()
    # segment[0:4] = "ATCG"
    # complement = TAGC, reverse = CGAT
    inst = Invert(gene_id="TP53", start=0, end=4)
    new_state = inst.apply(state)
    assert new_state.get_entity("TP53").get_attr("sequence") == "CGATATCG"


def test_invalid_sequence_raises():
    with pytest.raises(InvalidSequenceError):
        Substitute(gene_id="X", position=0, ref="Z", alt="A")


def test_substitute_bounds_check():
    state = _make_tp53()
    inst = Substitute(gene_id="TP53", position=100, ref="A", alt="G")
    with pytest.raises(ReferenceMismatchError):
        inst.apply(state)


def test_delete_bounds_check():
    state = _make_tp53()
    inst = Delete(gene_id="TP53", start=0, end=100)
    with pytest.raises(ReferenceMismatchError):
        inst.apply(state)


def test_to_dict_roundtrip_substitute():
    inst = Substitute(gene_id="TP53", position=5, ref="C", alt="T")
    d = inst.to_dict()
    assert d["op"] == "SUBSTITUTE"
    assert d["gene_id"] == "TP53"
    assert d["position"] == 5
