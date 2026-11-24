"""Unit tests for Cross-Modal Cell Alignment Contract (cell_alignment / cross_modal_cell_bridge)."""

from __future__ import annotations

from pathlib import Path

from geneforgelang.core.cell_alignment import CellAlignmentAuditor
from geneforgelang.core.gftypes import (
    GFLAST,
    CellAlignmentContract,
    CellAlignmentMapping,
    CellModality,
    CellStudySlice,
)
from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator


def _build_valid_contract() -> CellAlignmentContract:
    return CellAlignmentContract(
        contract_id="bloom_test_01",
        bridge_model="bloom_multiome_bridge_v1",
        bridge_species="Mus musculus",
        bridge_modalities=[CellModality.SCRNA_SEQ, CellModality.SCATAC_SEQ],
        reference_taxonomy="allen_brain_cell_atlas",
        anchor_cell_types=["CL:0000127"],
        min_mapping_confidence=0.75,
        max_unmapped_fraction=0.15,
        observed_unmapped_fraction=0.05,
        studies=[
            CellStudySlice(
                study_id="study_rna",
                modality=CellModality.SCRNA_SEQ,
                species="Mus musculus",
                cell_count=10000,
            ),
            CellStudySlice(
                study_id="study_ephys",
                modality=CellModality.ELECTROPHYSIOLOGY,
                species="Mus musculus",
                cell_count=900,
            ),
        ],
        mappings=[
            CellAlignmentMapping(
                source_study_id="study_ephys",
                target_study_id="study_rna",
                source_label="fast_spiking_basket",
                target_label="Pvalb_Gaba",
                taxonomy_curie="CL:0000127",
                mapping_confidence=0.92,
                is_anchor=True,
                artifact_ref="${bloom_align.pvalb}",
            )
        ],
    )


class TestCellAlignmentTypes:
    """AST serialization and alias parsing tests."""

    def test_contract_round_trip(self) -> None:
        contract = _build_valid_contract()
        rebuilt = CellAlignmentContract.from_dict(contract.to_dict())
        assert rebuilt.contract_id == "bloom_test_01"
        assert rebuilt.bridge_species == "Mus musculus"
        assert len(rebuilt.studies) == 2
        assert len(rebuilt.mappings) == 1

    def test_gfl_ast_alias_parsing(self) -> None:
        contract_dict = _build_valid_contract().to_dict()
        ast_primary = GFLAST.from_dict({"cell_alignment": contract_dict})
        ast_alias = GFLAST.from_dict({"cross_modal_cell_bridge": contract_dict})
        assert isinstance(ast_primary.cell_alignment, CellAlignmentContract)
        assert isinstance(ast_alias.cell_alignment, CellAlignmentContract)
        assert "cell_alignment" in ast_primary.to_dict()


class TestCellAlignmentAuditor:
    """Deterministic cross-modal cell alignment audit tests."""

    def test_valid_contract_passes(self) -> None:
        report = CellAlignmentAuditor.audit(_build_valid_contract())
        assert report.passed is True
        assert report.study_count == 2
        assert report.anchor_mapping_count == 1
        assert report.evidence_status == "CELL_ALIGNMENT_VERIFIED"
        assert len(report.verification_hash) == 64

    def test_rejects_disjoint_modalities_without_bridge_modalities(self) -> None:
        contract = _build_valid_contract()
        contract.bridge_modalities = []
        report = CellAlignmentAuditor.audit(contract)
        assert report.passed is False
        assert any("bridge_modalities" in v for v in report.violations)

    def test_rejects_silent_cross_species_transfer(self) -> None:
        contract = _build_valid_contract()
        contract.studies[1].species = "Homo sapiens"
        report = CellAlignmentAuditor.audit(contract)
        assert report.passed is False
        assert any("allow_cross_species_transfer" in v for v in report.violations)

    def test_allows_explicit_cross_species_transfer_with_orthologs(self) -> None:
        contract = _build_valid_contract()
        contract.studies[1].species = "Homo sapiens"
        contract.allow_cross_species_transfer = True
        contract.ortholog_anchors = ["PVALB", "GAD1"]
        report = CellAlignmentAuditor.audit(contract)
        assert report.passed is True

    def test_rejects_low_confidence_and_missing_anchor(self) -> None:
        contract = _build_valid_contract()
        contract.mappings[0].mapping_confidence = 0.42
        contract.mappings[0].is_anchor = False
        report = CellAlignmentAuditor.audit(contract)
        assert report.passed is False
        assert any("min_mapping_confidence" in v for v in report.violations)
        assert any("is_anchor=True" in v for v in report.violations)

    def test_rejects_invalid_artifact_ref(self) -> None:
        contract = _build_valid_contract()
        contract.mappings[0].artifact_ref = "0.92_raw_float"
        report = CellAlignmentAuditor.audit(contract)
        assert report.passed is False
        assert any("invalid artifact_ref" in v for v in report.violations)


class TestCellAlignmentValidator:
    """End-to-end parser + semantic validator integration tests."""

    def test_validate_official_exemplar(self) -> None:
        exemplar = (
            Path(__file__).resolve().parents[2] / "examples" / "features" / "bloom_cross_modal_cell_alignment.gfl"
        )
        ast = parse_gfl(exemplar.read_text(encoding="utf-8"))
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert result.is_valid, f"Validation errors: {[e.message for e in result.errors]}"

    def test_validator_rejects_unbridged_cross_species_alignment(self) -> None:
        gfl_text = """
cross_modal_cell_bridge:
  contract_id: "bad_align_01"
  bridge_model: "mouse_bridge"
  bridge_species: "Mus musculus"
  bridge_modalities: []
  anchor_cell_types:
    - "CL:0000127"
  studies:
    - study_id: "s1"
      modality: "scrna_seq"
      species: "Homo sapiens"
    - study_id: "s2"
      modality: "electrophysiology"
      species: "Mus musculus"
"""
        ast = parse_gfl(gfl_text)
        result = EnhancedSemanticValidator().validate_ast(ast)
        assert not result.is_valid
        assert len(result.errors) >= 2
