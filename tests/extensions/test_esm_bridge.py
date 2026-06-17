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

from geneforgelang.extensions.protein_evidence.esm_bridge import (
    ESMBridgeValidationError,
    SemanticBoundaryViolation,
    export_to_geneforge_adapter,
    import_embedding,
    validate_embedding_schema,
)


def _payload():
    return {
        "sequence_embedding": [0.1, -0.2, 0.3],
        "structure_confidence": 0.81,
        "neighborhood_hits": [{"neighbor_id": "ESM-1", "similarity": 0.7, "rank": 1}],
        "plausibility_score": 0.77,
        "source_model": "local-esm-scaffold",
        "provenance": {
            "adapter_role": "external_read_only_evidence",
            "backend": "local_scaffold",
            "source_model": "local-esm-scaffold",
            "semantic_mutation": False,
            "causal_completion": False,
        },
    }


def test_validate_embedding_schema_accepts_adapter_payload():
    assert validate_embedding_schema(_payload()) is True


def test_import_embedding_returns_metadata_only_node():
    node = import_embedding(_payload())

    assert node["node_type"] == "EmbeddingReferenceNode"
    assert node["provider"] == "local-esm-scaffold"
    assert node["semantic_role"] == "metadata_only"
    assert node["provenance"]["semantic_mutation"] is False
    assert node["provenance"]["causal_completion"] is False


def test_validate_embedding_schema_rejects_semantic_mutation():
    payload = _payload()
    payload["provenance"]["semantic_mutation"] = True

    with pytest.raises(ESMBridgeValidationError):
        validate_embedding_schema(payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "pathogenicity_prediction",
        "causal_effect",
        "inferred_mechanism",
        "disease_likelihood",
    ],
)
def test_validate_embedding_schema_rejects_forbidden_semantic_fields(field_name):
    payload = _payload()
    payload["neighborhood_hits"][0][field_name] = 0.9

    with pytest.raises(SemanticBoundaryViolation):
        validate_embedding_schema(payload)


def test_export_to_geneforge_adapter_declares_read_only_contract():
    contract = export_to_geneforge_adapter()

    assert contract["adapter"] == "esm"
    assert contract["role"] == "external_read_only_evidence"
    assert "causal_effect" in contract["forbidden_fields"]
    assert contract["semantic_mutation"] is False
    assert contract["causal_completion"] is False
