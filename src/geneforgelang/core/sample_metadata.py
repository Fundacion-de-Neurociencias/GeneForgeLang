"""SDRF-Proteomics Sample Metadata Auditor.

Inspired by the community SDRF-Proteomics curation workflow (PRIDE / iProX / MassIVE):
1. Enforces valid ProteomeXchange/PRIDE/iProX/MassIVE dataset accessions.
2. Enforces non-empty source citations (PMID, DOI, or PX record) to prevent
   fabricated sample or raw file names.
3. Validates required sample-to-raw-file fields and optional by-reference
   artifact handles via NumericProvenanceAuditor.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import ProteomicsRepository, SDRFMetadataContract
from geneforgelang.core.numeric_provenance import NumericProvenanceAuditor

_ACCESSION_PATTERN = re.compile(r"^(PXD|IPX|MSV|RPXD)[0-9]{6,}$")
_SYNTHETIC_PLACEHOLDER_PATTERN = re.compile(
    r"^(placeholder|dummy|fake|todo|tbd|unknown|sample_?x+|test_?file)",
    re.IGNORECASE,
)
_VALID_REPOSITORIES = {r.value for r in ProteomicsRepository}


@dataclass
class SDRFAuditReport:
    """Deterministic audit report for an SDRFMetadataContract."""

    contract_id: str
    accession: str
    passed: bool
    sample_count: int
    violations: list[str] = field(default_factory=list)
    verification_hash: str = ""
    evidence_status: str = "SDRF_METADATA_VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "accession": self.accession,
            "passed": self.passed,
            "sample_count": self.sample_count,
            "violations": list(self.violations),
            "verification_hash": self.verification_hash,
            "evidence_status": self.evidence_status,
        }


class SampleMetadataAuditor:
    """Deterministic auditor for SDRF sample metadata and anti-invention invariants."""

    @classmethod
    def audit(cls, contract: SDRFMetadataContract) -> SDRFAuditReport:
        """Audit an SDRFMetadataContract for repository accession, citations, and sample integrity."""
        violations: list[str] = []

        accession = contract.accession.strip()
        if not accession or not _ACCESSION_PATTERN.match(accession):
            violations.append(
                f"Invalid proteomics accession '{accession}'. "
                "Expected ProteomeXchange-style accession (PXD/IPX/MSV/RPXD followed by >=6 digits)."
            )

        repo_str = (
            contract.repository.value
            if isinstance(contract.repository, ProteomicsRepository)
            else str(contract.repository).strip().lower()
        )
        if repo_str not in _VALID_REPOSITORIES:
            violations.append(f"Invalid repository '{repo_str}'. Must be one of {sorted(_VALID_REPOSITORIES)}.")

        if contract.require_source_citations and not contract.source_citations:
            violations.append(
                "source_citations must be non-empty when require_source_citations is True "
                "(cite PMID, DOI, or ProteomeXchange record)."
            )

        if not contract.samples:
            violations.append("samples must contain at least one SDRFSampleEntry.")

        for idx, sample in enumerate(contract.samples):
            label = sample.source_name.strip() or f"sample_{idx}"
            for field_name, val in (
                ("source_name", sample.source_name),
                ("organism", sample.organism),
                ("assay_name", sample.assay_name),
                ("data_file", sample.data_file),
            ):
                cleaned = val.strip()
                if not cleaned:
                    violations.append(f"Sample '{label}' is missing required field '{field_name}'.")
                elif _SYNTHETIC_PLACEHOLDER_PATTERN.match(cleaned):
                    violations.append(
                        f"Sample '{label}' field '{field_name}' uses placeholder value '{cleaned}'; "
                        "never invent sample or file names."
                    )

            if sample.artifact_ref is not None and not NumericProvenanceAuditor.is_valid_reference(sample.artifact_ref):
                violations.append(
                    f"Sample '{label}' has invalid artifact_ref; expected ArtifactRef or '${{step.output}}' handle."
                )

        passed = len(violations) == 0
        payload = json.dumps(
            {
                "contract_id": contract.contract_id,
                "accession": accession,
                "repository": repo_str,
                "sample_count": len(contract.samples),
                "violations": violations,
                "passed": passed,
            },
            sort_keys=True,
        )
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return SDRFAuditReport(
            contract_id=contract.contract_id,
            accession=accession,
            passed=passed,
            sample_count=len(contract.samples),
            violations=violations,
            verification_hash=verification_hash,
            evidence_status="SDRF_METADATA_VERIFIED" if passed else "SDRF_METADATA_REJECTED",
        )


__all__ = ["SDRFAuditReport", "SampleMetadataAuditor"]
