"""
Genomic Governance & Policy Envelope Fabric
==========================================

This module defines the orthogonal governance and compliance layer for GeneForgeLang.
It strictly decouples Institutional Policy / Compliance (provenance scope, consent scopes,
jurisdiction, privacy risk, biosecurity) from the Epistemological Nucleus (EvidenceContract,
causal validity, contradiction states).

A PolicyEnvelope wraps any biological claim or EvidenceContract with institutional policy
metadata without mutating or contaminating the underlying scientific evidence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ProvenanceScope(Enum):
    PUBLIC = "PUBLIC"
    CONTROLLED = "CONTROLLED"
    CLINICAL = "CLINICAL"
    COMMERCIAL = "COMMERCIAL"
    RESTRICTED = "RESTRICTED"


class ConsentScope(Enum):
    RESEARCH_ONLY = "RESEARCH_ONLY"
    CLINICAL_CARE = "CLINICAL_CARE"
    COMMERCIAL_USE = "COMMERCIAL_USE"
    POPULATION_GENOMICS = "POPULATION_GENOMICS"
    UNKNOWN = "UNKNOWN"


class PopulationScope(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COHORT = "COHORT"
    POPULATION = "POPULATION"
    ANCESTRY_SPECIFIC = "ANCESTRY_SPECIFIC"


@dataclass(frozen=True)
class GovernancePolicy:
    """Genomic Governance & Data Sovereignty Policy (Corpas et al. 2026).
    
    Represents institutional usage policy, consent parameters, jurisdiction boundaries,
    and biosecurity/privacy risk assessments.
    """
    provenance_scope: ProvenanceScope = ProvenanceScope.PUBLIC
    consent_scope: ConsentScope = ConsentScope.RESEARCH_ONLY
    population_scope: PopulationScope = PopulationScope.POPULATION
    jurisdiction: Optional[str] = "GLOBAL"
    biosecurity_restricted: bool = False
    privacy_risk_score: float = 0.0

    def __post_init__(self):
        if not (0.0 <= self.privacy_risk_score <= 1.0):
            raise ValueError("GovernancePolicy.privacy_risk_score must be in range [0.0, 1.0]")
        if self.biosecurity_restricted and self.provenance_scope == ProvenanceScope.PUBLIC:
            raise ValueError("Incoherent policy: Biosecurity restricted data cannot have PUBLIC provenance scope.")


@dataclass(frozen=True)
class PolicyEnvelope:
    """Orthogonal wrapper pairing an artifact or EvidenceContract with its GovernancePolicy."""

    artifact: Any
    policy: GovernancePolicy = field(default_factory=GovernancePolicy)
