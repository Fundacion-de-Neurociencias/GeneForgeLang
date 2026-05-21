from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from geneforgelang.adapters.carbon import CarbonCapabilities
from geneforgelang.semantic import (
    AgentAction,
    BiologicalObservabilityFramework,
    BiologicalScale,
    CapabilityRegistry,
    CompressibilityEngine,
    EpistemicStatus,
    EvidenceNode,
    EvidenceView,
    HypothesisNode,
    InferenceNode,
    KnowledgeValidityWindow,
    MultiViewEvidenceTriangulator,
    ObservationStatus,
    Perturbation,
    PerturbationAlgebra,
    PerturbationSet,
    ScaleCompiler,
    SemanticDocument,
    SemanticRuntime,
    UncertaintyNode,
    VariantSpec,
)
from geneforgelang.semantic.epistemic import CausalInvalidationEngine
from geneforgelang.semantic.latent import LatentSpaceService
from geneforgelang.semantic.provenance import ProvenanceEdge, ProvenanceGraph, ProvenanceNode


class EntityType:
    GENE = "GENE"
    TRANSCRIPT = "TRANSCRIPT"
    PROTEIN = "PROTEIN"


class RelationType:
    DERIVES_FROM = "DERIVES_FROM"
    REGULATES = "REGULATES"
    CAUSES = "CAUSES"


@dataclass
class Entity:
    id: str
    type: str
    attrs: dict[str, object] = field(default_factory=dict)

    def get_attr(self, key: str, default: object = None) -> object:
        return self.attrs.get(key, default)

    def set_attr(self, key: str, value: object) -> None:
        self.attrs[key] = value


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    type: str


@dataclass
class BiologicalState:
    entities: dict[str, Entity] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.id] = entity

    def add_relation(self, relation: Relation) -> None:
        self.relations.append(relation)

    def get_entity(self, entity_id: str) -> Entity | None:
        return self.entities.get(entity_id)

    def get_downstream_entities(self, entity_id: str) -> list[str]:
        downstream: list[str] = []
        visited = {entity_id}
        frontier = [entity_id]
        while frontier:
            current = frontier.pop()
            for relation in self.relations:
                if relation.source == current and relation.target not in visited:
                    visited.add(relation.target)
                    downstream.append(relation.target)
                    frontier.append(relation.target)
        return downstream

    def fork(self) -> "BiologicalState":
        return deepcopy(self)


def test_carbon_is_registered_as_capability_engine():
    registry = CapabilityRegistry()
    carbon = CarbonCapabilities()

    registry.register(carbon)

    assert registry.available() == ("carbon",)
    score = registry.get("carbon").score_variant(VariantSpec("TP53", "R175H"))
    assert score.source == "carbon.vep"
    assert score.confidence > 0


def test_capability_registry_rejects_non_protocol_engine():
    registry = CapabilityRegistry()

    with pytest.raises(TypeError, match="CapabilityEngine protocol"):
        registry.register(object())  # type: ignore[arg-type]


def test_capability_registry_missing_engine_error_lists_available():
    registry = CapabilityRegistry()
    registry.register(CarbonCapabilities())

    with pytest.raises(KeyError, match="missing.*carbon"):
        registry.get("missing")


def test_semantic_document_serializes_epistemic_nodes():
    document = SemanticDocument(
        nodes=[
            HypothesisNode(
                id="h1",
                statement="TP53 R175H causes dominant negative behavior",
                confidence=0.71,
                evidence=("carbon.vep", "clinvar.prior"),
            ),
            UncertaintyNode(
                id="u1",
                value=0.29,
                kind="epistemic",
                sources=("carbon.vep",),
                method="calibrated_prior",
            ),
        ]
    )

    serialized = document.to_dict()

    assert serialized["version"] == "gfl.semantic.v2"
    assert serialized["nodes"][0]["node_type"] == "HypothesisNode"
    assert serialized["nodes"][1]["kind"] == "epistemic"


def test_semantic_document_serializes_nested_dataclasses_recursively():
    document = SemanticDocument(
        nodes=[
            InferenceNode(
                id="i1",
                conclusion="derived claim",
                provenance={"evidence": EvidenceNode(id="e1", source="assay", claim="primary claim")},
            )
        ]
    )

    serialized = document.to_dict()

    assert serialized["nodes"][0]["provenance"]["evidence"]["source"] == "assay"


def test_perturbation_algebra_tracks_non_linear_risk():
    algebra = PerturbationAlgebra()
    first = PerturbationSet((Perturbation("missense", "BRCA2", {"variant": "R3052W"}),))
    second = PerturbationSet((Perturbation("splice_site_disruption", "BRCA2", {"exon": 11}),))

    combined = algebra.compose(first, second)

    assert combined.operator == "compose"
    assert combined.interaction_uncertainty > first.interaction_uncertainty
    assert combined.nonlinear_effect_risk >= 0.2


def test_observability_distinguishes_absence_from_unobserved():
    framework = BiologicalObservabilityFramework()

    absent = framework.assess("TP53_binding", observed=False)
    unobserved = framework.assess("TP53_binding", observed=None)
    impossible = framework.assess("latent_state", observed=None, observable=False)

    assert absent.status == ObservationStatus.OBSERVED_ABSENT
    assert unobserved.status == ObservationStatus.NOT_OBSERVED
    assert impossible.status == ObservationStatus.NOT_OBSERVABLE


def test_causal_invalidation_marks_downstream_entities():
    state = BiologicalState()
    state.add_entity(Entity("TP53", EntityType.GENE))
    state.add_entity(Entity("TP53_mRNA", EntityType.TRANSCRIPT))
    state.add_entity(Entity("p53", EntityType.PROTEIN))
    state.add_relation(Relation("TP53", "TP53_mRNA", RelationType.DERIVES_FROM))
    state.add_relation(Relation("TP53_mRNA", "p53", RelationType.DERIVES_FROM))

    record = CausalInvalidationEngine().invalidate(state, "TP53", "variant reclassified")

    assert record.downstream == ("TP53_mRNA", "p53")
    assert state.get_entity("p53").get_attr("epistemic_status") == "invalidated"


def test_multiview_triangulation_preserves_source_uncertainty():
    estimate = MultiViewEvidenceTriangulator().estimate(
        [
            EvidenceView("carbon.vep", "TP53:R175H:pathogenicity", 0.91, "epistemic"),
            EvidenceView("clinvar.prior", "TP53:R175H:pathogenicity", 0.98, "structural"),
        ]
    )

    assert estimate.confidence > 0.9
    assert estimate.conflict_score > 0
    assert estimate.view_uncertainties["clinvar.prior"] == "structural"


def test_multiview_triangulation_models_contradictions_explicitly():
    estimate = MultiViewEvidenceTriangulator().estimate(
        [
            EvidenceView(
                "functional_assay",
                "TP53:R175H:pathogenicity",
                0.91,
                metadata={"polarity": "supports"},
            ),
            EvidenceView(
                "literature_reanalysis",
                "TP53:R175H:pathogenicity",
                0.88,
                metadata={"polarity": "refutes"},
            ),
        ]
    )

    assert estimate.contradiction_edges == (("functional_assay", "literature_reanalysis"),)
    assert estimate.consensus_instability > 0


def test_compressibility_profile_is_not_single_scalar():
    profile = CompressibilityEngine().profile(
        "TP53:R175H",
        evidence_count=5,
        conflict_score=0.2,
        observability_dependence=0.7,
    )

    assert profile.molecular > profile.organism
    assert profile.causal_entropy > 0
    assert profile.representation_stability != profile.molecular


def test_scale_compiler_crosses_biological_scales():
    compilation = ScaleCompiler().compile(
        BiologicalScale.PHENOTYPE,
        BiologicalScale.SEQUENCE_CONSTRAINTS,
    )

    assert compilation.steps[0] == BiologicalScale.PHENOTYPE
    assert compilation.steps[-1] == BiologicalScale.SEQUENCE_CONSTRAINTS
    assert compilation.confidence < 1.0


def test_latent_space_uses_capability_embeddings_not_backend_semantics():
    service = LatentSpaceService(CarbonCapabilities())

    neighbors = service.nearest("ACGT", {"same": "ACGT", "different": "AAAA"}, top_k=1)

    assert neighbors[0].item_id == "same"


def test_semantic_runtime_accumulates_epistemic_beliefs():
    runtime = SemanticRuntime()
    runtime.register_backend(CarbonCapabilities())

    score = runtime.score_variant(VariantSpec("TP53", "R175H"))

    assert score.source == "carbon.vep"
    assert runtime.epistemic.belief_state.confidence("TP53:R175H:pathogenicity") is not None
    assert runtime.epistemic.belief_state.statuses["TP53:R175H:pathogenicity"] == EpistemicStatus.SUPPORTED
    assert runtime.epistemic.provenance.downstream_of("carbon.vep")


def test_belief_state_transitions_to_conflicted_when_evidence_contradicts():
    runtime = SemanticRuntime()

    runtime.epistemic.ingest_evidence(
        [
            EvidenceView("assay_a", "claim:x", 0.9, metadata={"polarity": "supports"}),
            EvidenceView("assay_b", "claim:x", 0.9, metadata={"polarity": "refutes"}),
        ]
    )

    assert runtime.epistemic.belief_state.statuses["claim:x"] == EpistemicStatus.CONFLICTED
    assert runtime.epistemic.belief_state.transitions[-1].to_status == EpistemicStatus.CONFLICTED


def test_provenance_graph_tracks_lineage_and_validity():
    graph = ProvenanceGraph()
    graph.add_node(ProvenanceNode("clinvar.prior", "evidence_source", "ClinVar"))
    graph.add_node(
        ProvenanceNode(
            "variant_claim",
            "claim",
            "TP53:R175H pathogenicity",
            validity=KnowledgeValidityWindow(valid_from=datetime.now(timezone.utc)),
        )
    )
    graph.add_edge(ProvenanceEdge("clinvar.prior", "variant_claim", "supports"))

    assert graph.downstream_of("clinvar.prior") == ("variant_claim",)
    assert graph.nodes["variant_claim"].validity.is_active()


def test_agent_execution_requires_determinism_and_checkpoints_state():
    runtime = SemanticRuntime()
    state = BiologicalState(entities={"TP53": Entity("TP53", EntityType.GENE)})

    runtime.agent_execution.validate_action(AgentAction("inspect", "TP53"))
    checkpoint = runtime.agent_execution.checkpoint(state, ())
    state.get_entity("TP53").set_attr("status", "mutated")

    assert checkpoint.state.get_entity("TP53").get_attr("status") is None
