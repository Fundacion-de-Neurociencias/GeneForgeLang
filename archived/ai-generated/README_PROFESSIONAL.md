# GeneForgeLang

[![PyPI version](https://badge.fury.io/py/geneforgelang.svg)](https://badge.fury.io/py/geneforgelang)
[![Python Support](https://img.shields.io/pypi/pyversions/geneforgelang.svg)](https://pypi.org/project/geneforgelang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A professional domain-specific language (DSL) for genomic workflows and bioinformatics applications.

## Overview

GeneForgeLang (GFL) is a declarative language designed for specifying, validating, and executing genomic workflows. It provides a clean, YAML-like syntax for describing complex bioinformatics pipelines with built-in validation, type safety, and extensibility.

## Key Features

- **Declarative Syntax**: Clean, readable YAML-based workflow definitions
- **Type Safety**: Strong typing system with comprehensive validation
- **Plugin Architecture**: Extensible system for custom tools and algorithms
- **Web Interface**: Modern web UI for workflow creation and management
- **CLI Tools**: Comprehensive command-line interface for automation
- **API Integration**: RESTful API for programmatic access

## Quick Start

### Installation

```bash
# Basic installation
pip install geneforgelang

# With web interface
pip install geneforgelang[web]

# With CLI tools
pip install geneforgelang[cli]

# Full installation
pip install geneforgelang[all]
```

### Basic Usage

```python
from geneforgelang import parse, validate, execute

# Define a workflow
workflow = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: GCACTGCCATGGAGGAGCCG

analysis:
  type: efficiency_prediction
  model: cas9_efficiency_v2
"""

# Parse and validate
ast = parse(workflow)
errors = validate(ast)

if not errors:
    # Execute workflow
    result = execute(ast)
    print(f"Editing efficiency: {result['efficiency']:.2%}")
```

### Command Line Interface

```bash
# Parse and validate a workflow
gfl validate workflow.gfl

# Execute a workflow
gfl execute workflow.gfl

# Start web interface
gfl web --port 8080

# Get help
gfl --help
```

## Workflow Examples

### CRISPR Gene Editing

```yaml
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: BRCA1
    guide_rna: GCACTGCCATGGAGGAGCCG
    cell_line: HEK293T

analysis:
  type: off_target_prediction
  algorithm: cas_offinder
  params:
    max_mismatches: 3

validation:
  type: experimental
  replicates: 3
  controls: [negative, positive]
```

### Protein Design

```yaml
design:
  entity: ProteinSequence
  objective:
    maximize: stability
    target: therapeutic_protein
  constraints:
    - length: [50, 150]
    - synthesizability: ">0.8"
  count: 10

optimize:
  search_space:
    temperature: [25, 42]
    ph: [6.5, 8.0]
  strategy: bayesian_optimization
  objective:
    maximize: expression_level
  budget:
    max_experiments: 50
```

## Architecture

GeneForgeLang follows a modular architecture:

```
src/geneforgelang/
├── core/           # Core language functionality
│   ├── parser.py   # YAML/GFL parser
│   ├── validator.py # Semantic validation
│   ├── types.py    # Type system
│   └── api.py      # Public API
├── plugins/        # Plugin system
├── web/           # Web interface
├── cli/           # Command-line tools
└── utils/         # Shared utilities
```

## Plugin System

GeneForgeLang supports custom plugins for extending functionality:

```python
from geneforgelang.plugins import BasePlugin

class CustomAnalysisPlugin(BasePlugin):
    name = "custom_analysis"
    version = "1.0.0"

    def execute(self, params: dict) -> dict:
        # Custom analysis logic
        return {"result": "analysis_complete"}

# Register plugin
from geneforgelang.plugins import register_plugin
register_plugin(CustomAnalysisPlugin())
```

## Web Interface

Launch the web interface for interactive workflow development:

```bash
gfl web --host 0.0.0.0 --port 8080
```

Features:
- Visual workflow editor
- Real-time validation
- Execution monitoring
- Result visualization

## API Reference

### Core Functions

- `parse(text: str) -> Dict`: Parse GFL text into AST
- `validate(ast: Dict) -> List[str]`: Validate AST semantics
- `execute(ast: Dict) -> Dict`: Execute workflow
- `infer(model, ast: Dict) -> Dict`: Run ML inference

### CLI Commands

- `gfl validate <file>`: Validate workflow file
- `gfl execute <file>`: Execute workflow
- `gfl web`: Start web interface
- `gfl plugins`: List available plugins

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Project Structure

```
GeneForgeLang/
├── src/geneforgelang/    # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
├── tools/                # Development tools
└── pyproject.toml        # Project configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [User Guide](docs/user-guide/) - Complete usage documentation
- [API Reference](docs/api/) - Detailed API documentation
- [Architecture](docs/architecture/) - System design and decisions
- [Examples](examples/) - Practical workflow examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GeneForgeLang in your research, please cite:

```bibtex
@software{geneforgelang2025,
  title={GeneForgeLang: A Professional DSL for Genomic Workflows},
  author={GeneForgeLang Development Team},
  year={2025},
  url={https://github.com/Fundacion-de-Neurociencias/GeneForgeLang},
  version={1.0.0}
}
```

## Support

- [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues) - Bug reports and feature requests
- [Discussions](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions) - Community support
- [Documentation](https://geneforgelang.readthedocs.io) - Comprehensive guides

---

**GeneForgeLang** - Professional genomic workflow automation
