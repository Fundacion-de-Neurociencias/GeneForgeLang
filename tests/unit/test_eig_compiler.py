from geneforgelang import export_evidence_graph
from geneforgelang.adapters.carbon import CarbonCapabilityProvider
from geneforgelang.adapters.chai import ChaiCapabilityProvider
from geneforgelang.eig import (
    BiologicalScale,
    CrossScaleCompiler,
    EvidenceGraphCompiler,
    PerturbationSet,
)
from geneforgelang.semantic.capabilities import VariantSpec


def test_cross_scale_compiler_supports_required_directions():
    compiler = CrossScaleCompiler()

    phenotype_to_variant = compiler.phenotype_to_variant()
    variant_to_phenotype = compiler.variant_to_phenotype()

    assert phenotype_to_variant.steps == (
        BiologicalScale.PHENOTYPE,
        BiologicalScale.TISSUE,
        BiologicalScale.CELL,
        BiologicalScale.PATHWAY,
        BiologicalScale.DOMAIN,
        BiologicalScale.PROTEIN,
        BiologicalScale.TRANSCRIPT,
        BiologicalScale.GENE,
        BiologicalScale.VARIANT,
    )
    assert variant_to_phenotype.steps == tuple(reversed(phenotype_to_variant.steps))


def test_evidence_graph_compiler_produces_auditable_graph_from_line_program():
    program = """
    entity TP53
    perturbation missense(R175H)
    infer downstream effects
    """
    graph = EvidenceGraphCompiler(CarbonCapabilityProvider()).compile(program)
    exported = graph.to_dict()

    assert exported["kind"] == "EvidenceGraph"
    assert exported["metadata"]["exportable_to"] == ("PharmaOracle", "Neurodiagnoses")
    assert {node["scale"] for node in exported["nodes"]} >= {"gene", "pathway", "phenotype"}
    assert exported["edges"]
    assert exported["evidence"]
    assert exported["hypotheses"][0]["claim"] == "TP53 perturbation may alter downstream phenotype"
    assert exported["hypotheses"][0]["evidence"]
    assert exported["uncertainty"]


def test_public_api_exports_evidence_graph():
    exported = export_evidence_graph(
        {"entity": "TP53", "perturbation": "missense(R175H)", "infer": "downstream effects"}
    )

    assert exported["kind"] == "EvidenceGraph"
    assert exported["version"] == "gfl.eig.v1"


def test_perturbation_set_supports_mandated_perturbation_algebra():
    perturbations = PerturbationSet.from_specs(
        "gene:TP53",
        [
            "missense(R175H)",
            "splice(c.375+1G>T)",
            "promoter(low_activity)",
            "enhancer(disrupted)",
            {"type": "cnv", "parameters": {"copy_number": 1}},
            "knockout",
            "overexpression",
        ],
    )

    assert len(perturbations.to_eig()) == 7
    assert perturbations.by_type("missense")[0].description == "missense(R175H)"


def test_carbon_provider_exposes_only_capability_surface_for_semantic_compilation():
    provider = CarbonCapabilityProvider()

    assert provider.embedding("ACGT").values == (0.25, 0.25, 0.25, 0.25)
    assert provider.retrieve_context("TP53").metadata["semantics_defined_by"] == "geneforgelang.eig"
    assert provider.species_similarity("ACGT", "ACGA").value == 0.75
    assert provider.score_variant(VariantSpec("TP53", "R175H")).confidence > 0.0
    assert not hasattr(provider, "complete_sequence")


def test_chai_generates_evidence_while_gfl_generates_biological_meaning():
    program = """
    entity EGFR
    interacts_with ligand X
    effect:
        activation(MAPK)
    confidence:
        chai_interaction_score
    """

    exported = EvidenceGraphCompiler(ChaiCapabilityProvider()).export_evidence_graph(program)

    assert exported["kind"] == "EvidenceGraph"
    assert any(node["label"] == "EGFR" for node in exported["nodes"])
    assert any(node["label"] == "X" and node["attributes"]["role"] == "ligand" for node in exported["nodes"])
    assert any(node["label"] == "MAPK" and node["scale"] == "pathway" for node in exported["nodes"])
    assert any(edge["relation"] == "interacts_with" for edge in exported["edges"])
    assert any(edge["relation"] == "forms_complex" for edge in exported["edges"])
    assert any(edge["relation"] == "activates" for edge in exported["edges"])
    chai_evidence = [evidence for evidence in exported["evidence"] if evidence["source"] == "chai.interaction"]
    assert chai_evidence
    assert "chai_interaction_score" in chai_evidence[0]["provenance"]
    assert chai_evidence[0]["provenance"]["semantics_defined_by"] == "geneforgelang.eig"
    assert exported["hypotheses"][0]["claim"] == "EGFR-X complex activation affects MAPK"
