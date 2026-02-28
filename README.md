# 🧬 GeneForgeLang v2.0 Beta

> **The Symbolic Language for Biological Reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0--beta-blue.svg)](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)
[![PyPI](https://img.shields.io/pypi/v/geneforgelang.svg)](https://pypi.org/project/geneforgelang/)

## 🎉 **GeneForge v2.0 Beta - Multi-Omic Reasoning Platform**

**Revolutionary computational biology platform** that integrates multi-omic data with spatial genomic reasoning for biological discovery and design.

## What is GeneForgeLang v2.0?

GeneForgeLang (GFL) v2.0 is a **next-generation domain-specific language** for computational biology that enables researchers to reason across multiple omics layers while maintaining spatial genomic context. Building upon our proven workflow capabilities, v2.0 introduces comprehensive multi-omic integration, spatial genomic reasoning, and guided discovery frameworks.

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

Our platform has been validated through a comprehensive experiment discovering optimal gRNA candidates for CRISPR gene editing:

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

**📄 [Read the full scientific manuscript](examples/gfl-genesis/Manuscript_GeneForge_v2_Beta.md)**

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

### Basic Usage - Multi-Omic gRNA Discovery

```python
from geneforgelang import parse, validate, execute

# Define a multi-omic gRNA discovery workflow
workflow = """
# Multi-omic entity definitions
transcripts:
  - id: "BRCA1_transcript"
    gene_source: "BRCA1"
    exons: [1, 2, 3, 4, 5]
    identifiers:
      refseq: "NM_007294.4"

proteins:
  - id: "BRCA1_protein"
    translates_from: "transcript(BRCA1_transcript)"
    domains:
      - id: "BRCT_Domain"
        start: 1649
        end: 1736
    identifiers:
      uniprot: "P38398"

# Spatial genomic context
loci:
  - id: "BRCA1_GeneLocus"
    chromosome: "chr17"
    start: 43094495
    end: 43125483
    elements:
      - id: "BRCA1_Promoter"
        type: "promoter"

# Guided discovery for gRNA candidates
guided_discovery:
  name: "BRCA1_gRNA_Discovery"
  target: "BRCA1_protein"
  strategy:
    type: "iterative_refinement"
    max_iterations: 5

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

```
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

## Web Interface

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

### CLI Commands

- `gfl validate <file>`: Validate workflow file
- `gfl execute <file>`: Execute workflow
- `gfl web`: Start web interface
- `gfl plugins`: List available plugins

## Development

### Setup Development Environment

```
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

### Container-Based Execution

GeneForgeLang now supports container-based plugin execution for enhanced reproducibility:

1. Plugins can specify Docker container images through the `gfl.plugin_containers` entry point
2. The execution engine automatically detects and uses container images when available
3. Volume mounting is handled automatically for file I/O
4. Falls back to local execution when Docker is not available

To enable container execution during development:

```
# Install with container support
pip install -e .[containers]

# Or install docker package directly
pip install docker
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

```
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
