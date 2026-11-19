"""
Evidence Conflict Resolver

This module handles formal resolution of epistemic collisions between EvidenceContracts.
It goes beyond simple weighted averaging by categorizing conflicts into distinct
typologies (Scale, Temporal, Observational) and applying specific resolution algebra
to determine if a true contradiction exists, or merely a misalignment in domain.
"""

from enum import Enum, auto
from typing import List, Optional

from geneforgelang.semantic.evidence.contract import ContradictionState, EvidenceContract, ScaleAnchor


class ConflictType(Enum):
    ONTOLOGICAL = auto()  # Different entities mapped to same ID
    OBSERVATIONAL = auto()  # Same entity, direct contradiction in claim
    SCALE_MISALIGNMENT = auto()  # True at one scale (e.g. sequence), false at another (e.g. phenotype)
    TEMPORAL = auto()  # Valid at different time windows
    EXPERIMENTAL = auto()  # Artifact of different experimental resolutions


class ResolutionAction(Enum):
    ISOLATE = auto()  # Keep both contracts valid but isolated in their respective domains (e.g. scales)
    CONTEST = auto()  # True epistemic collision. Downgrade both (or the composition) to CONTESTED.
    SUPERSEDE = auto()  # One contract epistemically dominates the other.


class ConflictResolutionResult:
    def __init__(
        self, conflict_type: ConflictType, action: ResolutionAction, dominating_contract_id: Optional[str] = None
    ):
        self.conflict_type = conflict_type
        self.action = action
        self.dominating_contract_id = dominating_contract_id


class EvidenceConflictResolver:
    """
    Evaluates epistemic collisions between multiple evidence contracts and
    determines the formal resolution action.
    """

    @staticmethod
    def resolve(c1: EvidenceContract, c2: EvidenceContract) -> ConflictResolutionResult:
        # 1. Scale Misalignment Check
        if c1.scale_anchor != c2.scale_anchor:
            # Not a true contradiction. It's a scale boundary issue.
            return ConflictResolutionResult(ConflictType.SCALE_MISALIGNMENT, ResolutionAction.ISOLATE)

        # 2. Temporal Conflict Check
        v1_from = c1.temporal_validity.valid_from
        v2_from = c2.temporal_validity.valid_from

        # If they don't intersect, it's a temporal progression, not a contradiction.
        # But if they do intersect and claim opposite things, we must check if one supersedes.
        if v1_from > v2_from and c1.observability.resolution >= c2.observability.resolution:
            # Newer evidence with equal or better resolution dominates
            return ConflictResolutionResult(
                ConflictType.TEMPORAL, ResolutionAction.SUPERSEDE, dominating_contract_id=c1.contract_id
            )
        elif v2_from > v1_from and c2.observability.resolution >= c1.observability.resolution:
            return ConflictResolutionResult(
                ConflictType.TEMPORAL, ResolutionAction.SUPERSEDE, dominating_contract_id=c2.contract_id
            )

        # 3. Experimental Observability Check
        # If one has vastly superior resolution and accessibility, it overrides observational artifacts
        if c1.observability.identifiability > c2.observability.identifiability + 0.3:
            return ConflictResolutionResult(
                ConflictType.EXPERIMENTAL, ResolutionAction.SUPERSEDE, dominating_contract_id=c1.contract_id
            )
        elif c2.observability.identifiability > c1.observability.identifiability + 0.3:
            return ConflictResolutionResult(
                ConflictType.EXPERIMENTAL, ResolutionAction.SUPERSEDE, dominating_contract_id=c2.contract_id
            )

        # 4. True Observational/Ontological Contradiction
        # Same scale, overlapping time, comparable observability, but different claims.
        # This is a hard collision.
        return ConflictResolutionResult(ConflictType.OBSERVATIONAL, ResolutionAction.CONTEST)
