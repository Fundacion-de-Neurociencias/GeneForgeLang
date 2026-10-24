# Force Field Engine Portability & Inter-Engine Energy Consistency

## Overview

A fundamental challenge in computational structural biophysics and molecular dynamics (MD) is **engine portability**: ensuring that a given physical parameterization (e.g. Amber `ff14SB` or `ff19SB`) yields identical potential energy evaluations and trajectories across independent software implementations (such as GROMACS, Amber, and OpenMM).

As demonstrated by **Vedran Miletić, Miłosz Wieczór, Carlos Simmerling et al.** (*Journal of Chemical Theory and Computation / ChemRxiv*), superficial assumptions of force field equivalence often conceal subtle discrepancies:
1. **Residue-Specific CMAP Corrections**: `ff19SB` requires 2D energy surface correction grids ($\phi, \psi$ CMAPs) tailored to each of the 20 amino acids and their protonation states, rather than generic atom-type lookups.
2. **Improper Dihedral Atom Ordering**: Arbitrary atom permutations alter chiral inversion energy barriers.
3. **1-4 Non-Bonded Scaling Conventions**: Electrostatic ($1/1.2 \approx 0.8333333$) and van der Waals ($1/2.0 = 0.5$) scaling factors must be preserved bitwise.
4. **Optimal 4-Point Water Models**: `ff19SB` was parameterized against the `OPC` 4-point water model; using legacy `TIP3P` risks distorting local charge screening and loop solvation.

Miletić et al. achieved a benchmark standard of **$< 10^{-7}\text{ kJ/mol}$** interaction energy discrepancy between Amber and GROMACS, reproducing identical free energy landscapes over $10 \times 10\text{ }\mu\text{s}$ trajectories of ubiquitin.

GeneForgeLang (GFL) formalizes this gold standard with the `ForceFieldEngineContract` and `InterEngineEnergyTolerance`.

---

## Canonical Data Contracts (`src/geneforgelang/core/gftypes.py`)

### 1. Enums
```python
class ForceFieldFamily(str, Enum):
    AMBER_FF14SB = "amber_ff14sb"
    AMBER_FF19SB = "amber_ff19sb"
    CHARMM36M = "charmm36m"
    OPLS_AA = "opls_aa"


class SimulationEngine(str, Enum):
    GROMACS = "gromacs"
    AMBER = "amber"
    OPENMM = "openmm"
    NAMD = "namd"


class WaterModel(str, Enum):
    OPC = "opc"  # Recommended for ff19SB
    OPC3 = "opc3"
    TIP3P = "tip3p"
    TIP4P_EW = "tip4p_ew"
    TIP4P_D = "tip4p_d"
```

### 2. `InterEngineEnergyTolerance`
```python
@dataclass
class InterEngineEnergyTolerance:
    max_potential_energy_delta_kj_mol: float = 1e-6
    max_force_delta_kj_mol_nm: float = 1e-4
    audit_improper_dihedral_ordering: bool = True
    audit_cmap_residue_spec: bool = True
    electrostatic_14_scale: float = 0.8333333
    vdw_14_scale: float = 0.5000000

    def satisfies_inter_engine_portability(
        self,
        observed_energy_delta: float,
        observed_force_delta: float,
        improper_ordering_valid: bool = True,
        cmap_spec_valid: bool = True,
    ) -> bool:
        """Validates that potential energy and force differences remain within physical limits."""
```

### 3. `ForceFieldEngineContract`
```python
@dataclass
class ForceFieldEngineContract:
    contract_id: str
    force_field: ForceFieldFamily = ForceFieldFamily.AMBER_FF19SB
    primary_engine: SimulationEngine = SimulationEngine.GROMACS
    reference_engine: SimulationEngine = SimulationEngine.AMBER
    water_model: WaterModel = WaterModel.OPC
    energy_tolerance: InterEngineEnergyTolerance = field(default_factory=InterEngineEnergyTolerance)
    verified_portability: bool = True
    target_structure_ref: Optional[str] = None
```

---

## Declarative GFL Example (`examples/force_field_engine_consistency.gfl`)

```yaml
metadata:
  protocol_name: "GROMACS_Amber_ff19SB_OPC_Equivalence"
  target_organism: "Homo sapiens"
  benchmark_target: "Ubiquitin / Metalloprotease Loop"
  version: "2.4.0"

force_field_engine:
  contract_id: "ff19sb_gmx_amber_verification"
  force_field: "amber_ff19sb"
  primary_engine: "gromacs"
  reference_engine: "amber"
  water_model: "opc"
  target_structure_ref: "PDB:1UBQ"
  verified_portability: true
  energy_tolerance:
    max_potential_energy_delta_kj_mol: 0.000001
    max_force_delta_kj_mol_nm: 0.0001
    audit_improper_dihedral_ordering: true
    audit_cmap_residue_spec: true
    electrostatic_14_scale: 0.8333333
    vdw_14_scale: 0.5000000

decision:
  task_id: "inter_engine_clearance_gate"
  strategy: "system_1_calibrated"
  engine: "biodecision-4b"
  threshold: 0.95
  allowed_space:
    - "INTER_ENGINE_EQUIVALENCE_CONFIRMED"
    - "TOPOLOGY_DISCREPANCY_REJECTED"

experiment:
  tool: "gromacs"
  type: "inter_engine_validation"
  params:
    target_gene: "UBB"
    replicates: 3
```

---

## Scientific Grounding & Invariants (Rules 1, 4 & 5)

1. **Attribution**: The $10^{-7}\text{ kJ/mol}$ metric and $100\text{ }\mu\text{s}$ ubiquitin benchmark belong to Miletić, Wieczór, Simmerling et al.
2. **Empirical Verification**: GFL contracts do not claim "inter-engine equivalence certified" without performing an actual static single-point energy calculation on the executing node.
3. **Validation Suite**: Unit tests in [`tests/unit/test_force_field_engine_portability.py`](../../tests/unit/test_force_field_engine_portability.py) verify enum mappings, tolerance evaluation, AST roundtrips, and semantic parameter constraints.
