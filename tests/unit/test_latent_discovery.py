"""Unit tests for Latent Discovery & Biomarker Replication Gate (Glyph-inspired)."""

from __future__ import annotations

from pathlib import Path

from geneforgelang.core.gftypes import (
    GFLAST,
    ConfounderAdjustmentContract,
    DiscoveryNoveltyStatus,
    ExternalReplicationContract,
    LatentDiscoveryContract,
    LiteratureNoveltyTriageContract,
    SAEProbeSpec,
)
from geneforgelang.core.latent_discovery import LatentDiscoveryAuditor
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator


def _build_valid_contract() -> LatentDiscoveryContract:
    return LatentDiscoveryContract(
        contract_id="glyph_test_01",
        sae_probe=SAEProbeSpec(
            foundation_model="multimodal_ehr_fm_v2",
            target_layer="blocks.12.resid_post",
            dictionary_size=32768,
            sparsity_l0=32,
            multiple_testing_correction="fdr_bh",
            fdr_threshold=0.05,
        ),
        confounder_adjustment=ConfounderAdjustmentContract(
            confounders=["age", "sex", "site_id"],
            adjustment_method="multivariable_regression",
            require_residual_significance=True,
            max_adjusted_p_value=0.05,
        ),
        external_replication=ExternalReplicationContract(
            min_external_cohorts=2,
            cohort_ids=["hospital_a", "hospital_b", "hospital_c"],
            min_delta_auc=0.01,
            observed_delta_auc=0.025,
            require_direction_concordance=True,
        ),
        literature_triage=LiteratureNoveltyTriageContract(
            corpus_scope="pubmed",
            min_corpus_size=340000,
            require_positive_controls=True,
        ),
        findings=[
            {
                "latent_id": "sae_feat_01",
                "outcome": "heart_failure",
                "novelty_status": DiscoveryNoveltyStatus.REDISCOVERED_POSITIVE_CONTROL.value,
                "residual_p_value": 0.001,
                "replicated_cohorts": ["hospital_a", "hospital_b"],
                "direction_concordant": True,
                "citation_evidence": ["PMID:29420193"],
                "artifact_ref": "${sae_screen.feat_01}",
            },
            {
                "latent_id": "sae_feat_02",
                "outcome": "neurodegeneration",
                "novelty_status": DiscoveryNoveltyStatus.NOVEL_CANDIDATE.value,
                "residual_p_value": 0.003,
                "replicated_cohorts": ["hospital_a", "hospital_c"],
                "direction_concordant": True,
                "citation_evidence": [],
                "artifact_ref": "${sae_screen.feat_02}",
            },
        ],
    )


class TestLatentDiscoveryTypes:
    """AST serialization and alias parsing tests."""

    def test_contract_round_trip(self) -> None:
        contract = _build_valid_contract()
        rebuilt = LatentDiscoveryContract.from_dict(contract.to_dict())
        assert rebuilt.contract_id == "glyph_test_01"
        assert rebuilt.sae_probe.dictionary_size == 32768
        assert rebuilt.external_replication.min_external_cohorts == 2

    def test_gfl_ast_alias_parsing(self) -> None:
        contract_dict = _build_valid_contract().to_dict()
        ast_primary = GFLAST.from_dict({"latent_discovery": contract_dict})
        ast_alias = GFLAST.from_dict({"biomarker_discovery_gate": contract_dict})
        assert isinstance(ast_primary.latent_discovery, LatentDiscoveryContract)
        assert isinstance(ast_alias.latent_discovery, LatentDiscoveryContract)
        assert "latent_discovery" in ast_primary.to_dict()


class TestLatentDiscoveryAuditor:
    """Deterministic audit gate tests."""

    def test_valid_contract_passes(self) -> None:
        report = LatentDiscoveryAuditor.audit(_build_valid_contract())
        assert report.passed is True
        assert report.rediscovered_count == 1
        assert report.novel_candidate_count == 1
        assert report.evidence_status == "LATENT_DISCOVERY_VERIFIED"
        assert len(report.verification_hash) == 64

    def test_rejects_missing_confounders(self) -> None:
        contract = _build_valid_contract()
        contract.confounder_adjustment.confounders = []
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("confounders" in v for v in report.violations)

    def test_rejects_insufficient_external_cohorts(self) -> None:
        contract = _build_valid_contract()
        contract.findings[1]["replicated_cohorts"] = ["hospital_a"]
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("min_external_cohorts" in v for v in report.violations)

    def test_rejects_below_min_delta_auc(self) -> None:
        contract = _build_valid_contract()
        contract.external_replication.observed_delta_auc = 0.002
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("observed_delta_auc" in v for v in report.violations)

    def test_rejects_novel_candidate_without_positive_control(self) -> None:
        contract = _build_valid_contract()
        contract.findings = [contract.findings[1]]
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("rediscovered_positive_control" in v for v in report.violations)

    def test_rejects_novel_candidate_with_existing_citation(self) -> None:
        contract = _build_valid_contract()
        contract.findings[1]["citation_evidence"] = ["PMID:12345678"]
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("existing citation_evidence" in v for v in report.violations)

    def test_rejects_invalid_artifact_ref(self) -> None:
        contract = _build_valid_contract()
        contract.findings[0]["artifact_ref"] = "0.001_inline_literal"
        report = LatentDiscoveryAuditor.audit(contract)
        assert report.passed is False
        assert any("invalid artifact_ref" in v for v in report.violations)


class TestLatentDiscoveryValidator:
    """End-to-end parser + semantic validator integration tests."""

    def test_validate_official_exemplar(self) -> None:
        exemplar = Path(__file__).resolve().parents[2] / "examples" / "features" / "glyph_latent_discovery_gate.gfl"
        ast = parse_gfl(exemplar.read_text(encoding="utf-8"))
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert result.is_valid, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_unreplicated_novel_candidate(self) -> None:
        gfl_text = """
biomarker_discovery_gate:
  contract_id: "invalid_gate_01"
  sae_probe:
    foundation_model: "ehr_fm"
    target_layer: "layer_8"
    dictionary_size: 4096
    sparsity_l0: 16
  confounder_adjustment:
    confounders:
      - "age"
  external_replication:
    min_external_cohorts: 2
    cohort_ids:
      - "site_1"
      - "site_2"
  literature_triage:
    require_positive_controls: true
  findings:
    - latent_id: "feat_99"
      outcome: "mortality"
      novelty_status: "novel_candidate"
      residual_p_value: 0.001
      replicated_cohorts:
        - "site_1"
      direction_concordant: false
"""
        ast = parse_gfl(gfl_text)
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert not result.is_valid
        assert len(result.errors) >= 3
