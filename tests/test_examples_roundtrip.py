from pathlib import Path

import pytest

from gfl.api import parse, validate


EXAMPLES_DIR = Path("examples")


@pytest.mark.parametrize(
    "path,expect_errors",
    [
        (EXAMPLES_DIR / "test_valid_semantics.gfl", False),
        (EXAMPLES_DIR / "test_invalid_semantics.gfl", True),
    ],
)
def test_known_validity_examples(path: Path, expect_errors: bool):
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
        assert isinstance(ast, (dict, type(None))), f"Parse returned unexpected type for {p}"
