"""Simple protein sequence generator plugin."""

from typing import Dict, Any, List
from gfl.plugins.base import BaseGeneratorPlugin


class SimpleProteinGenerator(BaseGeneratorPlugin):
    """
    Simple protein sequence generator for demonstration purposes.
    
    This is a basic implementation that generates random protein sequences
    based on amino acid frequency distributions. For production use,
    more sophisticated methods like VAEs or transformers would be used.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "SimpleProteinGenerator"
        self.description = "Basic protein sequence generator"
        
        # Common amino acid frequencies in proteins
        self.aa_frequencies = {
            'A': 0.074, 'R': 0.042, 'N': 0.044, 'D': 0.059, 'C': 0.033,
            'Q': 0.037, 'E': 0.058, 'G': 0.074, 'H': 0.029, 'I': 0.038,
            'L': 0.076, 'K': 0.072, 'M': 0.018, 'F': 0.040, 'P': 0.050,
            'S': 0.081, 'T': 0.062, 'W': 0.013, 'Y': 0.033, 'V': 0.068
        }
    
    def generate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate protein sequences based on parameters."""
        import random
        
        count = params.get('count', 10)
        length = params.get('length', 100)
        
        # Create weighted amino acid list
        amino_acids = []
        for aa, freq in self.aa_frequencies.items():
            amino_acids.extend([aa] * int(freq * 1000))
        
        sequences = []
        for i in range(count):
            sequence = ''.join(random.choices(amino_acids, k=length))
            sequences.append({
                'id': f'generated_{i+1}',
                'sequence': sequence,
                'length': length,
                'method': 'frequency_based_sampling'
            })
        
        return {
            'sequences': sequences,
            'count': len(sequences),
            'method': 'SimpleProteinGenerator',
            'parameters_used': params
        }
