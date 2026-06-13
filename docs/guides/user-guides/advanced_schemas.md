# Tutorial: Using Custom Schemas in IO Contracts

_This document is a companion to the Quickstart Guide. It covers advanced schema types (VCF, CUSTOM base types), complex validation rules, and genomic-specific schema patterns. Refer to the Quickstart for basic schema usage and IO contracts._

Custom schemas in GFL enforce data integrity between workflow steps. While the Quickstart covers CSV-based schemas for common use cases, advanced genomic workflows often require more specialized types with stricter validation. This guide covers those patterns.

## 1. Advanced Base Types

Beyond CSV, GFL schemas support two additional base types suited for specialized genomic data:

- **Variant Call Format files. Enables attributes specific to variant annotation workflows**.VCF —
- **Arbitrary data structures where no standard format applies (e.g., phylogenetic trees, custom matrices)**.CUSTOM —

VCF Schema: Variant Annotation
Use this schema when your workflow produces or consumes annotated variant calls with clinical significance data:

```bash
# advanced_genomics_schemas.yml
version: 1.0
schemas:
  - name: VariantAnnotation
    base_type: VCF
    description: "Annotated variant call format with clinical significance"
    attributes:
      annotated:
        required: true
        value: true
      clinical_significance:
        required: true
        value: [benign, likely_benign, uncertain, likely_pathogenic, pathogenic]
      population_frequency:
              required: false
        type: float
      prediction_score:
        required: false
        type: float
      functional_impact:
        required: false
        value: [high, moderate, low, modifier]
```

 CUSTOM Schema: Phylogenetic Tree
Use CUSTOM base type for non-standard data structures such as phylogenetic trees:

```bash
 - name: PhylogeneticTree
    base_type: CUSTOM
    description: "Phylogenetic tree with bootstrap support values"
    attributes:
      rooted:
        required: false
        type: boolean
      bootstrap_threshold:
        required: true
        type: float
      leaf_count:
        required: true
        type: integer
      newick_format:
        required: true
        value: true
```

## 2. Full Advanced Workflow Example

This example uses both VCF and CUSTOM schemas in a variant analysis pipeline that produces a phylogenetic tree:

```bash
# variant_analysis.gfl
import_schemas:
  - ./schemas/advanced_genomics_schemas.yml

metadata:
  experiment_id: VARIANT_ANALYSIS_001
  researcher: Dr. John Doe
  date: 2025-08-31

experiment:
  tool: WGS
  type: sequencing
  contract:
    outputs:
      raw_variants:
        type: VariantAnnotation
        attributes:
          annotated: true
          clinical_significance: pathogenic
  params:
    coverage: 30x
    platform: Illumina
  output: variant_calls

analyze:
  strategy: variant
  contract:
    inputs:
      variants:
        type: VariantAnnotation
        attributes:
          annotated: true
    outputs:
      phylo_tree:
        type: PhylogeneticTree
        attributes:
          bootstrap_threshold: 0.7
          leaf_count: 50
          newick_format: true
  data: variant_calls
  filters:
    - quality > 30
    - depth > 10
  operations:
    - build_phylogeny:
        method: maximum_likelihood
        bootstrap_replicates: 1000
  output: phylogenetic_tree
```

## 3. Attribute Types Reference
The following attribute types are available across all schema definitions:

| Type | Example value | Description |
| :--- | :--- | :--- |
| boolean | true / false | Logical flag; validated as a YAML boolean. |
| integer | 12 | Whole number; validated as an integer. |
| float | 1.5 | Decimal number; validated as a floating-point value. |
| string | "GRCh38" | Arbitrary text value. |
| value (literal) | true | Exact value that must match; used for enum-like constraints. |
| value (list) | [benign, pathogenic] | One of the listed values must be present; acts as an enum. |

## 4. Validation Error Reference

Missing Required Attribute

```bash
Error: Required attribute 'sample_count' missing in contract outputs
       'raw_expression' for schema type 'GeneExpressionMatrix'
Fix:   Add the 'sample_count' attribute to your contract definition.
```

Invalid Enum Value

```bash
Error: Attribute 'clinical_significance' in contract inputs 'variants' must
       have value '[benign, likely_benign, uncertain, likely_pathogenic,
       pathogenic]' for schema type 'VariantAnnotation', got 'unknown'
Fix:   Use one of the allowed values listed in the schema definition.
```

Type Mismatch

```bash
Error: Attribute 'bootstrap_threshold' expected type float, got string
Fix:   Remove quotes around numeric values in your contract.
```

## 5. Best Practices for Advanced Schemas

- **keep genomic variant schemas apart from expression schemas to avoid naming conflicts**. Separate schema files by domain:
- **bump the version field whenever you change attribute requirements to avoid breaking existing workflows**.Version every schema file:
- **enum-style constraints prevent invalid clinical significance values from propagating silently**.Use value lists for clinical fields:
- **makes schemas forward-compatible as new annotation sources are added.Set required**: false for optional annotations:
- **run gfl-validate on any workflow that uses advanced schemas before distributing it to collaborators**.Validate before sharing:

## 6. Related Resources

- **quickstart.md** — basic schemas, IO contracts, and first workflows.Quickstart Guide —
- **features/schema_registry.md** — complete attribute reference.Schema Registry Documentation —
- **features/io_contracts.md** — how contracts are evaluated at runtime.IO Contracts Documentation —
- **error_handling.md** — full list of validation error types and resolution steps.Error Handling Guide —
- **tutorials/guided_discovery.md** — combine custom schemas with AI-powered workflows.Guided Discovery Tutorial —
