"""RFdiffusion plugin for de novo protein design (GFL design block)."""

import logging
from typing import Any

from geneforgelang.plugins.interfaces import DesignCandidate, EntityType, GeneratorPlugin

logger = logging.getLogger(__name__)


class RFdiffusionPlugin(GeneratorPlugin):
    """Generator plugin wrapping RFdiffusion for de novo protein design."""

    @property
    def name(self) -> str:
        return "rfdiffusion"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_entities(self) -> list[EntityType]:
        return [EntityType.PROTEIN_SEQUENCE]

    def generate(
        self, entity: str, objective: dict[str, Any], constraints: list[str], count: int, **kwargs
    ) -> list[DesignCandidate]:
        """Generate protein candidates using RFdiffusion.

        Args:
            entity: Debe ser "ProteinSequence" (único tipo soportado)
            objective: p.ej. {"maximize": "binding_affinity"}
            constraints: lista de constraints genéricos (poco usado aquí,
                los constraints específicos de RFdiffusion van en kwargs)
            count: número de diseños a generar (mapea a num_designs)
            **kwargs: campos específicos de protein_design:
                - mode: "unconditional" | "scaffolding" | "binder"
                - input_pdb: ruta al PDB de entrada
                - motifs: string de contig syntax
                - constraints: dict con hotspots, symmetry, etc.
                - length: int o "min-max"

        Returns:
            Lista de DesignCandidate, una por diseño generado
        """
        if entity != EntityType.PROTEIN_SEQUENCE.value:
            raise ValueError(f"RFdiffusionPlugin only supports ProteinSequence, got '{entity}'")

        mode = kwargs.get("mode")
        if mode not in ("unconditional", "scaffolding", "binder"):
            raise ValueError(f"Invalid or missing 'mode' for RFdiffusion: {mode!r}")

        input_pdb = kwargs.get("input_pdb")
        motifs = kwargs.get("motifs")
        length = kwargs.get("length")

        logger.info(
            f"RFdiffusionPlugin: generating {count} candidates, mode={mode}, "
            f"input_pdb={input_pdb}, motifs={motifs}"
        )

        # TODO: sustituir este bloque por la llamada real al binario/script
        # de RFdiffusion (subprocess o binding Python), pasando mode,
        # input_pdb, motifs, length y constraints según corresponda.
        # De momento se simula el resultado, siguiendo el mismo patrón
        # que AlphaGenomePlugin (alphafold.py) hasta tener el wrapper real.
        candidates = []
        for i in range(count):
            candidates.append(
                DesignCandidate(
                    sequence="X" * (length if isinstance(length, int) else 100),
                    properties={"mode": mode},
                    confidence=None,
                    metadata={
                        "source": "RFdiffusion (simulated)",
                        "design_index": i,
                        "input_pdb": input_pdb,
                        "motifs": motifs,
                    },
                )
            )

        return candidates