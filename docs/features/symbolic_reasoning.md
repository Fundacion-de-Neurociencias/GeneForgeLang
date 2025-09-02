# Symbolic Reasoning in GeneForgeLang

GeneForgeLang now supports advanced symbolic reasoning capabilities that enable users to express biological knowledge, hypotheses, and temporal relationships in a structured way. This feature enhances GFL's expressiveness and allows for more sophisticated workflow designs.

## Overview

Symbolic reasoning in GFL includes:

1. **Rules and Hypotheses** - Express biological knowledge and scientific hypotheses
2. **Timeline Blocks** - Define temporal orchestration of experiments
3. **Biological Entities** - Define pathways and protein complexes
4. **Cross-Reference Validation** - Ensure consistency between different parts of a workflow

## Rules and Hypotheses

### Rules Block

Rules allow you to express conditional relationships in biological systems:

```yaml
rules:
  - id: rule1
    if:
      gene: TP53
      mutation: R175H
    then:
      effect: increased_risk
      cancer_type: breast
  - id: rule2
    if:
      gene: BRCA1
      expression: low
    then:
      effect: increased_risk
      cancer_type: ovarian
```

Each rule must contain:
- `id`: A unique identifier for the rule
- `if`: A dictionary describing the conditions
- `then`: A dictionary describing the consequences

### Hypothesis Block

Hypotheses allow you to formally express scientific hypotheses that your workflow aims to test:

```yaml
hypothesis:
  id: hypothesis1
  description: TP53 mutations increase cancer risk
  if:
    - gene: TP53
      mutation: R175H
    - expression: low
  then:
    - effect: increased_risk
      cancer_type: breast
    - biomarker: Ki67
      expression: high
```

A hypothesis must contain:
- `id`: A unique identifier for the hypothesis
- `description`: A human-readable description
- `if`: A list of conditions
- `then`: A list of expected outcomes

## Timeline Blocks

Timeline blocks allow you to define the temporal orchestration of your experiments:

```yaml
timeline:
  events:
    - at: "2024-01-01"
      actions:
        - type: sequencing
          sample: patient1
      expectations:
        - outcome: high_quality_data
    - at: "2024-01-15"
      actions:
        - type: analysis
          data: sequencing_results
```

Each timeline must contain:
- `events`: A list of temporal events
- Each event must have:
  - `at`: A time specification (string)
  - `actions`: A list of actions to perform
  - `expectations`: (Optional) A list of expected outcomes

## Biological Entities

### Pathways

Define metabolic and signaling pathways:

```yaml
pathways:
  UreaCycle:
    description: Urea cycle metabolic pathway
    genes: [ASS1, ASL, ARG1]
    enzymes: [ASS, ASL, ARG]
    reactions:
      - substrate: ornithine
        product: citrulline
  Glycolysis:
    description: Glycolysis pathway
    genes: [HK1, PGK1, PKM]
    enzymes: [Hexokinase, Phosphoglycerate kinase, Pyruvate kinase]
```

### Complexes

Define protein complexes:

```yaml
complexes:
  RNA_POLYMERASE_II:
    description: RNA polymerase II complex
    subunits: [POLR2A, POLR2B, POLR2C, POLR2D, POLR2E]
    function: transcription
  RIBOSOME_80S:
    description: 80S ribosome complex
    subunits: [RPSA, RPSB, RPLA, RPLB]
    function: translation
```

## Entity References

You can reference defined entities in experiment parameters using the syntax `entity_type(entity_name)`:

```yaml
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_pathway: pathway(UreaCycle)
    target_complex: complex(RNA_POLYMERASE_II)
    concentration: 50.0
```

Supported entity types:
- `pathway`: Reference a defined pathway
- `complex`: Reference a defined protein complex

## Hypothesis References

Both experiment and analysis blocks can reference hypotheses to indicate which hypothesis they are designed to test:

```yaml
# Reference a hypothesis in an experiment block
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
  validates_hypothesis: hypothesis1

# Reference a hypothesis in an analysis block
analyze:
  strategy: variant
  data: sequencing_results.csv
  validates_hypothesis: hypothesis1
```

## Validation

GeneForgeLang's semantic validator ensures:

1. **Rules validation**: Each rule has required fields (id, if, then)
2. **Hypothesis validation**: Each hypothesis has required fields (id, description, if, then)
3. **Timeline validation**: Each timeline event has required fields (at, actions)
4. **Entity reference validation**: Referenced entities must be defined
5. **Hypothesis reference validation**: Referenced hypotheses must be defined

## Error Handling

When validation fails, GFL provides specific error codes:

- `SEMANTIC_UNDEFINED_HYPOTHESIS` (SEMANTIC009): Referenced hypothesis is not defined
- `SEMANTIC_UNDEFINED_ENTITY_REFERENCE` (SEMANTIC010): Referenced entity is not defined

## Example Workflow

Here's a complete example that uses all symbolic reasoning features:

```yaml
# Define biological entities
pathways:
  UreaCycle:
    description: Urea cycle metabolic pathway
    genes: [ASS1, ASL, ARG1]

complexes:
  RNA_POLYMERASE_II:
    description: RNA polymerase II complex
    subunits: [POLR2A, POLR2B]

# Define a scientific hypothesis
hypothesis:
  id: urea_cycle_hypothesis
  description: Disruption of urea cycle genes affects RNA polymerase II expression
  if:
    - gene: ASS1
      mutation: null
  then:
    - complex: RNA_POLYMERASE_II
      expression: decreased

# Define rules about the biological system
rules:
  - id: urea_cycle_rule
    if:
      pathway: UreaCycle
      disrupted: true
    then:
      disease: hyperammonemia

# Timeline for experimental orchestration
timeline:
  events:
    - at: "2024-01-01"
      actions:
        - type: crispr_editing
          target_gene: ASS1
      expectations:
        - outcome: successful_knockout
    - at: "2024-01-15"
      actions:
        - type: expression_analysis
          target_complex: complex(RNA_POLYMERASE_II)
      expectations:
        - outcome: decreased_expression

# Experiment that tests the hypothesis
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: ASS1
    target_pathway: pathway(UreaCycle)
  validates_hypothesis: urea_cycle_hypothesis

# Analysis that tests the hypothesis
analyze:
  strategy: expression
  data: expression_results.csv
  validates_hypothesis: urea_cycle_hypothesis
```

This symbolic reasoning framework enables more expressive and scientifically rigorous workflow definitions in GeneForgeLang.