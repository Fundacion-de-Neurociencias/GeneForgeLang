# User Quickstart Guide

This guide will help you get started with GeneForgeLang by creating your first workflow. We'll walk through installation, creating a simple workflow, and running it with plugins.

## Prerequisites

Before starting, make sure you have:
1. Python 3.9 or higher installed
2. GeneForgeLang installed (see [Installation Guide](installation.md))
3. Basic understanding of biological workflows

## Step 1: Verify Installation

First, let's verify that GeneForgeLang is properly installed:

```bash
# Check GeneForgeLang installation
python -c "import geneforgelang; print(f'GeneForgeLang version: {geneforgelang.__version__}')"

# Check available plugins
gfl --list-plugins
```

## Step 2: Create Your First Workflow

Create a new file called `my_first_workflow.gfl` with the following content:

```gfl
# My First GeneForgeLang Workflow
# This workflow demonstrates basic GFL functionality

# Define input parameters
input:
  sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
  database: "nt"

# Run a BLAST search
run:
  - plugin: "blast"
    operation: "blastn"
    sequence: "${sequence}"
    database: "${database}"
    expect_threshold: 0.001
    as_var: "blast_results"

# Process the results
process:
  - name: "filter_hits"
    input: "${blast_results}"
    operation: "filter"
    condition: "evalue < 0.01"
    as_var: "filtered_hits"

# Output the results
output:
  - blast_hits: "${filtered_hits}"
  - summary: "Found ${len(filtered_hits)} significant hits"
```

## Step 3: Run Your Workflow

Execute your workflow using the GFL command-line tool:

```bash
gfl run my_first_workflow.gfl
```

## Step 4: View Results

The results will be displayed in the terminal and saved to output files. You can also specify output formats:

```bash
# Save results in JSON format
gfl run my_first_workflow.gfl --output-format json --output-file results.json

# Save results in YAML format
gfl run my_first_workflow.gfl --output-format yaml --output-file results.yaml
```

## Step 5: Create a CRISPR Design Workflow

Let's create a more advanced workflow using the Genesis plugins for CRISPR design:

```gfl
# CRISPR Design Workflow
# This workflow designs and evaluates gRNA candidates

# Define input sequences
input:
  target_sequence: "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
  genome_context: "ACGTGCAATGGAGCGGCTTGCGGATCGATCGATCGATCGATCGATCG"

# Generate gRNA candidates
design:
  entity: "gRNA"
  count: 5
  constraints:
    - "length(20)"
    - "gc_content(40, 60)"

# Evaluate candidates
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
    params:
      max_mismatches: 3
      genome_reference: "GRCh38"
    as_var: "off_target_risk"
  
  # Combine scores
  - plugin: "gfl-crispr-evaluator"
    input:
      grna_candidates: "${evaluate.candidates}"
    params:
      weight_factor: 0.3
    as_var: "final_scores"

# Visualize results
visualize:
  plugin: "gfl-crispr-visualizer"
  input:
    evaluation_results: "${final_scores.results}"
  params:
    output_format: "html"
    chart_type: "bar"
  as_var: "visualization"

# Output final results
output:
  - ranked_candidates: "${final_scores.results}"
  - visualization: "${visualization}"
  - summary: "Evaluated ${len(final_scores.results)} gRNA candidates"
```

## Step 6: Advanced Workflow Features

### Using Variables and Expressions

GFL supports variables and expressions for dynamic workflow configuration:

```gfl
input:
  organism: "human"
  analysis_type: "rnaseq"

variables:
  database_map:
    human: "GRCh38"
    mouse: "GRCm39"
  threads: "${os.cpu_count() // 2}"

run:
  - plugin: "gatk"
    operation: "variant_calling"
    reference_genome: "${database_map[organism]}"
    threads: "${threads}"
    as_var: "variants"
```

### Conditional Execution

Use conditions to control workflow execution:

```gfl
input:
  quality_score: 85

process:
  - name: "high_quality_analysis"
    condition: "${quality_score >= 90}"
    plugin: "advanced_analysis"
    # ... parameters
  
  - name: "standard_analysis"
    condition: "${quality_score < 90}"
    plugin: "basic_analysis"
    # ... parameters
```

## Step 7: Best Practices

### Workflow Organization

1. **Modular Design**: Break complex workflows into smaller, reusable components
2. **Clear Naming**: Use descriptive names for variables, steps, and outputs
3. **Documentation**: Add comments to explain complex logic
4. **Error Handling**: Include validation and error handling steps

### Plugin Usage

1. **Plugin Selection**: Choose plugins that match your specific needs
2. **Parameter Tuning**: Experiment with plugin parameters for optimal results
3. **Version Control**: Specify plugin versions for reproducibility
4. **Resource Management**: Monitor memory and CPU usage for large datasets

## Next Steps

- Explore the [Plugin Ecosystem](../ecosystem/plugins_overview.md) to learn about available plugins
- Read the [Language Specification](../gfl_yaml/) for detailed syntax information
- Check out the [Tutorials](../tutorials/) for more advanced examples
- Join the [Community](../support/community.md) to connect with other users

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](installation.md#troubleshooting)
2. Review the [API Reference](../api/)
3. Search the [Documentation](../)
4. Ask questions in the [Discussion Forum](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions)