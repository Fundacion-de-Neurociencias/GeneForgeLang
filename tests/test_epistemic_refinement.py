"""
test_epistemic_refinement.py — Tests for GFL Epistemic Refinement & Partitioning
===============================================================================
Verifies the GFL Hypothesis:
  1. Representations as Priors (Bayesian update via ContractAlgebra.refine).
  2. Non-destructive claim partitioning (ContractAlgebra.partition).
  3. Epistemic state transition and uncertainty propagation.
"""

from datetime import datetime
import pytest

from geneforgelang.semantic.evidence.algebra import ContractAlgebra
from geneforgelang.semantic.evidence.contract import (
    EvidenceContract,
    ScaleAnchor,
    ObservabilityProfile,
    CompressibilityProfile,
    TemporalValidity,
    ContradictionState,
    Provenance,
    InvalidationDependency,
)


def create_mock_contract(contract_id: str, claim: str, uncertainty: float = 0.4) -> EvidenceContract:
    obs = ObservabilityProfile(0.8, 0.8, 0.8, 0.8, "base_pair")
    comp = CompressibilityProfile(0.5, 0.5, True)
    temp = TemporalValidity(datetime.now(), None, 0.9, "exponential")
    prov = Provenance("GFLSystem", contract_id, datetime.now(), [])
    inval = InvalidationDependency([], [])

    return EvidenceContract(
        contract_id=contract_id,
        claim=claim,
        scale_anchor=ScaleAnchor.SEQUENCE,
        observability=obs,
        compressibility=comp,
        temporal_validity=temp,
        contradiction_state=ContradictionState.SUPPORTED,
        uncertainty=uncertainty,
        provenance=prov,
        invalidation_dependencies=inval,
    )


def test_epistemic_refine_bayesian_prior_update():
    """Refinement updates prior uncertainty non-destructively."""
    prior = create_mock_contract("EC-PRIOR-001", "PCSK9_LDL_association", uncertainty=0.40)
    new_evidence = create_mock_contract("EC-EV-002", "PCSK9_GWAS_replication", uncertainty=0.20)

    refined = ContractAlgebra.refine(prior, new_evidence)

    assert refined.uncertainty < prior.uncertainty
    assert refined.uncertainty < new_evidence.uncertainty
    assert "REFINED_PRIOR" in refined.claim
    assert "EC-PRIOR-001" in refined.invalidation_dependencies.upstream_contract_ids
    assert "EC-EV-002" in refined.invalidation_dependencies.upstream_contract_ids


def test_epistemic_partition_contextual_claims():
    """Partitioning splits a prior claim into conditional contexts without overwriting prior."""
    prior = create_mock_contract("EC-PRIOR-APOE", "APOE4_Alzheimers_risk", uncertainty=0.10)

    context_eur = create_mock_contract("EV-EUR", "EUR_cohort_odds_ratio_3.8", uncertainty=0.05)
    context_afr = create_mock_contract("EV-AFR", "AFR_cohort_odds_ratio_1.8", uncertainty=0.15)

    contextual_evidence = {
        "EUR": context_eur,
        "AFR": context_afr,
    }

    partitions = ContractAlgebra.partition(prior, contextual_evidence)

    assert "EUR" in partitions
    assert "AFR" in partitions
    assert partitions["EUR"].contradiction_state == ContradictionState.CONDITIONALLY_VALID
    assert partitions["AFR"].contradiction_state == ContradictionState.CONDITIONALLY_VALID
    assert "Context=EUR" in partitions["EUR"].claim
    assert "Context=AFR" in partitions["AFR"].claim
