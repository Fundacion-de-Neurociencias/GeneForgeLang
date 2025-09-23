# Off-Target Scorer Plugin

A plugin that identifies potential off-target cutting sites and calculates a global risk score for CRISPR gene editing applications.

## Description

This plugin identifies potential CRISPR-Cas9 off-target cutting sites and calculates a global risk score. It takes a gRNA sequence as input and uses tools like BLASTn to search for similar sequences in a reference genome (e.g., GRCh38). For each potential off-target site found, it calculates a risk score using algorithms like CFD (Cutting Frequency Determination). Finally, it returns an aggregated global risk score, where lower values indicate less off-target risk.

## Features

- **Genome Search**: Uses BLAST-like search against reference genomes
- **Risk Scoring**: Calculates risk scores using the CFD algorithm
- **Configurable Parameters**: Supports mismatch limits and genome references
- **Structured Output**: Returns risk scores and site details in JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-offtarget-scorer
```

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "gfl-offtarget-scorer"
    input_data: {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA"
    }
    params: {
      "max_mismatches": 3,
      "genome_reference": "GRCh38"
    }
    as_var: "risk_results"

output:
  - global_risk_score: "${risk_results.result.global_risk_score}"
```

## Input Parameters

The plugin expects a dictionary with the following key:
- `grna_sequence`: The 20-nucleotide gRNA sequence (string)

Optional parameters:
- `max_mismatches`: Maximum number of mismatches to consider (default: 3)
- `genome_reference`: Reference genome to search against (default: "GRCh38")

## Output

The plugin returns a dictionary with:
- `global_risk_score`: A float between 0 and 1 representing the global off-target risk (lower is better)
- `grna_sequence`: The input gRNA sequence
- `genome_reference`: The genome reference used
- `max_mismatches`: The maximum mismatches parameter used
- `off_target_sites`: List of potential off-target sites with details
- `algorithm_used`: The algorithm used for risk calculation

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "blast_db_path": "/path/to/blast/db",  # Path to BLAST database
    "cfd_model_path": "/path/to/cfd/model"  # Path to CFD model
}

plugin = ScorerPlugin(config=config)
```

## API Reference

### Class: ScorerPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the Off-Target Scorer plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute the off-target risk scoring.

**Parameters:**
- `input_data`: Input data containing gRNA sequence
- `params`: Optional parameters for the scoring process

**Returns:**
- Dictionary containing risk scoring results

##### `validate_input(self, input_data: Any) -> bool`
Validate input data for the plugin.

**Parameters:**
- `input_data`: Input data to validate

**Returns:**
- True if input is valid, False otherwise

##### `_process_data(self, input_data: Any, params: Dict[str, Any]) -> Any`
Process the input data according to plugin logic.

**Parameters:**
- `input_data`: Input data to process
- `params`: Parameters for processing

**Returns:**
- Processed data with risk score

##### `_validate_sequence(self, sequence: str) -> bool`
Validate DNA sequence format.

**Parameters:**
- `sequence`: DNA sequence to validate

**Returns:**
- True if sequence is valid, False otherwise

##### `_find_off_target_sites(self, grna_sequence: str, max_mismatches: int, genome_reference: str) -> List[Dict[str, Any]]`
Find potential off-target sites using a BLAST-like approach.

**Parameters:**
- `grna_sequence`: The gRNA sequence to search for
- `max_mismatches`: Maximum number of mismatches to consider
- `genome_reference`: Reference genome to search against

**Returns:**
- List of potential off-target sites with their details

##### `_calculate_global_risk_score(self, off_target_sites: List[Dict[str, Any]]) -> float`
Calculate global off-target risk score using the CFD algorithm.

**Parameters:**
- `off_target_sites`: List of potential off-target sites

**Returns:**
- Global risk score (lower is better)

## Dependencies

- numpy >= 1.24.0
- pandas >= 2.0.0
- biopython >= 1.80

## Development

### Setting Up for Development

```bash
git clone <repository-url>
cd gfl-plugin-offtarget-scorer
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_offtarget_scorer/
ruff check gfl_plugin_offtarget_scorer/
```

## Troubleshooting

### Common Issues

1. **Sequence Format Errors**: Ensure input sequences contain only valid nucleotides (A, C, G, T, N)
2. **Database Issues**: Verify BLAST database paths and permissions
3. **Performance Issues**: For large genomes, consider limiting search regions

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Risk Scoring

```gfl
input:
  grna_sequence: "GCAATGGAGCGGCTTGCGGA"

run:
  - plugin: "gfl-offtarget-scorer"
    input_data: {
      "grna_sequence": "${grna_sequence}"
    }
    params: {
      "max_mismatches": 3,
      "genome_reference": "GRCh38"
    }
    as_var: "risk_result"

output:
  - global_risk_score: "${risk_result.result.global_risk_score}"
  - off_target_sites: "${risk_result.result.off_target_sites}"
```

### Comprehensive Off-Target Analysis

```gfl
input:
  grna_candidates: [
    "GCAATGGAGCGGCTTGCGGA",
    "GTCGATCGATCGATCGATCG",
    "ATCGATCGATCGATCGATCG"
  ]
  genome_reference: "GRCh38"

process:
  - name: "analyze_candidate"
    for_each: "sequence in grna_candidates"
    run:
      - plugin: "gfl-offtarget-scorer"
        input_data: {
          "grna_sequence": "${sequence}"
        }
        params: {
          "max_mismatches": 4,
          "genome_reference": "${genome_reference}"
        }
        as_var: "analysis_result_${loop.index}"
    
    output:
      - analyzed_candidates: [
          {
            "sequence": "${sequence}",
            "risk_score": "${analysis_result_${loop.index}.result.global_risk_score}",
            "sites_found": "${len(analysis_result_${loop.index}.result.off_target_sites)}"
          }
          for sequence in grna_candidates
        ]

output:
  - risk_analysis: "${analyzed_candidates}"
```

### Advanced Configuration with Custom Parameters

```gfl
input:
  grna_sequence: "GCAATGGAGCGGCTTGCGGA"

run:
  - plugin: "gfl-offtarget-scorer"
    input_data: {
      "grna_sequence": "${grna_sequence}"
    }
    params: {
      "max_mismatches": 2,
      "genome_reference": "GRCh38",
      "chromosomes": ["chr1", "chr2", "chr3"],  # Limit search to specific chromosomes
      "exclude_regions": ["chr1:1000000-2000000"]  # Exclude specific regions
    }
    as_var: "custom_result"

output:
  - custom_analysis: "${custom_result}"
```

## Integration with Other Plugins

The Off-Target Scorer plugin is designed to work with other Genesis plugins:

- **[On-Target Scorer](ontarget_scorer.md)**: For comprehensive CRISPR efficiency assessment
- **[CRISPR Evaluator](evaluator.md)**: For combining efficiency and risk scores
- **[CRISPR Visualizer](visualizer.md)**: For visualizing risk scoring results

## License

This plugin is part of the GeneForgeLang ecosystem and is licensed under the MIT License.

## Author

Manuel Menendez Gonzalez - manuelmenendes@fneurociencias.org