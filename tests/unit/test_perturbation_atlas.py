"""Unit tests for PerturbationAtlasContract, ReasoningAtlasCompiler, and GFL validation.

Grounded in the distributed biological reasoning framework (Sun et al., 2026, bioRxiv;
Shi et al., 2026, bioRxiv; OpenAI, Scripps Research, PerturbAI).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from geneforgelang.core.gftypes import (
    GFLAST,
    AtlasModality,
    CellAtlasReference,
    ParalogDivergenceContract,
    PerturbationAtlasContract,
    PerturbationAtlasTarget,
    PhenotypicRelationshipType,
    ReasoningAtlasEdge,
    ReasoningAtlasGraph,
    SwarmGranularity,
    SwarmReasoningPolicy,
    VirtualCellPerturbationContract,
)
from geneforgelang.core.reasoning_atlas import ReasoningAtlasCompiler
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_perturbation_atlas_enums_and_dataclasses() -> None:
    """Verify all enums and dataclasses instantiate with expected defaults."""
    assert str(AtlasModality.IN_VIVO_PERTURB_SEQ) == "in_vivo_perturb_seq"
    assert str(SwarmGranularity.PER_PERTURBATION) == "per_perturbation"
    assert str(PhenotypicRelationshipType.OPPOSING) == "opposing"
    assert str(CellAtlasReference.SHI_BRAIN_PERTURB_SEQ) == "shi_brain_perturb_seq"
    assert str(CellAtlasReference.PERTURBAI_BRAIN_ATLAS) == "perturbai_brain_atlas"

    policy = SwarmReasoningPolicy()
    assert policy.agent_granularity == SwarmGranularity.PER_PERTURBATION
    assert policy.literature_grounding is True
    assert policy.min_expert_preference_score == 0.75
    assert policy.synthesis_aggregator == "reasoning_atlas"

    target = PerturbationAtlasTarget(
        gene="DCTN1",
        pathway_focus="cholesterol_metabolism",
        target_cell_types=["cortical_neuron"],
    )
    assert target.gene == "DCTN1"
    assert target.pathway_focus == "cholesterol_metabolism"
    assert target.target_cell_types == ["cortical_neuron"]

    paralog = ParalogDivergenceContract(
        evaluate_paralog_opposition=True,
        pair=["GRIN2A", "GRIN2B"],
        min_transcriptional_divergence=0.35,
    )
    assert paralog.pair == ["GRIN2A", "GRIN2B"]
    assert paralog.min_transcriptional_divergence == 0.35


def test_perturbation_atlas_contract_roundtrip() -> None:
    """Test full serialization roundtrip of PerturbationAtlasContract."""
    contract = PerturbationAtlasContract(
        name="whole_brain_crispr_screen",
        organism="Mus musculus",
        dataset_ref="doi:10.64898/2026.10.15.759436v1",
        cell_atlas_size=7700000,
        modality=AtlasModality.IN_VIVO_PERTURB_SEQ,
        perturbation_targets=[
            PerturbationAtlasTarget(
                gene="DCTN1",
                pathway_focus="cholesterol_metabolism",
                target_cell_types=["cortical_neuron"],
                expected_phenotype="lipid_accumulation",
                causal_transition_refs=["CAUSAL_NODE_1"],
            ),
            PerturbationAtlasTarget(gene="GRIN2A"),
            PerturbationAtlasTarget(gene="GRIN2B"),
        ],
        swarm_policy=SwarmReasoningPolicy(
            agent_granularity=SwarmGranularity.PER_PERTURBATION,
            literature_grounding=True,
            min_expert_preference_score=0.75,
        ),
        divergence_check=ParalogDivergenceContract(
            evaluate_paralog_opposition=True,
            pair=["GRIN2A", "GRIN2B"],
            min_transcriptional_divergence=0.35,
        ),
        mcp_endpoint="https://sites-publish-check-20261021.as-alexander-sun.chatgpt.site/api/shi-mcp",
        virtual_cell_link="sim_vc_dctn1",
    )

    data = contract.to_dict()
    assert data["name"] == "whole_brain_crispr_screen"
    assert data["cell_atlas_size"] == 7700000
    assert len(data["perturbation_targets"]) == 3
    assert data["mcp_endpoint"].startswith("https://")
    assert data["virtual_cell_link"] == "sim_vc_dctn1"

    reconstructed = PerturbationAtlasContract.from_dict(data)
    assert reconstructed.name == contract.name
    assert reconstructed.cell_atlas_size == contract.cell_atlas_size
    assert len(reconstructed.perturbation_targets) == 3
    assert reconstructed.perturbation_targets[0].gene == "DCTN1"
    assert reconstructed.divergence_check is not None
    assert reconstructed.divergence_check.pair == ["GRIN2A", "GRIN2B"]


def test_gfl_ast_roundtrip_with_perturbation_atlas() -> None:
    """Test GFLAST serialization and deserialization with perturbation_atlas block."""
    contract = PerturbationAtlasContract(
        name="brain_atlas_test",
        organism="Mus musculus",
        dataset_ref="shi_2026",
        perturbation_targets=[PerturbationAtlasTarget(gene="DCTN1")],
    )

    ast = GFLAST()
    ast.perturbation_atlas = contract

    ast_dict = ast.to_dict()
    assert "perturbation_atlas" in ast_dict
    assert ast_dict["perturbation_atlas"]["name"] == "brain_atlas_test"

    restored_ast = GFLAST.from_dict(ast_dict)
    assert isinstance(restored_ast.perturbation_atlas, PerturbationAtlasContract)
    assert restored_ast.perturbation_atlas.name == "brain_atlas_test"


def test_reasoning_atlas_compiler_causality_graph() -> None:
    """Test compilation into ReasoningAtlasGraph, paralog opposition edges, and pathway synergy."""
    contract = PerturbationAtlasContract(
        name="brain_screen_compiler_test",
        organism="Mus musculus",
        dataset_ref="doi:10.64898/2026.10.15.759436v1",
        perturbation_targets=[
            PerturbationAtlasTarget(
                gene="DCTN1",
                pathway_focus="cholesterol_metabolism",
                target_cell_types=["cortical_neuron"],
            ),
            PerturbationAtlasTarget(
                gene="NPC1",
                pathway_focus="cholesterol_metabolism",
                target_cell_types=["cortical_neuron"],
            ),
            PerturbationAtlasTarget(gene="GRIN2A"),
            PerturbationAtlasTarget(gene="GRIN2B"),
        ],
        divergence_check=ParalogDivergenceContract(
            evaluate_paralog_opposition=True,
            pair=["GRIN2A", "GRIN2B"],
            min_transcriptional_divergence=0.35,
        ),
        mcp_endpoint="https://sites-publish-check-20261021.as-alexander-sun.chatgpt.site/api/shi-mcp",
    )

    compiler = ReasoningAtlasCompiler(contract)
    graph = compiler.compile()

    assert isinstance(graph, ReasoningAtlasGraph)
    assert graph.atlas_name == "brain_screen_compiler_test"
    assert set(graph.nodes) == {"DCTN1", "NPC1", "GRIN2A", "GRIN2B"}

    # 1. Paralog opposition edge
    opposing_edges = [e for e in graph.edges if e.relationship_type == PhenotypicRelationshipType.OPPOSING]
    assert len(opposing_edges) == 1
    assert opposing_edges[0].source_gene == "GRIN2A"
    assert opposing_edges[0].target_gene == "GRIN2B"
    assert opposing_edges[0].transcriptional_cosine_similarity == -0.35

    # 2. Pathway synergy edge (DCTN1 + NPC1 in cholesterol_metabolism)
    synergistic_edges = [e for e in graph.edges if e.relationship_type == PhenotypicRelationshipType.SYNERGISTIC]
    assert len(synergistic_edges) == 1
    assert {synergistic_edges[0].source_gene, synergistic_edges[0].target_gene} == {"DCTN1", "NPC1"}

    # 3. Paralog divergences record
    assert len(graph.paralog_divergences) == 1
    assert graph.paralog_divergences[0]["status"] == "CONFIRMED_OPPOSITION"

    # 4. MCP metadata binding
    assert "mcp_binding" in graph.metadata
    assert graph.metadata["mcp_binding"]["endpoint_url"].startswith("https://")


def test_reasoning_atlas_compiler_causal_nodes_and_virtual_cell_bridge() -> None:
    """Test generating CausalTransitionNode instances and VirtualCellPerturbationContract."""
    contract = PerturbationAtlasContract(
        name="bridge_test",
        organism="Mus musculus",
        dataset_ref="doi:10.64898/2026.10.15.759436v1",
        perturbation_targets=[
            PerturbationAtlasTarget(
                gene="DCTN1",
                pathway_focus="cholesterol_metabolism",
                target_cell_types=["cortical_neuron"],
                expected_phenotype="lipid_accumulation",
                causal_transition_refs=["CAUSAL_NEURODEGEN_1"],
            )
        ],
        virtual_cell_link="sim_vc_dctn1_cortical",
    )

    compiler = ReasoningAtlasCompiler(contract)

    # CausalTransitionNodes
    nodes = compiler.to_causal_nodes()
    assert len(nodes) == 1
    assert nodes[0].node_id == "CAUSAL_PERTURB_DCTN1"
    assert nodes[0].entity_name == "DCTN1"
    assert nodes[0].biological_state == "lipid_accumulation"
    assert "CAUSAL_NEURODEGEN_1" in nodes[0].outgoing_edges

    # VirtualCellPerturbationContract
    vc = compiler.to_virtual_cell_contract("DCTN1")
    assert isinstance(vc, VirtualCellPerturbationContract)
    assert vc.simulation_id == "sim_vc_dctn1_cortical"
    assert vc.target_gene_or_compound == "DCTN1"
    assert vc.cell_type == "cortical_neuron"
    assert vc.atlas_ref == CellAtlasReference.SHI_BRAIN_PERTURB_SEQ


def test_validator_rejects_invalid_perturbation_atlas_parameters() -> None:
    """Test validator detection and fixes for malformed perturbation_atlas parameters."""
    validator = EnhancedSemanticValidator()

    # 1. Missing name
    res1 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "dataset_ref": "doi:1234",
                "perturbation_targets": [{"gene": "DCTN1"}],
            }
        }
    )
    assert not res1.is_valid
    assert any("missing required 'name'" in e.message for e in res1.errors)

    # 2. Missing dataset_ref
    res2 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "perturbation_targets": [{"gene": "DCTN1"}],
            }
        }
    )
    assert not res2.is_valid
    assert any("missing required 'dataset_ref'" in e.message for e in res2.errors)

    # 3. Non-positive cell_atlas_size
    res3 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "dataset_ref": "doi:1234",
                "cell_atlas_size": -100,
                "perturbation_targets": [{"gene": "DCTN1"}],
            }
        }
    )
    assert not res3.is_valid
    assert any("cell_atlas_size must be a positive integer" in e.message for e in res3.errors)

    # 4. Empty perturbation_targets
    res4 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "dataset_ref": "doi:1234",
                "perturbation_targets": [],
            }
        }
    )
    assert not res4.is_valid
    assert any("perturbation_targets list cannot be empty" in e.message for e in res4.errors)

    # 5. Invalid preference score in swarm_policy
    res5 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "dataset_ref": "doi:1234",
                "perturbation_targets": [{"gene": "DCTN1"}],
                "swarm_policy": {"min_expert_preference_score": 1.5},
            }
        }
    )
    assert not res5.is_valid
    assert any("min_expert_preference_score must be a float between 0.0 and 1.0" in e.message for e in res5.errors)

    # 6. Single-gene paralog divergence pair
    res6 = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "dataset_ref": "doi:1234",
                "perturbation_targets": [{"gene": "DCTN1"}],
                "divergence_check": {"pair": ["GRIN2A"]},
            }
        }
    )
    assert not res6.is_valid
    assert any("requires at least one homologous gene pair" in e.message for e in res6.errors)


def test_validator_cross_contract_synergy_with_virtual_cell() -> None:
    """Test validator cross-contract checks between perturbation_atlas and virtual_cell."""
    validator = EnhancedSemanticValidator()

    # Mismatched virtual_cell_link triggers a warning
    res = validator.validate_ast(
        {
            "perturbation_atlas": {
                "name": "screen1",
                "dataset_ref": "doi:1234",
                "perturbation_targets": [{"gene": "DCTN1"}],
                "virtual_cell_link": "sim_different_id",
            },
            "virtual_cell": {
                "simulation_id": "sim_expected_id",
                "cell_type": "cortical_neuron",
                "target_gene_or_compound": "DCTN1",
            },
        }
    )
    assert any("virtual_cell_link 'sim_different_id' does not match simulation_id" in w.message for w in res.warnings)


def test_exemplar_whole_brain_perturbation_atlas_file_validates() -> None:
    """Verify that examples/whole_brain_perturbation_reasoning_atlas.gfl parses and validates cleanly."""
    exemplar_path = Path(__file__).parent.parent.parent / "examples" / "whole_brain_perturbation_reasoning_atlas.gfl"
    assert exemplar_path.exists(), f"Exemplar file missing at {exemplar_path}"

    with open(exemplar_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(data)
    assert result.is_valid, f"Validation failed with errors: {[e.message for e in result.errors]}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0

    # Also test compiling the exemplar
    compiler = ReasoningAtlasCompiler(data["perturbation_atlas"])
    graph = compiler.compile()
    assert graph.atlas_name == "whole_brain_crispr_screen"
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 1
    assert graph.edges[0].source_gene == "GRIN2A"
    assert graph.edges[0].target_gene == "GRIN2B"
    assert graph.edges[0].relationship_type == PhenotypicRelationshipType.OPPOSING
