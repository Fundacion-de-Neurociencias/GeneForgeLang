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

### Loci Block (v1.3.0+)
- `loci` (list, optional): Genomic regions with coordinates
  - Each locus must contain:
    - `id` (string): Unique identifier
    - `chromosome` (string): Chromosome location
    - `start` (integer): Start coordinate
    - `end` (integer): End coordinate
    - `description` (string, optional): Description
    - `elements` (list, optional): Sub-elements within locus
    - `haplotype_panel` (string, optional, v1.5.0+): Path to reference haplotype sequences

### Haplotype Genotyping (v1.5.0+)

GFL v1.5.0 introduces support for genomic haplotyping using Locityper:

#### Haplotype Panel References
Loci can reference panels of known haplotype sequences:
```yaml
loci:
  - id: HLA_A_Locus
    chromosome: "chr6"
    start: 29941160
    end: 29945884
    haplotype_panel: "db/hla_a_alleles.fasta"
```

#### Locityper Analysis
Use the analyze block with `tool: "locityper"` for haplotype genotyping:
```yaml
analyze:
  tool: "locityper"
  target: locus(HLA_A_Locus)
  input: "patient_wgs.bam"
  output: "genotype_result"
```

#### Genotype Predicates
New predicates for reasoning about genotyping results:
- `genotype_contains(result, haplotype_id)`: Tests if genotype includes specific allele
- `genotype_indicates_absence(result, gene_id)`: Tests if gene is absent/deleted

## Entity and Hypothesis References

### Entity References
Entities defined in `pathways` and `complexes` blocks can be referenced in experiment parameters using the syntax:
- `pathway(entity_name)`
- `complex(entity_name)`

### Hypothesis References
Experiment and analysis blocks can reference hypotheses using the `validates_hypothesis` field.
