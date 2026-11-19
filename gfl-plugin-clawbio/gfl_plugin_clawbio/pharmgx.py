"""
pharmgx.py — GFL Plugin: PharmGx Reporter (ClawBio)
=====================================================
Wraps the ClawBio pharmgx-reporter skill as a GFL GeneratorPlugin.

GFL usage:
    experiment:
      tool: clawbio_pharmgx
      type: analysis
      contract:
        inputs:
          raw_genome: {type: TEXT, attributes: {format: "23andme_v5"}}
        outputs:
          pharmacogenomic_report: {type: JSON}
      params:
        input_file: "patient_genome.txt"

ADR-0003 compliance:
  - Does NOT import geneforgelang.core, geneforgelang.semantic,
    or geneforgelang.governance
  - Calls ClawBio exclusively via _clawbio_runner (subprocess)
  - Degrades gracefully if ClawBio is not installed
  - Score: 23/25 (see governance.json)
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

SKILL_NAME = "pharmgx"
PLUGIN_TOOL_ID = "clawbio_pharmgx"

# Pharmacogenomic genes covered by the skill (CPIC tier A/B)
PGX_GENES = [
    "CYP2D6",
    "CYP2C19",
    "CYP2C9",
    "TPMT",
    "DPYD",
    "SLCO1B1",
    "CYP3A5",
    "UGT1A1",
    "NUDT15",
    "CYP1A2",
    "CYP2B6",
    "G6PD",
]


class PharmGxPlugin(GeneratorPlugin):
    """GFL GeneratorPlugin wrapping ClawBio pharmgx-reporter.

    Reports pharmacogenomic diplotypes, metaboliser phenotypes,
    and CPIC-level drug recommendations from consumer genetic data
    (23andMe / AncestryDNA raw format).

    This plugin wraps 12 genes, 31 SNPs, and 51 drugs as per the
    ClawBio pharmgx-reporter skill specification v0.1.0.
    """

    name = PLUGIN_TOOL_ID
    version = "0.1.0"
    description = (
        "Pharmacogenomic report from DTC genetic data — " "12 genes, 31 SNPs, 51 drugs, CPIC guidelines (ClawBio)"
    )

    @property
    def supported_entities(self) -> list[EntityType]:
        # PharmGx generates pharmacogenomic reports — closest GFL entity is DNA_SEQUENCE
        # (the entity type here represents input modality, not output)
        return [EntityType.DNA_SEQUENCE]

    def generate(
        self,
        entity: str,
        objective: dict[str, Any],
        constraints: list[str],
        count: int,
        **kwargs: Any,
    ) -> list[DesignCandidate]:
        """Execute PharmGx analysis and return results as DesignCandidates.

        Args:
            entity: Entity type (DNA_SEQUENCE expected)
            objective: GFL objective dict (e.g., {"analyze": "pharmacogenomics"})
            constraints: List of constraint expressions (gene filters, CPIC levels)
            count: Number of reports (typically 1 per patient file)
            **kwargs: Additional params from GFL experiment.params

        Returns:
            List of DesignCandidate with pharmacogenomic report in properties
        """
        params = kwargs.copy()
        input_file = params.get("input_file")
        demo_mode = params.get("demo_mode", input_file is None)

        # Extract gene filter from constraints
        gene_filter = [c.split("gene==")[1].strip() for c in constraints if "gene==" in c]
        cpic_level = params.get("cpic_level_filter", ["A", "B"])

        logger.info(
            "PharmGxPlugin: running ClawBio skill '%s' " "(input=%s, demo=%s, genes=%s)",
            SKILL_NAME,
            input_file,
            demo_mode,
            gene_filter if gene_filter else "all",
        )

        run_params: dict[str, Any] = {}
        if input_file:
            run_params["input"] = input_file
        if gene_filter:
            run_params["genes"] = ",".join(gene_filter)

        result = run_skill(SKILL_NAME, run_params, demo_mode=demo_mode)

        if not result.clawbio_installed:
            logger.warning("PharmGxPlugin: ClawBio not installed — returning stub")
            return [
                DesignCandidate(
                    sequence="N/A",
                    properties={
                        "status": "clawbio_not_installed",
                        "skill": SKILL_NAME,
                        "genes_covered": PGX_GENES,
                        "cpic_level_filter": cpic_level,
                    },
                    confidence=None,
                    metadata={
                        "plugin": PLUGIN_TOOL_ID,
                        "install_hint": "pip install 'gfl-plugin-clawbio[clawbio]'",
                    },
                )
            ]

        if not result.success:
            logger.error(
                "PharmGxPlugin: skill failed (rc=%d): %s",
                result.return_code,
                result.error_message,
            )
            return [
                DesignCandidate(
                    sequence="N/A",
                    properties={"status": "skill_failed", "error": result.error_message},
                    confidence=0.0,
                    metadata={"plugin": PLUGIN_TOOL_ID, "skill": SKILL_NAME},
                )
            ]

        return [
            DesignCandidate(
                sequence="pharmacogenomic_report",
                properties={
                    "status": "success",
                    "skill": SKILL_NAME,
                    "output": result.output,
                    "genes_covered": PGX_GENES,
                    "cpic_level_filter": cpic_level,
                },
                confidence=1.0,
                metadata={
                    "plugin": PLUGIN_TOOL_ID,
                    "clawbio_version": result.skill_version,
                    "reproducible": True,
                },
            )
        ]

    def get_supported_constraints(self) -> list[str]:
        return ["gene", "cpic_level", "drug", "phenotype"]
