"""Unit tests for SDRF Sample Metadata Contract (sample_metadata / sdrf_contract)."""

from __future__ import annotations

from pathlib import Path

from geneforgelang.core.gftypes import (
    GFLAST,
    ProteomicsRepository,
    SDRFMetadataContract,
    SDRFSampleEntry,
)
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.sample_metadata import SampleMetadataAuditor
from geneforgelang.core.validator import EnhancedSemanticValidator


def _build_valid_contract() -> SDRFMetadataContract:
    return SDRFMetadataContract(
        contract_id="sdrf_test_01",
        accession="PXD000001",
        repository=ProteomicsRepository.PRIDE,
        sdrf_version="1.0",
        source_citations=["PMID:23626761", "PXD000001"],
        samples=[
            SDRFSampleEntry(
                source_name="Erwinia_carotovora_sample_1",
                organism="Pectobacterium atrosepticum",
                assay_name="run_01",
                data_file="TMT_Erwinia_1uLSike_Top10HCD_f01.raw",
                artifact_ref="${pride_ingest.run_01_raw}",
            )
        ],
    )


class TestSampleMetadataTypes:
    """AST serialization and alias parsing tests."""

    def test_contract_round_trip(self) -> None:
        contract = _build_valid_contract()
        rebuilt = SDRFMetadataContract.from_dict(contract.to_dict())
        assert rebuilt.contract_id == "sdrf_test_01"
        assert rebuilt.accession == "PXD000001"
        assert rebuilt.repository == ProteomicsRepository.PRIDE
        assert len(rebuilt.samples) == 1

    def test_gfl_ast_alias_parsing(self) -> None:
        contract_dict = _build_valid_contract().to_dict()
        ast_primary = GFLAST.from_dict({"sample_metadata": contract_dict})
        ast_alias = GFLAST.from_dict({"sdrf_contract": contract_dict})
        assert isinstance(ast_primary.sample_metadata, SDRFMetadataContract)
        assert isinstance(ast_alias.sample_metadata, SDRFMetadataContract)
        assert "sample_metadata" in ast_primary.to_dict()


class TestSampleMetadataAuditor:
    """Deterministic SDRF audit gate tests."""

    def test_valid_contract_passes(self) -> None:
        report = SampleMetadataAuditor.audit(_build_valid_contract())
        assert report.passed is True
        assert report.sample_count == 1
        assert report.evidence_status == "SDRF_METADATA_VERIFIED"
        assert len(report.verification_hash) == 64

    def test_rejects_invalid_accession(self) -> None:
        contract = _build_valid_contract()
        contract.accession = "FAKE123"
        report = SampleMetadataAuditor.audit(contract)
        assert report.passed is False
        assert any("Invalid proteomics accession" in v for v in report.violations)

    def test_rejects_missing_source_citations(self) -> None:
        contract = _build_valid_contract()
        contract.source_citations = []
        report = SampleMetadataAuditor.audit(contract)
        assert report.passed is False
        assert any("source_citations" in v for v in report.violations)

    def test_rejects_placeholder_sample_and_file_names(self) -> None:
        contract = _build_valid_contract()
        contract.samples[0].data_file = "placeholder_file.raw"
        report = SampleMetadataAuditor.audit(contract)
        assert report.passed is False
        assert any("placeholder" in v for v in report.violations)

    def test_rejects_invalid_artifact_ref(self) -> None:
        contract = _build_valid_contract()
        contract.samples[0].artifact_ref = "raw_literal_path.raw"
        report = SampleMetadataAuditor.audit(contract)
        assert report.passed is False
        assert any("invalid artifact_ref" in v for v in report.violations)


class TestSampleMetadataValidator:
    """End-to-end parser + semantic validator integration tests."""

    def test_validate_official_exemplar(self) -> None:
        exemplar = Path(__file__).resolve().parents[2] / "examples" / "features" / "sdrf_sample_metadata_contract.gfl"
        ast = parse_gfl(exemplar.read_text(encoding="utf-8"))
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert result.is_valid, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_ungrounded_sdrf_contract(self) -> None:
        gfl_text = """
sdrf_contract:
  contract_id: "bad_sdrf_01"
  accession: "BAD_ACC"
  repository: "pride"
  source_citations: []
  samples:
    - source_name: "dummy_sample"
      organism: "Homo sapiens"
      assay_name: "run_1"
      data_file: ""
"""
        ast = parse_gfl(gfl_text)
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert not result.is_valid
        assert len(result.errors) >= 3
