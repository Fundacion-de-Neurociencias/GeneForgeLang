# Tutorial: Using Custom Schemas in IO Contracts

This tutorial will guide you through defining custom data types using schema files and using them in IO contracts to ensure data integrity in your GeneForgeLang workflows.

## Prerequisites

Before starting this tutorial, you should be familiar with:
- Basic GFL syntax
- IO contracts
- YAML file structure

## Step 1: Define a Custom Schema

First, let's create a schema file that defines a custom data type for gene expression data:

```yaml
# gene_expression_schemas.yml
version: 1.0
schemas:
  - name: GeneExpressionMatrix
    base_type: CSV
    description: "Gene expression data matrix with genes as rows and samples as columns"
    attributes:
      normalized:
        required: true
        value: true
      log_transformed:
        required: false
        type: boolean
      sample_count:
        required: true
        type: integer
      gene_count:
        required: true
        type: integer
      contains_metadata:
        required: false
        value: true

  - name: DifferentialExpressionResults
    base_type: CSV
    description: "Results from differential expression analysis"
    attributes:
      p_value_adjusted:
        required: true
        value: true
      fold_change_threshold:
        required: true
        type: float
      significant_genes_count:
        required: false
        type: integer
```

## Step 2: Import the Schema in Your GFL File

Create a GFL workflow that imports your custom schema:

```yaml
# rna_seq_analysis.gfl
import_schemas:
  - ./schemas/gene_expression_schemas.yml

metadata:
  experiment_id: RNA_SEQ_001
  researcher: Dr. Jane Smith
  date: 2025-08-31

experiment:
  tool: RNAseq
  type: sequencing
  contract:
    outputs:
      raw_expression:
        type: GeneExpressionMatrix
        attributes:
          normalized: true
          sample_count: 12
          gene_count: 25000
          contains_metadata: true
  params:
    protocol: standard
    read_length: 150
    paired_end: true
  output: expression_data

analyze:
  strategy: differential
  contract:
    inputs:
      expression_data:
        type: GeneExpressionMatrix
        attributes:
          normalized: true
    outputs:
      de_results:
        type: DifferentialExpressionResults
        attributes:
          p_value_adjusted: true
          fold_change_threshold: 1.5
  data: expression_data
  thresholds:
    p_value: 0.05
    fold_change: 1.5
  output: differential_results
```

## Step 3: Validate Your Workflow

Run the GFL validator to check that your custom schemas are correctly defined and used:

```bash
gfl-validate rna_seq_analysis.gfl
```

If everything is correct, you should see no errors. If there are issues, the validator will provide specific error messages.

## Step 4: Advanced Schema Definitions

You can also define more complex schemas with validation rules:

```yaml
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

## Step 5: Using Advanced Schemas

Use your advanced schemas in a more complex workflow:

```yaml
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

## Step 6: Handling Schema Validation Errors

When there are issues with your schema definitions or usage, GFL provides detailed error messages:

### Missing Required Attribute Error
```
Error: Required attribute 'sample_count' missing in contract outputs 'raw_expression' for schema type 'GeneExpressionMatrix'
Fix: Add the required 'sample_count' attribute to your contract definition
```

### Invalid Attribute Value Error
```
Error: Attribute 'clinical_significance' in contract inputs 'variants' must have value '[benign, likely_benign, uncertain, likely_pathogenic, pathogenic]' for schema type 'VariantAnnotation', got 'unknown'
Fix: Use one of the allowed values for clinical_significance
```

## Best Practices

1. **Organize Schema Files**: Group related schemas in logical files
2. **Version Your Schemas**: Include version information for tracking changes
3. **Document Thoroughly**: Provide clear descriptions for schemas and attributes
4. **Validate Early**: Check schema definitions before using them in workflows
5. **Reuse When Possible**: Design schemas to be reusable across multiple projects

## Next Steps

- [Schema Registry Documentation](../features/schema_registry.md) - Complete reference for schema definitions
- [IO Contracts Documentation](../features/io_contracts.md) - Learn more about data integrity features
- [Guided Discovery Tutorial](guided_discovery.md) - Combine custom schemas with AI workflows
- [Error Handling Guide](../error_handling.md) - Understand all validation error types
