from gfl.api import infer, parse, validate
from gfl.models.dummy import DummyGeneModel


def test_parse_and_validate_minimal():
    text = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""
    ast = parse(text)
    assert isinstance(ast, dict)
    errs = validate(ast)
    assert isinstance(errs, list)


def test_infer_with_dummy_model():
    ast = {
        "experiment": {
            "tool": "CRISPR_cas9",
            "type": "gene_editing",
            "params": {"target_gene": "TP53"},
        }
    }
    result = infer(DummyGeneModel(), ast)
    assert set(result.keys()) >= {"label", "confidence", "explanation"}
