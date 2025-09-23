# Biopython Tools Plugin

Biopython Tools plugin for GeneForgeLang that provides bioinformatics utilities and sequence analysis capabilities directly from GFL workflows.

## Overview

This plugin provides integration with Biopython, offering a collection of bioinformatics tools and utilities for sequence analysis, file parsing, and biological data manipulation directly from GeneForgeLang workflows. It supports common bioinformatics operations including sequence manipulation, file format conversion, and basic sequence analysis.

## Features

- **Sequence Manipulation**: Reverse complement, translation, and other sequence operations
- **File Parsing**: Read and write various biological file formats (FASTA, GenBank, etc.)
- **Sequence Analysis**: Basic sequence analysis including GC content, molecular weight, etc.
- **Configurable Parameters**: Set parameters for each operation
- **Structured Output**: Returns parsed results in a clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-biopython-tools
```

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "biopython-tools"
    operation: "reverse_complement"
    sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
    as_var: "reverse_comp_result"

output:
  - reverse_complement: "${reverse_comp_result.result}"
```

### Parameters

- `operation`: The Biopython operation to perform (reverse_complement, translate, gc_content, etc.)
- `sequence`: Input sequence (for sequence operations)
- `input_file`: Input file path (for file operations)
- `output_file`: Output file path (for file operations)
- Additional operation-specific parameters

## Supported Operations

### reverse_complement

Generates the reverse complement of a DNA sequence.

**Parameters:**
- `sequence`: Input DNA sequence

**Returns:**
- Reverse complement sequence

### translate

Translates a DNA or RNA sequence to protein sequence.

**Parameters:**
- `sequence`: Input DNA or RNA sequence
- `table`: Translation table (default: 1, Standard Genetic Code)
- `to_stop`: Translate to stop codon (default: False)

### gc_content

Calculates the GC content of a DNA sequence.

**Parameters:**
- `sequence`: Input DNA sequence

**Returns:**
- GC content as a percentage

### molecular_weight

Calculates the molecular weight of a sequence.

**Parameters:**
- `sequence`: Input sequence
- `seq_type`: Sequence type (DNA, RNA, protein)

### parse_fasta

Parses a FASTA file and returns sequence records.

**Parameters:**
- `input_file`: Path to input FASTA file

**Returns:**
- List of sequence records

### write_fasta

Writes sequences to a FASTA file.

**Parameters:**
- `sequences`: List of sequences to write
- `output_file`: Path to output FASTA file
- `descriptions`: Optional descriptions for sequences

### parse_genbank

Parses a GenBank file and returns sequence records.

**Parameters:**
- `input_file`: Path to input GenBank file

**Returns:**
- List of sequence records

## Output Format

The plugin returns structured results containing:

- `operation`: The Biopython operation that was performed
- `result`: The result of the operation (for sequence operations)
- `output_files`: Dictionary of output files created (for file operations)
- `records`: Parsed sequence records (for file parsing operations)
- `status`: Execution status (success/failure)

## Requirements

- GeneForgeLang >= 1.0.0
- Biopython >= 1.80

## API Reference

### Class: BiopythonToolsPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the Biopython Tools plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute a Biopython operation.

**Parameters:**
- `input_data`: Input data containing sequences or file paths
- `params`: Optional parameters for the Biopython operation

**Returns:**
- Dictionary containing Biopython results

##### `validate_input(self, input_data: Any) -> bool`
Validate input data for the plugin.

**Parameters:**
- `input_data`: Input data to validate

**Returns:**
- True if input is valid, False otherwise

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "default_sequence_type": "DNA",  # Default sequence type
    "temp_dir": "/tmp/biopython"  # Temporary directory for file operations
}

plugin = BiopythonToolsPlugin(config=config)
```

## Development

### Setting Up for Development

```bash
git clone https://github.com/Fundacion-de-Neurociencias/gfl-plugin-biopython-tools.git
cd gfl-plugin-biopython-tools
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_biopython_tools/
ruff check gfl_plugin_biopython_tools/
```

## Troubleshooting

### Common Issues

1. **Sequence Format Errors**: Ensure input sequences are in the correct format
2. **File Parsing Issues**: Verify input file formats and permissions
3. **Translation Table Issues**: Check that the correct translation table is specified
4. **Memory Errors**: For large files, consider processing in chunks

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Sequence Operations

```gfl
input:
  dna_sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"

run:
  - plugin: "biopython-tools"
    operation: "reverse_complement"
    sequence: "${dna_sequence}"
    as_var: "reverse_comp"

  - plugin: "biopython-tools"
    operation: "gc_content"
    sequence: "${dna_sequence}"
    as_var: "gc_content_result"

  - plugin: "biopython-tools"
    operation: "translate"
    sequence: "${dna_sequence}"
    as_var: "translation_result"

output:
  - reverse_complement: "${reverse_comp.result}"
  - gc_content: "${gc_content_result.result}"
  - protein_sequence: "${translation_result.result}"
```

### File Processing Workflow

```gfl
input:
  input_fasta: "/data/sequences/proteins.fasta"
  output_dir: "/data/processed"

run:
  - plugin: "biopython-tools"
    operation: "parse_fasta"
    input_file: "${input_fasta}"
    as_var: "fasta_records"

process:
  - name: "analyze_sequences"
    for_each: "record in fasta_records.records"
    run:
      - plugin: "biopython-tools"
        operation: "molecular_weight"
        sequence: "${record.seq}"
        seq_type: "protein"
        as_var: "mw_result_${record.id}"
      
      - plugin: "biopython-tools"
        operation: "gc_content"
        sequence: "${record.seq}"
        as_var: "gc_result_${record.id}"

output:
  - processed_sequences: "${fasta_records.records}"
  - analysis_results: "Molecular weights and GC content calculated for all sequences"
```

### Multi-Operation Analysis Pipeline

```gfl
input:
  sequences: [
    "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG",
    "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG",
    "CGATCGATCGATCGATCGATCGATCGATCGATCGATCGATC"
  ]
  output_dir: "/data/analysis"

process:
  - name: "analyze_sequence"
    for_each: "seq in sequences"
    run:
      - plugin: "biopython-tools"
        operation: "reverse_complement"
        sequence: "${seq}"
        as_var: "rc_result"
      
      - plugin: "biopython-tools"
        operation: "gc_content"
        sequence: "${seq}"
        as_var: "gc_result"
      
      - plugin: "biopython-tools"
        operation: "molecular_weight"
        sequence: "${seq}"
        seq_type: "DNA"
        as_var: "mw_result"
    
    output:
      - sequence_${loop.index}: {
          "original": "${seq}",
          "reverse_complement": "${rc_result.result}",
          "gc_content": "${gc_result.result}",
          "molecular_weight": "${mw_result.result}"
        }

output:
  - sequence_analysis: "All sequences analyzed"
```

## License

This project is licensed under the MIT License.