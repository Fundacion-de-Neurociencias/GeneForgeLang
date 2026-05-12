# CRISPR Visualizer Plugin

A plugin that visualizes CRISPR efficiency and risk scores.

## Description

This plugin generates visualizations of CRISPR evaluation results, including on-target efficiency scores, off-target risk scores, and combined scores. It takes evaluation results from the CRISPR evaluator plugin and produces charts and graphs in various formats (HTML, PNG, SVG) to help researchers quickly identify the best gRNA candidates.

## Features

- **Multiple Visualization Formats**: Generate visualizations in HTML, PNG, or SVG formats
- **Chart Types**: Support for bar charts and scatter plots
- **Customizable Themes**: Light and dark themes for different preferences
- **Configurable Dimensions**: Set custom width and height for visualizations
- **GFL Integration**: Seamlessly integrates with GeneForgeLang's plugin system

## Installation

```bash
pip install gfl-plugin-crispr-visualizer
```

## Usage

Once installed, the plugin is automatically discovered by the GeneForgeLang service through entry points.

### Example GFL Workflow

```gfl
input:
  evaluation_results: [
    {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
      "on_target_score": 0.87,
      "off_target_risk": 0.23,
      "combined_score": 0.80
    },
    {
      "grna_sequence": "GTCGATCGATCGATCGATCG",
      "on_target_score": 0.65,
      "off_target_risk": 0.45,
      "combined_score": 0.52
    }
  ]

run:
  - plugin: "gfl-crispr-visualizer"
    input_data: {
      "evaluation_results": "${evaluation_results}"
    }
    params: {
      "output_format": "html",
      "chart_type": "bar"
    }
    as_var: "visualization"

output:
  - visualization: "${visualization.result.visualization}"
```

## Input Parameters

The plugin expects a dictionary with the following key:
- `evaluation_results`: List of evaluation results to visualize, each with:
  - `grna_sequence`: The gRNA sequence
  - `on_target_score`: On-target efficiency score
  - `off_target_risk`: Off-target risk score
  - `combined_score`: Combined score

Optional parameters:
- `output_format`: Format of the visualization ("html", "png", "svg") (default: "html")
- `chart_type`: Type of chart to generate ("bar", "scatter") (default: "bar")
- `theme`: Visualization theme ("light", "dark") (default: "light")
- `width`: Chart width in pixels (default: 800)
- `height`: Chart height in pixels (default: 600)

## Output

The plugin returns a dictionary with:
- `evaluation_results_count`: Number of results visualized
- `output_format`: The output format used
- `chart_type`: The chart type used
- `visualization`: The visualization content in the specified format

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "theme": "light",  # Visualization theme
    "width": 800,      # Chart width in pixels
    "height": 600      # Chart height in pixels
}

plugin = VisualizerPlugin(config=config)
```

## API Reference

### Class: VisualizerPlugin

#### Methods

##### `__init__(self, config: Optional[Dict[str, Any]] = None)`
Initialize the CRISPR Visualizer plugin.

**Parameters:**
- `config`: Optional configuration dictionary

##### `run(self, input_data: Any, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Generate visualizations of CRISPR evaluation results.

**Parameters:**
- `input_data`: Input data containing evaluation results
- `params`: Optional parameters for visualization

**Returns:**
- Dictionary containing visualization results

##### `validate_input(self, input_data: Any) -> bool`
Validate input data for the plugin.

**Parameters:**
- `input_data`: Input data to validate

**Returns:**
- True if input is valid, False otherwise

##### `_generate_bar_chart(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> str`
Generate a bar chart visualization.

**Parameters:**
- `data`: Evaluation results data
- `params`: Visualization parameters

**Returns:**
- Visualization content as string

##### `_generate_scatter_plot(self, data: List[Dict[str, Any]], params: Dict[str, Any]) -> str`
Generate a scatter plot visualization.

**Parameters:**
- `data`: Evaluation results data
- `params`: Visualization parameters

**Returns:**
- Visualization content as string

## Dependencies

- geneforgelang >= 1.0.0
- matplotlib >= 3.7.0
- plotly >= 5.15.0
- pandas >= 2.0.0
- numpy >= 1.24.0

## Development

### Setting Up for Development

```bash
git clone <repository-url>
cd gfl-plugin-crispr-visualizer
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black gfl_plugin_crispr_visualizer/
ruff check gfl_plugin_crispr_visualizer/
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required packages are installed
2. **Invalid Data Format**: Verify input data structure matches expected format
3. **Memory Errors**: For large datasets, consider reducing chart dimensions

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Basic Visualization

```gfl
input:
  evaluation_results: [
    {
      "grna_sequence": "GCAATGGAGCGGCTTGCGGA",
      "on_target_score": 0.87,
      "off_target_risk": 0.23,
      "combined_score": 0.80
    }
  ]

run:
  - plugin: "gfl-crispr-visualizer"
    input_data: {
      "evaluation_results": "${evaluation_results}"
    }
    as_var: "basic_viz"

output:
  - visualization: "${basic_viz.result.visualization}"
```

### Customized Visualization

```gfl
input:
  evaluation_results: [
    # ... evaluation results ...
  ]

run:
  - plugin: "gfl-crispr-visualizer"
    input_data: {
      "evaluation_results": "${evaluation_results}"
    }
    params: {
      "output_format": "png",
      "chart_type": "scatter",
      "theme": "dark",
      "width": 1000,
      "height": 800
    }
    as_var: "custom_viz"

output:
  - visualization_file: "${custom_viz.result.visualization}"
```

### Integration with Evaluation Pipeline

```gfl
# First evaluate candidates
evaluate:
  candidates: "${design.candidates}"

  # Score on-target efficiency
  - plugin: "gfl-ontarget-scorer"
    input:
      grna_sequence: "${candidate.sequence}"
      genome_sequence: "${genome_context}"
    as_var: "on_target_score"

  # Score off-target risk
  - plugin: "gfl-offtarget-scorer"
    input:
      grna_sequence: "${candidate.sequence}"
    as_var: "off_target_risk"

  # Combine scores
  - plugin: "gfl-crispr-evaluator"
    input:
      grna_candidates: "${evaluate.candidates}"
    as_var: "final_scores"

# Then visualize results
run:
  - plugin: "gfl-crispr-visualizer"
    input_data: {
      "evaluation_results": "${final_scores.results}"
    }
    params: {
      "output_format": "html",
      "chart_type": "bar"
    }
    as_var: "visualization"

output:
  - ranked_candidates: "${final_scores.results}"
  - visualization: "${visualization.result.visualization}"
```

## Integration with Other Plugins

The CRISPR Visualizer plugin is designed to work with other Genesis plugins:

- **[On-Target Scorer](ontarget_scorer.md)**: For efficiency scoring data
- **[Off-Target Scorer](offtarget_scorer.md)**: For risk assessment data
- **[CRISPR Evaluator](evaluator.md)**: For combined scoring results

## License

This plugin is part of the GeneForgeLang ecosystem and is licensed under the MIT License.

## Author

Manuel Menendez Gonzalez - manuelmenendes@fneurociencias.org
