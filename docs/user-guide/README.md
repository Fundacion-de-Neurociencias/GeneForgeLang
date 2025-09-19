# GeneForgeLang (GFL)

A domain-specific language for computational biology and genetic engineering workflows.

## Overview

GeneForgeLang provides a structured way to describe and execute computational biology workflows, including:

- Protein sequence design and optimization
- CRISPR guide RNA design and evaluation  
- Molecular simulation and analysis
- Experimental parameter optimization

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from gfl.api import parse, validate, execute

# Define a protein design workflow
gfl_code = """
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  count: 10
  output: designed_proteins
"""

# Parse and execute
ast = parse(gfl_code)
errors = validate(ast)
if not errors:
    result = execute(ast)
    print(f"Generated {result['design']['count']} protein sequences")
```

## Scientific Accuracy

This software implements established computational biology methods:

- **Protein Design**: Uses frequency-based amino acid sampling as a baseline method
- **Optimization**: Implements random search and can be extended with Bayesian optimization
- **Plugin Architecture**: Allows integration of established tools and models

All implementations are transparent about their methods and limitations. For production use, users should integrate established tools through the plugin system.

## Plugin System

GFL uses a plugin architecture to integrate computational biology tools:

```python
from gfl.plugins.base import BaseGeneratorPlugin

class MyProteinGenerator(BaseGeneratorPlugin):
    def generate(self, params):
        # Your implementation here
        return results
```

## Contributing

Please ensure all contributions:
1. Include proper scientific references
2. Are transparent about method limitations  
3. Include comprehensive tests
4. Follow established computational biology practices

## License

MIT License - see LICENSE file for details.
