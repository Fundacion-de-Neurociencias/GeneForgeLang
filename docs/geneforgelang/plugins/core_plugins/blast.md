# BLAST Plugin

NCBI BLAST plugin for GeneForgeLang that enables sequence alignment searches directly from GFL workflows.

## Overview

This plugin provides integration with NCBI BLAST, allowing users to perform sequence similarity searches against NCBI's databases directly from GeneForgeLang workflows. It supports both BLASTP (protein sequences) and BLASTN (nucleotide sequences) searches.

## Features

- **BLASTP Support**: Search protein sequences against protein databases
- **BLASTN Support**: Search nucleotide sequences against nucleotide databases
- **Configurable Parameters**: Set database, E-value thresholds, and other parameters
- **Structured Output**: Returns parsed BLAST results in a clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-blast
```

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "blast"
    operation: "blastp"
    sequence: "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    database: "nr"
    expect_threshold: 0.001
    as_var: "blast_results"

output:
  - blast_hits: "${blast_results.blast_results}"
```

### Parameters

- `operation`: Either "blastp" or "blastn"
- `sequence`: The sequence to search
- `database`: Database to search against (default: "nr" for blastp, "nt" for blastn)
- `expect_threshold`: E-value threshold for reporting hits (default: 10.0)

## Output Format

The plugin returns a structured list of BLAST hits, each containing:

- `id`: Hit identifier
- `definition`: Hit description
- `accession`: Accession number
- `length`: Sequence length
- `hits`: List of HSPs (High-scoring Segment Pairs) with detailed alignment information

## Requirements

- GeneForgeLang >= 1.0.0
- Biopython >= 1.80

## API Reference

### Class: BlastPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the BLAST plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute a BLAST search.

**Parameters:**
- `input_data`: Input data containing sequence information
- `params`: Optional parameters for the BLAST search

**Returns:**
- Dictionary containing BLAST results

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
    "blast_path": "/path/to/blast/binaries",  # Path to BLAST executables
    "default_database": "nr",  # Default database to use
    "max_hits": 100  # Maximum number of hits to return
}

plugin = BlastPlugin(config=config)
```

## Development

### Setting Up for Development

```bash
git clone https://github.com/Fundacion-de-Neurociencias/gfl-plugin-blast.git
cd gfl-plugin-blast
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_blast/
ruff check gfl_plugin_blast/
```

## Troubleshooting

### Common Issues

1. **BLAST Not Found**: Ensure BLAST+ is installed and in your PATH
2. **Database Issues**: Verify database paths and permissions
3. **Memory Errors**: For large searches, consider limiting the number of hits

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Protein Search

```gfl
input:
  protein_sequence: "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"

run:
  - plugin: "blast"
    operation: "blastp"
    sequence: "${protein_sequence}"
    database: "nr"
    expect_threshold: 1e-5
    as_var: "results"

output:
  - hits: "${results.blast_results[:10]}"  # Top 10 hits
```

### Nucleotide Search with Custom Parameters

```gfl
input:
  dna_sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"

run:
  - plugin: "blast"
    operation: "blastn"
    sequence: "${dna_sequence}"
    database: "nt"
    expect_threshold: 0.001
    word_size: 11
    gapopen: 5
    gapextend: 2
    as_var: "results"

process:
  - name: "filter_low_identity"
    input: "${results.blast_results}"
    operation: "filter"
    condition: "identity > 95"
    as_var: "high_identity_hits"

output:
  - filtered_hits: "${high_identity_hits}"
```

## License

This project is licensed under the MIT License.
