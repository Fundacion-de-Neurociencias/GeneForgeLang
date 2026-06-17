import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "src" / "geneforgelang"
sys.modules.setdefault("geneforgelang", types.ModuleType("geneforgelang")).__path__ = [
    str(PACKAGE_ROOT)
]
sys.modules.setdefault(
    "geneforgelang.extensions", types.ModuleType("geneforgelang.extensions")
).__path__ = [str(PACKAGE_ROOT / "extensions")]
sys.modules.setdefault(
    "geneforgelang.extensions.protein_evidence",
    types.ModuleType("geneforgelang.extensions.protein_evidence"),
).__path__ = [str(PACKAGE_ROOT / "extensions" / "protein_evidence")]

import pytest

from geneforgelang.extensions.protein_evidence.ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)
from geneforgelang.extensions.protein_evidence.grammar import (
    ProteinEvidenceSyntaxError,
    parse_protein_evidence,
)
from geneforgelang.extensions.protein_evidence.normalizer import normalize_protein_evidence


def test_parse_supported_protein_evidence_constructs():
    source = """
    PROTEIN("TP53")
    SEQUENCE("MEEPQSDPSV")
    EMBEDDING_REF("esm")
    STRUCTURE_CONFIDENCE(0.82)
    PLAUSIBILITY_SCORE(0.74)
    """

    nodes = parse_protein_evidence(source)

    assert [node["kind"] for node in nodes] == [
        "PROTEIN",
        "SEQUENCE",
        "EMBEDDING_REF",
        "STRUCTURE_CONFIDENCE",
        "PLAUSIBILITY_SCORE",
    ]


def test_normalize_to_canonical_metadata_nodes():
    nodes = normalize_protein_evidence(
        'PROTEIN("TP53") SEQUENCE("MEEPQSDPSV") EMBEDDING_REF("esm") '
        "STRUCTURE_CONFIDENCE(0.82) PLAUSIBILITY_SCORE(0.74)"
    )

    assert isinstance(nodes[0], ProteinNode)
    assert isinstance(nodes[1], SequenceNode)
    assert isinstance(nodes[2], EmbeddingReferenceNode)
    assert isinstance(nodes[3], EvidenceScoreNode)
    assert isinstance(nodes[4], EvidenceScoreNode)
    assert all(node.semantic_role == "metadata_only" for node in nodes)


def test_rejects_causal_claims_and_semantic_completion():
    with pytest.raises(ProteinEvidenceSyntaxError):
        parse_protein_evidence('EMBEDDING_REF("esm") infer likely pathogenic effect')

    with pytest.raises(ProteinEvidenceSyntaxError):
        parse_protein_evidence('PROTEIN("TP53") rule synthesis from embeddings')


def test_rejects_out_of_range_scores():
    with pytest.raises(ProteinEvidenceSyntaxError):
        parse_protein_evidence("PLAUSIBILITY_SCORE(1.4)")
