# GeneForge Language (GFL) Specification v0.1

GFL is a declarative YAML-based language for defining biological workflows.

## Root Object
The root of any GFL file must be a `plan` object.

## The `plan` Object
- `goal` (string, required): A high-level description of the scientific objective.
- `steps` (list, required): A list of one or more step objects to be executed.

## Additional Top-Level Blocks

GFL also supports several optional top-level blocks that enhance its symbolic reasoning capabilities:

### Rules Block
- `rules` (list, optional): A list of conditional rules that define biological relationships.
  - Each rule must contain:
    - `id` (string): A unique identifier
    - `if` (object): Conditions for the rule
    - `then` (object): Consequences of the rule

### Hypothesis Block
- `hypothesis` (object, optional): A scientific hypothesis to be tested.
  - Must contain:
    - `id` (string): A unique identifier
    - `description` (string): Human-readable description
    - `if` (list): List of conditions
    - `then` (list): List of expected outcomes

### Timeline Block
- `timeline` (object, optional): Temporal orchestration of experiments.
  - Must contain:
    - `events` (list): List of temporal events
    - Each event must have:
      - `at` (string): Time specification
      - `actions` (list): Actions to perform

### Biological Entities
- `pathways` (object, optional): Metabolic and signaling pathways
- `complexes` (object, optional): Protein complexes

## Entity and Hypothesis References

### Entity References
Entities defined in `pathways` and `complexes` blocks can be referenced in experiment parameters using the syntax:
- `pathway(entity_name)`
- `complex(entity_name)`

### Hypothesis References
Experiment and analysis blocks can reference hypotheses using the `validates_hypothesis` field.