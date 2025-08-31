# Plugin Ecosystem Documentation

## Overview

GeneForgeLang's plugin ecosystem provides a sophisticated framework for integrating external AI/ML tools and experimental systems with GFL workflows. The plugin system standardizes how the GFL execution engine interacts with specialized tools for biological entity generation and experimental optimization.

## Architecture

### Core Components

1. **Plugin Interfaces**: Abstract base classes defining contracts for plugin types
2. **Plugin Registry**: Discovery, lifecycle, and dependency management system
3. **Execution Engine**: Orchestrates plugin invocation during workflow execution
4. **Example Implementations**: Reference plugins demonstrating best practices

### Plugin Types

#### GeneratorPlugin
- **Purpose**: Create new biological entities (proteins, DNA, RNA, molecules)
- **Use Case**: Powers GFL `design` blocks
- **Interface**: `gfl.plugins.GeneratorPlugin`
- **Methods**: `generate()`, `validate_objective()`, `validate_constraints()`

#### OptimizerPlugin
- **Purpose**: Intelligent parameter space exploration and optimization
- **Use Case**: Powers GFL `optimize` blocks
- **Interface**: `gfl.plugins.OptimizerPlugin`
- **Methods**: `setup()`, `suggest_next()`, `should_stop()`

#### PriorsPlugin
- **Purpose**: Bayesian prior integration for enhanced experimental design
- **Use Case**: Powers GFL `with_priors` clauses
- **Interface**: `gfl.plugins.PriorsPlugin`
- **Methods**: `specify_priors()`, `update_posteriors()`

## Getting Started

### Installing Plugins

Plugins can be installed via pip if they're packaged properly:

```bash
pip install geneforge-protein-vae-plugin
pip install geneforge-bayesian-optimizer
```

### Registering Plugins

#### Entry Point Registration (Recommended)

Add to your plugin package's `pyproject.toml`:

```toml
[project.entry-points."gfl.plugins"]
protein_vae = "my_package.plugins:ProteinVAEGenerator"
bayesian_opt = "my_package.plugins:BayesianOptimizer"
```

#### Manual Registration

```python
from gfl.plugins import register_generator_plugin, register_optimizer_plugin
from my_package.plugins import MyGenerator, MyOptimizer

register_generator_plugin(MyGenerator, "my_generator", version="1.0.0")
register_optimizer_plugin(MyOptimizer, "my_optimizer", version="1.0.0")
```

### Using Plugins in GFL

Once registered, plugins can be referenced directly in GFL workflows:

```yaml
design:
  entity: ProteinSequence
  model: MyGeneratorPlugin  # Plugin name
  objective:
    maximize: stability
  count: 10
  output: designed_proteins

optimize:
  search_space:
    temperature: range(25, 42)
    concentration: range(10, 100)
  strategy:
    name: MyOptimizerStrategy  # Strategy provided by plugin
  objective:
    maximize: efficiency
  budget:
    max_experiments: 50
  run:
    experiment:
      # Your experimental setup here
```

## Developing Plugins

### Generator Plugin Example

```python
from gfl.plugins import GeneratorPlugin, EntityType, DesignCandidate
from typing import List, Dict, Any

class MyProteinGenerator(GeneratorPlugin):
    @property
    def name(self) -> str:
        return "MyProteinGenerator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_entities(self) -> List[EntityType]:
        return [EntityType.PROTEIN_SEQUENCE]

    def generate(
        self,
        entity: str,
        objective: Dict[str, Any],
        constraints: List[str],
        count: int,
        **kwargs
    ) -> List[DesignCandidate]:
        # Your generation logic here
        candidates = []
        for i in range(count):
            sequence = self._generate_protein_sequence(objective, constraints)
            properties = self._predict_properties(sequence)
            confidence = self._calculate_confidence(sequence, properties)

            candidates.append(DesignCandidate(
                sequence=sequence,
                properties=properties,
                confidence=confidence,
                metadata={"method": "my_algorithm", "iteration": i}
            ))

        return candidates

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"plugin_type": "generator", "status": "processed"}
```

### Optimizer Plugin Example

```python
from gfl.plugins import OptimizerPlugin, OptimizationStrategy, OptimizationStep, ExperimentResult
from typing import List, Dict, Any

class MyBayesianOptimizer(OptimizerPlugin):
    @property
    def name(self) -> str:
        return "MyBayesianOptimizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_strategies(self) -> List[OptimizationStrategy]:
        return [OptimizationStrategy.BAYESIAN_OPTIMIZATION]

    def setup(
        self,
        search_space: Dict[str, str],
        strategy: Dict[str, Any],
        objective: Dict[str, Any],
        budget: Dict[str, Any]
    ) -> None:
        # Initialize your optimization algorithm
        self.search_space = search_space
        self.strategy_config = strategy
        self.objective_config = objective
        self.budget_config = budget
        # Set up Gaussian Process, acquisition function, etc.

    def suggest_next(self, experiment_history: List[ExperimentResult]) -> OptimizationStep:
        # Your optimization algorithm logic
        if len(experiment_history) < 3:
            # Random sampling for initial points
            parameters = self._sample_random_parameters()
        else:
            # Use GP + acquisition function for intelligent selection
            parameters = self._optimize_acquisition_function(experiment_history)

        return OptimizationStep(
            parameters=parameters,
            iteration=len(experiment_history) + 1,
            expected_improvement=self._calculate_expected_improvement(parameters),
            uncertainty=self._estimate_uncertainty(parameters)
        )

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"plugin_type": "optimizer", "status": "processed"}
```

## Advanced Features

### Dependency Management

Plugins can declare dependencies on external packages:

```python
from gfl.plugins import PluginDependency

class MyMLPlugin(GeneratorPlugin):
    @property
    def dependencies(self) -> List[PluginDependency]:
        return [
            PluginDependency("torch", ">=1.9.0", optional=False),
            PluginDependency("transformers", ">=4.0.0", optional=False),
            PluginDependency("rdkit", ">=2020.09.0", optional=True)
        ]
```

### Plugin Lifecycle Hooks

```python
class MyPlugin(GeneratorPlugin):
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print("Initializing ML model...")
        self.model = self._load_pretrained_model()

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print("Cleaning up resources...")
        if hasattr(self, 'model'):
            del self.model

    def on_activate(self) -> None:
        """Called when plugin becomes active."""
        print("Plugin activated")

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        print("Plugin deactivated")
```

### Configuration Validation

```python
class MyPlugin(GeneratorPlugin):
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration."""
        errors = []

        if "model_path" not in config:
            errors.append("Missing required 'model_path' configuration")

        if "temperature" in config:
            temp = config["temperature"]
            if not isinstance(temp, (int, float)) or temp <= 0:
                errors.append("Temperature must be a positive number")

        return errors
```

## Plugin Discovery

The plugin system supports multiple discovery mechanisms:

### 1. Entry Points (Recommended)
Plugins are automatically discovered via entry points when packages are installed.

### 2. Manual Registration
Direct registration for development or special cases.

### 3. Directory Scanning
Scan specific directories for plugin files (advanced usage).

## Testing Plugins

### Unit Testing

```python
import pytest
from gfl.plugins.interfaces import DesignCandidate, EntityType
from my_package.plugins import MyProteinGenerator

class TestMyProteinGenerator:
    def test_generation(self):
        generator = MyProteinGenerator()

        candidates = generator.generate(
            entity="ProteinSequence",
            objective={"maximize": "stability"},
            constraints=["length(50, 100)"],
            count=5
        )

        assert len(candidates) == 5
        assert all(isinstance(c, DesignCandidate) for c in candidates)
        assert all(50 <= len(c.sequence) <= 100 for c in candidates)

    def test_entity_support(self):
        generator = MyProteinGenerator()
        assert EntityType.PROTEIN_SEQUENCE in generator.supported_entities
```

### Integration Testing

```python
def test_gfl_integration():
    from gfl.api import parse, validate, execute

    # Register plugin
    register_generator_plugin(MyProteinGenerator, "my_generator")

    # Test GFL execution
    gfl_script = '''
    design:
      entity: ProteinSequence
      model: my_generator
      objective:
        maximize: stability
      count: 3
      output: proteins
    '''

    ast = parse(gfl_script)
    errors = validate(ast)
    assert not errors

    result = execute(ast)
    assert len(result['design']['candidates']) == 3
```

## Best Practices

### 1. Error Handling

```python
def generate(self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs) -> List[DesignCandidate]:
    try:
        # Validate inputs
        if entity not in [e.value for e in self.supported_entities]:
            raise ValueError(f"Unsupported entity type: {entity}")

        if count <= 0:
            raise ValueError("Count must be positive")

        # Generation logic
        return self._perform_generation(entity, objective, constraints, count)

    except Exception as e:
        # Log error and re-raise with context
        logger.error(f"Generation failed in {self.name}: {e}")
        raise RuntimeError(f"Plugin {self.name} generation failed: {e}")
```

### 2. Resource Management

```python
class MyPlugin(GeneratorPlugin):
    def __init__(self):
        super().__init__()
        self._model = None
        self._device = None

    def _ensure_model_loaded(self):
        """Lazy loading of expensive resources."""
        if self._model is None:
            self._model = self._load_model()
            self._device = self._get_best_device()

    def generate(self, ...):
        self._ensure_model_loaded()
        # Use self._model for generation
```

### 3. Caching and Performance

```python
from functools import lru_cache

class MyPlugin(GeneratorPlugin):
    @lru_cache(maxsize=1000)
    def _predict_properties(self, sequence: str) -> Dict[str, float]:
        """Cache expensive property predictions."""
        return self._compute_properties(sequence)
```

### 4. Logging and Monitoring

```python
import logging

logger = logging.getLogger(__name__)

class MyPlugin(GeneratorPlugin):
    def generate(self, ...):
        logger.info(f"Starting generation: {count} {entity} candidates")
        start_time = time.time()

        try:
            candidates = self._perform_generation(...)
            duration = time.time() - start_time

            logger.info(f"Generated {len(candidates)} candidates in {duration:.2f}s")
            return candidates

        except Exception as e:
            logger.error(f"Generation failed after {time.time() - start_time:.2f}s: {e}")
            raise
```

## Deployment

### Packaging Plugins

Create a proper Python package structure:

```
my-geneforge-plugin/
├── pyproject.toml
├── README.md
├── my_gfl_plugin/
│   ├── __init__.py
│   ├── generators.py
│   ├── optimizers.py
│   └── models/
└── tests/
    ├── test_generators.py
    └── test_optimizers.py
```

Example `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-geneforge-plugin"
version = "1.0.0"
description = "Custom GFL plugins for my research"
dependencies = [
    "geneforgeLang>=0.1.0",
    "torch>=1.9.0",
    "transformers>=4.0.0"
]

[project.entry-points."gfl.plugins"]
my_protein_generator = "my_gfl_plugin.generators:MyProteinGenerator"
my_molecule_generator = "my_gfl_plugin.generators:MyMoleculeGenerator"
my_bayesian_optimizer = "my_gfl_plugin.optimizers:MyBayesianOptimizer"
```

### Distribution

Publish to PyPI for easy installation:

```bash
pip install build twine
python -m build
twine upload dist/*
```

Users can then install with:

```bash
pip install my-geneforge-plugin
```

## Troubleshooting

### Common Issues

#### 1. Plugin Not Found
- Check entry point configuration in `pyproject.toml`
- Verify plugin is installed: `pip list | grep geneforge`
- Check plugin discovery logs: Enable debug logging

#### 2. Import Errors
- Verify all dependencies are installed
- Check Python version compatibility
- Ensure plugin package is in Python path

#### 3. Validation Failures
- Implement all required abstract methods
- Check method signatures match interface
- Validate return types and data structures

#### 4. Performance Issues
- Use lazy loading for expensive resources
- Implement caching for repeated computations
- Profile your plugin code for bottlenecks

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or specifically for plugins
logging.getLogger('gfl.plugins').setLevel(logging.DEBUG)
```

Check plugin status:

```python
from gfl.api import list_available_plugins, get_api_info

# List all registered plugins
plugins = list_available_plugins()
print("Generators:", plugins['generators'])
print("Optimizers:", plugins['optimizers'])

# Check API capabilities
info = get_api_info()
print("Plugin system enabled:", info['features']['plugin_system'])
```

## Examples Repository

For complete working examples, see:
- `gfl/plugins/example_implementations.py` - Reference implementations
- `tests/test_plugin_interfaces.py` - Comprehensive test suite
- `docs/examples/` - Real-world plugin examples

## Community

### Contributing Plugins

We welcome community contributions! To submit your plugin:

1. Follow the plugin development guidelines
2. Include comprehensive tests
3. Add documentation and examples
4. Submit a PR or publish to PyPI with proper metadata

### Plugin Registry

Maintain a community registry at: https://github.com/GeneForgeLang/plugins

### Support

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share plugins
- Documentation: Submit improvements and examples

---

*The GeneForgeLang plugin ecosystem enables the seamless integration of cutting-edge AI/ML tools with genomic workflows, democratizing access to advanced computational biology capabilities.*
