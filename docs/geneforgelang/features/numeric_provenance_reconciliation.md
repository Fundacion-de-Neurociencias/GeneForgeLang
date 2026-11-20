# Strict By-Reference Provenance & Numeric Reconciliation Gate

## Overview & Language Rationale

Inspired by the **Human Protein Atlas v26 / AtlasAI** data-integrity discipline, GeneForgeLang (GFL) enforces two compile-time invariants on quantitative workflows and reports (`numeric_provenance:`, `reconciled_report:`):

1. **No Model Retype (`strict_reference`)**: Downstream analytical or reporting claims cannot supply raw numeric values without a typed by-reference handle (`ArtifactRef` or `${step.output}`), preventing agents from altering or inventing numbers between steps.
2. **Citation-to-Record Reconciliation (`require_reconciliation: true`)**: A GFL report contract is rejected during validation unless every declared numeric claim matches its cited `source_records` entry within the declared tolerance.

*(Active analytical execution, visualization rendering, and conversational tool orchestration remain outside GFL in the downstream GeneForge runtime.)*

---

## Declarative GFL Syntax

```gfl
numeric_provenance:
  contract_id: "hpa_v26_trem2_microglia_reconciliation_01"
  provenance_binding: "strict_reference"
  require_reconciliation: true
  source_records:
    HPA_ENSG00000095977_RNA:
      microglia_ntpm: 142.8
  cited_claims:
    - claim_id: "trem2_microglia_rna_level"
      metric_key: "microglia_ntpm"
      declared_value: 142.8
      source_record_id: "HPA_ENSG00000095977_RNA"
      artifact_ref: "${hpa_rna_query_01.microglia_ntpm}"
      tolerance: 1e-6
```
