# Getting Started Tutorial

This tutorial will guide you through creating your first GeneForgeLang (GFL) workflow, from basic syntax to advanced AI-powered analysis.

## What is GeneForgeLang?

GeneForgeLang (GFL) is a domain-specific language designed for:
- 🧬 **Genomic workflow specification** - Define complex experiments in structured format
- ✅ **Validation and verification** - Catch errors before execution
- 🤖 **AI-powered analysis** - Get intelligent predictions and insights
- 🔄 **Reproducibility** - Share and reproduce workflows easily

## Your First GFL Workflow

### Step 1: Basic CRISPR Experiment

Create a file called `my_first_workflow.gfl`:

```yaml
# Basic CRISPR gene editing experiment
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: GGGCCGGGCGGGCTCCCAGA
    vector: lentiviral
    cell_line: HEK293T

analyze:
  strategy: knockout_validation
  thresholds:
    efficiency: 0.8
    off_target_score: 0.1
```

### Step 2: Parse and Validate

```bash
# Parse the workflow
gfl-parse my_first_workflow.gfl

# Validate the workflow
gfl-validate my_first_workflow.gfl
```

Expected output:
```
✓ Parsing successful
✓ Validation passed: 0 errors, 0 warnings
```

### Step 3: Run AI Analysis

```bash
# Get AI predictions
gfl-inference analyze my_first_workflow.gfl --model heuristic
```

Expected output:
```
🤖 AI Analysis Results:
Prediction: edited (confidence: 85%)
Explanation: High-confidence CRISPR editing predicted based on:
- Strong guide RNA binding score
- Efficient Cas9 cutting site
- Low off-target probability
```

## Advanced Examples

### RNA-seq Differential Expression

```yaml
experiment:
  tool: illumina_novaseq
  type: rna_seq
  params:
    samples: 24
    reads_per_sample: 30M
    paired_end: true
    conditions:
      - control: 12
      - treated: 12

analyze:
  strategy: differential_expression
  thresholds:
    p_value: 0.01
    log2FoldChange: 1.5
    fdr: 0.05
  tools:
    - DESeq2
    - edgeR
```

### Protein Structure Analysis

```yaml
experiment:
  tool: alphafold2
  type: protein_structure
  params:
    target_gene: BRCA1
    analysis_type: domain_prediction
    confidence_threshold: 0.7

analyze:
  strategy: functional_domains
  params:
    domain_types:
      - kinase
      - nuclear_localization
      - dna_binding
    pathogenicity_prediction: true
```

### Variant Analysis Pipeline

```yaml
experiment:
  tool: whole_exome_seq
  type: variant_analysis
  params:
    genome_build: hg38
    coverage_threshold: 20x
    quality_score: 30

analyze:
  strategy: variant_classification
  filters:
    maf: 0.01
    functional_impact:
      - missense
      - nonsense
      - frameshift
  annotation:
    - ClinVar
    - COSMIC
    - gnomAD
```

## Using the Web Interface

### Launch Web Interface

```bash
gfl-server --web-only
```

Navigate to `http://127.0.0.1:7860`

### Web Interface Features

1. **📝 GFL Editor Tab**
   - Syntax highlighting
   - Real-time validation
   - Sample workflows
   - Error highlighting

2. **🤖 AI Inference Tab**
   - Model selection
   - Confidence scoring
   - Detailed explanations
   - Feature importance

3. **📊 Model Comparison Tab**
   - Side-by-side comparisons
   - Performance metrics
   - Model recommendations

4. **🔧 Management Tab**
   - System statistics
   - Model information
   - Health monitoring

5. **📦 Batch Processing Tab**
   - Multi-file upload
   - Batch analysis
   - Results export

## API Integration

### REST API Usage

```bash
# Start API server
gfl-server --api-only
```

```python
import requests

# Parse workflow
response = requests.post('http://localhost:8000/parse',
    json={'content': gfl_content})
ast = response.json()

# Run inference
response = requests.post('http://localhost:8000/infer',
    json={
        'content': gfl_content,
        'model_name': 'heuristic',
        'explain': True
    })
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.1%}")
```

### Client SDK Usage

```python
from gfl.client_sdk import create_client

# Create client
client = create_client('http://localhost:8000')

# Parse and analyze
result = client.parse(gfl_content)
inference = client.infer(gfl_content, model_name='heuristic')

print(f"Analysis: {inference.explanation}")
```

## Best Practices

### 1. Workflow Organization

```yaml
# Use clear, descriptive names
experiment:
  name: "BRCA1_knockout_HEK293T_validation"
  description: "Validate CRISPR knockout efficiency in HEK293T cells"

  # Group related parameters
  target:
    gene: BRCA1
    exon: 2
    coordinates: "chr17:43094290-43094390"

  # Specify experimental conditions clearly
  conditions:
    temperature: 37C
    co2_concentration: 5%
    culture_medium: DMEM
```

### 2. Parameter Validation

```yaml
# Include validation parameters
analyze:
  strategy: efficiency_validation
  controls:
    negative: untransfected_cells
    positive: known_efficient_gRNA

  # Set realistic thresholds
  thresholds:
    min_efficiency: 0.7
    max_off_target: 0.05
    confidence_level: 0.95
```

### 3. Documentation

```yaml
# Document your workflow
metadata:
  author: "Dr. Jane Smith"
  institution: "University Research Lab"
  date: "2025-01-15"
  version: "1.0"
  references:
    - "doi:10.1038/nature12111"

  notes: |
    This workflow validates CRISPR knockout efficiency
    using flow cytometry and Western blot analysis.
    Expected results: >80% knockout efficiency.
```

## Common Patterns

### Conditional Analysis

```yaml
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: ${TARGET_GENE}  # Variable substitution

analyze:
  strategy: adaptive_validation
  conditions:
    - if: efficiency < 0.5
      then:
        action: optimize_gRNA
        suggestions:
          - increase_concentration
          - extend_incubation
    - if: off_target > 0.1
      then:
        action: redesign_gRNA
        filter: specificity_score > 0.9
```

### Batch Processing

```yaml
experiment:
  tool: high_throughput_screening
  type: multi_target_editing
  params:
    targets:
      - gene: TP53
        priority: high
      - gene: BRCA1
        priority: high
      - gene: EGFR
        priority: medium

analyze:
  strategy: parallel_validation
  batch_size: 96
  quality_filters:
    - min_coverage: 100x
    - quality_score: 30
```

## Troubleshooting

### Common Errors

#### Syntax Errors
```yaml
# ❌ Wrong: Missing quotes
target_gene: TP-53  # Dash causes parsing error

# ✅ Correct: Use quotes for special characters
target_gene: "TP-53"
```

#### Validation Errors
```yaml
# ❌ Wrong: Invalid tool name
tool: crispr_cas9  # Lowercase not recognized

# ✅ Correct: Use standard tool names
tool: CRISPR_cas9
```

#### Type Mismatches
```yaml
# ❌ Wrong: String instead of number
efficiency: "0.8"

# ✅ Correct: Use proper data types
efficiency: 0.8
```

### Getting Help

1. **Validation Messages**: Always check validation output for specific error details
2. **Examples**: Browse the `examples/` directory for reference workflows
3. **Web Interface**: Use the built-in editor for syntax highlighting and validation
4. **Documentation**: Refer to [API Reference](API_REFERENCE.md) for detailed specifications
5. **Community**: Join discussions on [GitHub](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)

## Next Steps

Now that you've created your first GFL workflow:

1. **[Advanced Examples](language/examples.md)** - Explore complex workflow patterns
2. **[AI Features](ENHANCED_INFERENCE_SUMMARY.md)** - Learn about machine learning integration
3. **[Web Platform](WEB_API_IMPLEMENTATION_SUMMARY.md)** - Master the web interface
4. **[API Integration](api/client-sdk.md)** - Build custom applications
5. **[Best Practices](language/best-practices.md)** - Write production-ready workflows

## Sample Workflows Library

Explore our collection of pre-built workflows:

- **[CRISPR Workflows](../examples/enhanced_inference_demo.py)**
- **[RNA-seq Analysis](../examples/web_api_integration_demo.py)**
- **[Variant Calling](../gfl_examples.gfl)**
- **[Protein Analysis](../examples/)**

Happy workflow building! 🧬✨
