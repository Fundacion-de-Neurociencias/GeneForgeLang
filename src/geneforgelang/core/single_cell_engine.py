"""Single-Cell Immune Regulation and Cell-State Dynamics Engine for GeneForgeLang.

Grounded in the TenK10K Phase 1 landmark dataset:
Cuomo, A. S. E., Spenceley, E., Tanudisastro, H. A., et al., Powell, J. E., MacArthur, D. G., et al.
"Rare and common genetic variants shape single-cell immune gene expression."
Nature (2026). DOI: 10.1038/s41586-026-10721-2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import (
    CellAbundanceQTLContract,
    CellStateAxis,
    CellStateInteractionContract,
    ColocalizationGateContract,
    RegulatoryQTLType,
    SingleCellRegulatoryContract,
    TenK10KImmuneCellType,
)


@dataclass
class StatePointEvaluation:
    """Evaluation of an eQTL effect size at a specific cellular state point."""

    state_value: float
    effective_beta: float
    standard_error: float
    z_score: float
    p_value: float
    is_significant: bool


@dataclass
class StateTrajectoryResult:
    """Full trajectory of dynamic eQTL effects across a continuous activation axis."""

    state_axis: str
    state_points: list[StatePointEvaluation]
    max_beta: float
    min_beta: float
    dynamic_range_delta: float
    state_sensitivity_gamma: float


@dataclass
class AbundanceEvaluationResult:
    """Result of evaluating a genetic variant's impact on cell subpopulation abundance."""

    target_cell_type: str
    baseline_frequency: float
    perturbed_frequency: float
    absolute_delta: float
    relative_fold_change: float
    direction: str  # "EXPANSION", "DEPLETION", "STABLE"
    is_statistically_significant: bool


@dataclass
class ColocalizationEvaluationResult:
    """Bayesian colocalization analysis result (Wakefield ABF framework)."""

    gwas_trait_id: str
    candidate_gene: str
    pp0: float  # Neither trait associated
    pp1: float  # Only GWAS associated
    pp2: float  # Only sc-eQTL associated
    pp3: float  # Both associated, different variants
    pp4: float  # Shared causal variant
    is_colocalized: bool
    threshold: float


@dataclass
class SingleCellSimulationResult:
    """Comprehensive output of single-cell regulatory circuit simulation."""

    contract_id: str
    target_gene: str
    variant: str
    cell_type: str
    qtl_type: str
    is_cell_type_specific: bool
    distance_to_tss_bp: int
    is_distal_enhancer: bool
    marginal_beta: float
    state_trajectory: StateTrajectoryResult | None = None
    abundance_result: AbundanceEvaluationResult | None = None
    colocalization_result: ColocalizationEvaluationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert simulation result to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "target_gene": self.target_gene,
            "variant": self.variant,
            "cell_type": self.cell_type,
            "qtl_type": self.qtl_type,
            "is_cell_type_specific": self.is_cell_type_specific,
            "distance_to_tss_bp": self.distance_to_tss_bp,
            "is_distal_enhancer": self.is_distal_enhancer,
            "marginal_beta": self.marginal_beta,
            "state_trajectory": (
                {
                    "state_axis": self.state_trajectory.state_axis,
                    "max_beta": self.state_trajectory.max_beta,
                    "min_beta": self.state_trajectory.min_beta,
                    "dynamic_range_delta": self.state_trajectory.dynamic_range_delta,
                    "state_sensitivity_gamma": self.state_trajectory.state_sensitivity_gamma,
                    "points_count": len(self.state_trajectory.state_points),
                }
                if self.state_trajectory
                else None
            ),
            "abundance_result": (
                {
                    "target_cell_type": self.abundance_result.target_cell_type,
                    "baseline_frequency": self.abundance_result.baseline_frequency,
                    "perturbed_frequency": self.abundance_result.perturbed_frequency,
                    "absolute_delta": self.abundance_result.absolute_delta,
                    "relative_fold_change": self.abundance_result.relative_fold_change,
                    "direction": self.abundance_result.direction,
                }
                if self.abundance_result
                else None
            ),
            "colocalization_result": (
                {
                    "gwas_trait_id": self.colocalization_result.gwas_trait_id,
                    "candidate_gene": self.colocalization_result.candidate_gene,
                    "pp4": self.colocalization_result.pp4,
                    "is_colocalized": self.colocalization_result.is_colocalized,
                    "threshold": self.colocalization_result.threshold,
                }
                if self.colocalization_result
                else None
            ),
            "metadata": dict(self.metadata),
        }


class SingleCellRegulatoryEngine:
    """Computational simulation engine for single-cell immune genomics.

    Implements:
    1. Linear-interaction cell-state eQTL kinetics: beta_eff(s) = beta_0 + gamma * s.
    2. Population cell abundance shift (caQTL) under multinomial simplex conservation.
    3. Wakefield Approximate Bayes Factor (ABF) colocalization between GWAS and sc-eQTLs.
    4. Distance-dependent enhancer chromatin looping probability.
    """

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Compute cumulative distribution function of standard normal distribution."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _two_tailed_p_value(z: float) -> float:
        """Compute two-tailed p-value from Z-score."""
        abs_z = abs(z)
        p = 2.0 * (1.0 - SingleCellRegulatoryEngine._normal_cdf(abs_z))
        return max(1e-300, min(1.0, p))

    def evaluate_state_point(
        self,
        interaction: CellStateInteractionContract,
        state_value: float,
        baseline_se: float = 0.02,
        gamma_se: float = 0.04,
    ) -> StatePointEvaluation:
        """Evaluate eQTL effect size and significance at a single continuous state value."""
        clamped_state = max(interaction.state_range[0], min(interaction.state_range[1], state_value))
        beta_eff = interaction.beta_baseline + interaction.gamma_interaction * clamped_state

        # Variance propagation: Var(beta_eff) = Var(beta_0) + s^2 * Var(gamma)
        se_eff = math.sqrt(baseline_se**2 + (clamped_state**2) * (gamma_se**2))
        z_score = beta_eff / max(se_eff, 1e-9)
        p_val = self._two_tailed_p_value(z_score)

        return StatePointEvaluation(
            state_value=clamped_state,
            effective_beta=round(beta_eff, 6),
            standard_error=round(se_eff, 6),
            z_score=round(z_score, 4),
            p_value=p_val,
            is_significant=p_val < interaction.fdr,
        )

    def evaluate_state_trajectory(
        self,
        interaction: CellStateInteractionContract,
        steps: int = 11,
        baseline_se: float = 0.02,
        gamma_se: float = 0.04,
    ) -> StateTrajectoryResult:
        """Evaluate dynamic eQTL effect across the entire state range [s_min, s_max]."""
        s_min, s_max = interaction.state_range
        step_size = (s_max - s_min) / max(1, steps - 1)

        points: list[StatePointEvaluation] = []
        for i in range(steps):
            s = s_min + i * step_size
            eval_pt = self.evaluate_state_point(interaction, s, baseline_se=baseline_se, gamma_se=gamma_se)
            points.append(eval_pt)

        betas = [p.effective_beta for p in points]
        max_b = max(betas)
        min_b = min(betas)

        return StateTrajectoryResult(
            state_axis=str(interaction.state_axis),
            state_points=points,
            max_beta=round(max_b, 6),
            min_beta=round(min_b, 6),
            dynamic_range_delta=round(max_b - min_b, 6),
            state_sensitivity_gamma=interaction.gamma_interaction,
        )

    def evaluate_abundance_shift(
        self,
        abundance_contract: CellAbundanceQTLContract,
    ) -> AbundanceEvaluationResult:
        """Compute proportional cell frequency shift (caQTL) under simplex normalization."""
        f0 = abundance_contract.baseline_fraction
        delta = abundance_contract.effect_size_delta

        # Non-linear logistic simplex constraint to guarantee 0 < f_perturbed < 1
        # f_new = f0 * (1 + delta) / (1 + f0 * delta)
        denominator = 1.0 + f0 * delta
        if denominator <= 0.01:
            denominator = 0.01

        f_pert = (f0 * (1.0 + delta)) / denominator
        f_pert = max(0.0001, min(0.9999, f_pert))

        abs_delta = f_pert - f0
        fold_change = f_pert / max(f0, 1e-6)

        if abs_delta > 0.01:
            direction = "EXPANSION"
        elif abs_delta < -0.01:
            direction = "DEPLETION"
        else:
            direction = "STABLE"

        return AbundanceEvaluationResult(
            target_cell_type=abundance_contract.target_cell_type,
            baseline_frequency=round(f0, 4),
            perturbed_frequency=round(f_pert, 4),
            absolute_delta=round(abs_delta, 4),
            relative_fold_change=round(fold_change, 4),
            direction=direction,
            is_statistically_significant=abundance_contract.p_value < 5e-8,
        )

    def evaluate_colocalization_abf(
        self,
        gwas_beta: float,
        gwas_se: float,
        eqtl_beta: float,
        eqtl_se: float,
        prior_p1: float = 1e-4,
        prior_p2: float = 1e-4,
        prior_p12: float = 1e-5,
        pp4_threshold: float = 0.80,
        gwas_trait_id: str = "GWAS_TRAIT",
        candidate_gene: str = "GENE",
    ) -> ColocalizationEvaluationResult:
        """Evaluate Wakefield Approximate Bayes Factor (ABF) colocalization between GWAS and sc-eQTL."""
        # Prior variance of true effect sizes
        w_gwas = 0.04  # ~ 0.2^2
        w_eqtl = 0.16  # ~ 0.4^2

        v_gwas = gwas_se**2
        v_eqtl = eqtl_se**2

        z_gwas = gwas_beta / max(gwas_se, 1e-9)
        z_eqtl = eqtl_beta / max(eqtl_se, 1e-9)

        # Wakefield ABF for single-variant model:
        # ABF = sqrt(V / (V + W)) * exp( 0.5 * Z^2 * W / (V + W) )
        r_gwas = w_gwas / (v_gwas + w_gwas)
        exponent_gwas = 0.5 * (z_gwas**2) * r_gwas
        exponent_gwas = min(300.0, exponent_gwas)  # Prevent math overflow
        abf_gwas = math.sqrt(v_gwas / (v_gwas + w_gwas)) * math.exp(exponent_gwas)

        r_eqtl = w_eqtl / (v_eqtl + w_eqtl)
        exponent_eqtl = 0.5 * (z_eqtl**2) * r_eqtl
        exponent_eqtl = min(300.0, exponent_eqtl)
        abf_eqtl = math.sqrt(v_eqtl / (v_eqtl + w_eqtl)) * math.exp(exponent_eqtl)

        # Likelihoods of 5 hypotheses
        l_h0 = 1.0
        l_h1 = prior_p1 * abf_gwas
        l_h2 = prior_p2 * abf_eqtl
        l_h3 = prior_p1 * prior_p2 * abf_gwas * abf_eqtl
        l_h4 = prior_p12 * abf_gwas * abf_eqtl

        total_sum = l_h0 + l_h1 + l_h2 + l_h3 + l_h4
        if total_sum <= 0:
            total_sum = 1e-300

        pp0 = l_h0 / total_sum
        pp1 = l_h1 / total_sum
        pp2 = l_h2 / total_sum
        pp3 = l_h3 / total_sum
        pp4 = l_h4 / total_sum

        return ColocalizationEvaluationResult(
            gwas_trait_id=gwas_trait_id,
            candidate_gene=candidate_gene,
            pp0=round(pp0, 6),
            pp1=round(pp1, 6),
            pp2=round(pp2, 6),
            pp3=round(pp3, 6),
            pp4=round(pp4, 6),
            is_colocalized=pp4 >= pp4_threshold,
            threshold=pp4_threshold,
        )

    def simulate_circuit(
        self,
        contract: SingleCellRegulatoryContract,
        gwas_summary: tuple[float, float] | None = None,
    ) -> SingleCellSimulationResult:
        """Run full circuit simulation for a single-cell regulatory contract."""
        trajectory_res: StateTrajectoryResult | None = None
        if contract.state_interaction is not None:
            trajectory_res = self.evaluate_state_trajectory(
                contract.state_interaction,
                steps=11,
                baseline_se=contract.standard_error,
            )

        abundance_res: AbundanceEvaluationResult | None = None
        if contract.abundance_qtl is not None:
            abundance_res = self.evaluate_abundance_shift(contract.abundance_qtl)

        coloc_res: ColocalizationEvaluationResult | None = None
        if contract.colocalization_gate is not None:
            if gwas_summary is not None:
                gwas_beta, gwas_se = gwas_summary
            else:
                # Derive plausible GWAS concordance from gate contract
                gwas_beta = contract.beta_marginal * 0.8
                gwas_se = contract.standard_error * 1.2

            coloc_res = self.evaluate_colocalization_abf(
                gwas_beta=gwas_beta,
                gwas_se=gwas_se,
                eqtl_beta=contract.beta_marginal,
                eqtl_se=contract.standard_error,
                pp4_threshold=contract.colocalization_gate.pp4_threshold,
                gwas_trait_id=contract.colocalization_gate.gwas_trait_id or "GWAS",
                candidate_gene=contract.target_gene,
            )

        # Distal enhancer threshold: TenK10K cell-type specific eQTLs are significantly distal (>20kb)
        is_distal = contract.is_distal_enhancer or (contract.distance_to_tss_bp >= 20000)

        return SingleCellSimulationResult(
            contract_id=contract.contract_id,
            target_gene=contract.target_gene,
            variant=contract.variant,
            cell_type=str(contract.cell_type),
            qtl_type=str(contract.qtl_type),
            is_cell_type_specific=contract.is_cell_type_specific,
            distance_to_tss_bp=contract.distance_to_tss_bp,
            is_distal_enhancer=is_distal,
            marginal_beta=contract.beta_marginal,
            state_trajectory=trajectory_res,
            abundance_result=abundance_res,
            colocalization_result=coloc_res,
            metadata=dict(contract.metadata),
        )
