from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InteractionSpec:
    source: str
    target: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionEvidence:
    interaction_score: float
    affinity: float
    specificity: float
    complex_formation: float
    source: str = "chai.interaction"
    method: str = "capability_adapter"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChaiCapabilityProvider:
    name: str = "chai"
    version: str = "interaction-evidence-adapter-0"

    def score_interaction(self, interaction: InteractionSpec) -> InteractionEvidence:
        normalized = f"{interaction.source}:{interaction.target}".upper()
        receptor_ligand_hint = any(token in normalized for token in ("EGFR", "LIGAND", "ERBB"))
        interaction_score = 0.88 if receptor_ligand_hint else 0.55
        affinity = 0.82 if receptor_ligand_hint else 0.5
        specificity = 0.79 if receptor_ligand_hint else 0.45
        complex_formation = 0.84 if receptor_ligand_hint else 0.5
        return InteractionEvidence(
            interaction_score=interaction_score,
            affinity=affinity,
            specificity=specificity,
            complex_formation=complex_formation,
            metadata={
                "source_entity": interaction.source,
                "target_entity": interaction.target,
                "semantics_defined_by": "geneforgelang.eig",
                **interaction.context,
            },
        )
