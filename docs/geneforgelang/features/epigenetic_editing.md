# Epigenetic Editing in GFL

## Overview

GFL v1.6.0 introduces support for **epigenetic editing** - the ability to modify gene expression through changes to chromatin state rather than DNA sequence alterations. This capability models tools like CRISPRoff and CRISPRon that create heritable, reversible changes in gene expression without causing DNA double-strand breaks.

## Conceptual Foundation

### Epigenetic vs Genetic Editing

Traditional CRISPR (Cas9) creates **permanent DNA sequence changes**:
- Causes double-strand breaks (DSBs)
- Risk of off-target mutations
- Irreversible modifications

Epigenetic editors (CRISPRoff/on) create **reversible expression changes**:
- Modify DNA methylation patterns
- No DNA sequence alteration
- Heritable through cell divisions
- Reversible with opposing tools

### Why Model Epigenetic State?

Understanding and manipulating epigenetic state enables:
- **Safer gene silencing**: No DSBs or permanent mutations
- **Reversible therapeutics**: Can be undone if needed
- **Long-lasting effects**: Methylation persists through divisions
- **Complex regulation**: Model real biological gene regulation

## GFL Syntax for Epigenetic Editing

### 1. Representing Epigenetic State

Define the epigenetic state of genomic regions using the `epigenetic_state` block:

```yaml
epigenetic_state:
  - region: locus(VEGFA_Promoter)
    marks:
      - type: "DNA_methylation"
        pattern: "CpG_islands"
        level: "hypermethylated"  # hypermethylated, hypomethylated, normal
        percentage: 85.0
      - type: "histone_modification"
        mark: "H3K9me3"
        enrichment: "high"
    expression_consequence: "silenced"

  - region: locus(MYC_Enhancer)
    marks:
      - type: "DNA_methylation"
        level: "hypomethylated"
        percentage: 15.0
      - type: "histone_modification"
        mark: "H3K27ac"
        enrichment: "high"
    expression_consequence: "active"
```

**Key Concepts:**
- `region`: References a locus or genomic element
- `marks`: List of epigenetic modifications
  - `DNA_methylation`: CpG methylation state
  - `histone_modification`: Chromatin marks (H3K4me3, H3K27ac, etc.)
- `expression_consequence`: Predicted effect on gene expression

### 2. Epigenetic Editing Operations

Use the `edit` block with epigenetic modifiers:

#### CRISPRoff - Add DNA Methylation (Gene Silencing)

```yaml
loci:
  - id: VEGFA_Promoter
    chromosome: "chr6"
    start: 43737946
    end: 43738946
    description: "VEGFA promoter region for therapeutic silencing"

edit:
  tool: "CRISPRoff"
  target: locus(VEGFA_Promoter)
  guide_rna: "GGGCGAGCGCGGCGGCTCGG"
  operation:
    add_methylation:
      region: locus(VEGFA_Promoter)
      pattern: "CpG_islands"
      target_level: "hypermethylated"
      mechanism: "DNMT3A_DNMT3L_recruitment"
  expected_outcome:
    expression_change:
      gene: "VEGFA"
      from_level: "normal"
      to_level: "silenced"
      persistence: "heritable"
      reversibility: true
```

#### CRISPRon - Remove DNA Methylation (Gene Activation)

```yaml
loci:
  - id: BDNF_Promoter_IV
    chromosome: "chr11"
    start: 27722824
    end: 27723824
    description: "BDNF promoter IV, therapeutically silenced by methylation"

edit:
  tool: "CRISPRon"
  target: locus(BDNF_Promoter_IV)
  guide_rna: "GCCGAGCGCGGCGATCGCGG"
  operation:
    remove_methylation:
      region: locus(BDNF_Promoter_IV)
      mechanism: "TET1_recruitment"
      target_level: "hypomethylated"
  expected_outcome:
    expression_change:
      gene: "BDNF"
      from_level: "silenced"
      to_level: "reactivated"
      persistence: "stable_through_divisions"
```

### 3. Comparing Editing Modalities

GFL can now express and compare different gene regulation strategies:

```yaml
# Define the target gene locus
loci:
  - id: Target_Gene_Locus
    chromosome: "chr1"
    start: 1000000
    end: 1050000

# Strategy 1: Traditional Cas9 knockout
experiment:
  name: "Cas9_Knockout_Strategy"
  tool: "CRISPR_cas9"
  edit_type: "knockout"
  target: locus(Target_Gene_Locus)
  characteristics:
    permanence: "irreversible"
    safety_risk: "DSBs_off_target_mutations"
    expression_outcome: "complete_loss"

# Strategy 2: CRISPRi repression (requires continuous expression)
experiment:
  name: "CRISPRi_Repression_Strategy"
  tool: "CRISPRi_dCas9_KRAB"
  target: locus(Target_Gene_Locus)
  characteristics:
    permanence: "transient_requires_maintenance"
    safety_risk: "minimal"
    expression_outcome: "reversible_silencing"

# Strategy 3: CRISPRoff epigenetic silencing
experiment:
  name: "CRISPRoff_Epigenetic_Strategy"
  tool: "CRISPRoff"
  operation:
    add_methylation:
      region: locus(Target_Gene_Locus)
  characteristics:
    permanence: "heritable_long_lasting"
    safety_risk: "no_DSBs"
    expression_outcome: "stable_silencing"
    reversibility: "can_reverse_with_CRISPRon"

# Reasoning: Choose optimal strategy based on requirements
rules:
  - id: R_Strategy_Selection
    description: "Select editing strategy based on therapeutic requirements"
    if:
      - requires_reversibility: true
      - requires_heritability: true
      - minimize_genotoxicity: true
    then:
      - select_strategy: "CRISPRoff_Epigenetic_Strategy"
      - rationale: "Combines reversibility, heritability, and safety"
```

### 4. Epigenetic State Queries in Rules

Reason about epigenetic modifications and their consequences:

```yaml
rules:
  - id: R_Methylation_Silencing_Link
    description: "Promoter hypermethylation leads to gene silencing"
    if:
      - epigenetic_state_is:
          region: locus(VEGFA_Promoter)
          mark_type: "DNA_methylation"
          level: "hypermethylated"
          threshold: 70.0
    then:
      - predict_expression:
          gene: "VEGFA"
          level: "silenced"
          mechanism: "methylation_mediated_silencing"

  - id: R_H3K27ac_Activation_Link
    description: "H3K27ac enrichment indicates active regulatory regions"
    if:
      - epigenetic_state_is:
          region: locus(Enhancer_Region)
          mark_type: "histone_modification"
          mark: "H3K27ac"
          enrichment: "high"
    then:
      - predict_activity:
          element: "Enhancer_Region"
          state: "active"
```

### 5. Temporal Dynamics of Epigenetic Changes

Model the establishment and maintenance of epigenetic modifications:

```yaml
timeline:
  - at: "t0"
    description: "Baseline state before CRISPRoff treatment"
    actions:
      - measure_epigenetic_state:
          region: locus(Target_Promoter)
          output: "baseline_methylation"

  - at: "t1_CRISPRoff_treatment"
    description: "Apply CRISPRoff for 48 hours"
    actions:
      - apply_edit:
          tool: "CRISPRoff"
          operation:
            add_methylation:
              region: locus(Target_Promoter)
          duration: "48_hours"

  - at: "t2_post_treatment_72h"
    description: "72 hours after CRISPRoff removal"
    actions:
      - measure_epigenetic_state:
          region: locus(Target_Promoter)
          output: "early_methylation"
      - measure_expression:
          gene: "Target_Gene"
          output: "early_expression"

  - at: "t3_post_treatment_30days"
    description: "30 days post-treatment (assess heritability)"
    actions:
      - measure_epigenetic_state:
          region: locus(Target_Promoter)
          output: "stable_methylation"
      - measure_expression:
          gene: "Target_Gene"
          output: "stable_expression"

  - at: "t4_reversal_CRISPRon"
    description: "Apply CRISPRon to reverse silencing"
    actions:
      - apply_edit:
          tool: "CRISPRon"
          operation:
            remove_methylation:
              region: locus(Target_Promoter)
          duration: "48_hours"

  - at: "t5_post_reversal"
    description: "Verify gene reactivation"
    actions:
      - measure_expression:
          gene: "Target_Gene"
          output: "reactivated_expression"

# Validate expected dynamics
rules:
  - id: R_Methylation_Persistence
    description: "CRISPRoff-induced methylation persists after tool removal"
    if:
      - methylation_at_t3_greater_than:
          threshold: 70.0
    then:
      - validation_passed: "methylation_is_heritable"

  - id: R_Expression_Correlates_Methylation
    description: "Gene expression inversely correlates with methylation"
    if:
      - methylation_level: "hypermethylated"
    then:
      - expression_should_be: "low_or_silenced"
```

## Complete Example: Therapeutic VEGFA Silencing

```yaml
# Therapeutic Silencing of VEGFA for Anti-Angiogenesis
# =====================================================
# Models CRISPRoff-mediated epigenetic silencing as described in
# Nunez et al. (2021) Cell

# Define target locus
loci:
  - id: VEGFA_Promoter
    chromosome: "chr6"
    start: 43737946
    end: 43738946
    description: "VEGFA promoter - target for anti-angiogenic therapy"
    cpg_islands:
      - start: 43738100
        end: 43738600
        density: "high"

# Baseline epigenetic state
epigenetic_state:
  - region: locus(VEGFA_Promoter)
    baseline_marks:
      - type: "DNA_methylation"
        level: "hypomethylated"
        percentage: 20.0
    expression_consequence: "active"

# Apply CRISPRoff for therapeutic silencing
edit:
  name: "VEGFA_Therapeutic_Silencing"
  tool: "CRISPRoff"
  target: locus(VEGFA_Promoter)
  guide_rnas:
    - "GGGCGAGCGCGGCGGCTCGG"
    - "GCGGCGGCTCGGCGCTGAGG"  # Tiling strategy
  operation:
    add_methylation:
      region: locus(VEGFA_Promoter)
      target_cpgs: "promoter_cpg_islands"
      target_level: "hypermethylated"
      target_percentage: 85.0
      mechanism:
        effector: "DNMT3A_DNMT3L_fusion"
        recruitment: "dCas9_guided"
  parameters:
    delivery_method: "AAV9_vector"
    dosage: "1e11_genome_copies"
    treatment_duration: "48_hours"
    
# Expected outcomes and validation
hypothesis:
  id: "H_CRISPRoff_Durable_Silencing"
  description: "CRISPRoff induces heritable VEGFA silencing without DSBs"
  if:
    - epigenetic_edit_applied:
        tool: "CRISPRoff"
        target: locus(VEGFA_Promoter)
  then:
    - methylation_increases:
        from: 20.0
        to: ">80.0"
        timeline: "within_72_hours"
    - expression_decreases:
        gene: "VEGFA"
        from: "normal"
        to: "silenced"
        reduction: ">90_percent"
    - modification_persists:
        duration: ">30_days_post_treatment"
    - no_dsbs_detected:
        method: "GUIDE-seq"
    - reversible_with:
        tool: "CRISPRon"

# Safety and reversibility rules
rules:
  - id: R_Epigenetic_Safety_Advantage
    description: "Epigenetic editing avoids genotoxicity of Cas9"
    if:
      - edit_tool_is: "CRISPRoff"
    then:
      - safety_profile:
          dsb_risk: "none"
          off_target_mutations: "none"
          reversibility: "yes_with_CRISPRon"
          
  - id: R_Silencing_Persistence
    description: "Methylation-based silencing is mitotically heritable"
    if:
      - methylation_level_exceeds: 70.0
      - region_is: "promoter"
    then:
      - expression_state: "silenced"
      - heritability: "stable_through_divisions"
      - maintenance: "passive_via_DNMT1"

# Comparison with alternative strategies
design:
  goal: "Therapeutic VEGFA downregulation for anti-angiogenesis"
  candidate_strategies:
    - strategy_1:
        name: "Cas9_Knockout"
        tool: "CRISPR_cas9"
        permanence: "irreversible"
        safety: "DSB_risk"
        outcome: "complete_loss_of_function"
        
    - strategy_2:
        name: "CRISPRi_Repression"
        tool: "dCas9_KRAB"
        permanence: "transient"
        safety: "high"
        outcome: "requires_continuous_expression"
        limitation: "not_heritable"
        
    - strategy_3:
        name: "CRISPRoff_Epigenetic"
        tool: "CRISPRoff"
        permanence: "heritable_but_reversible"
        safety: "no_DSBs"
        outcome: "stable_silencing"
        advantage: "best_of_both_worlds"

  optimization_criteria:
    - maximize: "safety"
    - maximize: "durability"
    - require: "reversibility"
    - minimize: "off_target_effects"
  
  selected_strategy: "strategy_3"
  rationale: "CRISPRoff provides heritable silencing without genotoxicity, with option for reversal"

# Output comprehensive epigenetic editing report
output:
  - editing_tool: "CRISPRoff"
  - target_locus: "VEGFA_Promoter"
  - methylation_change: "${baseline -> post_treatment}"
  - expression_change: "${normal -> silenced}"
  - safety_profile: "${no_DSBs_no_mutations}"
  - reversibility_option: "CRISPRon_available"
  - clinical_application: "Anti-angiogenic_therapy_macular_degeneration"
```

## Epigenetic State Predicates

### New Predicates for Rules

#### epigenetic_state_is()
```yaml
if:
  - epigenetic_state_is:
      region: locus(Promoter)
      mark_type: "DNA_methylation"
      level: "hypermethylated"
```

#### histone_mark_present()
```yaml
if:
  - histone_mark_present:
      region: locus(Enhancer)
      mark: "H3K27ac"
      enrichment: "high"
```

#### methylation_exceeds()
```yaml
if:
  - methylation_exceeds:
      region: locus(CpG_Island)
      threshold: 75.0
```

## Integration with Existing GFL Features

### Combining with Spatial Genomics

```yaml
loci:
  - id: Gene_Promoter
    chromosome: "chr1"
    start: 1000000
    end: 1001000
    
  - id: Distal_Enhancer
    chromosome: "chr1"
    start: 2500000
    end: 2501000

# Epigenetic state affects 3D interactions
rules:
  - id: R_Methylation_Disrupts_Contacts
    description: "Promoter methylation can disrupt enhancer-promoter contacts"
    if:
      - epigenetic_state_is:
          region: locus(Gene_Promoter)
          mark_type: "DNA_methylation"
          level: "hypermethylated"
      - is_in_contact:
          element_a: locus(Gene_Promoter)
          element_b: locus(Distal_Enhancer)
          using: "hic_map.cool"
    then:
      - contact_strength: "reduced"
      - expression_outcome: "silenced"
```

### Integration with Multi-Omic Reasoning

```yaml
# Connect epigenetic state to protein output
proteins:
  - id: VEGFA_Protein
    gene_source: gene(VEGFA)
    expected_abundance: "normal"

rules:
  - id: R_Epigenetic_To_Proteomic
    description: "Promoter methylation reduces protein abundance"
    if:
      - epigenetic_state_is:
          region: locus(VEGFA_Promoter)
          level: "hypermethylated"
    then:
      - protein_abundance:
          protein: protein(VEGFA_Protein)
          level: "low_or_absent"
      - pathway_activity:
          pathway: "angiogenesis"
          state: "suppressed"
```

## Use Cases

### 1. Precision Oncology
- Silencing oncogenes (MYC, VEGFA) without mutagenesis
- Reactivating tumor suppressors silenced by methylation
- Reversible if therapy needs adjustment

### 2. Neurodegenerative Diseases
- Activating neuroprotective genes (BDNF, NGF)
- Silencing neurotoxic pathways
- Long-lasting effects without genome editing

### 3. Metabolic Engineering
- Epigenetic reprogramming of metabolic genes
- Stable phenotype changes without transgenes
- Cell-type specific silencing

### 4. Developmental Biology Research
- Modeling natural epigenetic regulation
- Studying methylation maintenance mechanisms
- Understanding cell fate decisions

## Key Advantages Modeled

1. **Safety**: No DNA breaks, no mutations
2. **Reversibility**: CRISPRon can reverse CRISPRoff effects
3. **Heritability**: Methylation maintained through cell divisions
4. **Specificity**: Targeted to specific genomic regions
5. **Durability**: Lasts weeks-months after transient treatment

## Technical Considerations

### Methylation Patterns
- **CpG Islands**: Dense CpG regions, often in promoters
- **CpG Shores**: Regions flanking CpG islands
- **Gene Body**: Methylation in coding regions

### Histone Modifications
- **Activating**: H3K4me3 (promoters), H3K27ac (enhancers)
- **Repressive**: H3K9me3, H3K27me3 (silencing)
- **Bivalent**: Both activating and repressive marks

### Tool Mechanisms
- **CRISPRoff**: Recruits DNMT3A/DNMT3L for de novo methylation
- **CRISPRon**: Recruits TET1 for active demethylation
- **Targeting**: dCas9 guides to specific genomic locations

## References

- Nunez et al. (2021) "Genome-wide programmable transcriptional memory by CRISPR-based epigenome editing." Cell
- Klann et al. (2017) "CRISPR-Cas9 epigenome editing enables high-throughput screening for functional regulatory elements." Nature Biotechnology
- Liu et al. (2016) "Editing DNA Methylation in the Mammalian Genome." Cell

## See Also

- [Large-Scale Editing Operations](../conformance_suite/v1.4.0/large_scale_editing/)
- [Loci Block Specification](./loci_blocks.md)
- [Spatial Genomics](./spatial_genomic_capabilities.md)
- [Multi-Omic Integration](./multi_omic_integration.md)

