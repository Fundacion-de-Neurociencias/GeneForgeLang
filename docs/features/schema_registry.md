# Schema Registry & Type System

GeneForgeLang v1.0.0 introduces a powerful Schema Registry system that allows users to define custom data types in external schema files. This extensible type system enhances the language's flexibility and domain-specific capabilities.

## Overview

The Schema Registry enables users to:
- Define custom data types in YAML schema files
- Import schema definitions using the `import_schemas` directive
- Use custom types in IO contracts for enhanced validation
- Create domain-specific types for specialized workflows

## Schema Definition Files

Schema definitions are written in YAML files with a specific structure:

```yaml
# custom_types.yml
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
      sample_count:
        required: true
        type: integer

  - name: ProteinStructure
    base_type: CUSTOM
    description: "3D protein structure in PDB format with metadata"
    attributes:
      resolution:
        required: true
        type: float
      atom_count:
        required: false
        type: integer
```

## Importing Schemas

Use the `import_schemas` directive at the top level of your GFL file to import schema definitions:

```yaml
import_schemas:
  - ./schemas/custom_types.yml
  - ./schemas/domain_specific.yml

experiment:
  tool: RNAseq
  type: sequencing
  contract:
    outputs:
      expression_data:
        type: GeneExpressionMatrix
        attributes:
          normalized: true
          sample_count: 12
```

## Using Custom Types in Contracts

Once imported, custom types can be used in IO contracts just like built-in types:

```yaml
analyze:
  strategy: differential
  contract:
    inputs:
      expression_data:
        type: GeneExpressionMatrix
        attributes:
          normalized: true
    outputs:
      significant_genes:
        type: CSV
        attributes:
          format: gene_list
```

## Schema Validation

The Schema Registry provides robust validation for custom types:

1. **Required Attributes**: Ensures all required attributes are present
2. **Value Constraints**: Validates attribute values against expected values
3. **Type Checking**: Verifies attribute types match schema definitions
4. **Base Type Compatibility**: Checks compatibility with base types

## Example Schema File

Here's a complete example of a schema definition file:

```yaml
# genomics_schemas.yml
version: 1.0
schemas:
  - name: VariantCallFormat
    base_type: VCF
    description: "Variant call format file with genomic variants"
    attributes:
      compressed:
        required: false
        value: true
      annotated:
        required: true
        value: true
      sample_count:
        required: true
        type: integer

  - name: PhylogeneticTree
    base_type: CUSTOM
    description: "Phylogenetic tree representation in Newick format"
    attributes:
      rooted:
        required: false
        type: boolean
      bootstrap_values:
        required: false
        value: true
      leaf_count:
        required: true
        type: integer

  - name: GenomeAssembly
    base_type: FASTA
    description: "Genome assembly in FASTA format"
    attributes:
      contig_count:
        required: true
        type: integer
      assembly_level:
        required: true
        value: [complete, chromosome, scaffold, contig]
      gc_content:
        required: false
        type: float
```

## Error Handling

When schema validation fails, GeneForgeLang provides clear error messages:

```
Required attribute 'sample_count' missing in contract outputs 'expression_data' for schema type 'GeneExpressionMatrix'
```

## Best Practices

1. **Organize Schemas**: Group related types in logical schema files
2. **Version Control**: Include version information in schema files
3. **Documentation**: Provide clear descriptions for each schema and attribute
4. **Validation**: Define required attributes to ensure data quality
5. **Reusability**: Design schemas to be reusable across multiple workflows

## Next Steps

- [IO Contracts Documentation](io_contracts.md) - Learn how to use custom types in contracts
- [Design Block Documentation](design_block.md) - See how custom types work with AI workflows
- [Error Handling Guide](../error_handling.md) - Understand schema validation errors