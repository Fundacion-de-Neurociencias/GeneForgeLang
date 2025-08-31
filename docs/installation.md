# Installation Guide

This guide will help you install and set up GeneForgeLang on your system.

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM
- **Storage**: 2GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.11 or higher
- **Memory**: 8GB RAM
- **Storage**: 10GB free space (for ML models)
- **GPU**: CUDA-compatible (optional, for advanced ML features)

## Installation Methods

### 1. Quick Installation (Recommended)

```bash
# Install from source (development version)
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang
pip install -e .
```

### 2. Full Installation with All Features

```bash
# Clone repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Install with all optional dependencies
pip install -e .[full]
```

### 3. Minimal Installation

```bash
# Basic functionality only
pip install -e .
```

### 4. Feature-Specific Installation

```bash
# Web interface and API server
pip install -e .[server,apps]

# Machine learning features
pip install -e .[ml]

# Grammar-based parser
pip install -e .[lexer]

# Development tools
pip install -e .[dev]
```

## Dependency Groups

| Group | Description | Use Case |
|-------|-------------|----------|
| `basic` | Core GFL functionality | Basic parsing and validation |
| `server` | API server components | REST API, rate limiting |
| `apps` | Web applications | Gradio interface, demos |
| `ml` | Machine learning | PyTorch, Transformers |
| `lexer` | Advanced parsing | PLY-based grammar parser |
| `dev` | Development tools | Testing, linting, formatting |
| `full` | Everything included | Complete installation |

## Verification

After installation, verify everything works:

```bash
# Test basic functionality
python -c "from gfl.api import parse, validate; print('✓ GFL API working')"

# Test CLI tools
gfl-server --help

# Run platform test suite
python test_platform.py
```

Expected output:
```
GeneForgeLang Platform Test Suite
==================================================
Testing basic GFL API...
✓ API Version: 0.1.0
✓ Available models: ['heuristic', 'enhanced_heuristic']
✓ Parsing successful: CRISPR_cas9
✓ Validation: Valid
...
Test Results: 3/4 passed
🎉 All tests passed! Platform is working correctly.
```

## Starting the Platform

### Web Interface + API Server
```bash
# Start complete platform
gfl-server --all

# Access interfaces:
# Web: http://127.0.0.1:7860
# API: http://127.0.0.1:8000/docs
```

### API Server Only
```bash
gfl-server --api-only
```

### Web Interface Only
```bash
gfl-server --web-only
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Error: No module named 'gfl'
# Solution: Install in editable mode
pip install -e .
```

#### Missing Dependencies
```bash
# Error: ModuleNotFoundError: No module named 'fastapi'
# Solution: Install server dependencies
pip install -e .[server]
```

#### Permission Issues (Windows)
```bash
# Run as administrator or use:
pip install -e . --user
```

#### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv gfl-env

# Activate (Windows)
gfl-env\Scripts\activate

# Activate (macOS/Linux)
source gfl-env/bin/activate

# Install
pip install -e .[full]
```

### Getting Help

If you encounter issues:

1. **Check Dependencies**: Run `gfl-server --check-deps`
2. **Review Logs**: Check console output for error messages
3. **Update Dependencies**: `pip install --upgrade -e .[full]`
4. **Report Issues**: [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues)

## Next Steps

Once installed successfully:

1. **[Getting Started Tutorial](tutorial.md)** - Create your first GFL workflow
2. **[CLI Guide](cli.md)** - Learn command-line tools
3. **[Web Interface Guide](web-interface/getting-started.md)** - Use the web platform
4. **[API Documentation](API_REFERENCE.md)** - Integrate with your applications

## Development Installation

For contributors and developers:

```bash
# Clone with development tools
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

See [Contributing Guide](../CONTRIBUTING.md) for detailed development setup.
