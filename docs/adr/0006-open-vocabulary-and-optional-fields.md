# ADR-0006: Open Vocabulary and Optional Fields

**Status:** Accepted  
**Date:** 2026-06-13  
**Supersedes:** Partial constraints in ADR-0002 (Syntactic Minimality)  
**Related:** ADR-0003 (Extension Orthogonality), ADR-0004 (Public Contract Stability), ADR-0005 (Semantic Behavioral Contract)

---

## Context

The GFL brutal test against 100 real scientific paper workflows (RNA-seq longitudinal, GWAS, CRISPR screens, pharmacogenomics, metagenomics) revealed three genuine architectural gaps:

1. **Hard-coded experiment type registry** — Six types were all that existed. Standard literature types like `RNAseq`, `GWAS`, `CRISPR_cas9`, `Metagenomics` were rejected as errors.
2. **`tool` mandatory in `experiment` blocks** — In real scientific methodology, the experimental phase (e.g., Illumina sequencing) is often agnostic of the downstream analytical software. Forcing a `tool` field conflates the experimental and analytical phases.
3. **`strategy` mandatory in `analyze` blocks** — When a `tool` already specifies the analytical method (e.g., `DESeq2`, `PLINK2`), a separate `strategy` field is redundant and artificial.
4. **Single-input constraint in `analyze`** — Multi-omic integrations (e.g., drug response IC50 + RNA expression) require multiple input sources. GFL's `input` singular field was insufficient.
5. **No `design` extension point in `experiment`** — Complex experimental designs (longitudinal, paired, covariate-rich) had nowhere to be expressed.

---

## Decision

### 1. Extended Experiment Type Vocabulary (open, additive)

The validator now recognises two tiers of experiment types:

- **Core types** (stable, ADR-0002): `gene_editing`, `sequencing`, `analysis`, `simulation`, `validation`, `metagenomics`
- **Extended literature-canonical types** (ADR-0006): `RNAseq`, `scRNAseq`, `GWAS`, `WGS`, `WES`, `ChIPseq`, `ATACseq`, `CRISPR_cas9`, `CRISPR_cas12`, `Metagenomics`, `Proteomics`, `Metabolomics`, `Pharmacogenomics`, `ClinicalTrial`, `spatial_transcriptomics`, `HiC`, `multiomics`

Unknown types beyond this set still produce a **WARNING** (not an ERROR), allowing future vocabulary growth without breaking existing workflows.

### 2. `tool` is Optional in `experiment` Blocks

Rationale: an experiment block describes *what was done*, not *with which software it will be analysed*. Platforms (e.g., Illumina NovaSeq) are not "tools" in the computational sense. Only `type` remains required.

If `tool` is present, it is validated as before. If absent, no error is raised.

### 3. `strategy` is Optional in `analyze` Blocks (recommended, not required)

Rationale: when `tool` is present in an `analyze` block, the strategy is implicit. Requiring both is redundant for real-world methodologies.

- If neither `strategy` nor `tool` is present → **WARNING** (informational).
- If `strategy` is present → validated against the known strategy vocabulary as before.

### 4. `inputs` List Accepted in `analyze` Blocks

A new field `inputs` (YAML list of strings) is accepted alongside the existing singular `input`. This enables multi-omic analysis patterns without breaking existing single-input workflows.

### 5. `design` Dict Accepted as Open Extension in `experiment` Blocks

A `design` field (YAML dictionary, content opaque to the core validator) is accepted in `experiment` blocks. Its interpretation is delegated to plugins (ADR-0003). This enables expression of:
- Longitudinal designs (`time_series`, `timepoints`)
- Paired sample designs (`pairing`)
- Statistical models (`design_formula`)
- Screen parameters (`library`, `moi`, `sgRNAs_per_gene`)

---

## Consequences

### Positive
- GFL can now express ≥ 5 major scientific domains (transcriptomics, genomics, CRISPR, pharmacogenomics, metagenomics) without validator rejections.
- The ClawBio brutal test regression remains at **100% parse and valid rate** — no breaking change.
- Real paper corpus (5 domains): **0 hard errors, 0 warnings** after fixes.
- The language remains a "Scientific Language", not a "ClawBio DSL" — it is now more neutral, not more specialised.

### Negative / Trade-offs
- A less strict `experiment` block means less automatic quality enforcement at the schema level. Downstream quality is deferred to plugin validators and human review.
- The extended type vocabulary is manually maintained. A future ADR may introduce a plugin-driven type registry.

### Neutralised Risk
- **Risk (from user):** GFL absorbs ClawBio semantics. This ADR moves in the opposite direction — GFL becomes *more generic*, not more ClawBio-specific.
