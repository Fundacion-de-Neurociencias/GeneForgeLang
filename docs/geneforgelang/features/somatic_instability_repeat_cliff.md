# Microsatellite Somatic Instability & Catastrophe Cliff Gating

## Overview

Developed in direct alignment with **Neurodiagnoses** and fundamental axioms of repeat expansion neurodegenerative diseases (Huntington's Disease, Spinocerebellar Ataxias, C9orf72 FTD/ALS, Myotonic Dystrophy).

### The Somatic Instability Paradigm

Historically, repeat expansions were evaluated using a single static scalar: the **germline repeat count** (e.g. $CAG = 42$). However, clinical onset and selective striatal projection neuron vulnerability are governed by **somatic expansion drift**:
1. Post-mitotic neurons undergo continuous, progressive repeat tract lengthening over decadal time horizons ($t$ years).
2. The drift rate is strongly modulated by DNA mismatch repair (MMR) pathway genes, such as **MSH3** risk variants and **MLH1** expression levels.
3. Pathological neurodegeneration does not progress linearly; it features a non-linear **toxicity catastrophe cliff** ($CAG \ge 150$) where cellular proteostasis fails and rapid apoptotic collapse occurs.

---

## Contract Architecture

### 1. `SomaticInstabilityContract`
- `target_gene`: Target repeat expansion locus (e.g. `HTT`, `C9orf72`, `ATXN1`).
- `germline_repeat_count` (alias `germline_cag_repeat`): Inherited baseline tract length.
- `cell_type`: Vulnerable anatomical sub-population (e.g. `striatal_projection_neuron`).
- `modifiers`: Quantitative genetic and epigenetic modulators (e.g. `msh3_genotype`, `mlh1_expression`).
- `simulation`: Stochastic drift configuration.

### 2. `SomaticDriftSimulationContract`
- `time_horizon_years`: Biological age or observation duration.
- `toxicity_cliff_threshold` (alias `toxicity_cliff_cag`): Critical threshold where cell viability collapses.
- `stochastic_drift_rate_per_year`: Basal units gained per year.
- `stochastic_dispersion`: Variance across single cells in the tissue.
- `drift_model`: Drift distribution mode (`stochastic_expansion`, `lognormal_population`, `poisson_jump_diffusion`).

### 3. Fast System 1 Decision Gating
Integrates with GFL's `DecisionContract` for discrete pre-screening:
- `SUB_THRESHOLD_LATENT`: Repeat length remains below the catastrophe cliff; cellular viability is intact.
- `CLIFF_COLLAPSE_IMMINENT`: Repeat length has crossed or is imminently crossing the catastrophe threshold ($P \ge \text{threshold}$).

---

## GFL Syntax

```yaml
metadata:
  name: "Huntington_Somatic_Instability_Gating"
  version: "1.0.0"

protocol:
  name: "HuntingtonSomaticInstabilitySimulator"
  target_gene: "HTT"
  locus: "chr4:3074877-3074933"
  repeat_unit: "CAG"
  germline_cag_repeat: 42
  cell_type: "striatal_projection_neuron"
  modifiers:
    msh3_genotype: "risk_variant_rs1805355"
    mlh1_expression: 1.15

  SomaticDrift:
    time_horizon_years: 65
    toxicity_cliff_cag: 150
    stochastic_drift_rate_per_year: 2.3
    stochastic_dispersion: 0.25

  decision:
    task_id: "NeurodegenerationTippingPoint"
    strategy: "SYSTEM_1_CALIBRATED"
    engine: "biodecision-4b"
    threshold: 0.85
    allowed_space:
      - "SUB_THRESHOLD_LATENT"
      - "CLIFF_COLLAPSE_IMMINENT"
```
