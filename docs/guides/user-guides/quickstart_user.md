## GeneForgeLang quickstart guide

GeneForgeLang (GFL) is a domain-specific language designed for genomic workflow specification, validation, and AI-powered analysis. This guide walks you through installation, your first workflows, custom schemas, and best practices to get you up and running quickly.

## Prerequisites

Before starting, make sure you have:
1. Python 3.9 or higher installed
2. GeneForgeLang installed (see [Installation Guide](installation.md))
3. Basic understanding of biological workflows

## 1. Installation

```bash
 # Check GeneForgeLang installation
python -c "import geneforgelang; print(f'Version: {geneforgelang.__version__}')"

# Check available plugins
gfl --list-plugins"
```

If both commands run without errors, you are ready to create your first workflow.

## 2. Your First Workflow

Create a file called my_first_workflow.gfl with the following content. It runs a BLAST search and filters the results:

```bash
# my_first_workflow.gfl
input:
  sequence: "ATGCGATCGATCGATCGATCGATCGATCG"
  database: "nt"

run:
  - plugin: "blast"
    operation: "blastn"
    sequence: "${sequence}"
    database: "${database}"
    expect_threshold: 0.001
    as_var: "blast_results"

process:
 - name: "filter_hits"
    input: "${blast_results}"
    operation: "filter"
    condition: "evalue < 0.01"
    as_var: "filtered_hits"

output:
  - blast_hits: "${filtered_hits}"
  - summary: "Found ${len(filtered_hits)} significant hits"
```

Run it and optionally save the output in different formats:

```bash
# Run the workflow
gfl run my_first_workflow.gfl

# Save results as JSON
gfl run my_first_workflow.gfl --output-format json --output-file results.json
```

The following workflow uses Genesis plugins to design and evaluate gRNA candidates:

```bash
# crispr_design.gfl
input:
  target_sequence: "ATGCGATCGATCGATCGATCG"
  genome_context: "ACGTGCAATGGAGCGGCTTGCGG"

design:
  entity: "gRNA"
  count: 5
  constraints:
    - "length(20)"
    - "gc_content(40, 60)"

evaluate:
  candidates: "${design.candidates}"
  - plugin: "gfl-ontarget-scorer"
    input:
      grna_sequence: "${candidate.sequence}"
      genome_sequence: "${genome_context}"
    as_var: "on_target_score"
  - plugin: "gfl-offtarget-scorer"
    input:
      grna_sequence: "${candidate.sequence}"
    params:
      max_mismatches: 3
      genome_reference: "GRCh38"
    as_var: "off_target_risk"
  - plugin: "gfl-crispr-evaluator"
    input:
      grna_candidates: "${evaluate.candidates}"
    params:
      weight_factor: 0.3
       as_var: "final_scores"

output:
  - ranked_candidates: "${final_scores.results}"
  - summary: "Evaluated ${len(final_scores.results)} gRNA candidates"
```

GFL supports dynamic variables and conditional steps:

```bash
input:
  organism: "human"
  quality_score: 85

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

process:
  - name: "high_quality_analysis"
    condition: "${quality_score >= 90}"
    plugin: "advanced_analysis"
  - name: "standard_analysis"
    condition: "${quality_score < 90}"
    plugin: "basic_analysis"
```

## 3. Custom schemas and IO contracts

Custom schemas let you define typed data contracts between workflow steps, catching errors before execution. Schemas are defined in separate YAML files and imported into your workflow.

Define a schema file:

```bash
# gene_expression_schemas.yml
version: 1.0
schemas:
  - name: GeneExpressionMatrix
    base_type: CSV
    description: "Gene expression data matrix"
    attributes:
      normalized:
        required: true
        value: true
      sample_count:
        required: true
        type: integer
      gene_count:
        required: true
        type: integer

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
```

Use the schema in a window
Import the schema file and reference schema types in your contract blocks:

```bash
# rna_seq_analysis.gfl
import_schemas:
  - ./schemas/gene_expression_schemas.yml

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

Validate Your Workflow
Run the validator after adding schemas to catch contract mismatches early:

```bash
gfl-validate rna_seq_analysis.gfl

# Expected output:
# ✓ Parsing successful
# ✓ Validation passed: 0 errors, 0 warnings
```

Common Schema Validation Errors

```bash
# Missing required attribute
Error: Required attribute 'sample_count' missing in contract outputs
       'raw_expression' for schema type 'GeneExpressionMatrix'
Fix:   Add the required 'sample_count' attribute to your contract definition

# Invalid attribute value
Error: Attribute 'clinical_significance' must have one of the allowed values,
       got 'unknown'
Fix:   Use one of: benign, likely_benign, uncertain, likely_pathogenic, pathogenic
```

NOTE: _For advanced schema features such as VCF/CUSTOM base types, complex validation rules, and phylogenetic data types, see the Advanced Schema Definitions reference document._

## 4. Best Practices

Workflow Organization
- Break complex workflows into smaller, reusable components.Modular Design:
- Use descriptive names for variables, steps, and outputs.Clear Naming:
- Add comments and include a metadata block with author, date, and version.Documentation:
- Include validation and conditional steps to handle edge cases.Error Handling:

Example metadata block:

```bash
metadata:
  author: "Dr. Jane Smith"
  institution: "University Research Lab"
  date: "2025-01-15"
  version: "1.0"
  notes: |
    This workflow validates CRISPR knockout efficiency.
    Expected results: >80% knockout efficiency.
```

Plugin Usage:
- Choose plugins that match your specific needs and verify compatibility.Plugin Selection:
- Experiment with parameters for optimal results on your data.Parameter Tuning:
- Specify plugin versions explicitly for reproducibility.Version Pinning:
- Monitor memory and CPU usage for large datasets.Resource Management:

Schema Best Practices
- Group related schemas in logical YAML files.Organize schema files:
- Include version information to track changes over time.Version your schemas:
- Run gfl-validate after every schema change.Validate early:
- Design schemas to be shared across multiple projects.Reuse schemas:

Common Syntax Pitfalls

```bash
# ❌ Wrong: dash in unquoted value
target_gene: TP-53

# ✅ Correct: quote special characters
target_gene: "TP-53"

# ❌ Wrong: lowercase tool name
tool: crispr_cas9

# ✅ Correct: standard tool name
tool: CRISPR_cas9

# ❌ Wrong: string instead of number
efficiency: "0.8"

# ✅ Correct: proper data type
efficiency: 0.8
```

## 5. Next Steps
Now that you have a working setup, explore these resources to go further:

- plugins_overview.md — browse available plugins and their parameters.Plugin Ecosystem —
- gfl_yaml/ — complete syntax reference.Language Specification —
- advanced_schemas.md — VCF/CUSTOM types and complex validation rules.Advanced Schema Definitions —
- tutorials/ — advanced workflow examples including batch processing and AI inference.Tutorials —
- api/ — REST API and client SDK documentation.API Reference —
- https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussionsCommunity —

Getting Help
1. Check the Troubleshooting Guide (installation.md#troubleshooting).
2. Review the API Reference (api/).
3. Search the project documentation.
4. Ask questions in the GitHub Discussion Forum.
