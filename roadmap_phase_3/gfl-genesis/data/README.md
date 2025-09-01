# Data Directory

This directory contains the genomic data required for the GFL Genesis project.

## Required Data

1. **Reference Genome** (genome/):
   - GRCh38 (hg38) human genome assembly
   - FASTA format

2. **Genomic Annotations** (annotations/):
   - GENCODE/Ensembl annotations for TP53 gene
   - GTF/GFF3 format

## Data Sources

- **Genome Reference**: UCSC Genome Browser / Ensembl
- **Annotations**: GENCODE / Ensembl

## Download Instructions

The data should be downloaded before running the GFL workflow:

```bash
# Download reference genome
wget [URL to GRCh38 FASTA]

# Download annotations
wget [URL to TP53 annotations]
```

## Data Structure

```
data/
├── genome/
│   └── GRCh38.fa
└── annotations/
    └── TP53.gtf
```