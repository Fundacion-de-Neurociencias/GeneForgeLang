"""Unit tests for BGC and Megasynthase domain architecture and assembly line plugin."""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("gfl-plugin-bgc"))

from geneforgelang.core.gftypes import (
    BGCAssemblyContract,
    BiosyntheticDomainType,
    MegasynthaseDomain,
    MegasynthaseModule,
)
from gfl_plugin_bgc.plugin import BGCPlugin


def test_bgc_domain_enums():
    assert BiosyntheticDomainType.KS == "KS"
    assert BiosyntheticDomainType.AT == "AT"
    assert BiosyntheticDomainType.KR == "KR"
    assert BiosyntheticDomainType.DH == "DH"
    assert BiosyntheticDomainType.ER == "ER"
    assert BiosyntheticDomainType.ACP == "ACP"
    assert BiosyntheticDomainType.TE == "TE"
    assert BiosyntheticDomainType.CONDENSATION == "CONDENSATION"
    assert BiosyntheticDomainType.ADENYLATION == "ADENYLATION"
    assert BiosyntheticDomainType.THIOLATION == "THIOLATION"


def test_valid_8_domain_megasynthase_assembly_line():
    plugin = BGCPlugin()
    assert plugin.name == "bgc"

    # Construct 8-domain ~2500 AA PKS assembly line for delta-valerolactam precursor
    mod1 = MegasynthaseModule(
        module_index=0,
        is_loading=True,
        elongation_substrate="malonyl-CoA",
        domains=[
            MegasynthaseDomain("mod1_at", BiosyntheticDomainType.AT, 1, 350, substrate_specificity="malonyl-CoA"),
            MegasynthaseDomain("mod1_acp", BiosyntheticDomainType.ACP, 360, 450),
        ],
    )
    mod2 = MegasynthaseModule(
        module_index=1,
        is_loading=False,
        is_termination=True,
        elongation_substrate="methylmalonyl-CoA",
        domains=[
            MegasynthaseDomain("mod2_ks", BiosyntheticDomainType.KS, 460, 880),
            MegasynthaseDomain("mod2_at", BiosyntheticDomainType.AT, 890, 1200),
            MegasynthaseDomain("mod2_dh", BiosyntheticDomainType.DH, 1210, 1400),
            MegasynthaseDomain("mod2_kr", BiosyntheticDomainType.KR, 1410, 1850),
            MegasynthaseDomain("mod2_acp", BiosyntheticDomainType.ACP, 1860, 1950),
            MegasynthaseDomain("mod2_te", BiosyntheticDomainType.TE, 1960, 2480),
        ],
    )

    contract = BGCAssemblyContract(
        cluster_id="BGC_VALEROLACTLM_01",
        cluster_type="PKS_TYPE_I",
        target_chemical_product="delta-valerolactam",
        modules=[mod1, mod2],
    )

    assert contract.total_domains() == 8
    is_valid, errors = plugin.validate_assembly_contract(contract)
    assert is_valid is True
    assert len(errors) == 0
    assert contract.validation_status == "VALIDATED"
    score = plugin.score_cross_domain_compatibility(contract.modules)
    assert score > 0.8


def test_bgc_validation_missing_carrier():
    plugin = BGCPlugin()
    broken_mod = MegasynthaseModule(
        module_index=0,
        is_loading=False,
        is_termination=True,
        domains=[
            MegasynthaseDomain("d_ks", BiosyntheticDomainType.KS, 1, 400),
            MegasynthaseDomain("d_te", BiosyntheticDomainType.TE, 410, 700),
        ],
    )
    contract = BGCAssemblyContract(
        cluster_id="BGC_INVALID_CARRIER",
        cluster_type="PKS_TYPE_I",
        target_chemical_product="test_product",
        modules=[broken_mod],
    )
    is_valid, errors = plugin.validate_assembly_contract(contract)
    assert is_valid is False
    assert contract.validation_status == "REJECTED"
    assert any("carrier" in err.lower() for err in errors)


def test_bgc_validation_missing_termination():
    plugin = BGCPlugin()
    mod = MegasynthaseModule(
        module_index=0,
        is_loading=True,
        is_termination=False,
        domains=[
            MegasynthaseDomain("d_at", BiosyntheticDomainType.AT, 1, 400),
            MegasynthaseDomain("d_acp", BiosyntheticDomainType.ACP, 410, 500),
        ],
    )
    contract = BGCAssemblyContract(
        cluster_id="BGC_INVALID_TERMINATION",
        cluster_type="PKS_TYPE_I",
        target_chemical_product="test_product",
        modules=[mod],
    )
    is_valid, errors = plugin.validate_assembly_contract(contract)
    assert is_valid is False
    assert any("termination" in err.lower() for err in errors)


def test_bgc_generation_candidates():
    plugin = BGCPlugin()
    candidates = plugin.generate(
        entity="ProteinSequence",
        objective={"target": "delta-valerolactam"},
        constraints=["length <= 2600"],
        count=2,
    )
    assert len(candidates) == 2
    assert "DELTA-VALEROLACTAM" in candidates[0].sequence
    assert candidates[0].properties["estimated_domains"] == 8
