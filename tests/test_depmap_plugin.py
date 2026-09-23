"""Tests for DepMap CRISPR Co-Dependency GFL Plugin and Causal Transition Nodes."""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("gfl-plugin-depmap"))

from geneforgelang.core.gftypes import (
    CausalLevel,
    CausalTransitionNode,
    CoDependencyTier,
    DepMapCoDependency,
)
from gfl_plugin_depmap.plugin import DepMapEvaluationResult, DepMapPlugin


def test_depmap_codependency_dataclass():
    dep = DepMapCoDependency(
        gene_a="DNM1",
        gene_b="SH3GL2",
        correlation_score=0.62,
        p_value=5.1e-09,
    )
    assert dep.codependency_tier == CoDependencyTier.HIGH
    assert dep.is_significant is True
    d = dep.to_dict()
    assert d["gene_a"] == "DNM1"
    assert d["codependency_tier"] == "HIGH"


def test_causal_transition_node_dataclass():
    node = CausalTransitionNode(
        node_id="NODE_DNM1_ENDOCYTOSIS",
        level=CausalLevel.MOLECULAR,
        entity_name="DNM1",
        biological_state="GTPase_Hydrolysis_Defective",
        confidence=0.95,
        evidence_sources=["AlphaGenome_AVI", "DepMap_CoDependency"],
    )
    assert node.level == CausalLevel.MOLECULAR
    assert node.biological_state == "GTPase_Hydrolysis_Defective"
    d = node.to_dict()
    assert d["level"] == "MOLECULAR"
    assert len(d["evidence_sources"]) == 2


def test_depmap_plugin_query_and_stop_gate_pass():
    plugin = DepMapPlugin()
    res = plugin.query_codependency("YAP1", "TEAD1")
    assert res.correlation_score >= 0.70
    assert res.codependency_tier == CoDependencyTier.HIGH

    passed, msg = plugin.validate_stopping_rule("YAP1", "TEAD1", min_correlation=0.30)
    assert passed is True
    assert "PASSED" in msg


def test_depmap_plugin_stop_gate_trigger_on_uncorrelated_pair():
    plugin = DepMapPlugin()
    passed, msg = plugin.validate_stopping_rule("GENE_FAKE_1", "GENE_FAKE_2", min_correlation=0.30)
    assert passed is False
    assert "STOP GATE TRIGGERED" in msg


def test_depmap_plugin_generate_candidate():
    plugin = DepMapPlugin()
    cands = plugin.generate(
        entity="RAMP1",
        objective={"maximize": "correlation_score"},
        constraints=["min_correlation(0.50)"],
        count=1,
        gene_a="RAMP1",
        gene_b="CALCRL",
        min_correlation=0.50,
    )
    assert len(cands) == 1
    cand = cands[0]
    assert cand.properties["stop_gate_passed"] is True
    assert cand.properties["plugin_name"] == "depmap"

