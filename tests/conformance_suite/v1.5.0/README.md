# GFL Conformance Test Suite v1.5.0

## Overview

This version of the GFL Conformance Test Suite introduces support for **genomic haplotyping** capabilities using Locityper. These tests validate the implementation of haplotype panel references, genotyping analysis workflows, and genotype-based reasoning.

## New Features

### Haplotype Panel References
- Tests for `haplotype_panel` field in loci definitions
- Validation of file path references to haplotype databases
- Support for complex, polymorphic genomic loci (HLA, KIR, etc.)

### Locityper Tool Integration  
- Tests for analyze blocks with `tool: "locityper"`
- Validation of locus target references
- Contract validation for genotyping inputs/outputs

### Genotyping Result Schemas
- Tests for `LocusGenotypeResult` schema structure
- Validation of required and optional fields
- Type checking for genotyping results

### Genotype Reasoning (Specification)
- Syntax for `genotype_contains()` predicate
- Syntax for `genotype_indicates_absence()` predicate
- Integration with rules blocks for clinical decisions

## Structure

- `locityper_haplotyping/` - Tests for Locityper-based haplotype genotyping
  - Haplotype panel references in loci
  - Locityper tool invocation
  - LocusGenotypeResult schema validation

## Usage

These tests validate that a GFL execution engine correctly:
1. Parses loci blocks with optional `haplotype_panel` field
2. Understands analyze blocks with `tool: "locityper"`
3. Validates contracts using LocusGenotypeResult type
4. Resolves locus references and accesses haplotype panel information

Run these tests during implementation to ensure proper support for genomic haplotyping features.

## Version Timeline

- **v1.2.0**: Timeline, rules/hypothesis, contracts/schemas
- **v1.3.0**: Loci management, spatial predicates, simulation
- **v1.4.0**: Large-scale genomic editing operations
- **v1.5.0**: Haplotype genotyping and complex locus analysis

## Clinical Applications

The haplotyping capabilities tested in this suite enable:
- Pharmacogenomic risk assessment (HLA-drug associations)
- Immunogenetic profiling (KIR gene content)
- Transplant compatibility screening
- Disease susceptibility analysis

These are critical capabilities for precision medicine applications of GeneForge.

