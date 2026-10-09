# Tangermeme Cis-Regulatory Logic & Context-Bound Claims

## Overview

Based on *Tangermeme: a toolkit for understanding cis-regulatory logic using deep learning models* (*Nature Methods*, Schreiber J. et al., 2025/2026), this feature integrates high-performance sequence-to-function (S2F) post-training interpretation into GeneForgeLang.

GeneForgeLang is thereby endowed with the capability to decipher **why and under what exact conditions a DNA sequence functions**, eliminating generic assertions and enabling both human researchers and autonomous AI agents to operate on contextualized, testable, and falsifiable hypotheses.

In GFL, biological assertions of regulatory activity, motif binding, and variant disruption are not global context-free truths. They are represented as **Context-Bound Claims**:
* **Claim**: The biological assertion (e.g. TF binding disruption, expression ablation).
* **ContextState**: The explicit contextual conditions (species, cell line/tissue, assay type, target factor, baseline vs stimulated condition).
* **Provenance**: Computational lineage and verification (model name, hash, attribution method, convergence delta verification).

## Architectural Capabilities

1. **Decoupled Sequence Manipulation & Attribution**:
   * Independent handling of mutations, deletions, dinucleotide shuffles, and marginalizations before computing model operations (DeepLIFT/SHAP, count predictions, profile shapes).
   * Built-in batching and low-precision (`bfloat16`) execution to prevent out-of-memory errors on large architectures.
   * Active monitoring and warning generation for DeepLIFT convergence delta instability.

2. **Recursive Variable-Length Seqlet Calling**:
   * Direct calling of variable-length functional seqlets via discrete convolution null distributions.
   * Dynamic subspan significance propagation ($P_{i,j} = \max(P_{i,j}, P_{i-1, j+1})$).
   * Elimination of fixed-width window distortion artifacts.

3. **Seqlet Annotation**:
   * Mapping seqlets to motif databases (e.g. JASPAR 2024 CORE) via `tomtom-lite`.

4. **Pairwise Cis-Regulatory Grammar & Spacing Matrix**:
   * Symmetric and asymmetric pairwise co-occurrence matrices ($P \in \mathbb{Z}^{n,m,m}$).
   * Spatial distance distributions between co-occurring transcription factors.

## GFL Syntax Example

```yaml
metadata:
  experiment_name: "PLD6 Promoter Cis-Regulatory Logic"
  version: "2.0.0"

experiment:
  tool: "tangermeme"
  type: "analysis"
  params:
    strategy: "cis_regulatory_syntax"
    target_gene: "PLD6"
    cell_line: "K562"
    assay: "ChIP-seq"
    model_name: "BPNet_MYC_fold0"
    attribution_method: "DeepLIFT"
    p_value_threshold: 0.01
    min_seqlet_len: 6
    max_seqlet_len: 25
    max_spacing_bp: 100
    symmetric_syntax: true
    motif_database:
      MYC: "CACGTG"
      E2F3: "TTTCGCGC"
      SP1: "GGGCGG"

analyze:
  strategy: "structural"
  data: "PLD6_promoter_attributions"
  thresholds:
    p_value: 0.01
    min_effect_size: 2.0
```
