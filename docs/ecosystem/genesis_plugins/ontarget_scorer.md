# On-Target Scorer Plugin

A plugin that predicts on-target cutting efficiency of a gRNA sequence for CRISPR gene editing applications.

## Description

This plugin predicts the efficiency of CRISPR-Cas9 cutting at the intended target site using pre-trained machine learning models such as DeepCRISPR or DeepHF. It takes a gRNA sequence and the surrounding genomic sequence as input and returns an efficiency score between 0 and 1, where higher scores indicate more efficient cutting.

## Features

- **Machine Learning Models**: Uses pre-trained models like DeepCRISPR or DeepHF for efficiency prediction
- **Sequence Validation**: Validates DNA sequence format and content
- **Configurable Parameters**: Supports model selection and custom parameters
- **Structured Output**: Returns efficiency scores in a clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-ontarget-scorer
```

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "gfl-ontarget-scorer"
    input_data: {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
      "genome_sequence": "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"
    }
    as_var: "efficiency_results"

output:
  - efficiency_score: "${efficiency_results.result.efficiency_score}"
```

## Input Parameters

The plugin expects a dictionary with the following keys:
- `grna_sequence`: The 20-nucleotide gRNA sequence (string)
- `genome_sequence`: The surrounding genomic sequence (string)

## Output

The plugin returns a dictionary with:
- `efficiency_score`: A float between 0 and 1 representing the cutting efficiency
- `grna_sequence`: The input gRNA sequence
- `genome_sequence`: The input genomic sequence
- `model_used`: The model used for prediction

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "model_type": "deephf",  # or "deepcrispr"
    "model_path": "/path/to/model"  # Path to pre-trained model
}

plugin = ScorerPlugin(config=config)
```

## API Reference

### Class: ScorerPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the On-Target Scorer plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute the on-target efficiency scoring.

**Parameters:**
- `input_data`: Input data containing gRNA and genome sequences
- `params`: Optional parameters for the scoring process

**Returns:**
- Dictionary containing efficiency scoring results

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
- Processed data with efficiency score

##### `_validate_sequence(self, sequence: str) -> bool`
Validate DNA sequence format.

**Parameters:**
- `sequence`: DNA sequence to validate

**Returns:**
- True if sequence is valid, False otherwise

##### `_calculate_efficiency_score(self, grna_sequence: str, genome_sequence: str) -> float`
Calculate on-target cutting efficiency score using a pre-trained model.

**Parameters:**
- `grna_sequence`: The gRNA sequence (typically 20 nucleotides)
- `genome_sequence`: The surrounding genomic sequence

**Returns:**
- Efficiency score between 0 and 1

## Dependencies

- numpy >= 1.24.0
- pandas >= 2.0.0
- scikit-learn >= 1.3.0
- tensorflow >= 2.10.0
- biopython >= 1.80

## Development

### Setting Up for Development

```bash
git clone <repository-url>
cd gfl-plugin-ontarget-scorer
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_ontarget_scorer/
ruff check gfl_plugin_ontarget_scorer/
```

## Troubleshooting

### Common Issues

1. **Sequence Format Errors**: Ensure input sequences contain only valid nucleotides (A, C, G, T, N)
2. **Model Loading Issues**: Verify model paths and compatibility
3. **Memory Errors**: For large-scale predictions, consider processing in batches

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Efficiency Scoring

```gfl
input:
  grna_sequence: "GCAATGGAGCGGCTTGCGGA"
  genome_context: "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"

run:
  - plugin: "gfl-ontarget-scorer"
    input_data: {
      "grna_sequence": "${grna_sequence}",
      "genome_sequence": "${genome_context}"
    }
    as_var: "scoring_result"

output:
  - efficiency_score: "${scoring_result.result.efficiency_score}"
  - model_used: "${scoring_result.result.model_used}"
```

### Batch Processing Multiple gRNAs

```gfl
input:
  grna_candidates: [
    {
      "sequence": "GCAATGGAGCGGCTTGCGGA",
      "context": "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"
    },
    {
      "sequence": "GTCGATCGATCGATCGATCG",
      "context": "CGATGTCGATCGATCGATCGATCGATCGATCGATCGAT"
    },
    {
      "sequence": "ATCGATCGATCGATCGATCG",
      "context": "TAGCATCGATCGATCGATCGATCGATCGATCGATCGAT"
    }
  ]

process:
  - name: "score_candidate"
    for_each: "candidate in grna_candidates"
    run:
      - plugin: "gfl-ontarget-scorer"
        input_data: {
          "grna_sequence": "${candidate.sequence}",
          "genome_sequence": "${candidate.context}"
        }
        as_var: "score_result_${loop.index}"
    
    output:
      - scored_candidates: [
          {
            "sequence": "${candidate.sequence}",
            "efficiency": "${score_result_${loop.index}.result.efficiency_score}"
          }
          for candidate in grna_candidates
        ]

output:
  - candidate_scores: "${scored_candidates}"
```

### Advanced Configuration

```gfl
input:
  grna_sequence: "GCAATGGAGCGGCTTGCGGA"
  genome_context: "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"

run:
  - plugin: "gfl-ontarget-scorer"
    input_data: {
      "grna_sequence": "${grna_sequence}",
      "genome_sequence": "${genome_context}"
    }
    params: {
      "model_type": "deepcrispr",
      "custom_parameter": "value"
    }
    as_var: "advanced_result"

output:
  - advanced_scoring: "${advanced_result}"
```

## Integration with Other Plugins

The On-Target Scorer plugin is designed to work with other Genesis plugins:

- **[Off-Target Scorer](offtarget_scorer.md)**: For comprehensive CRISPR risk assessment
- **[CRISPR Evaluator](evaluator.md)**: For combining efficiency and risk scores
- **[CRISPR Visualizer](visualizer.md)**: For visualizing scoring results

## License

This plugin is part of the GeneForgeLang ecosystem and is licensed under the MIT License.

## Author

Manuel Menendez Gonzalez - manuelmenendes@fneurociencias.org