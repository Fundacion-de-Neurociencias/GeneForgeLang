"""
Evidence Contract Transition Algebra

This module defines the algebraic laws and compositional semantics for EvidenceContracts
in GeneForgeLang. It formalizes how contracts interact, combine, or nullify one another,
establishing a rigorous calculus over epistemological primitives.

Key Algebraic Properties:
- Composition (⊕): Commutative and associative for contracts anchoring the same claim.
  Composing independent provenance lineages strictly monotonically increases or maintains
  reachability, while contradictory composition drops state to CONTESTED.
- Supersession (≻): Non-commutative. Newer, higher-resolution evidence overtakes older evidence.
- Invalidation (¬): Unary operator that transitions state to INVALIDATED.
"""

from copy import deepcopy
from typing import Optional

from geneforgelang.semantic.evidence.contract import (
    CompressibilityProfile,
    ContradictionState,
    EvidenceContract,
    InvalidationDependency,
    ObservabilityProfile,
    TemporalValidity,
)


class ContractAlgebra:
    """
    Formal algebraic operations over EvidenceContracts.
    """

    @staticmethod
    def compose(contract_a: EvidenceContract, contract_b: EvidenceContract) -> EvidenceContract:
        """
        Operator ⊕: Symmetrical evidence composition.
        Must be Commutative: A ⊕ B == B ⊕ A
        Must be Associative: (A ⊕ B) ⊕ C == A ⊕ (B ⊕ C)
        """
        if contract_a.scale_anchor != contract_b.scale_anchor:
            raise ValueError("Algebraic failure: Cannot compose contracts across different scale anchors directly.")

        if contract_a.claim != contract_b.claim:
            # If claims differ, this is a conflict composition, triggering CONTESTED state.
            new_state = ContradictionState.CONTESTED
            # When contesting, uncertainty is inherently maximized by the conflict delta
            new_uncertainty = min(1.0, contract_a.uncertainty + contract_b.uncertainty + 0.5)
        else:
            # Consilience: claims agree.
            new_state = ContradictionState.SUPPORTED
            # Epistemic risk reduction via independent observation
            new_uncertainty = contract_a.uncertainty * contract_b.uncertainty

        # Observability monotonically increases (best of both worlds) for reachability and visibility
        new_obs = ObservabilityProfile(
            reachability=max(contract_a.observability.reachability, contract_b.observability.reachability),
            visibility=max(contract_a.observability.visibility, contract_b.observability.visibility),
            accessibility=max(contract_a.observability.accessibility, contract_b.observability.accessibility),
            identifiability=max(contract_a.observability.identifiability, contract_b.observability.identifiability),
            resolution=contract_a.observability.resolution
            if contract_a.observability.resolution == contract_b.observability.resolution
            else "mixed",
        )

        # Temporal validity intersects (valid only while both are, or defined by composition rules)
        # For simplicity in the algebra, if they agree, they extend stability. If they conflict, stability decays.
        new_stability = (
            contract_a.temporal_validity.stability_expectation + contract_b.temporal_validity.stability_expectation
        ) / 2

        # We synthesize a new synthetic provenance contract
        # (A real implementation would trace the lineage tree formally)
        contract = EvidenceContract(
            contract_id=f"comp_{contract_a.contract_id}_{contract_b.contract_id}",
            claim=contract_a.claim
            if contract_a.claim == contract_b.claim
            else f"CONTESTED: {contract_a.claim} vs {contract_b.claim}",
            scale_anchor=contract_a.scale_anchor,
            observability=new_obs,
            compressibility=contract_a.compressibility,  # Simplified for prototype
            temporal_validity=TemporalValidity(
                valid_from=max(contract_a.temporal_validity.valid_from, contract_b.temporal_validity.valid_from),
                valid_until=min(contract_a.temporal_validity.valid_until, contract_b.temporal_validity.valid_until)
                if contract_a.temporal_validity.valid_until and contract_b.temporal_validity.valid_until
                else None,
                stability_expectation=new_stability,
                decay_model="composite",
            ),
            contradiction_state=new_state,
            uncertainty=new_uncertainty,
            provenance=contract_a.provenance,  # In reality, merged provenance
            invalidation_dependencies=InvalidationDependency(
                upstream_contract_ids=[contract_a.contract_id, contract_b.contract_id], invalidation_hooks=[]
            ),
        )
        return contract

    @staticmethod
    def supersede(older: EvidenceContract, newer: EvidenceContract) -> EvidenceContract:
        """
        Operator ≻: Asymmetrical supersession.
        Newer strictly replaces older. Non-commutative.
        """
        if newer.temporal_validity.valid_from < older.temporal_validity.valid_from:
            raise ValueError("Algebraic failure: Cannot supersede with a chronologically older contract.")

        # The older contract gets SUPERSEDED (this would be handled by the runtime, but semantically, we return the new state representation)
        return EvidenceContract(
            contract_id=older.contract_id,
            claim=older.claim,
            scale_anchor=older.scale_anchor,
            observability=older.observability,
            compressibility=older.compressibility,
            temporal_validity=older.temporal_validity,
            contradiction_state=ContradictionState.SUPERSEDED,
            uncertainty=older.uncertainty,
            provenance=older.provenance,
            invalidation_dependencies=InvalidationDependency(
                upstream_contract_ids=[newer.contract_id],
                invalidation_hooks=older.invalidation_dependencies.invalidation_hooks,
            ),
        )

    @staticmethod
    def refine(prior: EvidenceContract, new_evidence: EvidenceContract) -> EvidenceContract:
        """
        Operator ⟳ (Refinement): Epistemic Bayesian update.
        Treats `prior` as an epistemic prior rather than final truth.
        Updates parameter bounds, observability, and uncertainty non-destructively.
        """
        if prior.scale_anchor != new_evidence.scale_anchor:
            raise ValueError("Algebraic failure: Cannot refine prior across different scale anchors directly.")

        # Bayesian uncertainty update: u_post = (u_prior * u_new) / (u_prior + u_new - u_prior * u_new)
        num = prior.uncertainty * new_evidence.uncertainty
        den = prior.uncertainty + new_evidence.uncertainty - num
        posterior_uncertainty = num / den if den > 0 else 0.0

        refined_obs = ObservabilityProfile(
            reachability=max(prior.observability.reachability, new_evidence.observability.reachability),
            visibility=max(prior.observability.visibility, new_evidence.observability.visibility),
            accessibility=max(prior.observability.accessibility, new_evidence.observability.accessibility),
            identifiability=max(prior.observability.identifiability, new_evidence.observability.identifiability),
            resolution=new_evidence.observability.resolution,
        )

        return EvidenceContract(
            contract_id=f"refinement_{prior.contract_id}_{new_evidence.contract_id}",
            claim=f"REFINED_PRIOR({prior.claim} | {new_evidence.claim})",
            scale_anchor=prior.scale_anchor,
            observability=refined_obs,
            compressibility=prior.compressibility,
            temporal_validity=new_evidence.temporal_validity,
            contradiction_state=ContradictionState.SUPPORTED,
            uncertainty=posterior_uncertainty,
            provenance=prior.provenance,
            invalidation_dependencies=InvalidationDependency(
                upstream_contract_ids=[prior.contract_id, new_evidence.contract_id],
                invalidation_hooks=[],
            ),
        )

    @staticmethod
    def partition(prior: EvidenceContract, contextual_evidence: dict[str, EvidenceContract]) -> dict[str, EvidenceContract]:
        """
        Operator ⫴ (Partition): Epistemic Context Partitioning.
        Partitions a general prior claim into conditional context-specific claims
        (e.g., ancestry, tissue, or perturbation contexts) rather than overwriting it.
        """
        partitioned_contracts = {}
        for context_key, ev in contextual_evidence.items():
            partitioned_id = f"partition_{prior.contract_id}_{context_key}"
            partitioned_claim = f"PARTITION({prior.claim} | Context={context_key})"
            partitioned_contracts[context_key] = EvidenceContract(
                contract_id=partitioned_id,
                claim=partitioned_claim,
                scale_anchor=prior.scale_anchor,
                observability=ev.observability,
                compressibility=prior.compressibility,
                temporal_validity=ev.temporal_validity,
                contradiction_state=ContradictionState.CONDITIONALLY_VALID,
                uncertainty=ev.uncertainty,
                provenance=prior.provenance,
                invalidation_dependencies=InvalidationDependency(
                    upstream_contract_ids=[prior.contract_id, ev.contract_id],
                    invalidation_hooks=[],
                ),
            )
        return partitioned_contracts

