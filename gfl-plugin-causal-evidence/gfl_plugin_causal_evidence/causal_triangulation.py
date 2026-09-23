"""
causal_triangulation.py — GFL Plugin: Causal Evidence Triangulation & Equity Validation
========================================================================================
Wraps Mendelian Randomization instrument strength, pleiotropy invalidation,
and population equity checks into a GFL GeneratorPlugin.

ADR-0003 compliance:
  - Does NOT import geneforgelang.core, geneforgelang.semantic, or geneforgelang.governance
  - Amputatable by design
  - Integrates with GFL GeneratorPlugin interface
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.plugins.interfaces import (
    DesignCandidate,
    EntityType,
    GeneratorPlugin,
)

logger = logging.getLogger(__name__)

PLUGIN_TOOL_ID = "causal_evidence_triangulation"
MIN_F_STATISTIC = 10.0
EGGER_PLEIOTROPY_P_THRESHOLD = 0.05


@dataclass
class CausalTriangulationResult:
    """Result of causal evidence triangulation and validation."""

    exposure: str
    outcome: str
    valid_causal_claim: bool
    instrument_f_stat: float
    strong_instrument: bool
    egger_intercept_pvalue: float
    horizontal_pleiotropy_detected: bool
    equity_population_match: bool
    target_population: str
    validated_populations: list[str]
    invalidation_reason: str | None = None
    validation_tier: str = "BENCHMARKED"  # Tiered Validation Framework (Corpas et al. 2026)
    governance_profile: dict[str, Any] = field(
        default_factory=lambda: {
            "provenance_scope": "PUBLIC",
            "consent_scope": "RESEARCH_ONLY",
            "population_scope": "ANCESTRY_SPECIFIC",
            "jurisdiction": "GLOBAL",
            "biosecurity_restricted": False,
            "privacy_risk_score": 0.05,
        }
    )


class CausalEvidencePlugin(GeneratorPlugin):
    """GFL GeneratorPlugin for Causal Evidence & Population Equity Validation.

    Implements:
      1. Weak Instrument Verification (F >= 10)
      2. Horizontal Pleiotropy Invalidation (MR-Egger intercept p < 0.05)
      3. Equity-Aware Population Matching (Corpas et al. 2026)
    """

    name = PLUGIN_TOOL_ID
    version = "0.1.0"
    description = (
        "Causal evidence triangulation, MR instrument validation, "
        "pleiotropy invalidation, and population equity checks (Corpas et al. 2026)"
    )

    @property
    def supported_entities(self) -> list[EntityType]:
        return [EntityType.DNA_SEQUENCE, EntityType.RNA_SEQUENCE, EntityType.PROTEIN_SEQUENCE]

    def evaluate_causal_evidence(
        self,
        exposure: str,
        outcome: str,
        instrument_f_stat: float,
        egger_intercept_pvalue: float,
        target_population: str = "EUR",
        validated_populations: list[str] | None = None,
    ) -> CausalTriangulationResult:
        """Evaluate causal evidence and population equity constraints."""
        if validated_populations is None:
            validated_populations = ["EUR"]

        strong_instrument = instrument_f_stat >= MIN_F_STATISTIC
        horizontal_pleiotropy = egger_intercept_pvalue < EGGER_PLEIOTROPY_P_THRESHOLD
        equity_match = target_population in validated_populations

        invalidation_reasons = []
        if not strong_instrument:
            invalidation_reasons.append(
                f"WEAK_INSTRUMENT_BIAS: F-statistic ({instrument_f_stat:.2f}) < {MIN_F_STATISTIC}"
            )
        if horizontal_pleiotropy:
            invalidation_reasons.append(
                f"HORIZONTAL_PLEIOTROPY_DETECTED: Egger intercept p-value ({egger_intercept_pvalue:.4f}) < {EGGER_PLEIOTROPY_P_THRESHOLD}"
            )
        if not equity_match:
            invalidation_reasons.append(
                f"POPULATION_EQUITY_MISMATCH: Target population '{target_population}' is not in validated scope {validated_populations}"
            )

        is_valid = strong_instrument and (not horizontal_pleiotropy) and equity_match
        reason = " | ".join(invalidation_reasons) if invalidation_reasons else None

        return CausalTriangulationResult(
            exposure=exposure,
            outcome=outcome,
            valid_causal_claim=is_valid,
            instrument_f_stat=instrument_f_stat,
            strong_instrument=strong_instrument,
            egger_intercept_pvalue=egger_intercept_pvalue,
            horizontal_pleiotropy_detected=horizontal_pleiotropy,
            equity_population_match=equity_match,
            target_population=target_population,
            validated_populations=validated_populations,
            invalidation_reason=reason,
            validation_tier="BENCHMARKED",
        )

    def generate(
        self,
        entity: str,
        objective: dict[str, Any],
        constraints: list[str],
        count: int,
        **kwargs: Any,
    ) -> list[DesignCandidate]:
        """Execute causal triangulation and return DesignCandidate with epistemic evaluation."""
        exposure = kwargs.get("exposure", entity)
        outcome = kwargs.get("outcome", "Target_Disease")
        f_stat = float(kwargs.get("instrument_f_stat", 15.0))
        egger_p = float(kwargs.get("egger_intercept_pvalue", 0.5))
        target_pop = kwargs.get("target_population", "EUR")
        valid_pops = kwargs.get("validated_populations", ["EUR"])

        result = self.evaluate_causal_evidence(
            exposure=exposure,
            outcome=outcome,
            instrument_f_stat=f_stat,
            egger_intercept_pvalue=egger_p,
            target_population=target_pop,
            validated_populations=valid_pops,
        )

        candidate = DesignCandidate(
            sequence=entity,
            properties={
                "exposure": result.exposure,
                "outcome": result.outcome,
                "valid_causal_claim": result.valid_causal_claim,
                "instrument_f_stat": result.instrument_f_stat,
                "strong_instrument": result.strong_instrument,
                "egger_intercept_pvalue": result.egger_intercept_pvalue,
                "horizontal_pleiotropy_detected": result.horizontal_pleiotropy_detected,
                "equity_population_match": result.equity_population_match,
                "invalidation_reason": result.invalidation_reason,
                "validation_tier": result.validation_tier,
                "governance_profile": result.governance_profile,
                "plugin_name": self.name,
            },
        )

        return [candidate]
