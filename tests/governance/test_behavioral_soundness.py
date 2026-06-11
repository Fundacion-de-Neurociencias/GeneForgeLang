import pytest

from geneforgelang.core.parser import parse_gfl
from geneforgelang.governance.behavioral.semantic_hash import semantic_hash
from geneforgelang.governance.behavioral.semantic_projection import project


def test_projection_determinism():
    """1. Projection determinism"""
    source = "PROTEIN:\n  name: TP53\n  line_number: 10\n"
    ast = parse_gfl(source)
    proj1 = project(ast)
    proj2 = project(ast)
    proj3 = project(ast)
    assert proj1 == proj2 == proj3


def test_canonicalization_idempotence():
    """2. Canonicalization idempotence"""
    source = "PROTEIN:\n  name: TP53\n"
    ast = parse_gfl(source)
    proj1 = project(ast)
    proj2 = project(proj1)
    assert proj1 == proj2


def test_equivalence_class_collapse():
    """3. Equivalence-class collapse"""
    ast_upper = parse_gfl("protein: TP53")
    ast_lower = parse_gfl("protein: tp53")
    assert semantic_hash(project(ast_upper)) == semantic_hash(project(ast_lower))


def test_noise_resistance():
    """4. Noise resistance"""
    ast_clean = parse_gfl("gene: BRCA1")
    ast_noisy = parse_gfl(
        "gene: BRCA1\nline_number: 42\nparse_trace: token_gene\nannotations:\n  - type: comment\n    value: this is a comment"
    )
    assert semantic_hash(project(ast_clean)) == semantic_hash(project(ast_noisy))


def test_signal_sensitivity():
    """5. Signal sensitivity"""
    ast_1 = parse_gfl("gene: BRCA1")
    ast_2 = parse_gfl("gene: BRCA2")
    assert semantic_hash(project(ast_1)) != semantic_hash(project(ast_2))
