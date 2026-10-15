# Epigenetic Deconvolution & cfDNA Fragmentomics Contracts in GeneForgeLang (GFL)

## 1. Overview and Biological Rationale

In liquid biopsies, circulating cell-free DNA (cfDNA) carries crucial tissue-of-origin signatures encoded across two complementary axes:
1. **Epigenetics / Methylation:** Single-nucleotide CpG methylation patterns that identify cellular identity and organ damage.
2. **Fragmentomics:** DNA cleavage patterns, fragment length distributions, end-motif frequencies, and window protection scores reflecting nucleosomal positioning.

Foundation models such as **Pleiades** (90M, 600M, and 7B parameters) are pretrained jointly on both methylated and unmethylated sequence topologies using hierarchical attention across three tiers:
- **Fragment Level:** Individual molecules and local methylation context.
- **Region Level:** Chromatin context across regulatory windows.
- **Sample Level:** Whole-plasma sample aggregation for clinical status deconvolution.

## 2. GFL Contract Specification

In GFL, epigenetic deconvolution is formalized as a deterministic decision gate or analysis contract:

```gfl
decision EpigeneticDeconvolutionGate {
  strategy: SYSTEM_1_CALIBRATED
  engine: "pleiades-biodecision"
  target_tissue: "central_nervous_system"
  cfdna_methylation_profile: "patient_plasma_run_04"
  threshold: 0.90
  latency_budget_ms: 50.0
  calibration_error_max: 0.05
  mode: "binary"
}
```

## 3. Core Types and Data Structures

### `EpigeneticDeconvolutionContract`
- `deconvolution_id`: Unique identifier for the deconvolution run.
- `target_tissue`: Target organ or anatomical tissue (e.g. `central_nervous_system`, `cortex`, `hippocampus`).
- `cfdna_methylation_profile`: Identifier or dataset reference for the patient plasma cfDNA sequencing run.
- `engine`: Inference engine (`"pleiades-biodecision"`, `"pleiades-7b"`).
- `modality`: `FragmentomicsModality` (`HIERARCHICAL_STACKED_ATTENTION`, `METHYLATION_DENSITY`, `FRAGMENT_LENGTH_DISTRIBUTION`, `END_MOTIF_FREQUENCY`, `WINDOW_PROTECTION_SCORE`).
- `confidence_threshold`: Minimum calibrated probability (e.g. $0.90$).
- `min_fragment_coverage`: Minimum sequencing fragment depth for robust deconvolution (e.g. $100,000$).
- `sub_cell_types`: Optional breakdown of constituent cell types (`astrocytes`, `cortical_neurons`, `microglia`, `oligodendrocytes`).

## 4. Semantic Validation Rules

`EnhancedSemanticValidator` enforces:
- `target_tissue`: Must be a non-empty string when specified.
- `cfdna_methylation_profile`: Must be a non-empty string when specified.
- Registered tools: `"pleiades"`, `"pleiades-biodecision"`, `"pleiades-7b"`.
- Recognized analysis strategies: `"epigenetic_deconvolution"`, `"fragmentomics"`.
