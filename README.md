# 🧬 GeneForgeLang

> **The Symbolic Language for Biological Reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Notice.** Research software. Not a medical device, not for clinical use, and not legal or regulatory advice.

## What is GeneForgeLang?

GeneForgeLang (GFL) is a domain-specific language for describing biological design workflows. A GFL document is YAML with typed blocks (`design`, `optimize`, `experiment`, `analyze`, ...). The Python library parses and validates these documents and offers a plugin system for tools that act on them.

**Status.** GFL is under active development and has no published release yet. The documented public API and the `gfl` command-line tool do not work from an installed package in this version (see [Quick Start](#quick-start)). The language features listed below describe the language design; check the [feature documentation](docs/index.md) for what the current parser accepts.

## Language Capabilities

### **Multi-Omic Integration**

- **🧬 Transcripts Block**: Define transcript structures with exon annotations
- **🔬 Proteins Block**: Annotate proteins with functional domains
- **⚗️ Metabolites Block**: Chemical formula support with database integration
- **🔗 External Identifiers**: UniProt, RefSeq, ChEBI, HMDB, KEGG integration

### **Spatial Genomic Reasoning**

- **📍 Genomic Loci**: Define named genomic regions with coordinates
- **🎯 Spatial Predicates**: `is_within`, `distance_between`, `is_in_contact`
- **🧩 3D Chromatin**: Hi-C integration for spatial interactions
- **📐 Context-Aware Rules**: Spatial constraints in biological reasoning

### **Advanced Discovery Engine**

- **🔄 Guided Discovery**: Iterative learning and candidate optimization
- **⚙️ Capability-Aware**: Engine compatibility across deployment scenarios
- **📋 Rule-Based Logic**: Complex biological constraint expression
- **🎭 Simulation Framework**: What-if analysis and hypothesis testing

### **Local Execution**

- **🛡️ Data stays local**: the library parses and validates workflows on your machine; it sends no data to a cloud service.

## 🌐 Open-Source and Universal
GeneForgeLang is an **open-source project** dedicated to the entire scientific community. While it serves as the foundation for the GeneForge platform, its design and evolution are governed by universal biological principles, not by any specific commercial or execution environment.

*   **Universal Semantic Authority**: GFL defines the biological world independently of how it is executed.
*   **Open to Everyone**: Anyone can implement a GFL-compatible runtime or contribute to the language specifications.
*   **Decoupled Architecture**: Formal separation between Language Specification, Semantic Validation, and Execution Runtimes.

## 📜 Formal Specifications
To ensure consistency across the ecosystem, GFL maintains a set of formal specifications:
*   **[Architectural Directive](docs/architecture/ARCHITECTURAL_DIRECTIVE.md)**: The foundational decoupling mandate.
*   **[RFC Process](docs/rfc/README.md)**: Formal procedure for language evolution.
*   [Causal Semantics](docs/spec/causal_semantics.md): Rules for biological transformations.
*   [Biological State Space](docs/spec/state_space.md): Structural definition of the biological world.
*   [Instruction Set](docs/spec/instruction_set.md): Primitive biological operations.
*   [Execution Contract](docs/spec/execution_contract.md): Boundary between language and runtimes.
*   [Versioning Policy](docs/spec/versioning_policy.md): How the language evolves.
- **Type Safety**: Strong typing system with comprehensive validation
- **Plugin Architecture**: Extensible system for custom tools and algorithms
- **Web Interface**: Modern web UI for workflow creation and management
- **CLI Tools**: Comprehensive command-line interface for automation
- **API Integration**: RESTful API for programmatic access
- **Container Execution**: Reproducible execution using Docker containers

## 🧪 Example: BRCA1 gRNA Discovery (Illustrative simulation)

The [GFL Genesis example](examples/real_project/README.md) shows how a guided-discovery workflow for CRISPR gRNA candidates against BRCA1 is written in GFL. Its execution script draws every on-target and off-target score from `np.random.beta`: the numbers in its outputs are random scores, not a validation, and say nothing about real guide efficiency or safety. The accompanying [draft manuscript](examples/real_project/Manuscript_GeneForge_v2_Beta.md) is labelled the same way.

## Quick Start

### Installation

GeneForgeLang is not yet published on PyPI. Install it from source:

```bash
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang
pip install -e .

# Optional extras: web, cli, ml, containers, staging, lsp, dev
pip install -e ".[cli]"
```

### Basic Usage - Protein Design and Optimization

This is the target Python API. The top-level import below does not work in this version; feature F010 adds it. The workflow text itself parses and validates with the current parser.

<!-- does not run yet: F010 -->
```python
from geneforgelang import parse, validate, execute

# Simple GFL Workflow Example
workflow = """
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  count: 10
  length: 100
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    pH: "range(6.0, 8.0)"
    concentration: "range(10, 100)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: efficiency
  budget:
    max_experiments: 20
  run:
    experiment:
      tool: protein_assay
      type: efficiency_measurement
      params:
        temp: "${temperature}"
        pH: "${pH}"
        conc: "${concentration}"
"""

# Parse and validate
ast = parse(workflow)
errors = validate(ast)

if not errors:
    print("GFL file successfully validated")

    # Execute workflow
    result = execute(ast)
    print(f"Done: {result['design']['count']} proteins generated")
```

### Command Line Interface

The `gfl` command does not start in this version (feature F015 tracks the fix). These are the intended commands:

```bash
# Parse a workflow
gfl parse workflow.gfl

# Validate a workflow
gfl validate workflow.gfl

# or both!
gfl parse workflow.gfl --validate

# Execute a workflow
gfl infer workflow.gfl

# Get help (or check full options)
gfl --help
gfl -h
```

## Workflow Examples

### CRISPR Gene Editing

```gfl
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

```gfl
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  constraints:
    - length(50, 150)
    - synthesizability > 0.8
  count: 10
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    ph: "range(6.5, 8.0)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: expression_level
  budget:
    max_experiments: 50
  run:
    experiment:
      tool: protein_assay
      type: expression_measurement
      params:
        temp: "${temperature}"
        ph: "${ph}"
```

## Architecture

GeneForgeLang follows a modular architecture:

```text
src/geneforgelang/
├── core/           # Core language functionality
│   ├── parser.py   # YAML/GFL parser
│   ├── validator.py # Semantic validation
│   ├── gftypes.py    # Type system
│   └── api.py      # Public API
├── plugins/        # Plugin system
├── web/           # Web interface
├── cli/           # Command-line tools
└── utils/         # Shared utilities
```

## Plugin System

A plugin subclasses `BaseGFLPlugin` and implements `process`:

```python
from typing import Any

from geneforgelang.plugins.base import BaseGFLPlugin


class CustomAnalysisPlugin(BaseGFLPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = "custom_analysis"
        self.description = "Example analysis plugin"

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        # Custom analysis logic
        return {"result": "analysis_complete", "input_keys": sorted(data)}


plugin = CustomAnalysisPlugin()
print(plugin.process({"sequence": "MKTAYIAKQR"}))
```

Registering a plugin with `geneforgelang.plugins.plugin_registry.register_plugin` does not work in an installed package in this version: the registry module imports `src.geneforgelang`, which only resolves from a source checkout. Feature F010 fixes this.

## Web Interface (Not working!)

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

```text
GeneForgeLang/
├── src/geneforgelang/    # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
├── resources/            # Dev tools, scripts, ...
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

- [User Guide](docs/guides/user-guides/) - Complete usage documentation
- [API Reference](docs/geneforgelang/api.md) - Detailed API documentation
- [Architecture](docs/dev/decisions/organization.md) - System design and decisions
- [Examples](examples/) - Practical workflow examples

## License

This project is licensed under the MIT License - see the [license](license) file for details.

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

- [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues) - Bug reports, questions and feature requests
- [Documentation](docs/index.md) - Guides and reference in this repository

---

**GeneForgeLang** - Professional genomic workflow automation
