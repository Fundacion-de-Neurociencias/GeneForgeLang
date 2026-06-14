import importlib.util
import logging
import os
import sys

logger = logging.getLogger(__name__)


class VariantSimulationPlugin:
    def __init__(self):
        # Cargar el módulo simulate_variant_effect.py dinámicamente
        self.simulate_variant_effect_module = self._load_module()

    def _load_module(self):
        # Ruta al archivo simulate_variant_effect.py
        module_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "simulate_variant_effect.py",
        )

        if not os.path.exists(module_path):
            logger.error(f"Module not found at: {module_path}")
            raise FileNotFoundError(f"simulate_variant_effect.py not found at {module_path}")

        spec = importlib.util.spec_from_file_location("simulate_variant_effect", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["simulate_variant_effect"] = module
        spec.loader.exec_module(module)
        logger.info(f"Successfully loaded simulate_variant_effect.py from {module_path}")
        return module

    def execute(self, method_name: str, params: dict, symbol_table: dict):
        """
        Execute methods related to la variant simulation.
        """
        logger.info(f"VariantSimulationPlugin: Executing method '{method_name}' with params: {params}")

        if method_name == "translate_dna":
            dna_sequence = params.get("dna_sequence")
            if not dna_sequence:
                raise ValueError("Parameter 'dna_sequence' is required for translate_dna.")

            # Usar el código genético definido en el módulo cargado
            genetic_code = self.simulate_variant_effect_module.define_genetic_code
            result = self.simulate_variant_effect_module.translate_dna(dna_sequence, genetic_code)
            logger.info(f"Translated DNA: {dna_sequence} to Amino Acids: {result}")
            return result

        elif method_name == "introduce_point_mutation":
            dna_sequence = params.get("dna_sequence")
            position = params.get("position")
            new_base = params.get("new_base")

            if dna_sequence is None or position is None or new_base is None:
                raise ValueError(
                    "Parameters 'dna_sequence', 'position', and 'new_base' are required for introduce_point_mutation."
                )

            mutated_sequence = self.simulate_variant_effect_module.introduce_point_mutation(
                dna_sequence, position, new_base
            )
            logger.info(f"Original DNA: {dna_sequence}, Mutated DNA: {mutated_sequence}")
            return mutated_sequence

        else:
            raise NotImplementedError(f"VariantSimulation method '{method_name}' not implemented.")
