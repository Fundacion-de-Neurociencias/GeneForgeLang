"""Unit tests for AlphaFold v3.0.5 contract support and Upstream Bio-AI Release Watchdog."""

from __future__ import annotations

from geneforgelang.core.gftypes import (
    BoltzmannEnsembleContract,
    EnsembleGenerator,
    MultiModelConsensus,
)
from geneforgelang.core.upstream_watchdog import (
    UPSTREAM_BIOAI_REGISTRY,
    check_all_upstream_engines,
    evaluate_release_status,
    parse_semver,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestAlphaFold305ContractSupport:
    """Test AlphaFold v3.0.5 fast Jackhmmer MSA and version tracking in GFL contracts."""

    def test_multimodel_consensus_af3_defaults(self) -> None:
        consensus = MultiModelConsensus(af3_iptm=0.88, af3_ipae=1.9)
        assert consensus.af3_version == "3.0.5"
        assert consensus.af3_fast_jackhmmer_msa is True
        d = consensus.to_dict()
        assert d["af3_version"] == "3.0.5"
        assert d["af3_fast_jackhmmer_msa"] is True
        assert d["passes_consensus"] is True

    def test_boltzmann_ensemble_af3_version_roundtrip(self) -> None:
        contract = BoltzmannEnsembleContract.from_dict(
            {
                "target": "TDP43_HUMAN",
                "generator": "alphafold3",
                "engine_version": "3.0.5",
                "fast_jackhmmer_msa": True,
            }
        )
        assert contract.generator == EnsembleGenerator.ALPHAFOLD_3
        assert contract.engine_version == "3.0.5"
        assert contract.fast_jackhmmer_msa is True
        d = contract.to_dict()
        assert d["engine_version"] == "3.0.5"
        assert d["fast_jackhmmer_msa"] is True

    def test_validator_alphafold3_version_checks(self) -> None:
        validator = EnhancedSemanticValidator()

        # 1. Valid AlphaFold v3.0.5 -> 0 errors, 0 warnings
        res_ok = validator.validate_ast(
            {
                "ensemble": {
                    "target": "TDP43",
                    "generator": "alphafold3",
                    "engine_version": "3.0.5",
                    "fast_jackhmmer_msa": True,
                }
            }
        )
        assert res_ok.is_valid is True
        assert len(res_ok.warnings) == 0

        # 2. Outdated AlphaFold v3.0.1 -> emits warning advising upgrade to >=3.0.5
        validator_old = EnhancedSemanticValidator()
        res_old = validator_old.validate_ast(
            {
                "ensemble": {
                    "target": "TDP43",
                    "generator": "alphafold3",
                    "engine_version": "3.0.1",
                }
            }
        )
        assert any("older than v3.0.5" in w.message for w in res_old.warnings)


class TestUpstreamBioAIWatchdog:
    """Test semantic version parsing and release evaluation in upstream_watchdog."""

    def test_parse_semver(self) -> None:
        assert parse_semver("v3.0.5") == (3, 0, 5)
        assert parse_semver("3.0.6-rc1") == (3, 0, 6)
        assert parse_semver("invalid") is None

    def test_evaluate_release_status_alphafold(self) -> None:
        assert "alphafold3" in UPSTREAM_BIOAI_REGISTRY

        # Current baseline v3.0.5 -> UP_TO_DATE
        cur = evaluate_release_status("alphafold3", "v3.0.5")
        assert cur["status"] == "UP_TO_DATE"
        assert cur["upgrade_available"] is False

        # Upcoming release v3.0.6 -> UPGRADE_AVAILABLE
        nxt = evaluate_release_status("alphafold3", "v3.0.6")
        assert nxt["status"] == "UPGRADE_AVAILABLE"
        assert nxt["upgrade_available"] is True
        assert nxt["repo_slug"] == "google-deepmind/alphafold3"

    def test_check_all_upstream_engines_offline(self) -> None:
        reports = check_all_upstream_engines(live=False)
        assert len(reports) == len(UPSTREAM_BIOAI_REGISTRY)
        assert all(r["status"] == "UP_TO_DATE" for r in reports)
