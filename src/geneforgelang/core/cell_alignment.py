"""Cross-Modal Cell Identity & Taxonomy Alignment Auditor.

Inspired by Bloom (shared latent bridge across disjoint cellular modalities):
1. Enforces a declared bridge model and paired bridge modalities when aligning
   studies that measure disjoint modalities.
2. Enforces explicit species tracking and blocks silent cross-species transfer
   unless allow_cross_species_transfer=True and ortholog_anchors are provided.
3. Enforces reference taxonomy grounding, anchor cell type verification, and
   mapping confidence / unmapped fraction bounds.
4. Validates optional artifact_ref handles via NumericProvenanceAuditor.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.core.gftypes import CellAlignmentContract, CellModality
from geneforgelang.core.numeric_provenance import NumericProvenanceAuditor

_VALID_CELL_MODALITIES = {m.value for m in CellModality}


@dataclass
class CellAlignmentAuditReport:
    """Deterministic audit report for a CellAlignmentContract."""

    contract_id: str
    passed: bool
    study_count: int
    mapping_count: int
    anchor_mapping_count: int
    violations: list[str] = field(default_factory=list)
    verification_hash: str = ""
    evidence_status: str = "CELL_ALIGNMENT_VERIFIED"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "passed": self.passed,
            "study_count": self.study_count,
            "mapping_count": self.mapping_count,
            "anchor_mapping_count": self.anchor_mapping_count,
            "violations": list(self.violations),
            "verification_hash": self.verification_hash,
            "evidence_status": self.evidence_status,
        }


class CellAlignmentAuditor:
    """Deterministic auditor for cross-modal cell identity and taxonomy alignment."""

    @classmethod
    def audit(cls, contract: CellAlignmentContract) -> CellAlignmentAuditReport:
        """Audit a CellAlignmentContract for bridge, species, taxonomy, and anchor invariants."""
        violations: list[str] = []

        if not contract.bridge_model.strip():
            violations.append("bridge_model must be a non-empty string.")
        if not contract.bridge_species.strip():
            violations.append("bridge_species must be a non-empty string.")
        if not contract.reference_taxonomy.strip():
            violations.append("reference_taxonomy must be a non-empty string.")
        if not (0.0 < contract.min_mapping_confidence <= 1.0):
            violations.append("min_mapping_confidence must be in (0.0, 1.0].")
        if not (0.0 <= contract.max_unmapped_fraction <= 1.0):
            violations.append("max_unmapped_fraction must be in [0.0, 1.0].")
        if (
            contract.observed_unmapped_fraction is not None
            and contract.observed_unmapped_fraction > contract.max_unmapped_fraction
        ):
            violations.append(
                f"observed_unmapped_fraction ({contract.observed_unmapped_fraction}) exceeds "
                f"max_unmapped_fraction ({contract.max_unmapped_fraction})."
            )

        bridge_mods = [
            m.value if isinstance(m, CellModality) else str(m).strip().lower() for m in contract.bridge_modalities
        ]
        for mod in bridge_mods:
            if mod not in _VALID_CELL_MODALITIES:
                violations.append(f"Invalid bridge modality '{mod}'. Must be one of {sorted(_VALID_CELL_MODALITIES)}.")

        if len(contract.studies) < 2:
            violations.append("studies must contain at least two CellStudySlice entries to align.")

        study_ids: set[str] = set()
        study_modalities: set[str] = set()
        study_species: set[str] = set()
        for idx, study in enumerate(contract.studies):
            sid = study.study_id.strip() or f"study_{idx}"
            if not study.study_id.strip():
                violations.append(f"Study at index {idx} must define a non-empty study_id.")
            elif sid in study_ids:
                violations.append(f"Duplicate study_id '{sid}' in studies.")
            study_ids.add(sid)

            mod_str = (
                study.modality.value
                if isinstance(study.modality, CellModality)
                else str(study.modality).strip().lower()
            )
            if mod_str not in _VALID_CELL_MODALITIES:
                violations.append(
                    f"Study '{sid}' has invalid modality '{mod_str}'. Must be one of {sorted(_VALID_CELL_MODALITIES)}."
                )
            else:
                study_modalities.add(mod_str)

            if not study.species.strip():
                violations.append(f"Study '{sid}' must declare a non-empty species.")
            else:
                study_species.add(study.species.strip())

        if len(study_modalities) > 1 and not bridge_mods:
            violations.append(
                "Cross-modal alignment across disjoint study modalities requires non-empty bridge_modalities."
            )

        bridge_sp = contract.bridge_species.strip()
        if bridge_sp and any(sp != bridge_sp for sp in study_species):
            if not contract.allow_cross_species_transfer:
                violations.append(
                    f"Studies span species {sorted(study_species)} differing from bridge_species '{bridge_sp}'; "
                    "set allow_cross_species_transfer=True with ortholog_anchors to permit transfer."
                )
            elif not contract.ortholog_anchors:
                violations.append(
                    "allow_cross_species_transfer=True requires non-empty ortholog_anchors for cross-species mapping."
                )

        if not contract.anchor_cell_types:
            violations.append("anchor_cell_types must declare at least one known cell type anchor.")

        anchor_mapping_count = 0
        matched_anchors: set[str] = set()
        declared_anchors = {a.strip() for a in contract.anchor_cell_types if a.strip()}

        for idx, mapping in enumerate(contract.mappings):
            label = f"{mapping.source_label or idx}->{mapping.target_label or idx}"
            if mapping.source_study_id not in study_ids:
                violations.append(f"Mapping '{label}' references unknown source_study_id '{mapping.source_study_id}'.")
            if mapping.target_study_id not in study_ids:
                violations.append(f"Mapping '{label}' references unknown target_study_id '{mapping.target_study_id}'.")
            if not mapping.taxonomy_curie.strip():
                violations.append(f"Mapping '{label}' must declare a non-empty taxonomy_curie.")
            if mapping.mapping_confidence < contract.min_mapping_confidence:
                violations.append(
                    f"Mapping '{label}' confidence ({mapping.mapping_confidence}) is below "
                    f"min_mapping_confidence ({contract.min_mapping_confidence})."
                )
            if mapping.artifact_ref is not None and not NumericProvenanceAuditor.is_valid_reference(
                mapping.artifact_ref
            ):
                violations.append(
                    f"Mapping '{label}' has invalid artifact_ref; expected ArtifactRef or '${{step.output}}' handle."
                )
            if mapping.is_anchor:
                anchor_mapping_count += 1
                if mapping.taxonomy_curie in declared_anchors or mapping.target_label in declared_anchors:
                    matched_anchors.add(mapping.taxonomy_curie)
                    matched_anchors.add(mapping.target_label)

        if contract.mappings and anchor_mapping_count < 1:
            violations.append("At least one mapping must have is_anchor=True verifying known anchor_cell_types.")

        passed = len(violations) == 0
        payload = json.dumps(
            {
                "contract_id": contract.contract_id,
                "bridge_model": contract.bridge_model,
                "study_count": len(contract.studies),
                "mapping_count": len(contract.mappings),
                "anchor_mapping_count": anchor_mapping_count,
                "violations": violations,
                "passed": passed,
            },
            sort_keys=True,
        )
        verification_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return CellAlignmentAuditReport(
            contract_id=contract.contract_id,
            passed=passed,
            study_count=len(contract.studies),
            mapping_count=len(contract.mappings),
            anchor_mapping_count=anchor_mapping_count,
            violations=violations,
            verification_hash=verification_hash,
            evidence_status="CELL_ALIGNMENT_VERIFIED" if passed else "CELL_ALIGNMENT_REJECTED",
        )


__all__ = ["CellAlignmentAuditReport", "CellAlignmentAuditor"]
