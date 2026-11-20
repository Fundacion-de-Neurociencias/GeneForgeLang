"""Unit tests for strict by-reference provenance and numeric reconciliation gates."""

from __future__ import annotations

from pathlib import Path

import yaml

from geneforgelang.core.errors import ErrorCodes
from geneforgelang.core.gftypes import (
    GFLAST,
    ArtifactRef,
    NumericReconciliationContract,
    ProvenanceBindingMode,
)
from geneforgelang.core.numeric_provenance import NumericProvenanceAuditor
from geneforgelang.core.validator import EnhancedSemanticValidator


class TestNumericProvenanceTypes:
    """Tests for ArtifactRef, NumericReconciliationContract, and GFLAST roundtrip."""

    def test_artifact_ref_and_contract_roundtrip(self) -> None:
        ref = ArtifactRef(
            step_id="step_rna",
            output_key="ntpm",
            artifact_hash="sha256:abc123",
            source_record_id="HPA_01",
        )
        contract = NumericReconciliationContract(
            contract_id="num_prov_01",
            provenance_binding=ProvenanceBindingMode.STRICT_REFERENCE,
            source_records={"HPA_01": {"ntpm": 42.5}},
            cited_claims=[
                {
                    "claim_id": "c1",
                    "metric_key": "ntpm",
                    "declared_value": 42.5,
                    "source_record_id": "HPA_01",
                    "artifact_ref": ref.to_dict(),
                }
            ],
        )

        d = contract.to_dict()
        rec = NumericReconciliationContract.from_dict(d)
        assert rec.contract_id == "num_prov_01"
        assert rec.provenance_binding == ProvenanceBindingMode.STRICT_REFERENCE
        assert rec.source_records["HPA_01"]["ntpm"] == 42.5
        assert len(rec.cited_claims) == 1

    def test_gflast_roundtrip_and_alias(self) -> None:
        contract = NumericReconciliationContract(contract_id="ast_np_01")
        ast = GFLAST(numeric_provenance=contract)
        d = ast.to_dict()
        assert "numeric_provenance" in d

        rec1 = GFLAST.from_dict(d)
        assert rec1.numeric_provenance is not None
        assert rec1.numeric_provenance.contract_id == "ast_np_01"

        rec2 = GFLAST.from_dict({"reconciled_report": d["numeric_provenance"]})
        assert rec2.numeric_provenance is not None
        assert rec2.numeric_provenance.contract_id == "ast_np_01"


class TestNumericProvenanceAuditor:
    """Tests for strict no-retype reference checks and source-record reconciliation."""

    def test_reconcile_passes_with_valid_refs_and_matching_values(self) -> None:
        contract = NumericReconciliationContract(
            contract_id="audit_pass_01",
            provenance_binding=ProvenanceBindingMode.STRICT_REFERENCE,
            source_records={"REC_1": {"rna_tpm": 18.25, "protein_score": 2.0}},
            cited_claims=[
                {
                    "claim_id": "c_rna",
                    "metric_key": "rna_tpm",
                    "declared_value": 18.25,
                    "source_record_id": "REC_1",
                    "artifact_ref": ArtifactRef(step_id="s1", output_key="rna_tpm"),
                },
                {
                    "claim_id": "c_prot",
                    "metric_key": "protein_score",
                    "declared_value": 2.0,
                    "source_record_id": "REC_1",
                    "artifact_ref": "${s2.protein_score}",
                },
            ],
        )

        report = NumericProvenanceAuditor.reconcile(contract)
        assert report.passed is True
        assert report.checked_claims == 2
        assert report.mismatches == []
        assert report.retype_violations == []
        assert report.evidence_status == "NUMERIC_PROVENANCE_VERIFIED"
        assert len(report.verification_hash) == 64

    def test_reconcile_rejects_inline_retyped_value_without_ref(self) -> None:
        contract = NumericReconciliationContract(
            contract_id="audit_retype_fail",
            provenance_binding=ProvenanceBindingMode.STRICT_REFERENCE,
            source_records={"REC_1": {"rna_tpm": 18.25}},
            cited_claims=[
                {
                    "claim_id": "c_ungrounded",
                    "metric_key": "rna_tpm",
                    "declared_value": 18.25,
                    "source_record_id": "REC_1",
                    # Missing artifact_ref in strict_reference mode
                }
            ],
        )

        report = NumericProvenanceAuditor.reconcile(contract)
        assert report.passed is False
        assert len(report.retype_violations) == 1
        assert report.evidence_status == "NUMERIC_PROVENANCE_REJECTED"

    def test_reconcile_rejects_numeric_mismatch_against_source_record(self) -> None:
        contract = NumericReconciliationContract(
            contract_id="audit_mismatch_fail",
            provenance_binding=ProvenanceBindingMode.STRICT_REFERENCE,
            source_records={"REC_1": {"rna_tpm": 18.25}},
            cited_claims=[
                {
                    "claim_id": "c_hallucinated",
                    "metric_key": "rna_tpm",
                    "declared_value": 99.9,
                    "source_record_id": "REC_1",
                    "artifact_ref": "${s1.rna_tpm}",
                }
            ],
        )

        report = NumericProvenanceAuditor.reconcile(contract)
        assert report.passed is False
        assert len(report.mismatches) == 1
        assert "mismatch" in report.mismatches[0]


class TestNumericProvenanceValidator:
    """Tests for EnhancedSemanticValidator integration."""

    def test_validate_official_exemplar(self) -> None:
        exemplar_path = Path(__file__).parents[2] / "examples" / "features" / "atlas_numeric_provenance_gate.gfl"
        assert exemplar_path.exists()

        with open(exemplar_path, encoding="utf-8") as f:
            ast_data = yaml.safe_load(f.read())

        res = EnhancedSemanticValidator().validate_ast(ast_data)
        assert res.is_valid, f"Validation errors: {[e.message for e in res.errors]}"

    def test_validator_rejects_ungrounded_and_mismatched_claims(self) -> None:
        bad_ast = {
            "reconciled_report": {
                "contract_id": "bad_report_01",
                "provenance_binding": "strict_reference",
                "source_records": {"HPA_1": {"ntpm": 10.0}},
                "cited_claims": [
                    {
                        "claim_id": "c1",
                        "metric_key": "ntpm",
                        "declared_value": 25.0,
                        "source_record_id": "HPA_1",
                    }
                ],
            }
        }
        res = EnhancedSemanticValidator().validate_ast(bad_ast)
        assert not res.is_valid
        assert any(e.code == ErrorCodes.SEMANTIC_CONTRACT_MISMATCH for e in res.errors)
        messages = " | ".join(e.message for e in res.errors)
        assert "strict_reference" in messages
        assert "mismatch" in messages
