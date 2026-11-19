# Omnii-1 Multimodal Genome Language Model & Biosafe Bacteriophage Therapy

## Overview

The advent of **Omnii-1** (Radical Numerics, 2026) marks a watershed moment in artificial general biological intelligence. Rather than relying on disconnected, specialized models for isolated tasks (e.g. sequence design, protein structure, chromatin accessibility), Omnii-1 introduces a **unified foundation model across 28 biological modalities** (DNA, RNA, proteins, epigenomics, 5hmC, phage genomes, and structural interfaces).

Most critically, AI-generated bacteriophages designed with Omnii-1 have achieved **first-in-human compassionate clinical administration** against lethal antibiotic-resistant infections (*Pseudomonas aeruginosa*).

GeneForgeLang (GFL) integrates this unified paradigm with four core primitives:
1. **`5hmC` (5-hydroxymethylcytosine) Epigenomic Modality**: Elevates 5hmC across variant attribution (`AviModality`) and cell-free fragmentomics (`FragmentomicsModality`) for ultra-early cancer diagnostics and bacterial restriction/Cas evasion.
2. **`BacteriophageTherapyContract`**: Declarative synthesis of therapeutic virions targeting specific antimicrobial-resistant (AMR) bacterial pathogens.
3. **`BiodefenseSafetyGate`**: Enforces zero horizontal gene transfer of resistance factors, zero bacterial toxin homology, and strictly constrained off-target commensal microbiome disruption ($\le 1\%$).
4. **`omnii-1` Multimodal Tool Compatibility**: Certified in [`EnhancedSemanticValidator`](../../src/geneforgelang/core/validator.py) for de novo genome design, epigenomics, and multi-model consensus.

---

## Canonical Data Contracts (`src/geneforgelang/core/gftypes.py`)

### 1. `PhageCapsidArchitecture`
```python
class PhageCapsidArchitecture(str, Enum):
    MYOVIRIDAE_T4 = "myoviridae_t4"
    SIPHOVIRIDAE_LAMBDA = "siphoviridae_lambda"
    PODOVIRIDAE_T7 = "podoviridae_t7"
    TEQUATROVIRUS = "tequatrovirus"
    CUSTOM_CHASSIS = "custom_chassis"
```

### 2. `BiodefenseSafetyGate`
```python
@dataclass
class BiodefenseSafetyGate:
    max_immunogenicity_score: float = 0.15
    prohibit_amr_transfer_genes: bool = True
    prohibit_toxin_homology: bool = True
    max_off_target_microbiome_lysis: float = 0.01  # <= 1% commensal perturbation
    verified_clearance: bool = True

    def passes_safety_gate(
        self,
        immunogenicity: float,
        has_amr_genes: bool,
        has_toxin_homology: bool,
        off_target_lysis: float,
    ) -> bool:
        """Validates phage against strict clinical biodefense invariants."""
```

### 3. `BacteriophageTherapyContract`
```python
@dataclass
class BacteriophageTherapyContract:
    therapy_id: str
    target_pathogen: str
    model: str = "omnii-1"
    modalities: list[str] = field(
        default_factory=lambda: [
            "DNA_GENOME",
            "COAT_PROTEIN_STRUCTURE",
            "RECEPTOR_BINDING_FIBER",
            "EPIGENOMIC_5HMC_EVASION",
        ]
    )
    capsid_architecture: PhageCapsidArchitecture = PhageCapsidArchitecture.MYOVIRIDAE_T4
    host_range_expansion: bool = True
    receptor_binding_fiber_ref: Optional[str] = None
    biodefense_gate: BiodefenseSafetyGate = field(default_factory=BiodefenseSafetyGate)
    compassionate_use_approved: bool = True
    target_cfu_reduction_log10: float = 6.0
```

---

## Declarative GFL Example (`examples/omnii1_bacteriophage_therapy.gfl`)

```yaml
metadata:
  protocol_name: "OmniiPhageAMRRescue"
  target_organism: "Pseudomonas aeruginosa"
  clinical_indication: "Multidrug-Resistant Ventilator-Associated Pneumonia (Compassionate Use)"
  version: "2.2.0"

bacteriophage:
  therapy_id: "omnii_phage_pa01_rescue"
  target_pathogen: "Pseudomonas_aeruginosa_AMR_strain_01"
  model: "omnii-1"
  modalities:
    - "DNA_GENOME"
    - "COAT_PROTEIN_STRUCTURE"
    - "RECEPTOR_BINDING_FIBER"
    - "EPIGENOMIC_5HMC_EVASION"
  capsid_architecture: "myoviridae_t4"
  host_range_expansion: true
  receptor_binding_fiber_ref: "PA01_OprM_porin_targeted_fiber"
  compassionate_use_approved: true
  target_cfu_reduction_log10: 6.5
  biodefense_gate:
    max_immunogenicity_score: 0.10
    prohibit_amr_transfer_genes: true
    prohibit_toxin_homology: true
    max_off_target_microbiome_lysis: 0.005
    verified_clearance: true

decision:
  task_id: "compassionate_administration_gate"
  strategy: "system_1_calibrated"
  engine: "biodecision-4b"
  threshold: 0.90
  allowed_space:
    - "CLEARED_COMPASSIONATE_HUMAN_USE"
    - "CONTAMINATED_OR_UNSAFE_REJECTED"

experiment:
  tool: "omnii-1"
  type: "bacteriophage_design"
  params:
    target_gene: "oprM"
    replicates: 3
```

---

## Verification & Unit Testing

The test suite in [`tests/unit/test_omnii1_multimodal_bacteriophage.py`](../../tests/unit/test_omnii1_multimodal_bacteriophage.py) verifies:
1. `AviModality.FIVE_HMC` and `FragmentomicsModality.HYDROXYMETHYLATION_5HMC` enums.
2. `BiodefenseSafetyGate` invariant evaluation (AMR gene prohibition, toxin homology rejection, microbiome lysis boundaries).
3. Contract serialization and AST round-trip with `GFLAST`.
4. EnhancedSemanticValidator enforcement of biodefense rules and clean validation of real-world GFL example files.
