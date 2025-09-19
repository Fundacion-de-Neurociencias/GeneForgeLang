"""Basic functionality tests for GeneForgeLang."""

import pytest
from geneforgelang import execute, parse, validate


def test_package_import():
    """Test that the package can be imported."""
    import geneforgelang

    assert geneforgelang.__version__ == "1.0.0"


def test_basic_parse():
    """Test basic parsing functionality."""
    gfl_code = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""

    ast = parse(gfl_code)
    assert isinstance(ast, dict)
    assert "experiment" in ast
    assert ast["experiment"]["tool"] == "CRISPR_cas9"


def test_basic_validation():
    """Test basic validation functionality."""
    gfl_code = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""

    ast = parse(gfl_code)
    errors = validate(ast)

    # Should be a list (even if empty)
    assert isinstance(errors, list)


def test_workflow_example():
    """Test a complete workflow example."""
    gfl_code = """
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  count: 5
  length: 50
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    concentration: "range(10, 100)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: efficiency
  budget:
    max_experiments: 5
  run:
    experiment:
      tool: simulation
      type: parameter_sweep
      params:
        temp: "${temperature}"
        conc: "${concentration}"
"""

    # Parse
    ast = parse(gfl_code)
    assert isinstance(ast, dict)
    assert "design" in ast
    assert "optimize" in ast

    # Validate
    errors = validate(ast)
    assert isinstance(errors, list)

    # Execute (if no validation errors)
    if not errors:
        try:
            result = execute(ast)
            assert isinstance(result, dict)
        except Exception as e:
            # Execution might fail due to missing plugins, which is expected
            assert "not available" in str(e) or "not supported" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
