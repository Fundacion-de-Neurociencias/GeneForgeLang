"""
rnaseq_de.py — GFL Plugin: RNA-seq Differential Expression (ClawBio)
======================================================================
Wraps ClawBio rnaseq-de as a GFL GeneratorPlugin.

GFL usage:
    analyze:
      strategy: differential
      data: count_matrix.csv
      tool: clawbio_rnaseq_de
      thresholds:
        padj: 0.05
        log2fc_abs: 1.5

ADR-0003: No imports from geneforgelang.core/semantic/governance.
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

SKILL_NAME = "rnaseq"
PLUGIN_TOOL_ID = "clawbio_rnaseq_de"


class RnaseqDEPlugin(GeneratorPlugin):
    """GFL GeneratorPlugin wrapping ClawBio rnaseq-de.

    Differential expression analysis for bulk RNA-seq and pseudo-bulk
    count matrices. Backend: PyDESeq2.

    Steps: library QC → PCA → DESeq2 normalisation → contrast test →
           volcano plot → MA plot → results CSV.
    """

    name = PLUGIN_TOOL_ID
    version = "0.1.0"
    description = "Differential expression for bulk RNA-seq count matrices " "(PyDESeq2 backend, ClawBio)"

    @property
    def supported_entities(self) -> list[EntityType]:
        return [EntityType.RNA_SEQUENCE]

    def generate(
        self,
        entity: str,
        objective: dict[str, Any],
        constraints: list[str],
        count: int,
        **kwargs: Any,
    ) -> list[DesignCandidate]:
        """Execute RNA-seq DE and return results as DesignCandidates."""
        params = kwargs.copy()
        count_matrix = params.get("count_matrix") or params.get("data")
        metadata_file = params.get("sample_metadata")
        demo_mode = params.get("demo_mode", count_matrix is None)

        # Parse thresholds from constraints
        padj_threshold = 0.05
        lfc_threshold = 1.5
        for c in constraints:
            if "padj" in c:
                try:
                    padj_threshold = float(c.split("=")[-1].strip())
                except ValueError:
                    pass
            if "log2fc" in c:
                try:
                    lfc_threshold = float(c.split("=")[-1].strip())
                except ValueError:
                    pass

        run_params: dict[str, Any] = {}
        if count_matrix and metadata_file:
            run_params["input"] = f"{count_matrix},{metadata_file}"
        elif count_matrix:
            run_params["input"] = count_matrix

        condition_col = params.get("condition_col")
        treatment = params.get("treatment")
        control = params.get("control")

        if condition_col:
            run_params["formula"] = f"~ {condition_col}"
        if condition_col and treatment and control:
            run_params["contrast"] = f"{condition_col},{treatment},{control}"

        logger.info(
            "RnaseqDEPlugin: running '%s' (matrix=%s, demo=%s, padj<=%s, |lfc|>=%s)",
            SKILL_NAME,
            count_matrix,
            demo_mode,
            padj_threshold,
            lfc_threshold,
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
                sequence="rnaseq_de_results",
                properties={
                    "status": "success",
                    "skill": SKILL_NAME,
                    "output": result.output,
                    "thresholds": {
                        "padj": padj_threshold,
                        "log2fc_abs": lfc_threshold,
                    },
                },
                confidence=1.0,
                metadata={
                    "plugin": PLUGIN_TOOL_ID,
                    "backend": "PyDESeq2",
                    "reproducible": True,
                },
            )
        ]

    def get_supported_constraints(self) -> list[str]:
        return ["padj", "log2fc_abs", "log2fc", "baseMean_min", "min_count"]
