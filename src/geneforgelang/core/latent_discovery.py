"""Latent Discovery & Biomarker Replication Gate Engine.

Inspired by Glyph (Holland et al.):
1. Decomposes foundation-model representations via Sparse Autoencoders (SAEs).
2. Enforces confounder adjustment with residual significance before promotion.
3. Enforces external multi-cohort replication and incremental predictive gain.
4. Enforces literature novelty triage separating rediscovered positive controls
   from novel candidates, with optional by-reference handle validation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import (
    DiscoveryNoveltyStatus,
    LatentDiscoveryContract,
)
from geneforgelang.core.numeric_provenance import NumericProvenanceAuditor

_VALID_CORRECTIONS = {"fdr_bh", "bonferroni", "holm"}
_VALID_NOVELTY_STATUSES = {s.value for s in DiscoveryNoveltyStatus}


@dataclass
class LatentDiscoveryAuditReport:
    """Deterministic audit report for a LatentDiscoveryContract."""

    contract_id: str
    passed: bool
    total_findings: int
    rediscovered_count: int
    novel_candidate_count: int
    violations: list[str] = field(default_factory=list)
    verification_hash: str = ""
    evidence_status: str = "LATENT_DISCOVERY_VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "passed": self.passed,
            "total_findings": self.total_findings,
            "rediscovered_count": self.rediscovered_count,
            "novel_candidate_count": self.novel_candidate_count,
            "violations": list(self.violations),
            "verification_hash": self.verification_hash,
            "evidence_status": self.evidence_status,
        }


class LatentDiscoveryAuditor:
    """Deterministic auditor for SAE probing, confounder control, replication, and novelty triage."""

    @classmethod
    def audit(cls, contract: LatentDiscoveryContract) -> LatentDiscoveryAuditReport:
        """Audit a LatentDiscoveryContract against scientific discovery invariants."""
        violations: list[str] = []

        probe = contract.sae_probe
        if not probe.foundation_model.strip():
            violations.append("sae_probe.foundation_model must be a non-empty string.")
        if not probe.target_layer.strip():
            violations.append("sae_probe.target_layer must be a non-empty string.")
        if probe.dictionary_size <= 0:
            violations.append("sae_probe.dictionary_size must be > 0.")
        if probe.sparsity_l0 <= 0:
            violations.append("sae_probe.sparsity_l0 must be > 0.")
        if probe.multiple_testing_correction not in _VALID_CORRECTIONS:
            violations.append(
                f"Invalid multiple_testing_correction '{probe.multiple_testing_correction}'. "
                f"Must be one of {sorted(_VALID_CORRECTIONS)}."
            )
        if not (0.0 < probe.fdr_threshold <= 1.0):
            violations.append("sae_probe.fdr_threshold must be in (0.0, 1.0].")

        conf = contract.confounder_adjustment
        if conf.require_residual_significance and not [c for c in conf.confounders if str(c).strip()]:
            violations.append(
                "confounder_adjustment.confounders must be non-empty when require_residual_significance is True."
            )
        if not (0.0 < conf.max_adjusted_p_value <= 1.0):
            violations.append("confounder_adjustment.max_adjusted_p_value must be in (0.0, 1.0].")

        rep = contract.external_replication
        distinct_cohorts = {c.strip() for c in rep.cohort_ids if c.strip()}
        if rep.min_external_cohorts < 1:
            violations.append("external_replication.min_external_cohorts must be >= 1.")
        elif len(distinct_cohorts) < rep.min_external_cohorts:
            violations.append(
                f"external_replication requires at least {rep.min_external_cohorts} distinct cohort_ids, "
                f"got {len(distinct_cohorts)}."
            )
        if rep.observed_delta_auc is not None and rep.observed_delta_auc < rep.min_delta_auc:
            violations.append(
                f"external_replication observed_delta_auc ({rep.observed_delta_auc}) is below "
                f"min_delta_auc ({rep.min_delta_auc})."
            )

        lit = contract.literature_triage
        if not lit.corpus_scope.strip():
            violations.append("literature_triage.corpus_scope must be a non-empty string.")
        if lit.min_corpus_size < 1:
            violations.append("literature_triage.min_corpus_size must be >= 1.")

        rediscovered_count = 0
        novel_candidate_count = 0

        for idx, finding in enumerate(contract.findings):
            latent_id = str(finding.get("latent_id", f"finding_{idx}")).strip() or f"finding_{idx}"
            raw_status = str(finding.get("novelty_status", "")).strip()
            if raw_status not in _VALID_NOVELTY_STATUSES:
                violations.append(
                    f"Finding '{latent_id}' has invalid novelty_status '{raw_status}'. "
                    f"Must be one of {sorted(_VALID_NOVELTY_STATUSES)}."
                )
                continue

            if (
                "artifact_ref" in finding
                and finding["artifact_ref"] is not None
                and not NumericProvenanceAuditor.is_valid_reference(finding["artifact_ref"])
            ):
                violations.append(
                    f"Finding '{latent_id}' has invalid artifact_ref; "
                    "expected ArtifactRef or '${step.output}' handle."
                )

            is_promoted = raw_status in {
                DiscoveryNoveltyStatus.NOVEL_CANDIDATE.value,
                DiscoveryNoveltyStatus.REDISCOVERED_POSITIVE_CONTROL.value,
            }
            if is_promoted:
                if conf.require_residual_significance:
                    raw_p = finding.get("residual_p_value")
                    if raw_p is None:
                        violations.append(
                            f"Promoted finding '{latent_id}' is missing 'residual_p_value' after confounder adjustment."
                        )
                    else:
                        try:
                            p_val = float(raw_p)
                            if p_val > conf.max_adjusted_p_value:
                                violations.append(
                                    f"Promoted finding '{latent_id}' residual_p_value ({p_val}) exceeds "
                                    f"max_adjusted_p_value ({conf.max_adjusted_p_value})."
                                )
                        except (TypeError, ValueError):
                            violations.append(
                                f"Promoted finding '{latent_id}' has non-numeric residual_p_value '{raw_p}'."
                            )

                rep_cohorts = {str(c).strip() for c in finding.get("replicated_cohorts", []) if str(c).strip()}
                matched_cohorts = rep_cohorts & distinct_cohorts
                if len(matched_cohorts) < rep.min_external_cohorts:
                    violations.append(
                        f"Promoted finding '{latent_id}' replicated in {len(matched_cohorts)} declared "
                        f"external cohorts, below min_external_cohorts ({rep.min_external_cohorts})."
                    )

                if rep.require_direction_concordance and not bool(finding.get("direction_concordant", False)):
                    violations.append(
                        f"Promoted finding '{latent_id}' failed direction_concordant check across external cohorts."
                    )

            citations = [str(c).strip() for c in finding.get("citation_evidence", []) if str(c).strip()]
            if raw_status == DiscoveryNoveltyStatus.REDISCOVERED_POSITIVE_CONTROL.value:
                rediscovered_count += 1
                if not citations:
                    violations.append(
                        f"Rediscovered positive control '{latent_id}' must provide non-empty citation_evidence."
                    )
            elif raw_status == DiscoveryNoveltyStatus.NOVEL_CANDIDATE.value:
                novel_candidate_count += 1
                if citations:
                    violations.append(
                        f"Novel candidate '{latent_id}' declares existing citation_evidence {citations}; "
                        "reclassify as 'rediscovered_positive_control' if already established in literature."
                    )

        if lit.require_positive_controls and novel_candidate_count > 0 and rediscovered_count < 1:
            violations.append(
                "literature_triage.require_positive_controls is True: at least one "
                "'rediscovered_positive_control' finding is required alongside novel candidates."
            )

        passed = len(violations) == 0
        payload = json.dumps(
            {
                "contract_id": contract.contract_id,
                "total_findings": len(contract.findings),
                "rediscovered_count": rediscovered_count,
                "novel_candidate_count": novel_candidate_count,
                "violations": violations,
                "passed": passed,
            },
            sort_keys=True,
        )
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return LatentDiscoveryAuditReport(
            contract_id=contract.contract_id,
            passed=passed,
            total_findings=len(contract.findings),
            rediscovered_count=rediscovered_count,
            novel_candidate_count=novel_candidate_count,
            violations=violations,
            verification_hash=verification_hash,
            evidence_status="LATENT_DISCOVERY_VERIFIED" if passed else "LATENT_DISCOVERY_REJECTED",
        )


__all__ = ["LatentDiscoveryAuditReport", "LatentDiscoveryAuditor"]
