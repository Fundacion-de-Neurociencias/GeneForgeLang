import pytest
from parser import parse_geneforge_line

@pytest.mark.parametrize("input_line,expected_keys", [
    ("~d:[TATA]ATG[MUT:PAT:A>G@1001]", ["mutations"]),
    ("EDIT:Base(A→G@1001){efficacy=partial, cells=liver}", ["edits"]),
    ("DELIV(mRNA+LNP@IV)", ["delivery"]),
    ("DOSE(1):EDIT:Base(A→G@1001)", ["doses"]),
    ("TIME(0d):DELIV(mRNA@IV)", ["timed_events"]),
    ("EFFECT(restore function=urea cycle)", ["effects"]),
    ("HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)", ["hypotheses"]),
    ("SIMULATE: {EDIT:Base(A→G@1001), OUTCOME:↓ammonia}", ["simulations"]),
    ("PATHWAY: ARG + NH3 → CPS1 → Carbamoyl-P", ["pathways"]),
    ("MACRO:EDIT_CPS1 = {DELIV(mRNA+LNP@IV)-EDIT:Base(A→G@1001)}", ["macros"]),
    ("USE:EDIT_CPS1", ["macro_calls"])
])
def test_parser_comprehension(input_line, expected_keys):
    result = parse_geneforge_line(input_line)
    assert result["valid"] is True
    for key in expected_keys:
        assert key in result
        assert len(result[key]) > 0
