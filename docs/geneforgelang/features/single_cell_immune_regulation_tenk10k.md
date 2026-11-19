# Single-Cell Immune Regulation & Dynamic Cell States (TenK10K Paradigm)

## 1. Overview & Scientific Foundation

In human genetics, classical approaches (e.g. bulk tissue eQTLs from GTEx or naive GWAS variant-to-gene mappings) operate under the simplifying assumption that a genetic variant has an invariant, static effect on transcription. However, disease pathogenesis is fundamentally executed by specialized cellular lineages operating under continuous functional and activation states.

Phase 1 of the **TenK10K Initiative** (*Nature*, 2026; Cuomo, Spenceley, Tanudisastro et al., Powell & MacArthur; DOI: `10.1038/s41586-026-10721-2`), analyzing matched whole-genome sequencing (WGS) and single-cell RNA-sequencing (scRNA-seq) across **1,925 individuals and >5 million immune cells spanning 28 PBMC cell types**, establishes a new empirical paradigm:

1. **Cell-Type Specificity (50% Rule)**: Approximately 50% of expression quantitative trait loci (eQTLs) are specific to a single immune cell type or narrow lineage branch, rather than shared across the hematopoietic system.
2. **Distal Regulatory Architecture**: Cell-type-specific eQTLs are located significantly further away from the transcription start site ($>20\text{ kb}$) and strongly enriched in lineage-specific distal enhancers and promoters.
3. **Dynamic Cell-State Interaction eQTLs**: Thousands of eQTL effects are dynamically modulated along continuous biological functional axes (such as cytotoxicity in Natural Killer cells or interferon stimulation in monocytes).
4. **Cell Abundance QTLs (`caQTLs`)**: 164 genetic loci do not merely regulate transcript abundance per cell, but modulate the **proportional frequency and differentiation gating** of entire immune sublineages (e.g., *LYZ* in classical monocytes).
5. **High-Resolution GWAS Colocalization**: Over 60,000 Bayesian colocalizations connect complex traits and autoimmune diseases to specific immune cell subsets ($PP_4 \ge 0.80$).

GeneForgeLang (GFL) integrates this paradigm as a first-class language layer, enabling researchers to specify, simulate, and validate single-cell regulatory circuits conditioned on cell ontology and functional activation gradients.

---

## 2. Mathematical & Biophysical Formulation

### A. State-Dependent Interaction Kinetics
For an activation gradient $s \in [s_{\min}, s_{\max}] \subseteq [0.0, 1.0]$, the dynamic allelic effect size $\beta_{\text{eff}}(s)$ is modeled as:
$$\beta_{\text{eff}}(s) = \beta_0 + \gamma \cdot s$$

Where:
- $\beta_0$: Baseline marginal effect size in the resting state.
- $\gamma$: Cell-state interaction sensitivity slope ($\frac{\partial \beta}{\partial s}$).
- $s$: Continuous cellular functional score (e.g. cytotoxicity, exhaustion, interferon response).

Standard error propagation across the state gradient:
$$SE_{\text{eff}}(s) = \sqrt{SE(\beta_0)^2 + s^2 \cdot SE(\gamma)^2}$$
$$Z(s) = \frac{\beta_{\text{eff}}(s)}{SE_{\text{eff}}(s)}$$

### B. Cell Abundance Gating (caQTL Simplex Conservation)
To model the impact of an abundance QTL on the fraction $f_0$ of a target immune subpopulation without violating probability simplex constraints ($0 < f_{\text{perturbed}} < 1$):
$$f_{\text{perturbed}} = \frac{f_0 (1 + \Delta_{\text{caQTL}})}{1 + f_0 \cdot \Delta_{\text{caQTL}}}$$

Where $\Delta_{\text{caQTL}} \in [-1.0, 1.0]$ represents the fractional perturbation (e.g., $-0.18$ indicates an 18% depletion in subpopulation differentiation).

### C. Wakefield Approximate Bayes Factor (ABF) Colocalization
Evaluating shared causality between GWAS summary statistics ($\beta_{\text{GWAS}}, V_{\text{GWAS}} = SE_{\text{GWAS}}^2$) and single-cell eQTLs ($\beta_{\text{eQTL}}, V_{\text{eQTL}} = SE_{\text{eQTL}}^2$):
$$ABF = \sqrt{\frac{V}{V + W}} \exp\left( \frac{Z^2}{2} \cdot \frac{W}{V + W} \right)$$

With empirical prior effect variances $W_{\text{GWAS}} = 0.04$ and $W_{\text{eQTL}} = 0.16$. Posterior probability $PP_4$ of hypothesis $H_4$ (shared causal variant):
$$PP_4 = \frac{p_{12} \cdot ABF_{\text{GWAS}} \cdot ABF_{\text{eQTL}}}{1 + p_1 ABF_{\text{GWAS}} + p_2 ABF_{\text{eQTL}} + p_1 p_2 ABF_{\text{GWAS}} ABF_{\text{eQTL}} + p_{12} ABF_{\text{GWAS}} ABF_{\text{eQTL}}}$$
A threshold of $PP_4 \ge 0.80$ formally gates and validates colocalization.

---

## 3. Cell Ontology Mapping (28 TenK10K PBMC Lineages)

| Cell Lineage | Enum Identifier | Cell Ontology (CL) CURIE |
| :--- | :--- | :--- |
| **CD4+ Naive T** | `CD4_NAIVE` | `CL:0000895` |
| **CD4+ Central Memory T** | `CD4_CENTRAL_MEMORY` | `CL:0000897` |
| **CD4+ Effector Memory T** | `CD4_EFFECTOR_MEMORY` | `CL:0000905` |
| **CD4+ TEMRA** | `CD4_TEMRA` | `CL:0001084` |
| **CD4+ Regulatory T (Treg)** | `CD4_TREG` | `CL:0000815` |
| **CD4+ T Follicular Helper** | `CD4_FOLLICULAR_HELPER` | `CL:0002038` |
| **CD8+ Naive T** | `CD8_NAIVE` | `CL:0000900` |
| **CD8+ Central Memory T** | `CD8_CENTRAL_MEMORY` | `CL:0000907` |
| **CD8+ Effector Memory T** | `CD8_EFFECTOR_MEMORY` | `CL:0000910` |
| **CD8+ TEMRA** | `CD8_TEMRA` | `CL:0001085` |
| **CD8+ Cytotoxic T** | `CD8_CYTOTOXIC` | `CL:0000911` |
| **CD8+ Exhausted T** | `CD8_EXHAUSTED` | `CL:0002047` |
| **Gamma-Delta T** | `GAMMA_DELTA_T` | `CL:0000798` |
| **MAIT** | `MAIT_CELL` | `CL:0000940` |
| **Naive B** | `B_NAIVE` | `CL:0000788` |
| **Switched Memory B** | `B_SWITCHED_MEMORY` | `CL:0000972` |
| **Unswitched Memory B** | `B_UNSWITCHED_MEMORY` | `CL:0000970` |
| **Plasma Cell** | `PLASMA_CELL` | `CL:0000786` |
| **NK CD56-dim Cytotoxic** | `NK_CD56_DIM` | `CL:0000938` |
| **NK CD56-bright Cytokine**| `NK_CD56_BRIGHT` | `CL:0000939` |
| **Classical Monocyte** | `MONOCYTE_CLASSICAL` | `CL:0000860` |
| **Non-Classical Monocyte** | `MONOCYTE_NON_CLASSICAL` | `CL:0000875` |
| **Intermediate Monocyte** | `MONOCYTE_INTERMEDIATE` | `CL:0002396` |
| **Conventional DC 1 (cDC1)** | `DC_CONVENTIONAL_1` | `CL:0000990` |
| **Conventional DC 2 (cDC2)** | `DC_CONVENTIONAL_2` | `CL:0002399` |
| **Plasmacytoid DC (pDC)** | `DC_PLASMACYTOID` | `CL:0000784` |
| **Innate Lymphoid (ILC)** | `ILC_UNCOMMITTED` | `CL:0001065` |
| **Platelet** | `PLATELET` | `CL:0000233` |

---

## 4. GFL Language Syntax

A single-cell regulatory circuit can be authored using the top-level block `single_cell_regulation` (or its aliases `sc_regulation` / `cellular_context`):

```gfl
single_cell_regulation:
  contract_id: "nk_gzmb_cytotoxicity_circuit"
  target_gene: "GZMB"
  variant: "chr19:45823101:A>G"
  variant_type: "snv"
  cell_type: "CL:0000938"  # NK CD56-dim
  qtl_type: "cell_state_interaction"
  is_cell_type_specific: true
  is_distal_enhancer: false
  distance_to_tss_bp: 1250
  beta_marginal: 0.28
  standard_error: 0.035
  p_value_empirical: 2.4e-12

  state_interaction:
    state_axis: "cytotoxicity"
    beta_baseline: 0.14
    gamma_interaction: 0.52
    state_range: [0.10, 0.95]
    p_value_interaction: 4.1e-8
    fdr: 0.01

  abundance_qtl:
    target_cell_type: "CL:0000860"  # Classical Monocyte
    effect_size_delta: -0.18
    baseline_fraction: 0.12
    driver_gene: "LYZ"
    differentiation_mechanism: "monocyte_subpopulation_fate_bias"
    p_value: 3.2e-14

  colocalization_gate:
    gwas_trait_id: "EFO:0003885"  # Multiple Sclerosis
    gwas_trait_name: "Multiple Sclerosis Susceptibility"
    candidate_gene: "GZMB"
    posterior_prob_h4: 0.92
    pp4_threshold: 0.80
    credible_set_size: 2
    lead_variant_rsid: "rs11586201"
```

---

## 5. Synergies Across the GeneForge Ecosystem

- **Mesoscopic DNA Breathing**: Cell-type-specific distal eQTLs reside in accessible enhancers where thermal breathing bubbles facilitate lineage-defining transcription factor engagement.
- **ProTok Residue Tokens**: Protein structural effects from coding variants map directly to their downstream regulatory consequences in specific immune cell types.
- **Carbon-X**: Single-cell eQTL effect sizes and cell-abundance deltas serve as high-fidelity ground truth to calibrate Carbon-X conversational variant interpretations.
- **Neurodiagnoses Axis 3**: Bridges the systemic neuroimmune component (monocyte infiltration, microglial activation, and peripheral T-cell homing) to the tridimensional etiological framework.
