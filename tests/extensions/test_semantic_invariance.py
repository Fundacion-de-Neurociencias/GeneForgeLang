from geneforgelang.extensions.protein_evidence.esm_bridge import import_embedding
from geneforgelang.extensions.protein_evidence.grammar import parse_protein_evidence
from geneforgelang.extensions.protein_evidence.normalizer import (
    normalize_calls,
    normalize_protein_evidence,
)
from geneforgelang.semantic.lattice import EpistemicState
from geneforgelang.semantic.ontology import SemanticOntology
from geneforgelang.semantic.runtime import SemanticRuntime


def test_parsing_esm_linked_syntax_does_not_alter_lattice_semantics():
    ideal_before = EpistemicState.get_ideal_state()
    null_before = EpistemicState.get_null_state()
    meet_before = ideal_before.meet(null_before)
    join_before = ideal_before.join(null_before)

    normalize_protein_evidence('PROTEIN("TP53") EMBEDDING_REF("esm") MODEL_STRUCTURE_CONFIDENCE(0.9)')
    import_embedding({"protein": "TP53", "embedding_ref": "sha256:abc", "model": "esm"})

    assert EpistemicState.get_ideal_state() == ideal_before
    assert EpistemicState.get_null_state() == null_before
    assert ideal_before.meet(null_before) == meet_before
    assert ideal_before.join(null_before) == join_before


def test_protein_evidence_nodes_do_not_register_semantic_ontology_terms():
    ontology = SemanticOntology()

    normalize_protein_evidence('PROTEIN("TP53") SEQUENCE("MEEPQSDPSV") EMBEDDING_REF("esm")')

    assert ontology.terms == {}
    assert not ontology.has("ProteinNode")
    assert not ontology.has("EmbeddingReferenceNode")


def test_normalization_is_referentially_transparent_for_parsed_calls():
    source = 'PROTEIN("TP53") EMBEDDING_REF("esm") EMBEDDING_SCORE(0.99)'

    assert normalize_calls(parse_protein_evidence(source)) == normalize_protein_evidence(source)


def test_model_scores_are_not_promoted_to_epistemic_truth_support():
    runtime = SemanticRuntime()
    statuses_before = dict(runtime.epistemic.belief_state.statuses)

    normalize_protein_evidence('PROTEIN("TP53") EMBEDDING_SCORE(0.99)')
    import_embedding({"embedding_ref": "sha256:abc", "embedding_score": 0.99, "model": "esm"})

    assert runtime.epistemic.belief_state.statuses == statuses_before
