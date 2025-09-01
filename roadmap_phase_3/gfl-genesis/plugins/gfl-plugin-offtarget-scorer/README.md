# GFL Plugin: Off-Target Scorer

This plugin identifies and scores potential off-target sites throughout the genome using CFD scoring.

## Model Information

- **Model**: CFD (Cutting Frequency Determination) scoring algorithm
- **Source**: Doench, J. G., et al. (2016). Nature Biotechnology
- **Purpose**: Identify and score potential off-target cuts (lower score is better)

## Plugin Interface

Implements the `AnalyzerPlugin` interface from GFL.

### Input
- gRNA sequence (~20-23nt)

### Output
- Aggregate off-target risk score

## Installation

```bash
pip install -e .
```

## Usage

This plugin is designed to be used within GFL workflows as part of the CRISPR evaluation pipeline.