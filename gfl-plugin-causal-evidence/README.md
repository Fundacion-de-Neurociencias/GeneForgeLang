# gfl-plugin-causal-evidence

> GFL plugin adapter for **Causal Evidence Triangulation, Instrument Strength Verification, Horizontal Pleiotropy Invalidation, and Equity-Aware Population Checks**.
> **Amputatable by design** — ADR-0003 compliant.

## What this is

This plugin extends GeneForgeLang with formal **Causal Evidence & Epistemic Validation** primitives:

- **Instrument Strength Verification**: Ensures $F$-statistic $\ge 10$ to prevent weak instrument bias in Mendelian Randomization.
- **Horizontal Pleiotropy Invalidation**: Tests Egger intercept $p$-value ($p < 0.05$ invalidates causal claim).
- **Equity-Aware Population Check**: Verifies target vs validation population alignment (e.g. gnomAD stratified ancestry, AfriCArGene) to prevent automated European-ancestry bias propagation (*Corpas et al., Cell Genomics 2026*).

## GFL Usage

```yaml
experiment:
  tool: causal_evidence_triangulation
  type: analysis
  params:
    exposure: "LDL_cholesterol"
    outcome: "Coronary_artery_disease"
    instrument_f_stat: 24.5
    egger_intercept_pvalue: 0.42
    target_population: "AFR"
    validated_populations: ["AFR", "EUR", "EAS"]
```
