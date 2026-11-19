"""
gwas_lookup.py — GFL Plugin: GWAS Lookup (ClawBio)
====================================================
Wraps ClawBio gwas-lookup as a GFL GeneratorPlugin.
Federated variant lookup across 9 genomic databases.

GFL usage:
    experiment:
      tool: clawbio_gwas_lookup
      type: analysis
      params:
        rsid: "rs429358"
        databases: [gwas_catalog, open_targets, gtex_v8]

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

SKILL_NAME = "gwas"
PLUGIN_TOOL_ID = "clawbio_gwas_lookup"

SUPPORTED_DATABASES = [
    "gwas_catalog",
    "open_targets",
    "ukb_topmed_pheweb",
    "finngen_r12",
    "biobank_japan",
    "gtex_v8",
    "ebi_eqtl_catalogue",
    "locuszoom",
]


class GwasLookupPlugin(GeneratorPlugin):
    """GFL GeneratorPlugin wrapping ClawBio gwas-lookup.

    Federated variant lookup: takes a single rsID and queries up to 9
    genomic databases in parallel, returning unified GWAS associations,
    PheWAS results, eQTL data, and fine-mapping credible sets.

    Supported databases:
        GWAS Catalog, Open Targets, UKB-TOPMed, FinnGen r12,
        Biobank Japan, GTEx v8, EBI eQTL Catalogue, LocusZoom.
    """

    name = PLUGIN_TOOL_ID
    version = "0.1.0"
    description = (
        "Federated variant lookup across 9 genomic databases "
        "(GWAS Catalog, Open Targets, GTEx, eQTL, PheWAS — ClawBio)"
    )

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
        """Execute federated GWAS lookup for an rsID.

        kwargs.rsid is required (or demo_mode=True for demonstration).
        """
        params = kwargs.copy()
        rsid = params.get("rsid")
        databases = params.get("databases", SUPPORTED_DATABASES)
        genome_build = params.get("reference_build", "GRCh38")
        demo_mode = params.get("demo_mode", rsid is None)

        if not rsid and not demo_mode:
            return [
                DesignCandidate(
                    sequence="N/A",
                    properties={"status": "missing_rsid", "error": "rsid parameter is required (e.g., rsid: rs429358)"},
                    confidence=0.0,
                    metadata={"plugin": PLUGIN_TOOL_ID},
                )
            ]

        run_params: dict[str, Any] = {}
        if rsid:
            run_params["rsid"] = rsid
        if isinstance(databases, list):
            run_params["databases"] = ",".join(databases)
        run_params["build"] = genome_build

        logger.info(
            "GwasLookupPlugin: running '%s' (rsid=%s, databases=%s, demo=%s)",
            SKILL_NAME,
            rsid,
            databases,
            demo_mode,
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
                sequence=rsid or "demo_variant",
                properties={
                    "status": "success",
                    "skill": SKILL_NAME,
                    "rsid": rsid,
                    "genome_build": genome_build,
                    "databases_queried": databases,
                    "output": result.output,
                },
                confidence=1.0,
                metadata={
                    "plugin": PLUGIN_TOOL_ID,
                    "federated_sources": len(databases) if isinstance(databases, list) else "all",
                    "reproducible": True,
                },
            )
        ]

    def get_supported_constraints(self) -> list[str]:
        return ["rsid", "genome_build", "databases", "parallel_queries", "timeout_seconds"]
