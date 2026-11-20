"""Strict By-Reference Provenance and Numeric Reconciliation Engine.

Inspired by Human Protein Atlas v26 / AtlasAI (no-retype + citation gating):
1. Enforces strict_reference provenance binding so downstream claims and reports
   cannot pass ungrounded inline numeric literals without an upstream ArtifactRef
   or `${step.output}` handle.
2. Reconciles every declared numeric claim against its cited source_records entry
   within tolerance, rejecting any unverified or mismatched report.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import (
    ArtifactRef,
    NumericReconciliationContract,
    ProvenanceBindingMode,
)

_REF_STRING_PATTERN = re.compile(r"^\$\{[A-Za-z0-9_.-]+\}$")


@dataclass
class ReconciliationReport:
    """Deterministic audit report for numeric provenance and citation reconciliation."""

    contract_id: str
    passed: bool
    checked_claims: int
    mismatches: list[str] = field(default_factory=list)
    retype_violations: list[str] = field(default_factory=list)
    verification_hash: str = ""
    evidence_status: str = "NUMERIC_PROVENANCE_VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "passed": self.passed,
            "checked_claims": self.checked_claims,
            "mismatches": list(self.mismatches),
            "retype_violations": list(self.retype_violations),
            "verification_hash": self.verification_hash,
            "evidence_status": self.evidence_status,
        }


class NumericProvenanceAuditor:
    """Deterministic auditor for by-reference data handles and citation reconciliation."""

    @staticmethod
    def is_valid_reference(ref: Any) -> bool:
        """Return True if ref is a valid ArtifactRef, reference dict, or `${step.output}` string."""
        if isinstance(ref, ArtifactRef):
            return bool(ref.step_id.strip() and ref.output_key.strip())
        if isinstance(ref, dict):
            return bool(str(ref.get("step_id", "")).strip() and str(ref.get("output_key", "")).strip())
        if isinstance(ref, str):
            return bool(_REF_STRING_PATTERN.match(ref.strip()))
        return False

    @classmethod
    def reconcile(cls, contract: NumericReconciliationContract) -> ReconciliationReport:
        """Audit all cited claims for by-reference grounding and source-record reconciliation."""
        mismatches: list[str] = []
        retype_violations: list[str] = []

        for idx, claim in enumerate(contract.cited_claims):
            claim_id = str(claim.get("claim_id", f"claim_{idx}"))
            metric_key = str(claim.get("metric_key", "")).strip()
            source_id = str(claim.get("source_record_id", "")).strip()
            declared_raw = claim.get("declared_value")
            tolerance = float(claim.get("tolerance", 1e-6))

            if contract.provenance_binding == ProvenanceBindingMode.STRICT_REFERENCE and not cls.is_valid_reference(
                claim.get("artifact_ref")
            ):
                retype_violations.append(
                    f"Claim '{claim_id}' violates strict_reference binding: "
                    "missing valid ArtifactRef or '${step.output}' handle."
                )

            if contract.require_reconciliation:
                if not source_id or source_id not in contract.source_records:
                    mismatches.append(f"Claim '{claim_id}' cites missing source_record_id '{source_id}'.")
                    continue

                record = contract.source_records[source_id]
                if not metric_key or metric_key not in record:
                    mismatches.append(
                        f"Claim '{claim_id}' cites missing metric_key '{metric_key}' in record '{source_id}'."
                    )
                    continue

                try:
                    declared_val = float(declared_raw)  # type: ignore[arg-type]
                    source_val = float(record[metric_key])
                except (TypeError, ValueError):
                    mismatches.append(
                        f"Claim '{claim_id}' has non-numeric declared or source value for '{metric_key}'."
                    )
                    continue

                if abs(declared_val - source_val) > tolerance:
                    mismatches.append(
                        f"Claim '{claim_id}' mismatch for '{metric_key}' in '{source_id}': "
                        f"declared={declared_val} vs source={source_val} (tol={tolerance})."
                    )

        passed = len(mismatches) == 0 and len(retype_violations) == 0
        evidence_status = "NUMERIC_PROVENANCE_VERIFIED" if passed else "NUMERIC_PROVENANCE_REJECTED"
        payload = (
            f"{contract.contract_id}:{passed}:{len(contract.cited_claims)}:{len(mismatches)}:{len(retype_violations)}"
        )
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return ReconciliationReport(
            contract_id=contract.contract_id,
            passed=passed,
            checked_claims=len(contract.cited_claims),
            mismatches=mismatches,
            retype_violations=retype_violations,
            verification_hash=verification_hash,
            evidence_status=evidence_status,
        )
