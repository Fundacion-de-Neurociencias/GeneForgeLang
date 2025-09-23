# Installation Guide

This document provides comprehensive instructions for installing GeneForgeLang and its plugin ecosystem.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for development installations)

## Installation Options

### Option 1: Install GeneForgeLang Core

To install the core GeneForgeLang package:

```bash
pip install geneforgelang
```

### Option 2: Install with Core Plugins

To install GeneForgeLang with all core plugins:

```bash
pip install geneforgelang[all]
```

### Option 3: Install Individual Plugins

Install specific plugins as needed:

```bash
# Install core plugins
pip install gfl-plugin-blast
pip install gfl-plugin-gatk
pip install gfl-plugin-samtools
pip install gfl-plugin-biopython-tools

# Install Genesis plugins
pip install gfl-plugin-ontarget-scorer
pip install gfl-plugin-offtarget-scorer
pip install gfl-plugin-crispr-evaluator
pip install gfl-plugin-crispr-visualizer
```

### Option 4: Install from Local Development Versions

For development work with local versions:

```bash
# Clone the main repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Install in development mode
pip install -e .

# Install plugins in development mode
pip install -e gfl-plugin-blast/
pip install -e gfl-plugin-gatk/
pip install -e gfl-plugin-samtools/
pip install -e gfl-plugin-biopython-tools/
```

## Plugin Dependencies

Each plugin has specific dependencies:

### Core Plugins

#### gfl-plugin-blast
- Biopython >= 1.80

#### gfl-plugin-gatk
- gatk >= 4.0.0 (external dependency)

#### gfl-plugin-samtools
- pysam >= 0.15.0

#### gfl-plugin-biopython-tools
- Biopython >= 1.80

### Genesis Plugins

#### gfl-plugin-ontarget-scorer
- numpy >= 1.24.0
- pandas >= 2.0.0
- scikit-learn >= 1.3.0
- tensorflow >= 2.10.0
- biopython >= 1.80

#### gfl-plugin-offtarget-scorer
- numpy >= 1.24.0
- pandas >= 2.0.0
- biopython >= 1.80

#### gfl-plugin-crispr-evaluator
- gfl-plugin-ontarget-scorer >= 0.1.0
- gfl-plugin-offtarget-scorer >= 0.1.0
- numpy >= 1.24.0
- pandas >= 2.0.0

#### gfl-plugin-crispr-visualizer
- matplotlib >= 3.7.0
- plotly >= 5.15.0
- pandas >= 2.0.0
- numpy >= 1.24.0

## Development Setup

### Setting Up for Development

To set up the complete development environment:

```bash
# Clone the main repository
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

# Create a virtual environment
python -m venv gfl_env
source gfl_env/bin/activate  # On Windows: gfl_env\Scripts\activate

# Install the package in development mode
pip install -e ".[dev]"

# Install all plugins in development mode
pip install -e gfl-plugin-blast/
pip install -e gfl-plugin-gatk/
pip install -e gfl-plugin-samtools/
pip install -e gfl-plugin-biopython-tools/
```

### Running Tests

Each component includes tests that can be run with pytest:

```bash
# Run tests for the core package
pytest

# Run tests for each plugin
cd gfl-plugin-blast
pytest

cd ../gfl-plugin-gatk
pytest

cd ../gfl-plugin-samtools
pytest

cd ../gfl-plugin-biopython-tools
pytest
```

### Code Formatting

All components use black and ruff for code formatting:

```bash
# Format code for the core package
black src/
ruff check src/

# Format code for each plugin
cd gfl-plugin-blast
black gfl_plugin_blast/
ruff check gfl_plugin_blast/

cd ../gfl-plugin-gatk
black gfl_plugin_gatk/
ruff check gfl_plugin_gatk/

cd ../gfl-plugin-samtools
black gfl_plugin_samtools/
ruff check gfl_plugin_samtools/

cd ../gfl-plugin-biopython-tools
black gfl_plugin_biopython_tools/
ruff check gfl_plugin_biopython_tools/
```

## Integration with GFL

Plugins are designed to be used within the GFL workflow system. In a `.gfl` workflow file, you can reference them as tools:

```gfl
tool: "blast" {
  // Tool configuration
}

tool: "gatk" {
  // Tool configuration
}

tool: "samtools" {
  // Tool configuration
}

tool: "biopython-tools" {
  // Tool configuration
}

tool: "gfl-ontarget-scorer" {
  // Tool configuration
}

tool: "gfl-offtarget-scorer" {
  // Tool configuration
}

tool: "gfl-crispr-evaluator" {
  // Tool configuration
}

tool: "gfl-crispr-visualizer" {
  // Tool configuration
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all plugins are installed in the same Python environment
2. **Dependency Conflicts**: Use virtual environments to avoid conflicts
3. **Version Mismatches**: Ensure compatible versions of all components are installed
4. **External Tool Dependencies**: Some plugins require external tools (like GATK) to be installed separately

### Creating a Virtual Environment

```bash
# Create a virtual environment
python -m venv gfl_env

# Activate the virtual environment
# On Windows:
gfl_env\Scripts\activate
# On macOS/Linux:
source gfl_env/bin/activate

# Install GeneForgeLang and plugins
pip install geneforgelang[all]
```

### Verifying Installation

To verify that all components are installed correctly:

```bash
# Check GeneForgeLang installation
python -c "import geneforgelang; print(geneforgelang.__version__)"

# Check plugin installations
python -c "import gfl_plugin_blast; print('BLAST plugin installed')"
python -c "import gfl_plugin_gatk; print('GATK plugin installed')"
python -c "import gfl_plugin_samtools; print('SAMtools plugin installed')"
python -c "import gfl_plugin_biopython_tools; print('Biopython tools plugin installed')"
```

## Next Steps

After installation, proceed to the [User Quickstart Guide](quickstart_user.md) to learn how to create your first GFL workflow.