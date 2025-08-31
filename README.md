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
🌐 **Web Interface** - Modern web platform for interactive workflow creation and execution
🔌 **Plugin System** - Extensible architecture for custom tools and integrations
⚡ **High Performance** - Optimized for large-scale genomic data processing
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
from gfl.api import parse, validate, infer

# Define a CRISPR gene editing experiment
workflow = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: "GCCTACTGGTTCTGTACTGAGGG"
    cell_line: "HEK293T"

analyze:
  tools: ["off_target_prediction", "efficiency_scoring"]
  outputs: ["efficiency_score", "off_target_sites"]
"""

# Parse and validate
ast = parse(workflow)
errors = validate(ast)
print(f"Validation: {'✅ Passed' if not errors else '❌ Failed'}")

# Run AI-powered inference
result = infer(ast)
print(f"Predicted efficiency: {result.get('efficiency_score', 'N/A')}")
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

## 🎯 Use Cases

### 🧬 Genomics Research
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
- **Plugin Registry** - Extensible architecture for custom tools
- **Third-party Integration** - Connect with existing bioinformatics tools
- **Custom Validators** - Domain-specific validation rules
- **External APIs** - Integration with genomic databases and services

## 🔧 CLI Tools

GeneForgeLang provides powerful command-line tools for workflow management:

```bash
# Parse and validate workflows
gfl-parse workflow.gfl
gfl-validate workflow.gfl

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
├── gfl/                    # Core library
│   ├── api.py              # Public API
│   ├── parser.py           # YAML parser
│   ├── validator.py        # Semantic validation
│   ├── inference_engine.py # AI inference
│   ├── web_interface.py    # Web platform
│   └── plugins/            # Plugin system
├── applications/           # Demo applications
├── docs/                   # Documentation source
├── examples/               # Example workflows
├── tests/                  # Test suite
└── integrations/           # External integrations
```

## 🔒 Security & Quality

- ✅ **Comprehensive Testing** - Full test suite with 24+ passing tests
- 🔒 **Security Scanning** - Automated security analysis with Bandit
- 🧙 **Code Quality** - Enforced with Ruff, Black, and MyPy
- 🔄 **Continuous Integration** - Automated testing on multiple Python versions
- 📄 **Documentation** - Comprehensive docs with examples and tutorials

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

```bash
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

```bibtex
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
