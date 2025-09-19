import importlib.util
import logging
import os
import sys

logger = logging.getLogger(__name__)


class VariantSimulationPlugin:
    """Demo plugin that tries to load an external simulate_variant_effect.py.

    If the external module is not present, the plugin will raise a clear
    error at execution time instead of failing at import.
    """

    def __init__(self):
        self._module = None

    def _ensure_loaded(self):
        if self._module is not None:
            return
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        module_path = os.path.join(root, "simulate_variant_effect.py")
        if not os.path.exists(module_path):
            raise FileNotFoundError(
                "simulate_variant_effect.py not found. Provide it at repository root or "
                "replace VariantSimulationPlugin with a real implementation."
            )
        spec = importlib.util.spec_from_file_location("simulate_variant_effect", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["simulate_variant_effect"] = module
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self._module = module
        logger.info("Loaded simulate_variant_effect from %s", module_path)

    def execute(self, method_name: str, params: dict, symbol_table: dict):
        logger.info("VariantSimulationPlugin: %s(%s)", method_name, params)
        self._ensure_loaded()
        m = self._module

        if method_name == "translate_dna":
            dna_sequence = params.get("dna_sequence")
            if not dna_sequence:
                raise ValueError("Parameter 'dna_sequence' is required for translate_dna.")
            genetic_code = m.define_genetic_code  # type: ignore[attr-defined]
            return m.translate_dna(dna_sequence, genetic_code)  # type: ignore[attr-defined]

        if method_name == "introduce_point_mutation":
            dna_sequence = params.get("dna_sequence")
            position = params.get("position")
            new_base = params.get("new_base")
            if dna_sequence is None or position is None or new_base is None:
                raise ValueError("Parameters 'dna_sequence', 'position', and 'new_base' are required.")
            return m.introduce_point_mutation(dna_sequence, position, new_base)  # type: ignore[attr-defined]

        raise NotImplementedError(f"VariantSimulation method '{method_name}' not implemented.")


__all__ = ["VariantSimulationPlugin"]
