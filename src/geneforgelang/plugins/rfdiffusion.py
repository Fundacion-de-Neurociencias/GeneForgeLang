"""RFdiffusion plugin for de novo protein design (GFL design block)."""

import logging
from typing import Any

import torch

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

    def _resolve_device(self, requested_device: str) -> str:
        """Resolve requested device, falling back to CPU if GPU is unavailable."""

        if requested_device not in ("cpu", "gpu"):
            raise ValueError(
                f"Invalid device for RFdiffusion: {requested_device!r}. "
                "Expected 'cpu' or 'gpu'."
            )

        if requested_device == "cpu":
            return "cpu"

        if torch.cuda.is_available():
            return "cuda"

        logger.warning(
            "GPU requested for RFdiffusion, but no GPU is available. "
            "Falling back to CPU."
        )

        return "cpu"

    def generate(
        self,
        entity: str,
        objective: dict[str, Any],
        constraints: list[str],
        count: int,
        **kwargs,
    ) -> list[DesignCandidate]:
        """Generate protein candidates using RFdiffusion."""

        if entity != EntityType.PROTEIN_SEQUENCE.value:
            raise ValueError(
                f"RFdiffusionPlugin only supports ProteinSequence, got '{entity}'"
            )

        mode = kwargs.get("mode")
        if mode not in ("unconditional", "scaffolding", "binder"):
            raise ValueError(f"Invalid or missing 'mode' for RFdiffusion: {mode!r}")

        input_pdb = kwargs.get("input_pdb")
        motifs = kwargs.get("motifs")
        length = kwargs.get("length")

        requested_device = kwargs.get("device", "gpu")
        device = self._resolve_device(requested_device)

        logger.info(
            f"RFdiffusionPlugin: generating {count} candidates, "
            f"mode={mode}, device={device}, "
            f"input_pdb={input_pdb}, motifs={motifs}"
        )

        # TODO: sustituir este bloque por la llamada real al binario/script
        # de RFdiffusion, pasando mode, input_pdb, motifs, length,
        # constraints y device según corresponda.

        candidates = []

        for i in range(count):
            candidates.append(
                DesignCandidate(
                    sequence="X" * (
                        length if isinstance(length, int) else 100
                    ),
                    properties={
                        "mode": mode,
                        "device": device,
                    },
                    confidence=None,
                    metadata={
                        "source": "RFdiffusion (simulated)",
                        "design_index": i,
                        "input_pdb": input_pdb,
                        "motifs": motifs,
                        "requested_device": requested_device,
                        "device": device,
                    },
                )
            )

        return candidates