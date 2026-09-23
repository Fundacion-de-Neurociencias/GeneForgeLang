"""Unit tests for Jev / AnyJev discrete decision model and fast pre-screening plugin."""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("gfl-plugin-jev"))

from geneforgelang.core.gftypes import (
    DecisionContract,
    DecisionOption,
    DecisionOutcome,
    DecisionStrategy,
)
from geneforgelang.plugins.interfaces import DesignCandidate
from gfl_plugin_jev.plugin import JevDecisionPlugin


def test_decision_enums_and_contracts():
    assert DecisionStrategy.PERMUTATION_INVARIANT_LOGITS == "permutation_invariant_logits"
    assert DecisionStrategy.CALIBRATED_TEMPERATURE == "calibrated_temperature"
    assert DecisionStrategy.ENSEMBLE_MARGINALIZED == "ensemble_marginalized"

    contract = DecisionContract(
        task_id="pre_screen_screening",
        allowed_options=["ACCEPT", "REVISE", "REJECT"],
        confidence_threshold=0.85,
    )
    assert contract.confidence_threshold == 0.85
    assert len(contract.allowed_options) == 3


def test_permutation_invariance():
    plugin = JevDecisionPlugin()
    options_order1 = ["alpha", "beta", "gamma"]
    scores_order1 = [2.5, 1.2, 0.3]

    res1 = plugin.decide_discrete_option(
        context="select target component",
        options=options_order1,
        raw_scores=scores_order1,
        strategy=DecisionStrategy.PERMUTATION_INVARIANT_LOGITS,
    )

    options_order2 = ["gamma", "alpha", "beta"]
    scores_order2 = [0.3, 2.5, 1.2]

    res2 = plugin.decide_discrete_option(
        context="select target component",
        options=options_order2,
        raw_scores=scores_order2,
        strategy=DecisionStrategy.PERMUTATION_INVARIANT_LOGITS,
    )

    assert res1.selected_option_id == "alpha"
    assert res2.selected_option_id == "alpha"
    assert abs(res1.confidence - res2.confidence) < 1e-3


def test_confidence_calibration():
    plugin = JevDecisionPlugin()
    options = ["A", "B", "C", "D"]
    scores = [3.0, 1.0, 0.5, 0.1]

    res = plugin.decide_discrete_option(
        context="triage candidate",
        options=options,
        raw_scores=scores,
        temperature=1.2,
    )

    total_prob = sum(opt.calibrated_probability for opt in res.options_evaluated)
    assert abs(total_prob - 1.0) < 0.01
    assert res.selected_option_id == "A"
    assert res.confidence > 0.65


def test_ambiguity_detection_and_escalation():
    plugin = JevDecisionPlugin()
    options = ["A", "B"]
    scores = [2.01, 2.00]

    res = plugin.decide_discrete_option(
        context="ambiguous call",
        options=options,
        raw_scores=scores,
        ambiguity_margin=0.05,
    )

    assert res.is_ambiguous is True


def test_candidate_pre_screening_filter():
    plugin = JevDecisionPlugin()
    cands = [
        DesignCandidate(sequence="SEQ1", properties={"compatibility_score": 0.95}),
        DesignCandidate(sequence="SEQ2", properties={"compatibility_score": 0.40}),
        DesignCandidate(sequence="SEQ3", properties={"compatibility_score": 0.88}),
    ]

    passed, rejected = plugin.pre_screen_candidates(
        cands,
        property_key="compatibility_score",
        threshold=0.80,
    )

    assert len(passed) == 2
    assert len(rejected) == 1
    assert passed[0].sequence == "SEQ1"
    assert passed[1].sequence == "SEQ3"
    assert rejected[0].sequence == "SEQ2"
