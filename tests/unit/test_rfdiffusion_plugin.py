"""Unit tests for the rescued RFdiffusionPlugin."""

from __future__ import annotations

import pytest

from geneforgelang.plugins.interfaces import EntityType
from geneforgelang.plugins.rfdiffusion import RFdiffusionPlugin


def test_rfdiffusion_plugin_metadata() -> None:
    plugin = RFdiffusionPlugin()
    assert plugin.name == "rfdiffusion"
    assert plugin.version == "1.0.0"
    assert plugin.supported_entities == [EntityType.PROTEIN_SEQUENCE]


def test_rfdiffusion_device_resolution() -> None:
    plugin = RFdiffusionPlugin()
    assert plugin._resolve_device("cpu") == "cpu"
    assert plugin._resolve_device("gpu") in {"cuda", "cpu"}
    with pytest.raises(ValueError, match="Invalid device"):
        plugin._resolve_device("tpu")


def test_rfdiffusion_generate_and_validation() -> None:
    plugin = RFdiffusionPlugin()
    candidates = plugin.generate(
        entity="ProteinSequence",
        objective={"maximize": "stability"},
        constraints=[],
        count=2,
        mode="unconditional",
        length=64,
        device="cpu",
    )
    assert len(candidates) == 2
    assert len(candidates[0].sequence) == 64
    assert candidates[0].properties == {"mode": "unconditional", "device": "cpu"}
    assert candidates[0].metadata["evidence_status"] == "simulated"

    with pytest.raises(ValueError, match="only supports ProteinSequence"):
        plugin.generate("DNASequence", {}, [], 1, mode="unconditional")

    with pytest.raises(ValueError, match="Invalid or missing 'mode'"):
        plugin.generate("ProteinSequence", {}, [], 1, mode="invalid_mode")
