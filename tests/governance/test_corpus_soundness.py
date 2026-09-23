import copy
import os
from pathlib import Path

import pytest

from geneforgelang.core.parser import parse_gfl
from geneforgelang.governance.behavioral.semantic_hash import semantic_hash
from geneforgelang.governance.behavioral.semantic_projection import project

CORPUS_DIR = Path(__file__).parents[2] / "tests" / "fixtures" / "real_world_corpus"


def get_corpus_files():
    if not CORPUS_DIR.exists():
        return []
    return list(CORPUS_DIR.glob("*.gfl"))


@pytest.mark.parametrize("filepath", get_corpus_files(), ids=lambda p: p.name)
def test_corpus_determinism_and_idempotence(filepath: Path):
    """
    Ensures that for every real-world document:
    1. Projection is deterministic.
    2. Projection is idempotent.
    """
    source = filepath.read_text(encoding="utf-8")
    ast = parse_gfl(source)
    if not ast:
        pytest.skip(f"Could not parse {filepath.name}")

    proj1 = project(ast)
    proj2 = project(ast)

    assert proj1 == proj2, f"Projection determinism failed for {filepath.name}"

    proj3 = project(proj1)
    assert proj1 == proj3, f"Projection idempotence failed for {filepath.name}"


@pytest.mark.parametrize("filepath", get_corpus_files(), ids=lambda p: p.name)
def test_corpus_noise_resistance(filepath: Path):
    """
    Ensures that injecting metadata/syntactic noise into a real AST
    does not alter its semantic projection hash.
    """
    source = filepath.read_text(encoding="utf-8")
    clean_ast = parse_gfl(source)
    if not clean_ast:
        pytest.skip(f"Could not parse {filepath.name}")

    noisy_ast = copy.deepcopy(clean_ast)

    # Inject noise
    if isinstance(noisy_ast, dict):
        noisy_ast["line_number"] = 999
        noisy_ast["parse_trace"] = ["Token.ID", "Token.COLON"]
        noisy_ast["annotations"] = [{"type": "comment", "value": "This is synthetic noise"}]
        # Sometimes source_file is attached
        noisy_ast["source_file"] = "fake_path.gfl"

    clean_hash = semantic_hash(project(clean_ast))
    noisy_hash = semantic_hash(project(noisy_ast))

    assert clean_hash == noisy_hash, f"Noise resistance failed for {filepath.name}"
