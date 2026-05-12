# Creating Plugins for GeneForgeLang

This guide explains how to create custom plugins for GeneForgeLang using the cookiecutter template.

## Overview

GeneForgeLang plugins extend the platform's functionality by integrating external tools and services. Plugins can be generators, optimizers, or general-purpose tools that process data within GFL workflows.

## Prerequisites

- Python 3.9 or higher
- GeneForgeLang installed
- Basic understanding of Python programming
- Familiarity with the GFL plugin architecture

## Using the Cookiecutter Template

The easiest way to create a new plugin is to use the official cookiecutter template:

```bash
# Install cookiecutter if you haven't already
pip install cookiecutter

# Create a new plugin using the template
cookiecutter https://github.com/Fundacion-de-Neurociencias/cookiecutter-gfl-plugin.git
```

The template will prompt you for information about your plugin:

- Plugin name
- Plugin description
- Plugin type (generator, optimizer, or general)
- Author information
- Python version requirements

## Plugin Structure

A typical GFL plugin has the following structure:

```
my-gfl-plugin/
├── pyproject.toml           # Project configuration
├── README.md               # Plugin documentation
├── my_plugin/              # Plugin source code
│   ├── __init__.py         # Package initialization
│   ├── plugin.py           # Main plugin implementation
│   └── utils.py            # Utility functions
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_plugin.py      # Plugin tests
│   └── fixtures/           # Test data
└── examples/               # Example workflows
    └── example.gfl         # Example GFL workflow
```

## Plugin Types

### Generator Plugins

Generator plugins create new biological entities such as proteins, DNA sequences, or molecules.

```python
from gfl.plugins import GeneratorPlugin, DesignCandidate
from typing import List, Dict, Any

class MyGenerator(GeneratorPlugin):
    @property
    def name(self) -> str:
        return "my-generator"

    @property
    def version(self) -> str:
        return "1.0.0"

    def generate(
        self,
        entity: str,
        objective: Dict[str, Any],
        constraints: List[str],
        count: int,
        **kwargs
    ) -> List[DesignCandidate]:
        # Implementation here
        pass
```

### Optimizer Plugins

Optimizer plugins perform intelligent parameter space exploration and optimization.

```python
from gfl.plugins import OptimizerPlugin, OptimizationStep
from typing import List, Dict, Any

class MyOptimizer(OptimizerPlugin):
    @property
    def name(self) -> str:
        return "my-optimizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    def setup(
        self,
        search_space: Dict[str, str],
        strategy: Dict[str, Any],
        objective: Dict[str, Any],
        budget: Dict[str, Any]
    ) -> None:
        # Implementation here
        pass

    def suggest_next(self, experiment_history: List[Any]) -> OptimizationStep:
        # Implementation here
        pass
```

### General Plugins

General plugins can perform any operation within a GFL workflow.

```python
from gfl.plugins import Plugin
from typing import Dict, Any

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def run(self, input_data: Any, params: Dict[str, Any]) -> Any:
        # Implementation here
        pass
```

## Entry Points

To make your plugin discoverable by GFL, you need to register it as an entry point in your `pyproject.toml`:

```toml
[project.entry-points."gfl.plugins"]
my-plugin = "my_plugin.plugin:MyPlugin"
```

## Configuration

Plugins can accept configuration parameters:

```python
class MyPlugin(Plugin):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.config = config or {}
        self.some_parameter = self.config.get("some_parameter", "default_value")
```

## Testing Your Plugin

Write comprehensive tests for your plugin:

```python
import pytest
from my_plugin.plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    assert plugin.name == "my-plugin"
    assert plugin.version == "1.0.0"

def test_plugin_functionality():
    plugin = MyPlugin()
    result = plugin.run("input_data", {"param": "value"})
    # Add assertions based on expected behavior
```

## Publishing Your Plugin

1. Create a source distribution:
   ```bash
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

3. Users can then install your plugin:
   ```bash
   pip install my-gfl-plugin
   ```

## Best Practices

1. **Error Handling**: Implement proper error handling and validation
2. **Documentation**: Provide clear documentation and examples
3. **Testing**: Write comprehensive tests with good coverage
4. **Performance**: Optimize for performance, especially for computationally intensive operations
5. **Dependencies**: Minimize external dependencies and specify version constraints
6. **Logging**: Use appropriate logging levels for debugging and monitoring

## Example Plugin

Here's a complete example of a simple plugin:

```python
from gfl.plugins import Plugin
from typing import Dict, Any

class SequenceAnalyzer(Plugin):
    @property
    def name(self) -> str:
        return "sequence-analyzer"

    @property
    def version(self) -> str:
        return "1.0.0"

    def run(self, input_data: str, params: Dict[str, Any]) -> Dict[str, Any]:
        sequence = input_data
        analysis = {
            "length": len(sequence),
            "gc_content": self._calculate_gc_content(sequence),
            "is_valid_dna": self._validate_dna(sequence)
        }
        return {"analysis": analysis}

    def _calculate_gc_content(self, sequence: str) -> float:
        gc_count = sequence.upper().count('G') + sequence.upper().count('C')
        return (gc_count / len(sequence)) * 100 if sequence else 0

    def _validate_dna(self, sequence: str) -> bool:
        valid_bases = set('ACGTN')
        return all(base in valid_bases for base in sequence.upper())
```

## Getting Help

If you need help creating plugins:

1. Check the [Plugin Ecosystem Documentation](../ecosystem/plugins_overview.md)
2. Review existing plugins in the repository
3. Join the community discussions
4. Open an issue on GitHub for specific questions
