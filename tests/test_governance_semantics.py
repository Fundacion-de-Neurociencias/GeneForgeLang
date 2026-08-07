"""
test_governance_semantics.py — Tests for Genomic Data Governance & Sovereignty Semantics
======================================================================================
Verifies:
  1. GovernanceProfile initialization, fields, and privacy risk validation.
  2. EvidenceContract integration with GovernanceProfile.
  3. Incoherence validation (biosecurity restriction vs public scope).
  4. Integration with plugin outputs (ClawBio and Causal Evidence).
"""

from datetime import datetime
import pytest

from geneforgelang.semantic.evidence.contract import (
    EvidenceContract,
    GovernanceProfile,
    ProvenanceScope,
    ConsentScope,
    PopulationScope,
    ScaleAnchor,
    ObservabilityProfile,
    CompressibilityProfile,
    TemporalValidity,
    ContradictionState,
    Provenance,
    InvalidationDependency,
)
from gfl_plugin_causal_evidence.causal_triangulation import CausalEvidencePlugin
from gfl_plugin_clawbio._clawbio_runner import ClawBioRunResult


def test_governance_profile_defaults():
    """Verify default GovernanceProfile values."""
    gov = GovernanceProfile()
    assert gov.provenance_scope == ProvenanceScope.PUBLIC
    assert gov.consent_scope == ConsentScope.RESEARCH_ONLY
    assert gov.population_scope == PopulationScope.POPULATION
    assert gov.jurisdiction == "GLOBAL"
    assert not gov.biosecurity_restricted
    assert gov.privacy_risk_score == 0.0


def test_governance_profile_custom_values():
    """Verify custom GovernanceProfile values."""
    gov = GovernanceProfile(
        provenance_scope=ProvenanceScope.CLINICAL,
        consent_scope=ConsentScope.CLINICAL_CARE,
        population_scope=PopulationScope.INDIVIDUAL,
        jurisdiction="EU",
        biosecurity_restricted=False,
        privacy_risk_score=0.45,
    )
    assert gov.provenance_scope == ProvenanceScope.CLINICAL
    assert gov.consent_scope == ConsentScope.CLINICAL_CARE
    assert gov.jurisdiction == "EU"
    assert gov.privacy_risk_score == 0.45


def test_governance_privacy_risk_validation():
    """Privacy risk score out of range [0.0, 1.0] must raise ValueError."""
    with pytest.raises(ValueError, match="privacy_risk_score"):
        GovernanceProfile(privacy_risk_score=1.5)


def test_evidence_contract_with_governance():
    """EvidenceContract cleanly integrates GovernanceProfile."""
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "base_pair")
    comp = CompressibilityProfile(0.5, 0.5, True)
    temp = TemporalValidity(datetime.now(), None, 0.9, "exponential")
    prov = Provenance("ClinVar", "RCV000123", datetime.now(), ["germline"])
    inval = InvalidationDependency([], [])

    gov = GovernanceProfile(
        provenance_scope=ProvenanceScope.RESTRICTED,
        consent_scope=ConsentScope.RESEARCH_ONLY,
        population_scope=PopulationScope.COHORT,
        jurisdiction="US",
        biosecurity_restricted=True,
        privacy_risk_score=0.30,
    )

    contract = EvidenceContract(
        contract_id="EC-GOV-001",
        claim="BRCA1_pathogenic_variant",
        scale_anchor=ScaleAnchor.SEQUENCE,
        observability=obs,
        compressibility=comp,
        temporal_validity=temp,
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=0.05,
        provenance=prov,
        invalidation_dependencies=inval,
        governance_profile=gov,
    )

    assert contract.governance_profile is not None
    assert contract.governance_profile.biosecurity_restricted is True
    assert contract.governance_profile.provenance_scope == ProvenanceScope.RESTRICTED


def test_incoherent_governance_validation():
    """Biosecurity restricted data labeled PUBLIC provenance must raise ValueError."""
    obs = ObservabilityProfile(1.0, 1.0, 1.0, 1.0, "base_pair")
    comp = CompressibilityProfile(0.5, 0.5, True)
    temp = TemporalValidity(datetime.now(), None, 0.9, "exponential")
    prov = Provenance("Biobank", "BB-001", datetime.now(), [])
    inval = InvalidationDependency([], [])

    incoherent_gov = GovernanceProfile(
        provenance_scope=ProvenanceScope.PUBLIC,
        biosecurity_restricted=True,  # Incoherent combination
    )

    with pytest.raises(ValueError, match="Biosecurity restricted data cannot have PUBLIC provenance scope"):
        EvidenceContract(
            contract_id="EC-GOV-ERR",
            claim="Dual_use_pathogen_sequence",
            scale_anchor=ScaleAnchor.SEQUENCE,
            observability=obs,
            compressibility=comp,
            temporal_validity=temp,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=0.01,
            provenance=prov,
            invalidation_dependencies=inval,
            governance_profile=incoherent_gov,
        )


def test_plugin_governance_integration():
    """Verify plugin candidate outputs include governance profile metadata."""
    plugin = CausalEvidencePlugin()
    candidates = plugin.generate(
        entity="APOE",
        objective={"analyze": "causal_triangulation"},
        constraints=[],
        count=1,
        exposure="APOE4_expression",
        outcome="Alzheimers",
        instrument_f_stat=30.0,
        egger_intercept_pvalue=0.5,
        target_population="EUR",
        validated_populations=["EUR"],
    )
    assert len(candidates) == 1
    cand = candidates[0]
    assert "governance_profile" in cand.properties
    assert cand.properties["governance_profile"]["provenance_scope"] == "PUBLIC"

    run_res = ClawBioRunResult(
        success=True,
        output={},
        skill_name="pharmgx-reporter",
        skill_version="0.1.0",
        clawbio_installed=True,
    )
    assert "provenance_scope" in run_res.governance_profile
    assert run_res.governance_profile["provenance_scope"] == "CLINICAL"
