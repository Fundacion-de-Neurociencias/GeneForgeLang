# Virtual Cell In Silico Perturbation & Open Atlas Ground Truth

## Overview

The historic **$1.8B Virtual Biology Initiative** (Chan Zuckerberg Biohub, U.S. Department of Energy, NIH, Google DeepMind, Isomorphic Labs, and Meta) marks the dawn of **Predictive Cellular Biology**. As articulated at AIxBio (*"Why AlphaFold Didn't Solve Protein Folding"*), predicting static macromolecular structures is merely the initial phase; the real frontier lies in **modeling living cells as dynamic, multi-scale systems** capable of simulating phenotypic responses to genetic changes and drugs *in silico* prior to wet-lab experimentation.

GeneForgeLang (GFL) formalizes this whole-cell predictive paradigm with four foundational pillars:
1. **`VirtualCellPerturbationContract`**: Expresses in silico cellular perturbation experiments across genetic modalities (CRISPR KO, CRISPRi, CRISPRa, base editing) and pharmacological agents.
2. **`CellAtlasReference`**: Grounding predictions directly in open reference data foundations (**Tabula Sapiens**, **CELLxGENE**, **Zebrahub**).
3. **`PerturbationReadout`**: Multimodal phenotypic endpoints, including transcriptomic cosine distance, survival viability probability, and mitochondrial potential retention.
4. **Wet-Lab Clearance Decision Gates**: Integration with `biodecision-4b` (`SYSTEM_1_CALIBRATED`) to filter candidates before costly wet-lab validation.

---

## Canonical Data Contracts (`src/geneforgelang/core/gftypes.py`)

### 1. `PerturbationType` & `CellAtlasReference`
```python
class PerturbationType(str, Enum):
    CRISPR_KNOCKOUT = "crispr_knockout"
    CRISPR_INHIBITION = "crispr_inhibition"
    CRISPR_ACTIVATION = "crispr_activation"
    SMALL_MOLECULE_INHIBITION = "small_molecule_inhibition"
    BASE_EDITING = "base_editing"
    PRIME_EDITING = "prime_editing"
    OVEREXPRESSION = "overexpression"


class CellAtlasReference(str, Enum):
    TABULA_SAPIENS = "tabula_sapiens"
    CELLXGENE = "cellxgene"
    ZEBRAHUB = "zebrahub"
    HUMAN_CELL_ATLAS = "human_cell_atlas"
    CUSTOM_ATLAS = "custom_atlas"
```

### 2. `PerturbationReadout`
```python
@dataclass
class PerturbationReadout:
    max_transcriptome_cosine_distance: float = 0.15
    min_survival_probability: float = 0.85
    mitochondrial_potential_retention: float = 0.90
    off_target_pathway_disruption: float = 0.05

    def satisfies_phenotype_gate(
        self,
        observed_cosine_distance: float,
        observed_survival: float,
        observed_mito_retention: float,
        observed_off_target: float,
    ) -> bool:
        """Validates that in silico perturbation achieves desired effect without cellular collapse."""
```

### 3. `VirtualCellPerturbationContract`
```python
@dataclass
class VirtualCellPerturbationContract:
    simulation_id: str
    cell_type: str
    target_gene_or_compound: str
    perturbation_type: PerturbationType = PerturbationType.CRISPR_INHIBITION
    atlas_ref: CellAtlasReference = CellAtlasReference.TABULA_SAPIENS
    dose_or_fold_change: float = 0.20
    readout: PerturbationReadout = field(default_factory=PerturbationReadout)
    engine: str = "virtual-cell-foundation-1"
    wet_lab_clearance: bool = True
    tissue_context: Optional[str] = None
```

---

## Declarative GFL Example (`examples/virtual_cell_perturbation_screening.gfl`)

```yaml
metadata:
  protocol_name: "CorticalTauPerturbationInSilico"
  target_organism: "Homo sapiens"
  clinical_indication: "Frontotemporal Dementia / Alzheimer's Disease"
  version: "2.3.0"

virtual_cell:
  simulation_id: "mapt_crispri_cortical_rescue"
  cell_type: "human_cortical_neuron"
  target_gene_or_compound: "MAPT"
  perturbation_type: "crispr_inhibition"
  atlas_ref: "tabula_sapiens"
  dose_or_fold_change: 0.20
  tissue_context: "cerebral_cortex"
  engine: "virtual-cell-foundation-1"
  wet_lab_clearance: true
  readout:
    max_transcriptome_cosine_distance: 0.12
    min_survival_probability: 0.92
    mitochondrial_potential_retention: 0.95
    off_target_pathway_disruption: 0.03

decision:
  task_id: "virtual_to_wet_lab_gate"
  strategy: "system_1_calibrated"
  engine: "biodecision-4b"
  threshold: 0.88
  allowed_space:
    - "CLEARED_FOR_WET_LAB_VALIDATION"
    - "INSUFFICIENT_PREDICTIVE_CONFIDENCE"

experiment:
  tool: "virtual-cell-foundation-1"
  type: "virtual_cell_simulation"
  params:
    target_gene: "MAPT"
    replicates: 5
```

---

## Validation & Unit Tests

The test suite in [`tests/unit/test_virtual_cell_perturbation.py`](../../tests/unit/test_virtual_cell_perturbation.py) verifies:
1. `PerturbationType` and `CellAtlasReference` enum mappings.
2. `PerturbationReadout` gating against transcriptomic shifts and survival viability boundaries.
3. Contract roundtrip and `GFLAST` serialization/deserialization.
4. `EnhancedSemanticValidator` enforcement of domain constraints (survival probability $\in [0, 1]$, non-negative cosine distances) and clean zero-error/zero-warning validation of `.gfl` protocols.
