"""
Real Execution Integration Tests for gfl-plugin-clawbio
=======================================================
These tests invoke ClawBio via subprocess *for real*.
ClawBio must be installed (`pip install clawbio`).

Tests:
  1. GWAS Lookup: Queries actual external APIs via ClawBio.
  2. RNA-seq DE: Runs PyDESeq2 locally on a generated mock count matrix.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Ensure GFL and plugin are importable
PLUGIN_ROOT = Path(__file__).parent.parent.parent
ECOSYSTEM_ROOT = PLUGIN_ROOT.parent
GFL_SRC = ECOSYSTEM_ROOT / "GeneForgeLang" / "src"
if GFL_SRC.exists() and str(GFL_SRC) not in sys.path:
    sys.path.insert(0, str(GFL_SRC))

try:
    import clawbio

    HAS_CLAWBIO = True
except ImportError:
    HAS_CLAWBIO = False

pytestmark = pytest.mark.skipif(not HAS_CLAWBIO, reason="ClawBio is not installed")

from gfl_plugin_clawbio import GwasLookupPlugin, RnaseqDEPlugin


@pytest.mark.integration
def test_real_gwas_lookup():
    """
    Test real GWAS Lookup via ClawBio subprocess.
    Uses 'rs429358' (APOE e4 variant) against Open Targets & GWAS Catalog.
    """
    plugin = GwasLookupPlugin()

    # We pass demo_mode=False so it actually hits the network via ClawBio
    candidates = plugin.generate(
        entity="DNA_SEQUENCE",
        objective={"analyze": "find associations"},
        constraints=[],
        count=1,
        rsid="rs429358",
        databases=["gwas_catalog", "open_targets"],
        demo_mode=False,
    )

    assert len(candidates) == 1
    candidate = candidates[0]

    # Ensure it says success and returned real data
    assert candidate.properties.get("status") == "success"
    assert candidate.properties.get("skill") == "gwas"
    assert candidate.properties.get("rsid") == "rs429358"

    output_json = candidate.properties.get("output")
    assert output_json is not None
    assert isinstance(output_json, dict)

    # Ensure the subprocess actually succeeded and yielded results
    assert "raw_results.json" in output_json or "result.json" in output_json


@pytest.mark.integration
def test_real_rnaseq_de():
    """
    Test real RNA-seq Differential Expression via ClawBio (PyDESeq2).
    Generates a minimal valid count matrix and runs the plugin.
    """
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        counts_path = tmp_path / "counts.csv"
        metadata_path = tmp_path / "metadata.csv"

        # Write minimal count matrix (4 samples, 10 genes)
        # Needs to look like RNA-seq data (integers)
        with open(counts_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["gene", "S1", "S2", "S3", "S4"])
            writer.writerow(["GeneA", 100, 110, 500, 480])  # UP in Treated
            writer.writerow(["GeneB", 1000, 950, 100, 120])  # DOWN in Treated
            for i in range(8):
                # non-DE genes
                writer.writerow([f"Gene{i}", 200, 210, 195, 205])

        # Write metadata
        with open(metadata_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["sample_id", "condition"])
            writer.writerow(["S1", "Control"])
            writer.writerow(["S2", "Control"])
            writer.writerow(["S3", "Treated"])
            writer.writerow(["S4", "Treated"])

        plugin = RnaseqDEPlugin()

        candidates = plugin.generate(
            entity="RNA_SEQUENCE",
            objective={"analyze": "differential"},
            constraints=["padj=0.1"],
            count=1,
            count_matrix=str(counts_path),
            sample_metadata=str(metadata_path),
            condition_col="condition",
            treatment="Treated",
            control="Control",
            demo_mode=False,
        )

        assert len(candidates) == 1
        candidate = candidates[0]

        assert candidate.properties.get("status") == "success"
        assert candidate.properties.get("skill") == "rnaseq"

        output_json = candidate.properties.get("output")
        assert output_json is not None
        assert isinstance(output_json, dict)

        # We expect it ran PyDESeq2 and returned DE results
        # ClawBio rnaseq-de output returns files like result.json and tables/de_results.csv
        assert (
            "result.json" in output_json
            or "tables/de_results.csv" in output_json
            or "tables\\de_results.csv" in output_json
        )
