# 🧬 GFL v2.0 Beta

> **The Symbolic Language for Biological Reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0--beta-blue.svg)](.)
[![PyPI](https://img.shields.io/pypi/v/geneforgelang.svg)](https://pypi.org/project/geneforgelang/)

## **GFL v2.0 Beta - Multi-Omic Reasoning Language**

**Open-source domain-specific language for computational biology** that integrates multi-omic data with spatial genomic reasoning for biological discovery and design.

## What is GFL v2.0?

GFL v2.0 is a **next-generation domain-specific language** for computational biology that enables researchers to reason across multiple omics layers while maintaining spatial genomic context. Building on declarative workflow capabilities, v2.0 introduces comprehensive multi-omic integration, spatial genomic reasoning, and guided discovery frameworks.

## 🚀 **New in v2.0 - Multi-Omic Capabilities**

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

### **Privacy-Preserving Bio-Skills**

- **🧬 Local Bioinformatics**: High-precision analysis running 100% locally
- **✅ Scientific Reproducibility**: Automatic generation of Reproducibility Packages (hashes, timestamps, versions)
- **🧠 Clinical Neuro-Skills**: Specialized skills for PharmGx, Geriatric Risk, and NutriGx
- **🛡️ Data Sovereignty**: Genome-scale analysis without cloud dependencies or LLM hallucinations

## Key Features

- **Declarative Syntax**: Clean, readable YAML-based workflow definitions
- **Type Safety**: Strong typing system with comprehensive validation
- **Plugin Architecture**: Extensible system for custom tools and algorithms
- **Web Interface**: Modern web UI for workflow creation and management
- **CLI Tools**: Comprehensive command-line interface for automation
- **API Integration**: RESTful API for programmatic access
- **Container Execution**: Reproducible execution using Docker containers

## 🧪 **Scientific Validation - BRCA1 gRNA Discovery**

GFL has been validated through a comprehensive experiment discovering optimal gRNA candidates for CRISPR gene editing:

### **Results Summary**

- **🏆 Best Candidate**: BRCA1_gRNA_4_02
- **📈 Combined Score**: 89.7% efficiency
- **🎯 On-Target**: 84.8% efficiency with only 3.0% off-target risk
- **⚡ Discovery Time**: 24 seconds for 50 candidates across 5 cycles

### **Scientific Impact**

- **Clinical Relevance**: BRCA1 is critical for cancer research
- **Safety Focus**: <30% off-target risk across all top candidates
- **Efficiency**: >80% on-target activity for top 10 candidates
- **Reproducibility**: Complete workflow documented and open-source

Scientific manuscript available in the examples directory.

## Quick Start

### Installation

```
# Basic installation
pip install geneforgelang

# With web interface
pip install geneforgelang[web]

# With CLI tools
pip install geneforgelang[cli]

# With container support
pip install geneforgelang[containers]

# Full installation
pip install geneforgelang[all]
```

### Basic Usage - Protein Design and Optimization

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
    #print(result)
    print(f"Done!: {result['design']['count']} proteins generated")
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

```
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

```
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

```
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

GFL follows a modular architecture:

```
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

GFL supports custom plugins for extending functionality:

```
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

## Web Interface (Not working!)

Launch the web interface for interactive workflow development:

```
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

```
# Clone repository
git clone <repository-url>
cd <repository-directory>

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Project Structure

```
GFL/
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GFL in your research, please cite:

```
@software{geneforgelang2025,
  title={GFL: A Professional DSL for Genomic Workflows},
  author={GFL Development Team},
  year={2025},
  version={1.0.0}
}
```

## Support

- GitHub Issues - Bug reports and feature requests
- Discussions - Community support
- [Documentation](https://geneforgelang.readthedocs.io) - Comprehensive guides

---

**GFL** - Open-source language for genomic workflow specification
