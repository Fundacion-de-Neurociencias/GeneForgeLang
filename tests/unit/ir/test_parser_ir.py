import pytest

from geneforgelang.ir.parser_ir import parse_text, ParseError
from geneforgelang.ir.instruction import Substitute, Insert, Delete, Invert


def test_parse_entities():
    text = """
    entity TP53 GENE sequence=ATCG status=wildtype
    entity KRAS GENE sequence=GGC
    """
    state, insts = parse_text(text)
    assert len(state.entities) == 2
    assert state.get_entity("TP53").type == "GENE"
    assert state.get_entity("TP53").get_attr("sequence") == "ATCG"
    assert state.get_entity("TP53").get_attr("status") == "wildtype"
    assert len(insts) == 0


def test_parse_relation():
    text = "relation TP53 REGULATES KRAS confidence=0.9"
    state, insts = parse_text(text)
    assert len(state.relations) == 1
    r = state.relations[0]
    assert r.source == "TP53"
    assert r.target == "KRAS"
    assert r.type == "REGULATES"
    assert r.metadata["confidence"] == 0.9


def test_parse_substitute():
    text = "substitute TP53 0 A G"
    state, insts = parse_text(text)
    assert len(insts) == 1
    assert isinstance(insts[0], Substitute)
    assert insts[0].gene_id == "TP53"


def test_parse_insert_delete_invert():
    text = """
    insert TP53 2 GG
    delete TP53 1 3
    invert TP53 0 4
    """
    state, insts = parse_text(text)
    assert len(insts) == 3
    assert isinstance(insts[0], Insert)
    assert isinstance(insts[1], Delete)
    assert isinstance(insts[2], Invert)


def test_parse_error_unknown_command():
    with pytest.raises(ParseError):
        parse_text("foo bar")


def test_parse_error_bad_entity():
    with pytest.raises(ParseError):
        parse_text("entity TP53")


def test_parse_comments_and_blanks_ignored():
    text = """
    # this is a comment
    entity A GENE

    # another comment
    """
    state, insts = parse_text(text)
    assert len(state.entities) == 1
    assert len(insts) == 0
