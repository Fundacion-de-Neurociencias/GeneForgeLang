"r""Tests for AlphaGenome Atlas GFL Integration and Plugin."""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("gfl-plugin-alphagenome"))

from geneforgelang.core.gftypes import (
AviModality,
AviScore,
RegulatoryMotifAnnotation as CoreMotifAnnotation,
VariantImpact,
)
from gfl_plugin_alphagenome.plugin import (
AlphaGenomePlugin,
AviScoreResult,
RegulatoryMotifAnnotation,
)
from geneforgelang.plugins.interfaces import EntityType


def test_alphagenome_core_types():
    score = AviScore(
        phred=25.4,
        raw=0.82,
        quantile=0.00288,
        top_percentile=0.288,
        top_modality=AviModality.CHIP_TF.value,
        top_feature_importance=0.65,
        feature_importances={"ChIP-TF": 0.65, "DNASE-seq": 0.20},
    )
    assert score.is_high_impact is True
    assert score.is_ultra_rare_impact is False

    motif = CoreMotifAnnotation(
        motif_id="MOTIF_001",
        motif_name="E-box",
        chromosome="chr9",
        position=128225994,
        transcription_factors=["MYC", "MAX"],
    )
    assert motif.motif_name == "E-box"

    impact = VariantImpact(
        variant_str="chr9:128225994:G>A",
        chromosome="chr9",
        position=128225994,
        ref="G",
        alt="A",
        avi_score=score,
        regulatory_motifs=[motif],
    )
    assert "alphagenome/atlas/variant/chr9:128225994:G>A" in impact.atlas_url
    d = impact.to_dict()
    assert d["variant"] == "chr9:128225994:G>A"
    assert d["avi_score"]["is_high_impact"] is True


def test_alphagenome_plugin_initialization_and_parsing():
    plugin = AlphaGenomePlugin()
    assert plugin.name == "alphagenome_atlas"
    assert EntityType.DNA_SEQUENCE in plugin.supported_entities

    chrom, pos, ref, alt = plugin.parse_variant("chr11:5225488:A>T")
    assert chrom == "chr11"
    assert pos == 5225488
    assert ref == "A"
    assert alt == "T"

    with pytest.raises(ValueError):
        plugin.parse_variant("invalid_variant_syntax")


def test_alphagenome_plugin_score_variant():
    plugin = AlphaGenomePlugin()
    res = plugin.score_variant("chr9:128225994:G>A", min_phred=25.0)

    assert isinstance(res, AviScoreResult)
    assert res.variant == "chr9:128225994:G>A"
    assert res.avi_phred >= 20.0
    assert res.is_high_impact is True
    assert "https://deepmind.google.com/science/alphagenome/atlas/variant/" in res.atlas_url


def test_alphagenome_plugin_generate_candidate():
    plugin = AlphaGenomePlugin()
    candidates = plugin.generate(
        entity="DNASequence",
        objective={"maximize": "avi_phred"},
        constraints=["has_motif(E-box)"],
        count=1,
        variant="chr9:128225994:G>A",
        min_phred=22.0,
    )

    assert len(candidates) == 1
    cand = candidates[0]
    assert cand.properties["variant"] == "chr9:128225994:G>A"
    assert cand.properties["is_high_impact"] is True
    assert cand.properties["plugin_name"] == "alphagenome_atlas"
