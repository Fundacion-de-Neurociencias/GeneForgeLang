import copy
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

from geneforgelang.extensions.protein_evidence.normalizer import to_metadata_ast


SEMANTIC_LATTICE_SENTINEL = {
    "ontology": {
        "causal_primitives": ("causes", "regulates", "inhibits"),
        "epistemic_states": ("observed", "hypothesized", "contradicted"),
    },
    "contradiction_resolution": "unchanged",
    "inference_semantics": "unchanged",
}


def test_esm_linked_syntax_does_not_alter_lattice_semantics():
    before = copy.deepcopy(SEMANTIC_LATTICE_SENTINEL)

    metadata = to_metadata_ast(
        'PROTEIN("TP53") SEQUENCE("MEEPQSDPSV") EMBEDDING_REF("esm") '
        "STRUCTURE_CONFIDENCE(0.91) PLAUSIBILITY_SCORE(0.88)"
    )

    assert metadata
    assert SEMANTIC_LATTICE_SENTINEL == before
    assert all(node["semantic_role"] == "metadata_only" for node in metadata)
    assert not any("causal" in node for node in metadata)
