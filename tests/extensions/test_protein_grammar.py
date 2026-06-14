import pytest
from geneforgelang.extensions.protein_evidence.ast_nodes import (
    EmbeddingReferenceNode,
    EvidenceScoreNode,
    ProteinNode,
    SequenceNode,
)
from geneforgelang.extensions.protein_evidence.grammar import ProteinEvidenceSyntaxError
from geneforgelang.extensions.protein_evidence.normalizer import (
    normalize_protein_evidence,
    normalize_to_dict,
)


def test_protein_evidence_syntax_normalizes_to_metadata_nodes():
    nodes = normalize_protein_evidence(
        """
        PROTEIN("TP53")
        SEQUENCE("MEEPQSDPSVINFER")
        EMBEDDING_REF("esm")
        MODEL_STRUCTURE_CONFIDENCE(0.82)
        EMBEDDING_SCORE(0.41)
        """
    )

    assert nodes == [
        ProteinNode(identifier="TP53"),
        SequenceNode(sequence="MEEPQSDPSVINFER"),
        EmbeddingReferenceNode(source="esm"),
        EvidenceScoreNode(score_type="model_structure_confidence", value=0.82),
        EvidenceScoreNode(score_type="embedding_score", value=0.41),
    ]
    assert all(node.semantic_role == "metadata_only" for node in nodes)


def test_normalize_to_dict_is_serializable_extension_ast():
    normalized = normalize_to_dict('PROTEIN("TP53"), EMBEDDING_REF("esm")')

    assert normalized["extension"] == "protein_evidence"
    assert normalized["semantic_role"] == "metadata_only"
    assert [node["node_type"] for node in normalized["nodes"]] == [
        "ProteinNode",
        "EmbeddingReferenceNode",
    ]


@pytest.mark.parametrize(
    "source",
    [
        'CAUSES("TP53", "apoptosis")',
        "PLAUSIBILITY_SCORE(0.99)",
        'EMBEDDING_SCORE("0.5")',
        "MODEL_STRUCTURE_CONFIDENCE(1.2)",
        'IF EMBEDDING_CLUSTER("x") THEN CAUSAL_EFFECT("y")',
    ],
)
def test_protein_evidence_syntax_rejects_semantic_or_invalid_forms(source):
    with pytest.raises(ProteinEvidenceSyntaxError):
        normalize_protein_evidence(source)
