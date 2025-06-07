# --- gfl_sdk/external_integrations/enhancers.py
"""
Module to extend GeneForgeLang (GFL) with enhancer and AAV vector modeling.

Provides:
- Classes and functions to represent enhancers as regulatory DNA elements.
- Representation of AAV vectors with cell-type-specific enhancers.
- Basic simulation placeholders for enhancer-driven gene expression.
"""

from typing import Dict, Any, List

class Enhancer:
    def __init__(self, sequence: str, cell_type: str = None, species: str = None):
        self.sequence = sequence
        self.cell_type = cell_type
        self.species = species

    def info(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "cell_type": self.cell_type,
            "species": self.species
        }

class AAVVector:
    def __init__(self, capsid: str, enhancer: Enhancer, cargo_gene: str, target_species: str = None):
        self.capsid = capsid
        self.enhancer = enhancer
        self.cargo_gene = cargo_gene
        self.target_species = target_species

    def description(self) -> Dict[str, Any]:
        return {
            "capsid": self.capsid,
            "enhancer": self.enhancer.info(),
            "cargo_gene": self.cargo_gene,
            "target_species": self.target_species
        }

def simulate_enhancer_expression(aav_vector: AAVVector, cell_type_context: str) -> Dict[str, Any]:
    """
    Simulates gene expression of cargo gene in a given cell type context.
    Returns dict with predicted expression level and specificity.
    """
    if aav_vector.enhancer.cell_type == cell_type_context:
        expression = "high"
        specificity = "specific"
    else:
        expression = "low"
        specificity = "off-target or minimal"
    return {
        "cargo_gene": aav_vector.cargo_gene,
        "cell_type_context": cell_type_context,
        "predicted_expression": expression,
        "specificity": specificity
    }

# --- gfl_sdk/__init__.py (append imports and function) ---
from .external_integrations.enhancers import Enhancer, AAVVector, simulate_enhancer_expression

# --- test_enhancers.py (unit test for enhancers module) ---
import unittest
from gfl_sdk.external_integrations.enhancers import Enhancer, AAVVector, simulate_enhancer_expression

class TestEnhancers(unittest.TestCase):

    def test_enhancer_info(self):
        enhancer = Enhancer("ATCGATCG", cell_type="interneuron", species="mouse")
        info = enhancer.info()
        self.assertEqual(info["sequence"], "ATCGATCG")
        self.assertEqual(info["cell_type"], "interneuron")
        self.assertEqual(info["species"], "mouse")

    def test_aav_vector_description(self):
        enhancer = Enhancer("GGCTAGCT", cell_type="pyramidal_neuron")
        vector = AAVVector("AAV-PHP.B", enhancer, "GFP", target_species="mouse")
        desc = vector.description()
        self.assertIn("capsid", desc)
        self.assertIn("enhancer", desc)
        self.assertIn("cargo_gene", desc)
        self.assertEqual(desc["cargo_gene"], "GFP")

    def test_simulate_expression_specific(self):
        enhancer = Enhancer("AAAAGGGG", cell_type="striatal_interneuron")
        vector = AAVVector("AAV9", enhancer, "ChR2")
        result = simulate_enhancer_expression(vector, "striatal_interneuron")
        self.assertEqual(result["predicted_expression"], "high")
        self.assertEqual(result["specificity"], "specific")

    def test_simulate_expression_off_target(self):
        enhancer = Enhancer("TTTTCCCC", cell_type="cortical_pyramidal")
        vector = AAVVector("AAV9", enhancer, "ChR2")
        result = simulate_enhancer_expression(vector, "microglia")
        self.assertEqual(result["predicted_expression"], "low")
        self.assertEqual(result["specificity"], "off-target or minimal")

if __name__ == "__main__":
    unittest.main()

