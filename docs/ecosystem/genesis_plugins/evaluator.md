# CRISPR Evaluator Plugin

A plugin orchestrator that combines on-target and off-target scores into a final ranking for CRISPR gRNA candidates.

## Description

This plugin acts as an orchestrator that combines the scores from the on-target and off-target scorer plugins. It takes a list of gRNA candidates and internally invokes the other two plugins for each candidate. It then combines both scores into a single final metric using a weighted formula: `combined_score = on_target_score - (w * off_target_risk)`. The plugin returns a ranked table of gRNAs with their three scores (on-target, off-target, and combined).

## Features

- **Score Integration**: Combines on-target efficiency and off-target risk scores
- **Candidate Ranking**: Ranks gRNA candidates based on combined scores
- **Configurable Weighting**: Adjustable weight factor for risk scoring
- **Plugin Orchestration**: Automatically invokes other Genesis plugins
- **Structured Output**: Returns ranked results in clean JSON format
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-crispr-evaluator
```

**Note**: This plugin requires the following dependencies to be installed:
- gfl-plugin-ontarget-scorer
- gfl-plugin-offtarget-scorer

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
run:
  - plugin: "gfl-crispr-evaluator"
    input_data: {
      "grna_candidates": [
        {
          "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
          "genome_sequence": "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"
        }
      ]
    }
    params: {
      "weight_factor": 0.3
    }
    as_var: "evaluation_results"

output:
  - ranked_candidates: "${evaluation_results.result.results}"
```

## Input Parameters

The plugin expects a dictionary with the following key:
- `grna_candidates`: List of gRNA candidates to evaluate, each with:
  - `grna_sequence`: The 20-nucleotide gRNA sequence (string)
  - `genome_sequence`: The surrounding genomic sequence (string)

Optional parameters:
- `weight_factor`: Weight factor for off-target risk in combined score (default: 0.3)

## Output

The plugin returns a dictionary with:
- `candidates_evaluated`: Number of candidates evaluated
- `weight_factor`: The weight factor used
- `results`: List of evaluation results, sorted by combined score (descending)
  - `grna_sequence`: The gRNA sequence
  - `on_target_score`: On-target efficiency score (0-1, higher is better)
  - `off_target_risk`: Off-target risk score (0-1, lower is better)
  - `combined_score`: Combined score (higher is better)

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "ontarget_plugin_config": {},  # Configuration for on-target scorer plugin
    "offtarget_plugin_config": {},  # Configuration for off-target scorer plugin
    "default_weight_factor": 0.3    # Default weight factor for risk scoring
}

plugin = EvaluatorPlugin(config=config)
```

## API Reference

### Class: EvaluatorPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the CRISPR Evaluator plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute the CRISPR evaluation process.

**Parameters:**
- `input_data`: Input data containing gRNA candidates
- `params`: Optional parameters for the evaluation process

**Returns:**
- Dictionary containing evaluation results

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
- Processed data with evaluation results

##### `_evaluate_single_grna(self, candidate: Dict[str, Any], weight_factor: float) -> Dict[str, Any]`
Evaluate a single gRNA candidate by combining on-target and off-target scores.

**Parameters:**
- `candidate`: Dictionary containing gRNA candidate information
- `weight_factor`: Weight factor for off-target risk in combined score

**Returns:**
- Evaluation result for the candidate

## Dependencies

- gfl-plugin-ontarget-scorer >= 0.1.0
- gfl-plugin-offtarget-scorer >= 0.1.0
- numpy >= 1.24.0
- pandas >= 2.0.0

## Development

### Setting Up for Development

```bash
git clone <repository-url>
cd gfl-plugin-crispr-evaluator
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_crispr_evaluator/
ruff check gfl_plugin_crispr_evaluator/
```

## Troubleshooting

### Common Issues

1. **Plugin Dependencies**: Ensure all required plugins are installed
2. **Sequence Format Errors**: Verify input sequences are properly formatted
3. **Memory Issues**: For large candidate lists, consider batch processing

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Candidate Evaluation

```gfl
input:
  grna_candidates: [
    {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
      "genome_sequence": "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"
    },
    {
      "grna_sequence": "GTCGATCGATCGATCGATCG",
      "genome_sequence": "CGATGTCGATCGATCGATCGATCGATCGATCGATCGAT"
    }
  ]

run:
  - plugin: "gfl-crispr-evaluator"
    input_data: "${grna_candidates}"
    params: {
      "weight_factor": 0.3
    }
    as_var: "evaluation_result"

output:
  - ranked_candidates: "${evaluation_result.result.results}"
  - total_evaluated: "${evaluation_result.result.candidates_evaluated}"
```

### Comprehensive CRISPR Design Pipeline

```gfl
# This workflow demonstrates a complete CRISPR design pipeline
# using all Genesis plugins

input:
  target_gene_sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
  genome_context: "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCGATCGATCG"
  candidate_count: 10

# Step 1: Generate gRNA candidates
design:
  entity: "gRNA"
  count: "${candidate_count}"
  constraints:
    - "length(20)"
    - "gc_content(40, 60)"
  as_var: "grna_candidates"

# Step 2: Evaluate candidates using the orchestrator
evaluate:
  plugin: "gfl-crispr-evaluator"
  input_data: {
    "grna_candidates": [
      {
        "grna_sequence": "${candidate.sequence}",
        "genome_sequence": "${genome_context}"
      }
      for candidate in grna_candidates
    ]
  }
  params: {
    "weight_factor": 0.25
  }
  as_var: "evaluation_results"

# Step 3: Select top candidates
process:
  - name: "select_top_candidates"
    input: "${evaluation_results.result.results}"
    operation: "slice"
    start: 0
    end: 5
    as_var: "top_candidates"

# Step 4: Visualize results
visualize:
  plugin: "gfl-crispr-visualizer"
  input_data: {
    "evaluation_results": "${top_candidates}"
  }
  params: {
    "output_format": "html",
    "chart_type": "bar"
  }
  as_var: "visualization"

output:
  - top_5_candidates: "${top_candidates}"
  - visualization_html: "${visualization.result.visualization}"
  - summary: "Evaluated ${evaluation_results.result.candidates_evaluated} candidates"
```

### Advanced Configuration with Custom Parameters

```gfl
input:
  grna_candidates: [
    {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
      "genome_sequence": "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCG"
    }
  ]

run:
  - plugin: "gfl-crispr-evaluator"
    input_data: "${grna_candidates}"
    params: {
      "weight_factor": 0.4,
      "ontarget_params": {
        "model_type": "deepcrispr"
      },
      "offtarget_params": {
        "max_mismatches": 2,
        "genome_reference": "GRCh38"
      }
    }
    as_var: "advanced_evaluation"

output:
  - advanced_results: "${advanced_evaluation.result.results}"
```

## Integration with Other Plugins

The CRISPR Evaluator plugin orchestrates the following Genesis plugins:

- **[On-Target Scorer](ontarget_scorer.md)**: For calculating cutting efficiency
- **[Off-Target Scorer](offtarget_scorer.md)**: For assessing off-target risk
- **[CRISPR Visualizer](visualizer.md)**: For visualizing evaluation results

## License

This plugin is part of the GeneForgeLang ecosystem and is licensed under the MIT License.

## Author

Manuel Menendez Gonzalez - manuelmenendes@fneurociencias.org