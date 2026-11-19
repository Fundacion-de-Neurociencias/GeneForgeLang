# Viral Interactome Complexes & AlphaGenome Locus Linking in GeneForgeLang (GFL)

## 1. Overview and Biological Rationale

The expansion of the **AlphaFold Database into Pandemic Preparedness** (Google DeepMind, EMBL-EBI, NVIDIA, CEPI, SIB Swiss Institute of Bioinformatics, MRC-University of Glasgow CVR, and SKKU, 2026) systematically mapped viral protein complexes across **2,812 proteomes from 23 virus families**. Evaluating ~1.7 million homo- and heterodimers using an all-vs-all strategy identified **8,028 high-confidence complexes** integrated into the open-access Pandemic Preparedness Portal.

In pathogen biology and pandemic defense, molecular pathogenesis is fundamentally governed by:
1. **Quaternary Protein Interfaces:** Homo- and heterodimeric viral assemblies required for viral entry, replication, and immune evasion.
2. **Host Genomic Susceptibility / Escape Variants:** Genetic variations in human host receptors (e.g. *ACE2*, *NRP1*, *CD4*) that modulate binding affinity, expression levels, and disease severity.

GeneForgeLang provides the formal language specification linking **AlphaFold Database quaternary viral complexes** with **AlphaGenome Atlas nucleotide-resolution genomic loci**.

## 2. GFL Contract Specification

In GFL, viral complexes are declared within the `complexes` block using `ViralInteractomeComplexContract` and `AlphaGenomeLocusLink`:

```gfl
complexes {
  SpikeACE2Dimer {
    portal: "alphafold_pandemic_preparedness"
    viral_family: "coronaviridae"
    proteome_id: "UP000464024"
    interactome_type: "heterodimer"
    subunits: ["P0DTC2", "Q9BYF1"]

    iplddt_threshold: 80.0
    iptm_threshold: 0.75
    is_high_confidence_portal_hit: true

    // Cross-reference with AlphaGenome Atlas (1-based chr:pos:ref>alt)
    host_locus_link: {
      variant: "chrX:15579998:G>A"
      gene: "ACE2"
      biosample: "Lung"
      modalities: ["RNA_SEQ", "DNASE", "CHIP_TF"]
    }
  }
}
```

## 3. Semantic Validation Rules

`EnhancedSemanticValidator` enforces:
- `subunits`: Must be a list with at least 2 protein identifiers.
- `iplddt_threshold`: Must be a float within $[0.0, 100.0]$ (typically $\ge 75.0$).
- `iptm_threshold`: Must be a float within $[0.0, 1.0]$ (typically $\ge 0.70$).
- `host_locus_link.variant`: Must adhere strictly to the AlphaGenome 1-based format `chr:pos:ref>alt` (e.g. `chrX:15579998:G>A`). Non-compliant syntax (such as dbSNP rsIDs like `rs123456` or colon-separated alleles) is rejected.
