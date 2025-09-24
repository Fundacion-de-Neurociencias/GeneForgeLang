# GFL Genesis Project

This project demonstrates the capabilities of the GeneForgeLang (GFL) ecosystem with the Genesis plugin suite for CRISPR gene editing workflows.

## Project Overview

The GFL Genesis project provides a complete workflow for designing and evaluating gRNA candidates for CRISPR gene editing applications. It leverages the specialized Genesis plugins to:

1. Design gRNA candidates for target genes
2. Evaluate on-target efficiency using machine learning models
3. Assess off-target risk using sequence alignment
4. Combine scores for final candidate ranking
5. Visualize results for easy interpretation

## Setup Instructions

1. Install the GFL ecosystem:
   ```bash
   make install
   ```

2. Setup the data environment for the Genesis project:
   ```bash
   make setup-genesis-data
   ```

This will automatically:
- Download the GRCh38 human reference genome
- Download GENCODE gene annotations
- Preprocess the genome for BLAST searches

## Project Structure

- `genesis.gfl`: Main GFL workflow script
- `main.py`: Python execution script (placeholder until GeneForge engine is ready)
- `scripts/`: Data fetching and preprocessing scripts
- `databases/`: Downloaded and processed reference data
- `results/`: Output directory for workflow results (created during execution)

## Required Dependencies

- GeneForgeLang core package
- Genesis plugins (ontarget-scorer, offtarget-scorer, evaluator, visualizer)
- NCBI BLAST+ toolkit
- Internet connection for initial data download

## Execution

Once the GeneForge engine is ready, the workflow can be executed using:
```bash
python main.py
```

## Data Sources

- Reference Genome: GENCODE GRCh38 primary assembly
- Gene Annotations: GENCODE v44 comprehensive annotation
