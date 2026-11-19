# ClawBio × GFL Stress Test Report

**Run**: `2026-06-13T10:50:53.179212+00:00`
**GFL available**: ✅

## Summary

| Metric | Value |
|--------|-------|
| Total fixtures | 10 |
| Parse passed | 10 |
| Parse failed | 0 |
| Validate passed (clean) | 5 |
| Validate warned | 4 |
| Validate failed | 2 |

## Per-Fixture Results

### CB_001 — PharmGx Reporter

- **Domain**: pharmacogenomics
- **Parse**: ✅
- **Validate**: ✅
- **Errors (1)**:
  - `[WARNING] Unknown tool 'clawbio_pharmgx' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_pharmgx' plugin is available`
- **Warnings (1)**:
  - `[WARNING] Unknown tool 'clawbio_pharmgx' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_pharmgx' plugin is available`
- **Elapsed**: 5.0 ms

### CB_002 — CRISPR Screen Triage

- **Domain**: functional-genomics
- **Parse**: ✅
- **Validate**: ✅
- **Elapsed**: 6.2 ms

### CB_003 — RNA-seq DE

- **Domain**: transcriptomics
- **Parse**: ✅
- **Validate**: ✅
- **Elapsed**: 7.9 ms

### CB_004 — GWAS Lookup

- **Domain**: population-genomics
- **Parse**: ✅
- **Validate**: ✅
- **Errors (1)**:
  - `[WARNING] Unknown tool 'clawbio_gwas_lookup' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_gwas_lookup' plugin is available`
- **Warnings (1)**:
  - `[WARNING] Unknown tool 'clawbio_gwas_lookup' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_gwas_lookup' plugin is available`
- **Elapsed**: 8.1 ms

### CB_005 — scRNA Orchestrator

- **Domain**: single-cell
- **Parse**: ✅
- **Validate**: ❌
- **Errors (1)**:
  - `Validator exception: 'charmap' codec can't encode character '\u2192' in position 14: character maps to <undefined>`
- **Elapsed**: 10.0 ms

### CB_006 — Equity Scorer

- **Domain**: population-diversity
- **Parse**: ✅
- **Validate**: ✅
- **Elapsed**: 8.0 ms

### CB_007 — Pathway Enricher

- **Domain**: functional-genomics
- **Parse**: ✅
- **Validate**: ✅
- **Elapsed**: 7.7 ms

### CB_008 — DnaSP Population Genetics

- **Domain**: population-genetics
- **Parse**: ✅
- **Validate**: ✅
- **Errors (1)**:
  - `[WARNING] Unknown analysis strategy 'population_genetics' (SEMANTIC004)
  Context: valid_strategies=['pathway', 'expression', 'functional', 'comparative', 'structural', 'longitudinal', 'variant', 'differential']
  Suggested fixes:
    - Use one of: comparative, differential, expression, functional, longitudinal, pathway, structural, variant`
- **Warnings (1)**:
  - `[WARNING] Unknown analysis strategy 'population_genetics' (SEMANTIC004)
  Context: valid_strategies=['pathway', 'expression', 'functional', 'comparative', 'structural', 'longitudinal', 'variant', 'differential']
  Suggested fixes:
    - Use one of: comparative, differential, expression, functional, longitudinal, pathway, structural, variant`
- **Gap probe** (`MISSING_STRATEGY_ENUM`): Add 'population_genetics' to AnalysisStrategy enum in gftypes.py. This domain covers nucleotide diversity, selection tests, demographic inference, and molecular evolution metrics.

- **Elapsed**: 11.0 ms

### CB_009 — Metagenomics Profiler

- **Domain**: metagenomics
- **Parse**: ✅
- **Validate**: ✅
- **Errors (2)**:
  - `[WARNING] Unknown tool 'clawbio_metagenomics_profiler' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_metagenomics_profiler' plugin is available`
  - `[WARNING] Unknown experiment type 'metagenomics' (SEMANTIC005)
  Context: valid_types=['simulation', 'analysis', 'gene_editing', 'sequencing', 'validation']
  Suggested fixes:
    - Use one of: simulation, analysis, gene_editing, sequencing, validation`
- **Warnings (2)**:
  - `[WARNING] Unknown tool 'clawbio_metagenomics_profiler' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9', 'WES', 'targeted_seq', 'CRISPR_prime_editor', 'ATACseq', 'RNAseq', 'CRISPR_cas12', 'WGS', 'ChIPseq']
  Suggested fixes:
    - Use a known tool or ensure 'clawbio_metagenomics_profiler' plugin is available`
  - `[WARNING] Unknown experiment type 'metagenomics' (SEMANTIC005)
  Context: valid_types=['simulation', 'analysis', 'gene_editing', 'sequencing', 'validation']
  Suggested fixes:
    - Use one of: simulation, analysis, gene_editing, sequencing, validation`
- **Gap probe** (`MISSING_EXPERIMENT_TYPE`): Add 'metagenomics' to ExperimentType enum in gftypes.py. This is a distinct sequencing modality (shotgun WGS of microbial communities) that differs semantically from single-organism sequencing.

- **Elapsed**: 8.6 ms

### CB_010 — Genome Compare

- **Domain**: comparative-genomics
- **Parse**: ✅
- **Validate**: ✅
- **Elapsed**: 8.8 ms

## Identified Gaps

Gaps are derived from explicit `gap_probe` annotations in fixtures
and from systematic patterns in validation errors.

### Gap 1: MISSING_STRATEGY_ENUM

- **missing_value**: population_genetics
- **current_values**:
  - differential
  - pathway
  - variant
  - expression
  - structural
- **recommendation**: Add 'population_genetics' to AnalysisStrategy enum in gftypes.py. This domain covers nucleotide diversity, selection tests, demographic inference, and molecular evolution metrics.


### Gap 2: MISSING_EXPERIMENT_TYPE

- **missing_value**: metagenomics
- **current_values**:
  - gene_editing
  - sequencing
  - analysis
  - simulation
  - validation
- **recommendation**: Add 'metagenomics' to ExperimentType enum in gftypes.py. This is a distinct sequencing modality (shotgun WGS of microbial communities) that differs semantically from single-organism sequencing.


### Gap 3: VALIDATION_PATTERN

- **pattern**: Unknown tool
- **count**: 6
- **examples**:
  - CB_001: [WARNING] Unknown tool 'clawbio_pharmgx' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9',
  - CB_001: [WARNING] Unknown tool 'clawbio_pharmgx' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas9',
  - CB_004: [WARNING] Unknown tool 'clawbio_gwas_lookup' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas
  - CB_004: [WARNING] Unknown tool 'clawbio_gwas_lookup' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', 'CRISPR_cas
  - CB_009: [WARNING] Unknown tool 'clawbio_metagenomics_profiler' (SEMANTIC003)
  Context: suggested_tools=['CRISPR_base_editor', '

### Gap 4: VALIDATION_PATTERN

- **pattern**: Unknown experiment type
- **count**: 2
- **examples**:
  - CB_009: [WARNING] Unknown experiment type 'metagenomics' (SEMANTIC005)
  Context: valid_types=['simulation', 'analysis', 'gene_e
  - CB_009: [WARNING] Unknown experiment type 'metagenomics' (SEMANTIC005)
  Context: valid_types=['simulation', 'analysis', 'gene_e
