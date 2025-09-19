# Experiment Orchestration with the `optimize` Block

## Introduction

The `optimize` block represents one of the most significant advances in GeneForgeLang, transforming the language from a simple specification tool to a complete **scientific discovery orchestration** platform. This block automates the exploration of parameter spaces to find optimal experimental conditions, inspired by 'AI-driven experimentation' techniques that are revolutionizing genomic research.

Instead of running experiments sequentially with fixed parameters, the `optimize` block allows defining **intelligent experimental loops** that:

- **Learn** from each executed experiment
- **Adapt** parameter selection based on previous results
- **Converge** toward optimal experimental conditions efficiently
- **Minimize** the number of experiments needed to find solutions

This approach is especially valuable in genomics, where experiments can be costly, slow, and where the parameter space is typically very large and complex.

## Block Structure

The `optimize` block consists of five main components that fully define an experimental optimization loop:

### `search_space` - Search Space

Defines the parameters to be explored and their possible value ranges. Each parameter can be:

- **Continuous**: Using the syntax `range(min, max)` for numerical values
- **Discrete**: Using the syntax `choice([value1, value2, ...])` for specific options

**Syntax:**
```yaml
search_space:
  parameter_name: range(min_value, max_value)
  another_parameter: choice([option1, option2, option3])
```

**Examples:**
```yaml
search_space:
  temperature: range(25, 42)              # Temperature in °C
  guide_concentration: range(10, 100)      # Concentration in nM
  incubation_time: choice([6, 12, 24, 48])  # Hours of incubation
  buffer_type: choice([PBS, HEPES, Tris])     # Buffer types
```

### `strategy` - Optimization Strategy

Specifies the artificial intelligence algorithm that will be used to guide the exploration of the parameter space. The `name` field is mandatory and identifies the optimization plugin to use.

**Supported Algorithms:**

- **`ActiveLearning`**: Selects experiments that maximize information gained
- **`BayesianOptimization`**: Uses Gaussian processes to model the parameter space
- **`GeneticAlgorithm`**: Evolves populations of experimental configurations
- **`SimulatedAnnealing`**: Stochastic exploration with gradual cooling
- **`RandomSearch`**: Random selection (baseline)
- **`GridSearch`**: Systematic exhaustive exploration

**Syntax:**
```yaml
strategy:
  name: AlgorithmName
  specific_parameter: value
  another_parameter: value
```

**Examples:**
```yaml
# Active learning with uncertainty metric
strategy:
  name: ActiveLearning
  uncertainty_metric: entropy
  initial_samples: 5

# Bayesian optimization with specific acquisition function
strategy:
  name: BayesianOptimization
  acquisition_function: expected_improvement
  kernel: rbf
```

### `objective` - Optimization Objective

Defines which metric to optimize. It must contain exactly one of the following keys:

- **`maximize`**: To maximize a metric (e.g.: efficiency, performance)
- **`minimize`**: To minimize a metric (e.g.: cost, time, toxicity)

Optionally, it can include a `target` field that specifies the objective context.

**Syntax:**
```yaml
objective:
  maximize: metric_name
  # Or alternatively:
  minimize: metric_name
  target: optional_context
```

**Examples:**
```yaml
# Maximize editing efficiency
objective:
  maximize: editing_efficiency

# Minimize off-target effects
objective:
  minimize: off_target_effects
  target: complete_genome

# Maximize gene expression
objective:
  maximize: expression_level
  target: GFP_protein
```

### `budget` - Budget and Stopping Criteria

Establishes constraints and stopping criteria for the optimization loop. It must contain at least one constraint.

**Available Constraints:**

- **`max_experiments`**: Maximum number of experiments (integer)
- **`max_time`**: Maximum time (format: "24h", "7d", "30m")
- **`max_cost`**: Maximum budget (number)
- **`convergence_threshold`**: Convergence threshold (0.0 - 1.0)

**Syntax:**
```yaml
budget:
  max_experiments: number
  max_time: "time_with_unit"
  max_cost: amount
  convergence_threshold: threshold
```

**Examples:**
```yaml
# Multiple limits
budget:
  max_experiments: 100
  max_time: 72h
  max_cost: 15000
  convergence_threshold: 0.01

# Only experiment limit
budget:
  max_experiments: 50
```

### `run` - Execution Block

Defines the experiment or analysis that will be executed in each iteration of the optimization loop. It must contain exactly one of:

- **`experiment`**: A standard GFL experiment block
- **`analyze`**: A standard GFL analysis block

Parameters defined in `search_space` can be injected using the syntax `${parameter_name}`.

**Syntax:**
```yaml
run:
  experiment:
    tool: tool
    type: type
    params:
      parameter1: ${search_space_parameter}
      parameter2: fixed_value

# Or alternatively:
run:
  analyze:
    strategy: strategy
    data: data
    thresholds:
      threshold: ${search_space_parameter}
```

## Complete Example

The following is a complete example of parameter optimization for a PCR reaction:

```yaml
metadata:
  experiment_id: PCR_OPTIM_001
  researcher: Dr. María González
  project: pcr_optimization
  description: Optimization of PCR conditions to maximize specificity

optimize:
  # Define parameters to explore
  search_space:
    annealing_temperature: range(55, 72)      # Annealing temperature (°C)
    primer_concentration: range(0.1, 1.0)    # Primer concentration (μM)
    extension_time: choice([30, 45, 60])     # Extension time (seconds)
    mgcl2_concentration: range(1.5, 4.0)      # MgCl2 concentration (mM)

  # Optimization strategy with active learning
  strategy:
    name: ActiveLearning
    uncertainty_metric: entropy
    initial_samples: 8
    batch_size: 4

  # Objective: maximize PCR specificity
  objective:
    maximize: specificity_score

  # Budget constraints
  budget:
    max_experiments: 32
    max_time: 48h
    convergence_threshold: 0.005

  # Run PCR experiment in each iteration
  run:
    experiment:
      tool: PCR_amplifier
      type: thermal_cycling
      params:
        annealing_temp: ${annealing_temperature}
        primer_conc: ${primer_concentration}
        extension_time: ${extension_time}
        mgcl2_conc: ${mgcl2_concentration}
      output: pcr_results

  # Store optimized parameters
  output: optimized_pcr_conditions
```

## Advanced Features

### Multi-Fidelity Optimization

For complex optimization tasks with different fidelity levels:

```yaml
optimize:
  search_space:
    temperature: range(25, 42)
    concentration: range(10, 100)

  strategy:
    name: BayesianOptimization
    fidelity_levels: [low, medium, high]
    fidelity_switching: adaptive

  objective:
    maximize: efficiency_score

  budget:
    max_experiments: 50
    max_time: 24h

  run:
    experiment:
      tool: CRISPR_editor
      fidelity: ${current_fidelity}
      params:
        temp: ${temperature}
        conc: ${concentration}
```

### Multi-Objective Optimization

For scenarios with competing objectives:

```yaml
optimize:
  search_space:
    temperature: range(25, 42)
    concentration: range(10, 100)

  strategy:
    name: MultiObjectiveBayesian
    pareto_front: true

  objective:
    maximize:
      - efficiency
      - specificity
    minimize:
      - cost
      - time

  budget:
    max_experiments: 100

  run:
    experiment:
      tool: GeneEditor
      params:
        temp: ${temperature}
        conc: ${concentration}
```

## Integration with Other Blocks

The `optimize` block seamlessly integrates with other GFL workflow components:

- **`design`**: Optimize parameters for generative design processes
- **`analyze`**: Optimize analysis parameters based on results
- **`refine`**: Improve candidate quality through iterative optimization
- **`simulate`**: Optimize simulation parameters for accuracy

This integration enables sophisticated workflows that combine experimental optimization with generative design and analysis.

## Performance Considerations

When using the `optimize` block, consider:

1. **Computational Resources**: Optimization algorithms may require significant computing power
2. **Strategy Selection**: Choose algorithms appropriate for your specific optimization task
3. **Budget Constraints**: Define realistic constraints for time and resources
4. **Convergence Monitoring**: Track optimization progress to ensure effectiveness
5. **Result Validation**: Always validate optimized parameters experimentally

## Best Practices

1. **Start Simple**: Begin with basic optimization tasks and gradually increase complexity
2. **Define Clear Objectives**: Precise objectives lead to better optimization outcomes
3. **Set Realistic Budgets**: Include constraints that reflect experimental reality
4. **Validate Results**: Always experimentally validate optimized parameters
5. **Iterate**: Use optimization results to refine and improve subsequent iterations

The `optimize` block represents a powerful capability for automated experimental design, enabling researchers to harness the power of AI for scientific discovery and innovation.
