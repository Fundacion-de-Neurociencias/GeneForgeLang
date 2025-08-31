# GeneForgeLang (GFL) 🧬

[![CI](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions/workflows/ci.yml/badge.svg)](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions/workflows/ci.yml)
[![Documentation](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions/workflows/docs.yml/badge.svg)](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-bandit-yellow)](https://github.com/PyCQA/bandit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **A powerful Domain-Specific Language (DSL) for genomic workflows and bioinformatics applications with AI-powered analysis capabilities.**

GeneForgeLang (GFL) is a comprehensive framework for specifying, validating, and executing genomic workflows. It combines the simplicity of YAML-like syntax with advanced features like AI-powered inference, plugin extensibility, and web-based interfaces.

## ✨ Key Features

🔬 **Genomic Workflow Specification** - Declarative YAML-like syntax for complex genomic experiments
🤖 **AI-Powered Analysis** - Built-in inference engine with machine learning capabilities
🧪 **Workflow Execution Engine** - Execute design and optimize blocks with intelligent plugin dispatch
🔌 **Advanced Plugin System** - Extensible interfaces for generators, optimizers, and AI models
🌐 **Web Interface** - Modern web platform for interactive workflow creation and execution
⚡ **High Performance** - Optimized for large-scale genomic data processing with intelligent caching
🔒 **Secure & Robust** - Comprehensive security features and error handling

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install -e .

# With all features
pip install -e .[full]

# Optional extras
pip install -e .[apps]     # Demo applications with Gradio
pip install -e .[ml]       # Machine learning capabilities
pip install -e .[server]   # Web server and API
```

### Your First GFL Workflow

```python
from gfl.api import parse, validate, execute

# Define a protein design workflow with AI-powered generation
workflow = """
metadata:
  experiment_id: PROTEIN_DESIGN_001
  researcher: Dr. Jane Smith
  project: therapeutic_proteins

design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
    target: therapeutic_protein
  constraints:
    - length(50, 150)
    - synthesizability > 0.8
    - stability_score > 0.7
  count: 10
  output: designed_proteins

optimize:
  search_space:
    temperature: range(25, 42)
    concentration: range(10, 100)
  strategy:
    name: BayesianOptimization
  objective:
    maximize: expression_level
  budget:
    max_experiments: 25
  run:
    experiment:
      tool: protein_expression
      type: validation
      params:
        proteins: designed_proteins
        temp: ${temperature}
        conc: ${concentration}
"""

# Parse, validate, and execute
ast = parse(workflow)
errors = validate(ast)
print(f"Validation: {'✅ Passed' if not errors else '❌ Failed'}")

# Execute complete workflow with plugin dispatch
result = execute(ast)
print(f"Generated {result['design']['count']} protein candidates")
print(f"Best experimental conditions: {result['optimize']['best_parameters']}")
```

## 📚 Documentation

🌐 **[Complete Documentation](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)** - Full user guide, tutorials, and API reference

### Quick Links
- 🚀 **[Getting Started](https://fundacion-de-neurociencias.github.io/GeneForgeLang/installation/)** - Installation and setup guide
- 🎯 **[Tutorial](https://fundacion-de-neurociencias.github.io/GeneForgeLang/tutorial/)** - Step-by-step learning guide
- 🔧 **[API Reference](https://fundacion-de-neurociencias.github.io/GeneForgeLang/API_REFERENCE/)** - Complete API documentation
- 🌐 **[Web Platform](https://fundacion-de-neurociencias.github.io/GeneForgeLang/WEB_API_IMPLEMENTATION_SUMMARY/)** - Web interface guide
- 🤖 **[AI Features](https://fundacion-de-neurociencias.github.io/GeneForgeLang/ENHANCED_INFERENCE_SUMMARY/)** - Machine learning capabilities
- 🔒 **[Security](https://fundacion-de-neurociencias.github.io/GeneForgeLang/SECURITY_ADVISORY/)** - Security guidelines and best practices
- 🔌 **[Plugin Ecosystem](https://fundacion-de-neurociencias.github.io/GeneForgeLang/PLUGIN_ECOSYSTEM/)** - Advanced plugin system and workflow execution
- 🎯 **[Language Features](https://fundacion-de-neurociencias.github.io/GeneForgeLang/features/design_block/)** - Design and optimize block documentation
- 🧪 **[Workflow Examples](https://fundacion-de-neurociencias.github.io/GeneForgeLang/examples/)** - Complete workflow examples with AI integration

### 🧪 Advanced AI-Driven Workflows

**GeneForgeLang now supports intelligent experimental design with AI-powered plugins:**

#### Design Block - Biological Entity Generation
```yaml
design:
  entity: ProteinSequence           # or DNA, RNA, SmallMolecule
  model: ProteinVAEGenerator        # AI plugin for generation
  objective:
    maximize: binding_affinity
    target: SARS_CoV2_RBD
  constraints:
    - length(100, 200)
    - synthesizability > 0.8
    - stability_score > 0.7
  count: 50
  output: therapeutic_candidates
```

#### Optimize Block - Intelligent Parameter Search
```yaml
optimize:
  search_space:
    temperature: range(25, 42)      # Continuous parameters
    duration: choice([6, 12, 24])   # Discrete choices
    concentration: range(10, 100)
  strategy:
    name: BayesianOptimization      # AI optimization strategy
    uncertainty_metric: entropy
  objective:
    maximize: editing_efficiency
  budget:
    max_experiments: 100
    max_time: 48h
  run:
    experiment:
      tool: CRISPR_cas9
      params:
        temp: ${temperature}         # Parameter injection
        conc: ${concentration}
        dur: ${duration}h
```

**Key Features:**
- ✨ **AI-Powered Generation** - VAE, GAN, Transformer models for biological design
- 🤖 **Intelligent Optimization** - Bayesian, evolutionary, and reinforcement learning
- 🔄 **Parameter Injection** - Dynamic parameter substitution with `${...}` syntax
- 🔗 **Workflow Integration** - Seamless combination of design and optimization
- 📊 **Real-time Monitoring** - Live tracking of experimental campaigns

### 🌍 Industrial & Research Applications

🧬 Genomics Research
- **CRISPR Design** - Automated guide RNA design and off-target prediction
- **RNA-seq Analysis** - Differential expression and pathway analysis workflows
- **Variant Analysis** - SNP/INDEL interpretation and clinical annotation
- **Protein Studies** - Structure prediction and interaction analysis

### 🏥 Clinical Applications
- **Diagnostic Pipelines** - Automated variant interpretation workflows
- **Pharmacogenomics** - Drug response prediction based on genetic profiles
- **Cancer Genomics** - Somatic mutation analysis and treatment recommendations
- **Rare Disease** - Comprehensive genomic analysis for rare disorders

### 🌱 Agricultural & Industrial
- **Crop Improvement** - Gene editing workflows for enhanced traits
- **Bioengineering** - Synthetic biology pipeline automation
- **Quality Control** - Genomic validation and testing workflows

## 📦 Core Components

### 🔌 Advanced Plugin System
- **Generator Plugins** - AI models for biological entity creation (proteins, DNA, molecules)
- **Optimizer Plugins** - Intelligent algorithms for parameter space exploration
- **Prior Plugins** - Bayesian integration for enhanced experimental design
- **Plugin Registry** - Automatic discovery and lifecycle management
- **Extensible Interfaces** - Standard contracts for seamless integration

### 🧪 Workflow Execution Engine
- **Design Block Execution** - Automated dispatch to appropriate AI generators
- **Optimize Block Execution** - Intelligent experimental loops with parameter injection
- **State Management** - Persistent workflow variables and execution history
- **Error Recovery** - Comprehensive error handling and recovery mechanisms
- **Real-time Monitoring** - Live tracking of workflow execution progress

### 🔭 Language Core
- **Parser** - YAML-like DSL with stable, JSON-serializable AST
- **Validator** - Semantic validation with customizable rules
- **Interpreter** - Efficient AST execution with plugin support
- **Type System** - Strong typing for genomic entities and operations

### 🤖 AI & Machine Learning
- **Inference Engine** - Built-in ML models for genomic prediction
- **Natural Language** - Convert English descriptions to GFL workflows
- **Model Integration** - Support for custom models and external APIs
- **Probabilistic Reasoning** - Likelihood-based decision making

### 🌐 Web Platform
- **Interactive Interface** - Modern web UI for workflow creation
- **REST API** - Complete RESTful API for programmatic access
- **Real-time Execution** - Live workflow execution and monitoring
- **Collaboration Tools** - Share and collaborate on workflows

### 🔌 Extension System
- **Advanced Plugin Interfaces** - GeneratorPlugin, OptimizerPlugin, PriorsPlugin
- **Intelligent Dispatch** - Automatic plugin discovery and execution
- **Plugin Ecosystem** - Community-driven plugin development and sharing
- **Dependency Management** - Automatic dependency resolution and validation
- **Lifecycle Hooks** - Plugin loading, activation, and cleanup events

## 🔧 CLI Tools

GeneForgeLang provides powerful command-line tools for workflow management:

```
# Parse and validate workflows
gfl-parse workflow.gfl
gfl-validate workflow.gfl

# Execute complete workflows with AI plugins
gfl-execute workflow.gfl
gfl-plugins --list

# Run inference and analysis
gfl-inference workflow.gfl
gfl-enhanced workflow.gfl

# Start web server and API
gfl-server --port 8000
gfl-api --host 0.0.0.0

# Launch web interface
gfl-web

# Get system information
gfl-info
```

## 🌐 Web Applications

### Interactive Translator
Convert natural language descriptions to GFL workflows:

```bash
python applications/translator_app/app.py
```

**Features:**
- 🗣️ Natural language to GFL conversion
- ✅ Real-time validation and syntax checking
- 🤖 AI-powered workflow optimization
- 📊 Interactive visualization and analysis

### Web Platform
Full-featured web interface for genomic workflow management:

```bash
gfl-web --port 8080
```

**Access at:** `http://localhost:8080`

## 📦 Repository Structure

```
GeneForgeLang/
├── gfl/                         # Core library
│   ├── api.py                   # Public API with execute() function
│   ├── parser.py                # YAML parser
│   ├── validator.py             # Semantic validation
│   ├── execution_engine.py      # NEW: Workflow execution engine
│   ├── inference_engine.py      # AI inference
│   ├── web_interface.py         # Web platform
│   └── plugins/                 # NEW: Advanced plugin system
│       ├── interfaces.py        #   Plugin interface definitions
│       ├── example_implementations.py  #   Reference plugins
│       └── plugin_registry.py   #   Plugin discovery and management
├── applications/                # Demo applications
├── docs/                        # Documentation source
│   ├── features/                # NEW: Feature-specific documentation
│   ├── PLUGIN_ECOSYSTEM.md      # NEW: Plugin development guide
│   └── PHASE_3_PLUGIN_ECOSYSTEM_SUMMARY.md  # NEW: Implementation summary
├── examples/                    # Example workflows
├── tests/                       # Test suite
│   ├── test_new_features.py     # NEW: 24 regression tests
│   └── test_plugin_interfaces.py # NEW: Plugin interface tests
└── integrations/                # External integrations
```

## 🔒 Security & Quality

- ✅ **Comprehensive Testing** - 50+ tests including 24 new feature regression tests  
- ✅ **Plugin Ecosystem Testing** - Complete test coverage for AI workflow execution
- 🔒 **Security Scanning** - Automated security analysis with Bandit
- 🧙 **Code Quality** - Enforced with Ruff, Black, and MyPy
- 🔄 **Continuous Integration** - Automated testing on multiple Python versions
- 📄 **Documentation** - Comprehensive docs with plugin ecosystem guides

## 🛣️ API Stability

- **Public API** - `gfl.api` module provides stable interface for all operations
- **AST Format** - Dictionary-based AST with guaranteed backward compatibility
- **Plugin Interface** - Well-defined plugin system for extending functionality
- **Semantic Versioning** - Clear versioning strategy for API changes

## 🚀 Performance

- **Optimized Parsing** - Fast YAML processing with minimal overhead
- **Efficient Validation** - Incremental validation with early error detection
- **Scalable Execution** - Support for large-scale genomic datasets
- **Memory Efficient** - Optimized memory usage for large workflows

## 🌍 Community & Support

- 📚 **[Documentation](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)** - Comprehensive user guides and API reference
- 🐛 **[Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues)** - Bug reports and feature requests
- 💬 **[Discussions](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions)** - Community support and Q&A
- 🔄 **[Contributing](CONTRIBUTING.md)** - Guidelines for contributing to the project

## 🗺️ Roadmap

### 🔄 Current Version (v0.1.0)
- ✅ Core language implementation
- ✅ Web interface and API
- ✅ AI-powered inference engine
- ✅ Plugin system
- ✅ Comprehensive documentation

### 🔮 Upcoming Features
- 🔄 **Enhanced ML Models** - Advanced genomic prediction models
- 🔌 **More Integrations** - Support for popular bioinformatics tools
- 🌐 **Cloud Deployment** - Docker and Kubernetes support
- 📈 **Analytics Dashboard** - Workflow monitoring and metrics
- 🛠️ **Visual Editor** - Drag-and-drop workflow creation

**[View Full Roadmap](https://fundacion-de-neurociencias.github.io/GeneForgeLang/PHASE_4_PLANNING/)**

## 🤝 Contributing

We welcome contributions from the genomics and bioinformatics community!

### How to Contribute
1. 🍿 **Fork** the repository
2. 🌱 **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. ✨ **Make** your changes with tests
4. ✅ **Test** your changes (`pytest tests/`)
5. 📝 **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. 🚀 **Push** to the branch (`git push origin feature/amazing-feature`)
7. 🎉 **Open** a Pull Request

**[Read the Contributing Guide](CONTRIBUTING.md)** for detailed instructions.

### Development Setup

```
# Clone the repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Install in development mode
pip install -e .[full]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## 📜 Citation

If you use GeneForgeLang in your research, please cite:

```
@software{geneforgelang2025,
  title={GeneForgeLang: A Domain-Specific Language for Genomic Workflows},
  author={GeneForgeLang Development Team},
  year={2025},
  url={https://github.com/Fundacion-de-Neurociencias/GeneForgeLang},
  version={0.1.0}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Quick Links

| Resource | Link |
|----------|------|
| 📚 **Documentation** | [fundacion-de-neurociencias.github.io/GeneForgeLang](https://fundacion-de-neurociencias.github.io/GeneForgeLang/) |
| 🐛 **Issues** | [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions) |
| 🔄 **CI/CD** | [GitHub Actions](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/actions) |
| 📈 **Releases** | [GitHub Releases](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/releases) |

---

<div align="center">

**GeneForgeLang** - *Empowering genomic research through structured workflows and AI-powered analysis*

Made with ❤️ by the [Fundación de Neurociencias](https://github.com/Fundacion-de-Neurociencias)

[Get Started](https://fundacion-de-neurociencias.github.io/GeneForgeLang/installation/) • [Documentation](https://fundacion-de-neurociencias.github.io/GeneForgeLang/) • [Examples](https://fundacion-de-neurociencias.github.io/GeneForgeLang/tutorial/) • [API Reference](https://fundacion-de-neurociencias.github.io/GeneForgeLang/API_REFERENCE/)

</div>
