# Locityper Genomic Haplotyping in GFL

## Overview

GeneForgeLang v1.5.0 introduces support for **genomic haplotyping** using Locityper, enabling precise genotyping of complex, highly polymorphic genomic loci such as HLA genes and KIR (Killer Immunoglobulin-like Receptor) genes.

This capability allows researchers to:
- Define haplotype reference panels for complex loci
- Execute Locityper-based genotyping from WGS data
- Reason about genotyping results in GFL rules
- Make clinical decisions based on haplotype information

## Key Concepts

### Genomic Haplotyping

**Haplotyping** is the process of determining which specific alleles (haplotypes) an individual carries at complex, highly variable genomic loci. Unlike simple SNP genotyping, haplotyping considers:
- Long-range phasing information
- Structural variations
- Complex indels and rearrangements
- Entire gene sequences

### Locityper

Locityper is a specialized tool for genotyping complex loci using whole-genome sequencing data. It works by:
1. Aligning sequencing reads to a panel of known haplotype sequences
2. Determining which pair of haplotypes best explains the observed data
3. Reporting quality metrics for the assignment

## GFL Syntax for Haplotyping

### 1. Defining Loci with Haplotype Panels

The `loci` block now supports an optional `haplotype_panel` field that references a collection of known haplotype sequences:

```yaml
loci:
  - id: HLA_A_Locus
    chromosome: "chr6"
    start: 29941160
    end: 29945884
    description: "HLA-A gene locus, highly polymorphic MHC class I"
    haplotype_panel: "db/hla_a_alleles.fasta"
```

**Fields:**
- `id` (required): Unique identifier for the locus
- `chromosome` (required): Chromosome location
- `start`, `end` (required): Genomic coordinates
- `description` (optional): Human-readable description
- `haplotype_panel` (optional): Path to FASTA/VCF file containing known haplotype sequences

### 2. Invoking Locityper for Genotyping

Use the `analyze` block with `tool: "locityper"` to perform haplotype genotyping:

```yaml
analyze:
  tool: "locityper"
  target: locus(HLA_A_Locus)
  input: "patient_wgs.bam"
  output: "hla_a_genotype_result"
  contract:
    inputs:
      patient_wgs.bam:
        type: "BAM"
        description: "Whole genome sequencing alignment"
    outputs:
      hla_a_genotype_result:
        type: "LocusGenotypeResult"
        description: "Genotyping result for HLA-A locus"
```

**Key Parameters:**
- `tool`: Must be "locityper"
- `target`: Reference to a locus using `locus(LocusID)` syntax
- `input`: Path to WGS BAM file
- `output`: Variable name to store results
- `contract`: Defines input/output types for validation

### 3. The LocusGenotypeResult Schema

Locityper results follow the `LocusGenotypeResult` schema:

```yaml
import_schemas:
  - ./schema/locityper_types.yml

analyze:
  tool: "locityper"
  # ... genotyping configuration ...
  output: "genotype_result"
```

**LocusGenotypeResult Structure:**
- `haplotype1_id` (string): First allele identifier (e.g., "HLA-A*01:01")
- `haplotype2_id` (string): Second allele identifier (e.g., "HLA-A*02:01")
- `quality_value` (number): Phred-like QV for the prediction
- `confidence_score` (number, optional): Confidence in [0, 1]
- `locus_id` (string, optional): Which locus was genotyped
- `coverage_depth` (integer, optional): Average read depth

### 4. Reasoning About Genotypes in Rules

GFL's `rules` block can reason about genotyping results using new predicates:

#### genotype_contains Predicate

Tests if a genotype includes a specific haplotype allele:

```yaml
rules:
  - id: R_HLA_Drug_Risk
    description: "HLA-A*31:01 allele increases carbamazepine hypersensitivity risk"
    if:
      - genotype_contains:
          result: hla_a_genotype_result
          haplotype_id: "HLA-A*31:01"
    then:
      - set_risk_profile:
          drug: "Carbamazepine"
          risk_level: "high"
          evidence: "pharmacogenomic"
```

#### genotype_indicates_absence Predicate

Tests if a gene is absent from the genotype:

```yaml
rules:
  - id: R_KIR_Immune_Profile
    description: "KIR2DS4 absence affects NK cell response"
    if:
      - genotype_indicates_absence:
          result: kir_genotype_result
          gene_id: "KIR2DS4"
    then:
      - set_immune_phenotype:
          feature: "NK_cell_response"
          value: "altered"
```

## Complete Example Workflows

### Example 1: HLA-A Genotyping for Drug Safety

```yaml
# HLA-A Pharmacogenomic Risk Assessment
# ======================================

# Import Locityper type definitions
import_schemas:
  - ./schema/locityper_types.yml

# Define the HLA-A locus with haplotype panel
loci:
  - id: HLA_A_Locus
    chromosome: "chr6"
    start: 29941160
    end: 29945884
    description: "HLA-A gene, MHC class I molecule"
    haplotype_panel: "db/ipd_hla/hla_a_alleles_v3.48.0.fasta"

# Perform genotyping analysis
analyze:
  tool: "locityper"
  target: locus(HLA_A_Locus)
  input: "patient_001_wgs.bam"
  output: "hla_a_genotype"
  params:
    min_coverage: 30
    quality_threshold: 20
  contract:
    inputs:
      patient_001_wgs.bam:
        type: "BAM"
        attributes:
          sorted: true
          indexed: true
    outputs:
      hla_a_genotype:
        type: "LocusGenotypeResult"

# Clinical decision rules based on genotype
rules:
  - id: R_Carbamazepine_Risk
    description: "HLA-A*31:01 carriers have high risk of carbamazepine hypersensitivity"
    if:
      - genotype_contains:
          result: hla_a_genotype
          haplotype_id: "HLA-A*31:01"
    then:
      - set_risk_profile:
          drug: "Carbamazepine"
          risk_level: "high"
          recommendation: "Avoid or use alternative"
          evidence: "CPIC Level A"

  - id: R_Abacavir_Risk
    description: "HLA-B*57:01 is associated with abacavir hypersensitivity"
    if:
      - genotype_contains:
          result: hla_b_genotype
          haplotype_id: "HLA-B*57:01"
    then:
      - set_risk_profile:
          drug: "Abacavir"
          risk_level: "contraindicated"
          recommendation: "Do not prescribe"
          evidence: "CPIC Level A"

# Generate clinical report
output:
  - haplotype_1: "${hla_a_genotype.haplotype1_id}"
  - haplotype_2: "${hla_a_genotype.haplotype2_id}"
  - genotype_quality: "${hla_a_genotype.quality_value}"
  - drug_risk_profile: "${risk_profile}"
```

### Example 2: KIR Gene Presence/Absence Analysis

```yaml
# KIR Gene Copy Number and Immune Profiling
# ==========================================

import_schemas:
  - ./schema/locityper_types.yml

# Define multiple KIR loci
loci:
  - id: KIR2DL1_Locus
    chromosome: "chr19"
    start: 54784687
    end: 54799625
    haplotype_panel: "db/kir/kir2dl1_alleles.fasta"

  - id: KIR2DS4_Locus
    chromosome: "chr19"
    start: 54836984
    end: 54849995
    haplotype_panel: "db/kir/kir2ds4_alleles.fasta"

  - id: KIR3DL1_Locus
    chromosome: "chr19"
    start: 54741748
    end: 54757261
    haplotype_panel: "db/kir/kir3dl1_alleles.fasta"

# Batch genotyping of KIR loci
analyze:
  tool: "locityper"
  targets:
    - locus(KIR2DL1_Locus)
    - locus(KIR2DS4_Locus)
    - locus(KIR3DL1_Locus)
  input: "patient_wgs.bam"
  output: "kir_genotyping_results"
  params:
    mode: "batch"
    detect_deletions: true
  contract:
    outputs:
      kir_genotyping_results:
        type: "MultiLocusGenotypeResult"

# Immune phenotype inference rules
rules:
  - id: R_KIR2DS4_Absence
    description: "KIR2DS4 deletion affects NK cell diversity"
    if:
      - genotype_indicates_absence:
          result: kir_genotyping_results
          gene_id: "KIR2DS4"
    then:
      - set_immune_phenotype:
          feature: "NK_cell_diversity"
          value: "reduced"
          confidence: 0.85

  - id: R_KIR3DL1_High_Expression
    description: "Certain KIR3DL1 alleles have high expression"
    if:
      - genotype_contains:
          result: kir_genotyping_results
          haplotype_id: "KIR3DL1*00101"
    then:
      - set_immune_phenotype:
          feature: "KIR3DL1_expression"
          value: "high"
          impact: "enhanced_NK_inhibition"

# Combined immune profile
output:
  - kir_profile: "${kir_genotyping_results}"
  - immune_phenotype: "${immune_phenotype}"
```

## New Predicates

### genotype_contains()

**Signature:**
```
genotype_contains(result: LocusGenotypeResult, haplotype_id: string) -> boolean
```

**Description:** Returns true if either haplotype1_id or haplotype2_id matches the specified haplotype_id.

**Use Cases:**
- Pharmacogenomic risk assessment
- Disease susceptibility screening
- Transplant compatibility checking

### genotype_indicates_absence()

**Signature:**
```
genotype_indicates_absence(result: LocusGenotypeResult, gene_id: string) -> boolean
```

**Description:** Returns true if the gene appears to be deleted or absent (both haplotypes null or marked as deletion).

**Use Cases:**
- Copy number variation detection
- Gene deletion screening
- Immune repertoire analysis

## Integration with GFL Workflow

### Complete Haplotyping Pipeline

```yaml
# Step 1: Define genomic loci with haplotype panels
loci:
  - id: Target_Locus
    chromosome: "chr6"
    start: 29000000
    end: 30000000
    haplotype_panel: "reference_haplotypes.fasta"

# Step 2: Genotype from WGS data
analyze:
  tool: "locityper"
  target: locus(Target_Locus)
  input: "wgs_alignment.bam"
  output: "genotype"

# Step 3: Reason about results
rules:
  - if: [genotype_contains(result: genotype, haplotype_id: "Risk_Allele")]
    then: [flag_for_review(reason: "high_risk_allele")]

# Step 4: Generate report
output:
  - final_genotype: "${genotype}"
  - clinical_flags: "${flags}"
```

## Use Cases

### 1. Pharmacogenomics
- HLA genotyping for drug hypersensitivity prediction
- CYP2D6/CYP2C19 haplotyping for drug metabolism
- TPMT genotyping for thiopurine dosing

### 2. Immunogenetics
- KIR gene presence/absence for NK cell function
- HLA typing for transplant matching
- T-cell receptor diversity analysis

### 3. Disease Risk Assessment
- MHC haplotypes and autoimmune disease risk
- Complement gene variants and infection susceptibility
- Immune gene profiles for vaccine response

### 4. Population Genomics
- Haplotype frequency analysis
- Linkage disequilibrium studies
- Evolutionary genetics of complex loci

## Technical Notes

### Haplotype Panel Format

Haplotype panels should be in FASTA format with allele IDs in headers:

```
>HLA-A*01:01:01:01
ATGCGGGTCACGGCGCCCCG...
>HLA-A*02:01:01:01  
ATGCGGGTCATGGCGCCCCG...
```

### Quality Metrics

The `quality_value` in LocusGenotypeResult is a Phred-like score where:
- QV ≥ 30: High confidence (error rate < 0.1%)
- QV 20-30: Medium confidence
- QV < 20: Low confidence, manual review recommended

### Performance Considerations

- Haplotyping complex loci (e.g., HLA) requires ≥30x WGS coverage
- Processing time: ~1-5 minutes per locus depending on panel size
- Memory: Proportional to panel size (typically 2-4 GB for HLA)

## Best Practices

1. **Use Latest Panels**: Keep haplotype panels updated with latest allele databases
2. **Validate Coverage**: Ensure adequate sequencing depth at target loci
3. **Quality Thresholds**: Set appropriate QV thresholds for your application
4. **Batch Processing**: Genotype multiple loci in single analysis for efficiency
5. **Clinical Validation**: Confirm critical genotypes with orthogonal methods

## References

- IPD-IMGT/HLA Database: https://www.ebi.ac.uk/ipd/imgt/hla/
- KIR Database: https://www.ebi.ac.uk/ipd/kir/
- Locityper Documentation: (tool-specific documentation)

## See Also

- [Loci Block Specification](./loci_blocks.md)
- [Analyze Block Specification](./analyze_block.md)
- [Rules and Reasoning](./rules_system.md)
- [Schema Registry](./schema_registry.md)

