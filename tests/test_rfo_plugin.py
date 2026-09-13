"""Unit tests for RFOptimization rescue plugin and multi-model consensus."""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("gfl-plugin-rfo"))

from geneforgelang.core.gftypes import (
    CandidateStatus,
    ConsensusModel,
    MultiModelConsensus,
    RescuePolicy,
)
from geneforgelang.plugins.interfaces import DesignCandidate
from gfl_plugin_rfo.plugin import RFOptimizationPlugin, RescueAttemptResult


def test_consensus_model_and_candidate_status_enums():
    assert CandidateStatus.VALIDATED == "validated"
    assert CandidateStatus.NEAR_MISS == "near-miss" or CandidateStatus.NEAR_MISS == "near_miss"
    assert CandidateStatus.OPTIMIZED == "optimized"
    assert ConsensusModel.AF3 == "alphafold3"
    assert ConsensusModel.RF3 == "rosettafold3"
    assert ConsensusModel.BOLTZ == "boltz1"


def test_multi_model_consensus_pass_and_near_miss():
    # Candidate passing all three models
    pass_cand = MultiModelConsensus(
        af3_iptm=0.85,
        af3_ipae=1.8,
        rf3_confidence=0.88,
        boltz_confidence=0.90,
    )
    assert pass_cand.passes_consensus() is True
    assert pass_cand.is_near_miss() is False

    # Near-miss candidate (sits close to decision boundary)
    near_cand = MultiModelConsensus(
        af3_iptm=0.76,  # Unsatisfied but >= 0.65
        af3_ipae=2.8,   # Unsatisfied but <= 2.8
        rf3_confidence=0.79,
        boltz_confidence=0.78,
    )
    assert near_cand.passes_consensus() is False
    assert near_cand.is_near_miss() is True

    # Completely rejected candidate (poor structure)
    rej_cand = MultiModelConsensus(
        af3_iptm=0.30,
        af3_ipae=11.0,
        rf3_confidence=0.30,
        boltz_confidence=0.25,
    )
    assert rej_cand.passes_consensus() is False
    assert rej_cand.is_near_miss() is False


def test_rfo_plugin_classification_and_rescue():
    plugin = RFOptimizationPlugin()
    assert plugin.tool_id == "rfo"

    near_candidate = DesignCandidate(
        sequence="MSKVSDEEINKAVEELS",
        properties={
            "af3_iptm": 0.77,
            "af3_ipae": 2.7,
            "rf3_confidence": 0.79,
            "boltz_confidence": 0.78,
        },
        confidence=0.75,
    )

    status = plugin.classify_candidate(near_candidate)
    assert status == CandidateStatus.NEAR_MISS

    # Attempt rescue
    result = plugin.rescue_candidate(near_candidate)
    assert result.is_rescued is True
    assert result.status_before == CandidateStatus.NEAR_MISS
    assert result.status_after == CandidateStatus.OPTIMIZED
    assert result.cycles_performed > 0
    assert result.optimized_candidate is not None
    assert result.optimized_candidate.properties["rfo_rescued"] is True


def test_rfo_rejected_not_rescued():
    plugin = RFOptimizationPlugin()
    bad_candidate = DesignCandidate(
        sequence="MLLLLL",
        properties={
            "af3_iptm": 0.21,
            "af3_ipae": 14.2,
            "rf3_confidence": 0.23,
            "boltz_confidence": 0.20,
        },
        confidence=0.20,
    )

    status = plugin.classify_candidate(bad_candidate)
    assert status == CandidateStatus.REJECTED

    result = plugin.rescue_candidate(bad_candidate)
    assert result.is_rescued is False
    assert result.status_after == CandidateStatus.REJECTED
