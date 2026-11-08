# Autonomous Wet-Lab Protocol Execution & Synthesizability Engine (AutoDNA / Nature 2026 Synergy)

## Overview & Scientific Grounding

The **Autonomous Wet-Lab Protocol Execution & Synthesizability Engine** (`autonomous_execution`, `wet_lab_dispatch`, `laboratory_protocol`) establishes GeneForgeLang (GFL) as the formal compiler and deterministic verification layer for **AI-Native Self-Driving Laboratories (SDLs)**.

Grounded in the landmark publication in ***Nature*** (November 2026; Heidi Ledford, *"AI agents run this automated biology lab that sequences DNA and more"*, DOI: [10.1038/d41586-026-03552-8](https://doi.org/10.1038/d41586-026-03552-8); alongside research by Haibo Chen, Mingyu Wu et al., Shanghai Jiao Tong University: *"An AI-native experimental laboratory for autonomous biomolecular operations"*), this architecture replaces fragile, unconstrained natural language prompts with mathematically verified, biosecure, and hardware-executable protocols.

```
┌─────────────────────────────────────────────────────────────┐
│                    GeneForgeLang (GFL)                      │
│   • AST formal, contratos tipados y semántica biológica     │
│   • Verificación termodinámica (DNA breathing, Tm, hairpins)│
│   • Biosecurity Gates (Screening dual-use, SynthID Bio)     │
│   • Criptografía SHA-256 (clearance_hash, authorization)    │
└──────────────────────────────┬──────────────────────────────┘
                               │  Compila a SiLA 2 /
                               ▼  AutoDNA JSON IR
┌─────────────────────────────────────────────────────────────┐
│             AutoDNA / Self-Driving Wet-Lab                  │
│   • Red Multi-Agente de ejecución robótica física           │
│   • >20 instrumentos coordinados por brazos mecánicos       │
│   • Síntesis Enzimática (EDS con TdT) + NGS Feedback        │
└──────────────────────────────┬──────────────────────────────┘
                               │  Reads experimentales reales
                               ▼  (Ground Truth Telemetry)
┌─────────────────────────────────────────────────────────────┐
│             Causal Epistemic Refinement in GFL              │
│    evidence_status: "hypothesis" ──> "EMPIRICAL_VERIFIED"   │
└──────────────────────────────┴──────────────────────────────┘
```

---

## The Four Architectural Pillars

### 1. Intermediate Representation & Multi-Instrument Compilation
While robotic laboratories orchestrate heterogeneous hardware (synthesizers, thermocyclers, liquid handlers, centrifuges, capillary electrophoresis, and sequencers), AI agents communicating in unstructured natural language are prone to omissions and hallucinations. GFL compiles declarative biological intentions into standardized, vendor-neutral **SiLA 2 (Standardization in Lab Automation)** and AutoDNA JSON manifests with exact timings, temperatures, and device classes.

### 2. Manufacturability & Synthesizability Gates
Enzymatic DNA Synthesis (EDS) via Terminal Deoxynucleotidyl Transferase (TdT) operates in benign aqueous conditions and matches expert human step-wise yields ($\sim 97.7\%$), but is physically sensitive to:
* **Homopolymer slippage**: Runs $> 4\text{ bp}$ cause enzymatic stutter and insertion/deletion artifacts.
* **GC composition**: Sequences outside $[40\%, 60\%]$ lead to incomplete coupling or secondary structure stalling.
* **Hairpin secondary structure**: Stable stem-loop folding ($\Delta G_{\text{hairpin}} \le -8.0\text{ kcal/mol}$) resists thermal denaturation and stalls extension.
* **Linguistic complexity**: Low k-mer entropy ($< 0.45$) flags repetitive motifs prone to slippage.

### 3. Biosecurity Air-Gap & Cryptographic Authorization
To prevent autonomous robotic arms from synthesizing regulated select agents or lethal toxins, GFL enforces an automated biosecurity gate:
* K-mer screening against dual-use pathogen and toxin databases (e.g. ricin, botulinum, variola, anthrax lethal factor).
* Verification of **SynthID Bio** biological watermarks.
* Deterministic **SHA-256 dispatch authorization signatures** (`clearance_hash` and `authorization_token`), ensuring no physical synthesis step executes without cryptographic verification.

### 4. Closed-Loop Telemetry & Causal Epistemic Refinement
Upon protocol completion, physical sequencer reads (e.g. Nanopore or Illumina FastQ) or spectrophotometric step-wise yields are ingested directly into GFL. The engine computes base-by-base concordance:
$$\text{Concordance} = \frac{\sum \mathbb{I}(b_{\text{target}} == b_{\text{observed}})}{\max(L_{\text{target}}, L_{\text{observed}})}$$
When concordance $\ge 99\%$ (or step-wise yield $\ge 95\%$), the engine automatically promotes the biological claim from `"exploratory_hypothesis"` to `"EMPIRICAL_VERIFIED"`, sealing the physical Design-Build-Test-Learn (DBTL) cycle.

---

## GFL Protocol Syntax

```yaml
autonomous_execution:
  protocol_id: "AUTODNA-KRAS-EXON2-EDS-001"
  target_entity: "KRAS_Exon2_Amplicon"
  target_sequence: "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGAATCATTTTGTGGACGAATATGATCCAACAATAGAGGATTCCTACAGGAAGCAAGTA"
  evidence_promotion: "EMPIRICAL_VERIFIED"
  execution_status: "VERIFIED"
  export_format: "sila2_json"

  synthesizability:
    chemistry: "enzymatic_tdt"
    max_homopolymer: 4
    min_gc_content: 0.35
    max_gc_content: 0.65
    min_hairpin_free_energy: -8.0
    min_complexity: 0.45
    target_length_limit: 1000
    passed: true

  biosecurity:
    risk_tier: "benign_research"
    screening_passed: true
    watermark_verified: true
    operator_id: "autodna_planner_agent"

  steps:
    - step_id: "step_01_enzymatic_synthesis"
      instrument: "synthesizer"
      operation: "EnzymaticSynthesis_TdT"
      duration_seconds: 7200
      temperature_celsius: 37.0
      parameters:
        cycles: 135
        enzyme: "TdT_aqueous_cocktail"
        stepwise_target_yield: 0.977

    - step_id: "step_02_bead_purification"
      instrument: "liquid_handler"
      operation: "MagneticBead_CleanUp"
      duration_seconds: 900
      temperature_celsius: 22.0
      parameters:
        bead_ratio: 1.8
        wash_cycles: 2

    - step_id: "step_03_pcr_amplification"
      instrument: "thermocycler"
      operation: "Targeted_Amplification"
      duration_seconds: 3600
      parameters:
        denaturation_temp: 95.0
        annealing_temp: 58.0
        extension_temp: 72.0
        cycles: 25

    - step_id: "step_04_capillary_electrophoresis"
      instrument: "electrophoresis"
      operation: "Fragment_Size_Confirmation"
      duration_seconds: 1200
      temperature_celsius: 25.0
      parameters:
        expected_bp: 135
        tolerance_bp: 5

    - step_id: "step_05_nanopore_sequencing"
      instrument: "sequencer"
      operation: "Nanopore_Adaptive_Sampling"
      duration_seconds: 14400
      parameters:
        flowcell: "Flongle_R10.4.1"
        target_depth: 500

  telemetry:
    readout_type: "ngs_fastq_reads"
    observed_yield: 0.977
    observed_sequence: "ATGACTGAATATAAACTTGTGGTAGTTGGAGCTGGTGGCGTAGGCAAGAGTGCCTTGACGATACAGCTAATTCAGAATCATTTTGTGGACGAATATGATCCAACAATAGAGGATTCCTACAGGAAGCAAGTA"
    concordance_rate: 1.0
    quality_qscore: 39.5
```

---

## Python API Usage

```python
from geneforgelang.core.gftypes import AutonomousExecutionContract
from geneforgelang.core.wet_lab_engine import AutonomousExecutionEngine

# 1. Compile to SiLA 2 / AutoDNA JSON IR
ir = AutonomousExecutionEngine.compile_to_sila2_ir(contract)

# 2. Reconcile telemetry from physical assay
result = AutonomousExecutionEngine.reconcile_telemetry(contract, contract.telemetry)
assert result.reconciled is True
assert result.promoted_evidence_status == "EMPIRICAL_VERIFIED"
print(f"Audit Proof: {result.audit_proof_hash}")
```
