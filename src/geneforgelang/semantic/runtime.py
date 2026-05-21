from __future__ import annotations

from dataclasses import dataclass, field

from geneforgelang.semantic.agent import AgentExecutionLayer
from geneforgelang.semantic.capabilities import CapabilityEngine, CapabilityRegistry, VariantScore, VariantSpec
from geneforgelang.semantic.epistemic import EpistemicRuntime, EvidenceView


@dataclass
class SemanticRuntime:
    capabilities: CapabilityRegistry = field(default_factory=CapabilityRegistry)
    epistemic: EpistemicRuntime = field(default_factory=EpistemicRuntime)
    agent_execution: AgentExecutionLayer = field(init=False)

    def __post_init__(self) -> None:
        self.agent_execution = AgentExecutionLayer(self.epistemic.provenance)

    def register_backend(self, engine: CapabilityEngine) -> None:
        self.capabilities.register(engine)

    def score_variant(self, variant: VariantSpec) -> VariantScore:
        scores = [engine.score_variant(variant) for engine in self.capabilities.engines()]
        if not scores:
            raise RuntimeError("no capability engines are registered")
        views = [
            EvidenceView(
                source=score.source,
                claim=f"{variant.entity_id}:{variant.variant}:pathogenicity",
                confidence=score.confidence,
                metadata={"value": score.value, "method": score.method},
            )
            for score in scores
        ]
        self.epistemic.ingest_evidence(views)
        return max(scores, key=lambda score: score.confidence)
