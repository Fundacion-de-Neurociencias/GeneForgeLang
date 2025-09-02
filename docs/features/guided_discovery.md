# Guided Discovery Block

The `guided_discovery` block in GeneForgeLang v1.0.0 represents the pinnacle of AI-driven genomic workflow automation. This powerful block combines generative design and active learning optimization in a closed-loop discovery system.

## Overview

The `guided_discovery` block orchestrates iterative cycles of candidate generation and experimental validation, using AI to guide the discovery process toward optimal solutions. It's particularly effective for complex optimization problems in genomics and drug discovery.

## Syntax

```yaml
guided_discovery:
  design_params:
    # Design block configuration
    entity: <entity_type>
    model: <generative_model>
    objective:
      maximize|minimize: <metric>
    count: <integer>
    output: <output_name>
    # ... additional design parameters

  active_learning_params:
    # Optimize block configuration
    search_space:
      <parameter>: <range|choice>
    strategy:
      name: ActiveLearning
      # ... active learning parameters
    objective:
      maximize|minimize: <metric>
    budget:
      # ... budget constraints
    run:
      # ... experiment or analysis block

  budget:
    max_cycles: <integer>
    # ... additional budget constraints

  output: <final_output_name>
```

## Configuration Parameters

### design_params

The `design_params` section defines the generative design configuration, following the same structure as the standalone [design block](design_block.md):

- **entity** (string, required): Type of biological entity to design
- **model** (string, required): Generative model plugin to use
- **objective** (dict, required): Optimization objective
- **count** (integer, required): Number of candidates to generate per cycle
- **output** (string, required): Output variable name for generated candidates

### active_learning_params

The `active_learning_params` section defines the active learning optimization configuration:

- **search_space** (dict, required): Parameters to explore and their ranges
- **strategy** (dict, required): Must be `ActiveLearning` with nested configuration
- **objective** (dict, required): Optimization objective
- **budget** (dict, required): Stopping criteria
- **run** (dict, required): Nested experiment or analyze block to execute

### budget

Defines the overall budget for the guided discovery process:

- **max_cycles** (integer, optional): Maximum number of design-evaluate cycles
- **convergence_threshold** (float, optional): Threshold for early stopping
- **target_objective_value** (float, optional): Target objective value for early stopping

### output

The final output name for the discovered candidates.

## Example Usage

### Protein Sequence Optimization

```yaml
guided_discovery:
  design_params:
    entity: ProteinSequence
    model: ProteinVAEGenerator
    objective:
      maximize: binding_affinity
    count: 20
    output: candidate_proteins
    candidates_per_cycle: 5
    constraints:
      - length(50, 200)
      - stability_score > 0.7

  active_learning_params:
    search_space:
      temperature: range(25, 42)
      ph: range(6.5, 8.0)
    strategy:
      name: ActiveLearning
      surrogate_model: GaussianProcess
      active_learning:
        acquisition_function: ExpectedImprovement
        initial_experiments: 5
        max_uncertainty: 0.1
        convergence_threshold: 0.01
    objective:
      maximize: expression_level
    budget:
      max_experiments: 50
    run:
      experiment:
        tool: protein_expression
        type: validation
        params:
          proteins: candidate_proteins
          temp: ${temperature}
          ph: ${ph}
    experiments_per_cycle: 3

  budget:
    max_cycles: 10
    convergence_threshold: 0.05

  output: optimized_proteins
```

### gRNA Design for CRISPR

```yaml
guided_discovery:
  design_params:
    entity: DNASequence
    model: GuideRNADesigner
    objective:
      maximize: editing_efficiency
    count: 30
    output: candidate_guides
    candidates_per_cycle: 10
    constraints:
      - off_target_score < 0.1
      - gc_content(40, 60)

  active_learning_params:
    search_space:
      mg_concentration: range(5, 20)
      incubation_time: choice([30, 60, 120])
    strategy:
      name: ActiveLearning
      surrogate_model: RandomForestRegressor
      active_learning:
        acquisition_function: UpperConfidenceBound
        initial_experiments: 8
        max_uncertainty: 0.05
        convergence_threshold: 0.02
    objective:
      maximize: cleavage_rate
    budget:
      max_experiments: 40
    run:
      experiment:
        tool: CRISPR_cas9
        type: gene_editing
        params:
          guides: candidate_guides
          mg_conc: ${mg_concentration}
          incubation: ${incubation_time}
    experiments_per_cycle: 4

  budget:
    max_cycles: 8
    target_objective_value: 0.95

  output: optimal_guides
```

## Workflow Process

The `guided_discovery` block executes the following iterative process:

1. **Candidate Generation**: AI model generates candidate solutions
2. **Experimental Evaluation**: Active learning evaluates candidates
3. **Model Update**: Surrogate model is updated with new data
4. **Next Generation**: AI model generates improved candidates
5. **Convergence Check**: Process continues until budget or convergence criteria are met

## Integration with Other Features

### IO Contracts

```yaml
guided_discovery:
  design_params:
    entity: ProteinSequence
    model: ProteinVAEGenerator
    objective:
      maximize: stability
    count: 15
    output: candidate_proteins
    contract:  # Design contract
      outputs:
        candidates:
          type: FASTA
          attributes:
            sequence_type: protein
  # ... rest of configuration
```

### Schema Registry

```yaml
import_schemas:
  - ./schemas/protein_schemas.yml

guided_discovery:
  design_params:
    entity: ProteinSequence
    model: ProteinVAEGenerator
    objective:
      maximize: binding_affinity
    count: 25
    output: candidate_proteins
    contract:
      outputs:
        candidates:
          type: ProteinSequence  # Custom type from schema
          attributes:
            length_min: 50
            length_max: 200
  # ... rest of configuration
```

## Error Handling

Common errors with `guided_discovery` blocks include:

1. **Missing Required Parameters**: All required sections must be present
2. **Invalid Active Learning Configuration**: Active learning requires specific nested keys
3. **Budget Conflicts**: Budget constraints must be consistent
4. **Parameter Injection Issues**: Template variables must match search space

Example error message:
```
Missing required key 'candidates_per_cycle' in design_params
```

## Best Practices

1. **Start Simple**: Begin with basic configurations and gradually add complexity
2. **Monitor Convergence**: Track objective values to ensure the process is progressing
3. **Balance Exploration/Exploitation**: Adjust active learning parameters for optimal search
4. **Resource Planning**: Consider computational costs of both generation and evaluation
5. **Validation**: Always validate final candidates with independent experiments

## Next Steps

- [Design Block Documentation](design_block.md) - Learn about generative design
- [Optimize Block Documentation](optimize_block.md) - Understand active learning optimization
- [Schema Registry Documentation](schema_registry.md) - Define custom data types
- [Workflow Examples](../examples/) - See complete guided discovery workflows
