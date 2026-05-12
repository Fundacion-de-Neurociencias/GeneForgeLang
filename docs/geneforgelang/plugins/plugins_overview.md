# Plugin Ecosystem Overview

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

## Plugin Categories

The GFL plugin ecosystem is organized into two main categories:

### Core Plugins
These are essential plugins that provide fundamental bioinformatics capabilities:
- **BLAST**: Sequence alignment searches
- **GATK**: Genomic analysis toolkit
- **SAMtools**: Sequence alignment manipulation
- **Biopython Tools**: Bioinformatics utilities

### Genesis Plugins
These specialized plugins focus on CRISPR gene editing workflows:
- **On-Target Scorer**: Predicts CRISPR cutting efficiency
- **Off-Target Scorer**: Identifies potential off-target sites
- **CRISPR Evaluator**: Combines and ranks gRNA candidates
- **CRISPR Visualizer**: Generates visualizations of results

## Getting Started

### Installing Plugins

Plugins can be installed via pip if they're packaged properly:

```bash
# Install individual plugins
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

## Genesis Plugin Suite

The Genesis plugin suite provides a complete CRISPR evaluation pipeline:

### 1. gfl-plugin-ontarget-scorer

**Purpose**: Predicts the efficiency of CRISPR-Cas9 cutting at the intended target site.

**Key Features**:
- Takes a gRNA sequence and surrounding genomic sequence as input
- Uses pre-trained machine learning models (DeepCRISPR/DeepHF) to calculate efficiency
- Returns a score between 0 and 1 (higher is better)

### 2. gfl-plugin-offtarget-scorer

**Purpose**: Identifies potential off-target cutting sites and calculates a global risk score.

**Key Features**:
- Takes a gRNA sequence as input
- Uses BLAST-like search against reference genome (e.g., GRCh38)
- Calculates risk scores using the CFD algorithm
- Returns aggregated global risk score (lower is better)

### 3. gfl-plugin-crispr-evaluator

**Purpose**: Orchestrator that combines on-target and off-target scores into a final ranking.

**Key Features**:
- Takes a list of gRNA candidates as input
- Internally invokes the other two plugins for each candidate
- Combines scores using weighted formula: `combined_score = on_target_score - (w * off_target_risk)`
- Returns ranked table of gRNAs with all three scores

### 4. gfl-plugin-crispr-visualizer

**Purpose**: Generates visualizations of CRISPR evaluation results.

**Key Features**:
- Takes evaluation results from the evaluator plugin
- Produces charts and graphs in various formats (HTML, PNG, SVG)
- Supports different chart types (bar, scatter)
- Helps researchers quickly identify the best gRNA candidates

## Workflow Integration

These plugins work together to provide a complete CRISPR evaluation pipeline:

1. **Input**: List of gRNA candidates
2. **Evaluation**: On-target and off-target plugins calculate individual scores
3. **Combination**: CRISPR evaluator combines scores into final ranking
4. **Visualization**: CRISPR visualizer generates visual representations of results

## Next Steps

- Explore detailed documentation for [Core Plugins](core_plugins/)
- Learn about [Genesis Plugins](genesis_plugins/)
- Read the [Plugin Development Guide](../development/creating_plugins.md) to create your own plugins
