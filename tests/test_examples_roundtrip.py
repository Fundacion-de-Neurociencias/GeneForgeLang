from pathlib import Path

import pytest

from geneforgelang.core.api import parse, validate

EXAMPLES_DIR = Path("examples")


@pytest.mark.parametrize(
    "path,expect_errors",
    [
        (EXAMPLES_DIR / "syntax" / "example_valid_semantics.gfl", False),
        (EXAMPLES_DIR / "syntax" / "example_invalid_semantics.gfl", True),
    ],
)
def test_known_validity_examples(path: Path, expect_errors: bool):
    if not path.exists():
        pytest.skip(f"Test file does not exist: {path}")

    text = path.read_text(encoding="utf-8")
    ast = parse(text)
    assert isinstance(ast, dict)
    errs = validate(ast)
    if expect_errors:
        assert errs, f"Expected validation errors for {path}"
    else:
        assert not errs, f"Did not expect validation errors for {path}: {errs}"


def test_smoke_all_examples_parse():
    for p in EXAMPLES_DIR.glob("*.gfl"):
        text = p.read_text(encoding="utf-8")
        ast = parse(text)
        # Accept dict (YAML parsed), None (invalid YAML), or str (legacy DSL passthrough)
        assert isinstance(ast, (dict, type(None), str)), f"Parse returned unexpected type for {p}"
