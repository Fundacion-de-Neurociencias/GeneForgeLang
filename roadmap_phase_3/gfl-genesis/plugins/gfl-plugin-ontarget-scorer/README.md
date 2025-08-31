# GFL Plugin: On-Target Scorer

This plugin predicts the on-target cutting efficiency of a given gRNA sequence using the DeepHF model.

## Model Information

- **Model**: DeepHF (Deep learning for predicting CRISPR-Cas9 cleavage efficiency with high fidelity)
- **Source**: Wang, D., et al. (2019). Nature Biotechnology
- **Purpose**: Predict on-target cutting efficiency of a gRNA sequence (0 to 1 score)

## Plugin Interface

Implements the `AnalyzerPlugin` interface from GFL.

### Input
- gRNA sequence (~20-23nt)
- Genomic sequence surrounding the target site

### Output
- On-target efficiency score (0-1)

## Installation

```bash
pip install -e .
```

## Usage

This plugin is designed to be used within GFL workflows as part of the CRISPR evaluation pipeline.