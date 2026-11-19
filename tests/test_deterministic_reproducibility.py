"""Tests for Deterministic Replay Contracts and Retroelement Architecture.

Validates that autonomous agent discoveries (e.g. Anthropic Mythos ART discovery)
are bound to deterministic replay contracts and exhaustive coverage scanning to prevent
the stochasticity and non-reproducibility trap.
"""

import hashlib
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("src"))

from geneforgelang.core.gftypes import (
    DeterministicReplayContract,
    ExhaustiveCoverageContract,
    RetroelementArchitecture,
    RetroelementType,
)
from geneforgelang.core.parser import parse_gfl


def test_exhaustive_coverage_contract():
    """Verify that scanning parameters enforce continuous, non-fragmented base coverage."""
    raw_seq = "ATGAAACCCGGGTTTAAAGGGCCCTTT" * 40
    checksum = hashlib.sha256(raw_seq.encode()).hexdigest()

    contract = ExhaustiveCoverageContract(
        window_size_bp=500,
        stride_bp=100,
        min_coverage_pct=100.0,
        scan_both_strands=True,
        sequence_checksum=checksum,
    )
    d = contract.to_dict()
    assert d["min_coverage_pct"] == 100.0
    assert d["sequence_checksum"] == checksum
    assert d["scan_both_strands"] is True


def test_deterministic_replay_contract():
    """Verify that discovery candidates carry an immutable deterministic verification proof."""
    seq_checksum = hashlib.sha256(b"METAGENOMIC_CONTIG_ANTHROPIC_ART_001").hexdigest()

    replay = DeterministicReplayContract(
        seed=42,
        candidate_id="ART_001",
        target_checksum=seq_checksum,
        coordinates="12450-14890",
        catalytic_motifs_verified=["YADD", "LGDD"],
        required_reproducibility_rate=1.0,
    )

    assert replay.is_deterministic is True
    assert replay.required_reproducibility_rate == 1.0
    assert bool(replay.verification_hash) is True

    # Re-running with identical inputs must produce the identical verification hash
    replay2 = DeterministicReplayContract(
        seed=42,
        candidate_id="ART_001",
        target_checksum=seq_checksum,
        coordinates="12450-14890",
        catalytic_motifs_verified=["YADD", "LGDD"],
        required_reproducibility_rate=1.0,
    )
    assert replay.verification_hash == replay2.verification_hash


def test_retroelement_architecture_and_catalytic_triad():
    """Verify formal biological specification for Array-associated Reverse Transcriptases."""
    seq_checksum = hashlib.sha256(b"METAGENOMIC_CONTIG_ANTHROPIC_ART_001").hexdigest()

    replay_proof = DeterministicReplayContract(
        seed=42,
        candidate_id="ART_001",
        target_checksum=seq_checksum,
        coordinates="12450-14890",
        catalytic_motifs_verified=["YADD"],
    )

    art = RetroelementArchitecture(
        element_id="ART_CANDIDATE_1",
        element_type=RetroelementType.ARRAY_ASSOCIATED_RT,
        rt_domain_range=(150, 480),
        catalytic_triad="YADD",
        associated_repeat_array="GTTCATGGCGGCGTTCATGGCGGCGTTCATGGCGGC",
        flanking_genes=["cas1", "effector_nuclease"],
        replay_proof=replay_proof,
    )

    assert art.element_type == RetroelementType.ARRAY_ASSOCIATED_RT
    assert art.has_canonical_catalytic_triad is True
    assert art.replay_proof.is_deterministic is True

    d = art.to_dict()
    assert d["element_type"] == "ARRAY_ASSOCIATED_RT"
    assert d["catalytic_triad"] == "YADD"
    assert d["replay_proof"]["seed"] == 42


def test_parse_retroelement_gfl_workflow():
    """Verify GFL declarative workflow parsing for deterministic retroelement screening."""
    gfl_source = """
metadata:
  experiment_id: ANTHROPIC_ART_DETERMINISTIC_REPLAY_001
  researcher: Dr. Manuel Menendez Gonzalez
  project: metagenomic_retroelement_mining
  date: 2026-10-05

experiment:
  tool: retroelement_miner
  type: analysis
  strategy: continuous_scan
  params:
    target_class: ARRAY_ASSOCIATED_RT
    window_bp: 1000
    stride_bp: 200
    min_coverage_pct: 100.0
    required_catalytic_triad: ["YADD", "YMDD"]
    deterministic_seed: 42

analyze:
  strategy: deterministic_verification
  thresholds:
    min_reproducibility_rate: 1.0
    enforce_replay_contract: true
"""
    ast = parse_gfl(gfl_source)
    assert ast is not None
    assert "experiment" in ast
    assert ast["experiment"]["params"]["target_class"] == "ARRAY_ASSOCIATED_RT"
    assert ast["analyze"]["thresholds"]["min_reproducibility_rate"] == 1.0
