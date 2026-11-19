import pytest
from geneforgelang.extensions.protein_evidence.esm_bridge import (
    ESMBridgeValidationError,
    export_to_geneforge_adapter,
    import_embedding,
    validate_embedding_schema,
)


def test_import_embedding_converts_esm_payload_to_metadata_nodes():
    ast = import_embedding(
        {
            "protein": "TP53",
            "sequence": "MEEPQSDPSV",
            "embedding": [0.1, 0.2, 0.3],
            "embedding_model": "esm2_t33_650M",
            "model_structure_confidence": 0.87,
            "embedding_score": 0.62,
            "external_ref": "s3://bucket/tp53.embedding.json",
        }
    )

    assert ast["extension"] == "protein_evidence"
    assert ast["semantic_role"] == "metadata_only"
    assert [node["node_type"] for node in ast["nodes"]] == [
        "ProteinNode",
        "SequenceNode",
        "EmbeddingReferenceNode",
        "EvidenceScoreNode",
        "EvidenceScoreNode",
    ]
    assert ast["nodes"][2]["source"] == "esm2_t33_650M"
    assert ast["nodes"][2]["metadata"]["embedding_dimensions"] == 3


def test_validate_embedding_schema_allows_external_reference_linking():
    assert validate_embedding_schema({"embedding_ref": "sha256:abc", "model": "esm"}) is True


@pytest.mark.parametrize(
    "payload",
    [
        {"embedding": [0.1], "causal_claims": ["TP53 causes apoptosis"]},
        {"embedding": [0.1], "semantic_completion": "complete pathway"},
        {"embedding": [0.1], "rule_synthesis": ["if embedding then rule"]},
        {"embedding": ["bad"]},
        {"embedding": [0.1], "unknown": "field"},
    ],
)
def test_validate_embedding_schema_rejects_semantic_operations(payload):
    with pytest.raises(ESMBridgeValidationError):
        validate_embedding_schema(payload)


def test_export_to_geneforge_adapter_documents_syntax_only_contract():
    contract = export_to_geneforge_adapter()

    assert contract["mode"] == "syntax_interop"
    assert contract["semantic_role"] == "metadata_only"
    assert "rule_synthesis_from_embeddings" in contract["rejected_operations"]
    assert "score_promotion_to_truth_support" in contract["rejected_operations"]
    assert "external_reference_linking" in contract["allowed_operations"]
