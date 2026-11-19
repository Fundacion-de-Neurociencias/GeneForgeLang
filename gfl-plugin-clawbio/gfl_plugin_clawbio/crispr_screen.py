"""
crispr_screen.py — GFL Plugin: CRISPR Screen Triage (ClawBio)
==============================================================
Wraps ClawBio crispr-screen-triage as a GFL GeneratorPlugin.

GFL usage:
    analyze:
      strategy: variant
      data: guide_counts.csv
      tool: clawbio_crispr_screen
      thresholds:
        depletion_zscore_cutoff: -2.0
        min_guides_per_gene: 3

ADR-0003: No imports from geneforgelang.core/semantic/governance.
ClawBio called exclusively via subprocess (_clawbio_runner).
"""

from __future__ import annotations

import logging
from typing import Any

from geneforgelang.plugins.interfaces import (
    DesignCandidate,
    EntityType,
    GeneratorPlugin,
)

from ._clawbio_runner import run_skill

logger = logging.getLogger(__name__)

SKILL_NAME = "crispr-triage"
PLUGIN_TOOL_ID = "clawbio_crispr_screen"


class CrisprScreenPlugin(GeneratorPlugin):
    """GFL GeneratorPlugin wrapping ClawBio crispr-screen-triage.

    Deterministic CRISPR screen hit ranking from guide-level count tables.
    Computes log2 fold-change, depletion z-score, and a composite triage
    score (depletion + essentiality + druggability) per gene.

    Input: CSV with columns [guide_id, gene, control_count, treatment_count,
                              essentiality, druggability]
    Output: ranked hit report (Markdown), triage JSON, gene CSV, guide CSV.
    """

    name = PLUGIN_TOOL_ID
    version = "0.1.0"
    description = "Deterministic CRISPR screen hit ranking from guide-level count tables (ClawBio)"

    @property
    def supported_entities(self) -> list[EntityType]:
        return [EntityType.DNA_SEQUENCE]

    def generate(
        self,
        entity: str,
        objective: dict[str, Any],
        constraints: list[str],
        count: int,
        **kwargs: Any,
    ) -> list[DesignCandidate]:
        """Execute CRISPR screen triage and return ranked hits as DesignCandidates."""
        params = kwargs.copy()
        input_file = params.get("input_file") or params.get("data")
        demo_mode = params.get("demo_mode", input_file is None)

        # Extract thresholds from constraints
        thresholds: dict[str, float] = {}
        for c in constraints:
            if "depletion_zscore_cutoff" in c:
                try:
                    thresholds["zscore_cutoff"] = float(c.split("=")[-1].strip())
                except ValueError:
                    pass
            if "min_guides_per_gene" in c:
                try:
                    thresholds["min_guides"] = int(c.split("=")[-1].strip())
                except ValueError:
                    pass

        run_params: dict[str, Any] = {}
        if input_file:
            run_params["input"] = input_file

        logger.info(
            "CrisprScreenPlugin: running '%s' (input=%s, demo=%s, thresholds=%s)",
            SKILL_NAME,
            input_file,
            demo_mode,
            thresholds,
        )

        result = run_skill(SKILL_NAME, run_params, demo_mode=demo_mode)

        if not result.clawbio_installed:
            return [
                DesignCandidate(
                    sequence="N/A",
                    properties={"status": "clawbio_not_installed", "skill": SKILL_NAME},
                    confidence=None,
                    metadata={"plugin": PLUGIN_TOOL_ID, "install_hint": "pip install 'gfl-plugin-clawbio[clawbio]'"},
                )
            ]

        if not result.success:
            return [
                DesignCandidate(
                    sequence="N/A",
                    properties={"status": "skill_failed", "error": result.error_message},
                    confidence=0.0,
                    metadata={"plugin": PLUGIN_TOOL_ID},
                )
            ]

        return [
            DesignCandidate(
                sequence="crispr_screen_triage_report",
                properties={
                    "status": "success",
                    "skill": SKILL_NAME,
                    "output": result.output,
                    "thresholds_applied": thresholds,
                },
                confidence=1.0,
                metadata={
                    "plugin": PLUGIN_TOOL_ID,
                    "reproducible": True,
                    "deterministic": True,
                },
            )
        ]

    def get_supported_constraints(self) -> list[str]:
        return [
            "depletion_zscore_cutoff",
            "log2fc_cutoff",
            "min_guides_per_gene",
            "essentiality_min",
            "druggability_min",
        ]
