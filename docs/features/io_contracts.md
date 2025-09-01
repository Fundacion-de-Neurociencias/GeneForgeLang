# IO Contracts System

GeneForgeLang v1.0.0 introduces IO Contracts, a powerful system for ensuring data integrity between workflow blocks. IO Contracts provide static compatibility checking and type safety for genomic data flows.

## Overview

IO Contracts define the data requirements and guarantees for each workflow block, ensuring that outputs from one block are compatible with inputs to another. This system prevents runtime errors caused by incompatible data types and provides better tooling support.

## Contract Structure

IO Contracts are defined using the `contract` key in experiment and analyze blocks:

```yaml
experiment:
  tool: RNAseq
  type: sequencing
  contract:
    outputs:
      sequences:
        type: FASTQ
        attributes:
          quality_score: true
          paired_end: true
  params:
    # ... experiment parameters
```

### Contract Components

1. **Type**: Specifies the data type (e.g., FASTQ, BAM, CSV, JSON)
2. **Attributes**: Optional metadata about the data (e.g., quality scores, paired-end status)

## Available Data Types

GeneForgeLang supports several built-in data types:

- **Sequence Data**: FASTA, FASTQ, BAM, SAM, VCF
- **General Data**: CSV, JSON, TEXT, BINARY
- **Custom Types**: User-defined types via schema registry

## Example Usage

### Experiment Block with Output Contract

```yaml
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  contract:
    outputs:
      edited_sequences:
        type: FASTQ
        attributes:
          quality_score: true
          read_length: 150
  params:
    target_gene: BRCA1
    guide_rna: GCGTACGTTCAAGCGATCCG
```

### Analysis Block with Input Contract

```yaml
analyze:
  strategy: differential
  contract:
    inputs:
      sequences:
        type: FASTQ
        attributes:
          quality_score: true
  data: edited_sequences
```

## Static Compatibility Checking

GeneForgeLang's validator automatically checks compatibility between block contracts:

- **Type Matching**: Ensures output and input types are compatible
- **Attribute Validation**: Verifies required attributes are present
- **Custom Schema Support**: Works with user-defined types from schema registry

## Error Handling

When contracts are incompatible, GeneForgeLang provides detailed error messages:

```
Contract type mismatch: experiment output 'sequences' (type: FASTQ) is incompatible with analyze input 'sequences' (type: BAM)
```

## Best Practices

1. **Define Contracts Early**: Add contracts during workflow design to catch issues early
2. **Use Attributes**: Specify important data characteristics to ensure compatibility
3. **Leverage Custom Types**: Define domain-specific types in schema files for better validation
4. **Validate Before Execution**: Always validate contracts before running workflows

## Next Steps

- [Schema Registry Documentation](schema_registry.md) - Learn how to define custom types
- [Design Block Documentation](design_block.md) - See how contracts work with AI workflows
- [Error Handling Guide](../error_handling.md) - Understand contract validation errors