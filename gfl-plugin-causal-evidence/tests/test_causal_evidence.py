"""
test_causal_evidence.py — Unit tests for Causal Evidence & Equity Plugin
========================================================================
Validates:
  1. Weak instrument invalidation (F < 10)
  2. Horizontal pleiotropy invalidation (Egger intercept p < 0.05)
  3. Equity-aware population mismatch detection
  4. Valid causal evidence triangulation
"""

import pytest
from gfl_plugin_causal_evidence.causal_triangulation import (
    CausalEvidencePlugin,
    CausalTriangulationResult,
)


def test_valid_causal_triangulation():
    """Strong instrument + no pleiotropy + population match = valid causal claim."""
    plugin = CausalEvidencePlugin()
    res = plugin.evaluate_causal_evidence(
        exposure="LDL_cholesterol",
        outcome="CAD",
        instrument_f_stat=25.0,
        egger_intercept_pvalue=0.45,
        target_population="EUR",
        validated_populations=["EUR", "AFR"],
    )
    assert res.valid_causal_claim
    assert res.strong_instrument
    assert not res.horizontal_pleiotropy_detected
    assert res.equity_population_match
    assert res.invalidation_reason is None
    assert res.validation_tier == "BENCHMARKED"


def test_weak_instrument_invalidation():
    """F-statistic < 10 must flag weak instrument bias and invalidate claim."""
    plugin = CausalEvidencePlugin()
    res = plugin.evaluate_causal_evidence(
        exposure="Lp(a)",
        outcome="Stroke",
        instrument_f_stat=7.2,
        egger_intercept_pvalue=0.50,
        target_population="EUR",
        validated_populations=["EUR"],
    )
    assert not res.valid_causal_claim
    assert not res.strong_instrument
    assert "WEAK_INSTRUMENT_BIAS" in res.invalidation_reason


def test_horizontal_pleiotropy_invalidation():
    """Egger intercept p-value < 0.05 must flag pleiotropy and invalidate claim."""
    plugin = CausalEvidencePlugin()
    res = plugin.evaluate_causal_evidence(
        exposure="BMI",
        outcome="T2D",
        instrument_f_stat=30.0,
        egger_intercept_pvalue=0.01,
        target_population="EUR",
        validated_populations=["EUR"],
    )
    assert not res.valid_causal_claim
    assert res.horizontal_pleiotropy_detected
    assert "HORIZONTAL_PLEIOTROPY_DETECTED" in res.invalidation_reason


def test_population_equity_mismatch():
    """Unvalidated target population must flag equity mismatch."""
    plugin = CausalEvidencePlugin()
    res = plugin.evaluate_causal_evidence(
        exposure="HbA1c",
        outcome="Retinopathy",
        instrument_f_stat=20.0,
        egger_intercept_pvalue=0.30,
        target_population="AFR",
        validated_populations=["EUR"],  # Only validated on EUR
    )
    assert not res.valid_causal_claim
    assert not res.equity_population_match
    assert "POPULATION_EQUITY_MISMATCH" in res.invalidation_reason


def test_gfl_generator_plugin_interface():
    """Verify integration with GFL GeneratorPlugin contract."""
    plugin = CausalEvidencePlugin()
    candidates = plugin.generate(
        entity="PCSK9",
        objective={"analyze": "causal_triangulation"},
        constraints=[],
        count=1,
        exposure="PCSK9_expression",
        outcome="LDL_C",
        instrument_f_stat=45.0,
        egger_intercept_pvalue=0.8,
        target_population="AFR",
        validated_populations=["AFR", "EUR"],
    )
    assert len(candidates) == 1
    cand = candidates[0]
    assert cand.properties["valid_causal_claim"] is True
    assert cand.properties["validation_tier"] == "BENCHMARKED"
