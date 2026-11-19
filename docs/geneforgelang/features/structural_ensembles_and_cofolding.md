# Measurement-Consistent Structural Ensembles & Physics-Refined Co-folding

## Overview

Recent breakthroughs in structural biology and generative AI reveal that single-structure static predictions ("PDB ground states") are insufficient for functional drug discovery and biophysical modeling. In nature, macromolecular systems exist as dynamic conformational ensembles, binding pockets undergo ligand-induced transitions, and generative co-folding predictions often suffer from steric clash artifacts unless refined through fundamental physics.

GeneForgeLang (GFL) integrates six foundational advances into its constitutional multi-omic reasoning framework:

1. **Measurement-Guided Structural Ensembles** (*Experiment-guided AlphaFold3 resolves measurement-consistent protein ensembles*, Nature Methods 2025/2026):
   - Steers AI diffusion models via empirical sparse experimental restraints (NMR NOEs, Cryo-EM maps, cross-linking mass spectrometry, and SAXS envelopes).
   - Collapses stochastic sampling into biophysically validated, measurement-consistent conformational ensembles.

2. **Five-Model Co-folding Consensus** (*Runs N' Poses Benchmark 2026*):
   - Expands GFL's structural consensus to cross-validate candidates across **AlphaFold 3, RoseTTAFold 3, Boltz-1, Chai-1, and Protenix**.
   - Enforces the *Runs N' Poses* evaluation standard: filtering out hallucinated binding interactions via pose RMSD ($\le 2.0\text{ \AA}$) and clash gates.

3. **Ligand-Conditioned Cryptic Pocket Induction** (*The influence of ligands on AlphaFold3 prediction of cryptic pockets*, Nature 2025/2026):
   - Models the dynamic transition of allosteric and cryptic pockets: closed/collapsed in uninduced (*apo*) states, and open in the presence of cognate ligands (*holo*).
   - Enables differential cryptic scoring via `LigandConditionedPocketContract`.

4. **Physics-Based Refinement as Ground-Truth Epistemic Gate** (*On the generalization and usability of cofolding models for GPCR drug discovery*, 2025/2026):
   - Reconciles the fundamental dialectic: **AI guides physics** by navigating the global conformational search space, while **physics refines AI** by resolving van der Waals collisions and ensuring thermodynamic feasibility ($\Delta G$).
   - Couples generative co-folding predictions directly with force-field energy minimization (OpenMM / Amber14SB).

---

## Canonical Data Contracts (`src/geneforgelang/core/gftypes.py`)

### 1. `ConsensusModel` & `MultiModelConsensus`
```python
class ConsensusModel(str, Enum):
    AF3 = "alphafold3"
    RF3 = "rosettafold3"
    BOLTZ = "boltz1"
    CHAI_1 = "chai1"
    PROTENIX = "protenix"
    PROTEIN_MPNN = "protein_mpnn"
    LIGAND_MPNN = "ligand_mpnn"
```
Evaluates candidates across models with configurable confidence thresholds ($iPAE \le 2.5, iPTM \ge 0.8$, confidence $\ge 0.80$).

### 2. `ExperimentalRestraintsContract`
```python
@dataclass
class ExperimentalRestraintsContract:
    restraint_type: RestraintType  # 'nmr_noe', 'cryo_em_map', 'xl_ms', 'saxs_envelope', 'epr_deer'
    restraint_file: Optional[str]
    tolerance_angstrom: float = 3.0
    weight: float = 1.0
    satisfaction_ratio: Optional[float] = None
    min_satisfaction_threshold: float = 0.8
```

### 3. `RunsNPosesMetric`
```python
@dataclass
class RunsNPosesMetric:
    pose_rmsd: Optional[float] = None
    clash_score: Optional[float] = None
    contact_recovery: Optional[float] = None
    force_field_energy_kcal_mol: Optional[float] = None
```

### 4. `LigandConditionedPocketContract`
```python
@dataclass
class LigandConditionedPocketContract:
    target_receptor: str
    probe_ligand_smiles: Optional[str] = None
    pocket_mode: str = "differential"  # 'apo_uninduced', 'holo_induced', 'differential'
    cryptic_delta_score: Optional[float] = None
    min_cryptic_delta_threshold: float = 0.35
```

### 5. `PhysicsRefinementPolicy`
```python
@dataclass
class PhysicsRefinementPolicy:
    engine: str = "openmm"  # 'openmm', 'rosetta', 'amber'
    force_field: str = "amber14sb"
    max_iterations: int = 500
    tolerance_kj_mol: float = 10.0
    restrain_backbone: bool = True
```

---

## Declarative GFL Example Workflow

```yaml
metadata:
  experiment_name: "HTR2A Serotonin Receptor Co-folding & OpenMM Refinement"
  version: "2.0.0"
  target_organism: "Homo sapiens"

experiment:
  tool: "chai1"
  type: "analysis"
  params:
    target_receptor: "HTR2A_HUMAN"
    probe_ligand_smiles: "CCN(CC)C(=O)C1CN(C2CC3=CNC4=CC=CC(=C34)C2=C1)C"
    pocket_mode: "holo_induced"
    experimental_restraints:
      restraint_type: "nmr_noe"
      restraint_file: "data/restraints/htr2a_transmembrane_noe.tbl"
      tolerance_angstrom: 2.5
    consensus_screening:
      models: ["alphafold3", "boltz1", "chai1", "protenix", "rosettafold3"]
      min_iptm: 0.80
      max_ipae: 2.5
      min_confidence: 0.80
    physics_refinement:
      engine: "openmm"
      force_field: "amber14sb"
      max_iterations: 500
      tolerance_kj_mol: 10.0

analyze:
  strategy: "structural"
  data: "HTR2A_cofolded_ensemble"
  thresholds:
    max_pose_rmsd: 2.0
    max_clash_score: 10.0
    min_satisfaction_ratio: 0.85
```
