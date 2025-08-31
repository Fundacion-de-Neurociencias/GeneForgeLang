# GFL Plugin: CRISPR Evaluator

This plugin orchestrates the evaluation of gRNA sequences by calling both the on-target and off-target scorer plugins.

## Functionality

The CRISPR Evaluator plugin serves as an orchestrator that:

1. Takes a list of gRNA sequences as input
2. Calls the on-target scorer plugin to evaluate cutting efficiency
3. Calls the off-target scorer plugin to evaluate off-target risk
4. Combines the results into a comprehensive evaluation table

## Plugin Interface

Implements the `AnalyzerPlugin` interface from GFL.

### Input
- List of gRNA sequences

### Output
- Comprehensive evaluation table with both on-target and off-target scores

## Installation

```bash
pip install -e .
```

## Usage

This plugin is designed to be used within GFL workflows as the main evaluation pipeline for CRISPR gRNA design.