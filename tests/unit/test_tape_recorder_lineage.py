"""Unit tests for DNA Typewriter cellular tape recorder lineage tracing contracts.
================================================================================
Validates AST structures, semantic validation, capacity checks, and serialization
based on Science 2026 (Yu et al., DOI: 10.1126/science.ael0508).
"""

from __future__ import annotations

import pytest
from geneforgelang.core.gftypes import (
    GFLAST,
    CassetteArchitecture,
    LineageNode,
    ReadoutModality,
    TapeRecorderContract,
)
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestTapeRecorderContracts:
    """Test AST representation and domain contracts for DNA Typewriter."""

    def test_enums_values(self) -> None:
        assert CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL.value == "tandem_pegRNA_insertional"
        assert CassetteArchitecture.BASE_EDITOR_ACCUMULATION.value == "base_editor_accumulation"
        assert ReadoutModality.TARGETED_AMPLICON_DNA_SEQ.value == "targeted_amplicon_dna_seq"

    def test_contract_defaults_and_capacity(self) -> None:
        recorder = TapeRecorderContract(
            recorder_id="MouseEmbryoTape",
            cassette_architecture=CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL,
            tape_capacity_sites=50,
            recording_interval_hours=6.0,
            edit_signature_alphabet=["Ins_A1", "Ins_B2", "Ins_C3", "Del_D1"],
        )
        assert recorder.total_recording_capacity_hours == 300.0
        # 13.5 days = 324 hours
        assert recorder.can_accommodate_duration_hours(250.0) is True
        assert recorder.can_accommodate_duration_hours(350.0) is False

    def test_lineage_node_representation(self) -> None:
        node = LineageNode(
            cell_id="zygote_0",
            generation=0,
            tape_state=["Ins_A1"],
            children=["blastomere_1", "blastomere_2"],
            cell_type_annotation="totipotent_zygote",
            time_point_hours=0.0,
        )
        d = node.to_dict()
        assert d["cell_id"] == "zygote_0"
        assert d["generation"] == 0
        assert len(d["children"]) == 2

    def test_gflast_roundtrip_tape_recorder(self) -> None:
        contract = TapeRecorderContract(
            recorder_id="MouseEmbryoTape",
            cassette_architecture=CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL,
            tape_capacity_sites=50,
            recording_interval_hours=6.0,
            edit_signature_alphabet=["Ins_A1", "Ins_B2", "Ins_C3"],
            target_organism="mus_musculus",
            developmental_window="13.5_days",
            readout_modality=ReadoutModality.TARGETED_AMPLICON_DNA_SEQ,
        )
        ast = GFLAST(tape_recorder=contract)
        serialized = ast.to_dict()
        assert "tape_recorder" in serialized
        assert serialized["tape_recorder"]["tape_capacity_sites"] == 50
        assert serialized["tape_recorder"]["recording_interval_hours"] == 6.0

        recovered = GFLAST.from_dict(serialized)
        assert isinstance(recovered.tape_recorder, TapeRecorderContract)
        assert recovered.tape_recorder.recorder_id == "MouseEmbryoTape"
        assert recovered.tape_recorder.tape_capacity_sites == 50
        assert recovered.tape_recorder.edit_signature_alphabet == ["Ins_A1", "Ins_B2", "Ins_C3"]


class TestSemanticValidationTapeRecorder:
    """Validate semantic validation behavior for tape_recorder blocks."""

    def test_validate_valid_tape_recorder(self) -> None:
        validator = EnhancedSemanticValidator()
        ast = {
            "tape_recorder": {
                "recorder_id": "MouseEmbryoTape",
                "cassette_architecture": "tandem_pegRNA_insertional",
                "tape_capacity_sites": 50,
                "recording_interval_hours": 6.0,
                "edit_signature_alphabet": ["Ins_A1", "Ins_B2", "Ins_C3", "Del_D1"],
                "target_organism": "mus_musculus",
                "developmental_window": "13.5_days",
                "readout_modality": "targeted_amplicon_dna_seq",
            }
        }
        res = validator.validate_ast(ast)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_validate_tape_recorder_with_contract_instance(self) -> None:
        validator = EnhancedSemanticValidator()
        contract = TapeRecorderContract(
            recorder_id="MouseEmbryoTape",
            tape_capacity_sites=50,
            recording_interval_hours=6.0,
            edit_signature_alphabet=["Ins_A1"],
        )
        ast = {"tape_recorder": contract}
        res = validator.validate_ast(ast)
        assert res.is_valid is True
        assert len(res.errors) == 0

    def test_validate_invalid_tape_capacity_sites(self) -> None:
        validator = EnhancedSemanticValidator()
        ast = {
            "tape_recorder": {
                "recorder_id": "InvalidTape",
                "tape_capacity_sites": -10,  # invalid negative capacity
            }
        }
        res = validator.validate_ast(ast)
        assert res.is_valid is False
        assert any("tape_capacity_sites" in e.message for e in res.errors)

    def test_validate_invalid_recording_interval(self) -> None:
        validator = EnhancedSemanticValidator()
        ast = {
            "tape_recorder": {
                "recorder_id": "InvalidTape",
                "recording_interval_hours": 0.0,  # invalid non-positive
            }
        }
        res = validator.validate_ast(ast)
        assert res.is_valid is False
        assert any("recording_interval_hours" in e.message for e in res.errors)

    def test_validate_empty_edit_signatures(self) -> None:
        validator = EnhancedSemanticValidator()
        ast = {
            "tape_recorder": {
                "recorder_id": "InvalidTape",
                "edit_signature_alphabet": [],  # invalid empty
            }
        }
        res = validator.validate_ast(ast)
        assert res.is_valid is False
        assert any("edit_signature_alphabet cannot be empty" in e.message for e in res.errors)

    def test_validate_experiment_with_dna_typewriter(self) -> None:
        validator = EnhancedSemanticValidator()
        ast = {
            "experiment": {
                "tool": "dna_typewriter",
                "type": "gene_editing",
                "params": {
                    "target_gene": "Rosa26_tape",
                    "tape_capacity_sites": 50,
                },
            }
        }
        res = validator.validate_ast(ast)
        assert res.is_valid is True
        assert len(res.errors) == 0
