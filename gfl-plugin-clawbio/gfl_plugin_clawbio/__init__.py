"""gfl-plugin-clawbio — GFL Plugin adapters for ClawBio bioinformatics skills.

Constitutional guarantee (ADR-0003):
    This package is amputatable. Removing it leaves zero residue in
    geneforgelang.*. No GFL core module imports this package.

Plugins registered via entry_points in pyproject.toml:
    clawbio_pharmgx           → PharmGxPlugin
    clawbio_crispr_screen     → CrisprScreenPlugin
    clawbio_rnaseq_de         → RnaseqDEPlugin
    clawbio_gwas_lookup       → GwasLookupPlugin
"""

__version__ = "0.1.0"
__all__ = [
    "PharmGxPlugin",
    "CrisprScreenPlugin",
    "RnaseqDEPlugin",
    "GwasLookupPlugin",
]

from .crispr_screen import CrisprScreenPlugin
from .gwas_lookup import GwasLookupPlugin
from .pharmgx import PharmGxPlugin
from .rnaseq_de import RnaseqDEPlugin
