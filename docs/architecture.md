# GeneForgeLang (GFL) Architecture Specification

> **The Symbolic Language & Semantic Constitution for Biological Reasoning and Multi-Omic Design**  
> *Canonical Version: GFL v2.0+ (NeuroIA Ecosystem / Fundación de Neurociencias)*

---

## 1. Constitutional Mandate & Separation of Concerns

GeneForgeLang (GFL) is the **formal specification language and legislative authority** for representing biological reality across the NeuroIA ecosystem:

$$\text{GFL} = \text{Constitution \& Semantics} \quad\longleftrightarrow\quad \text{GeneForge} = \text{Executive \& Runtime} \quad\longleftrightarrow\quad \text{CAL} = \text{Judicial \& Evidence Arbitration}$$

GFL governs what biological transformations are valid, defines the canonical state space, and specifies mathematical, tensor, and governance contracts required for any hypothesis or design candidate to be admissible. GeneForge executes instructions and performs empirical inference, but **must never alter or bypass the semantic rules of the language** (Invariable Anti-Epistemic Collapse, `CONSTITUTION.md`).

---

## 2. Core Bio-Semantic Axioms

### 2.1. The Bio-Thermodynamic Metabolic Tax Axiom
> *"Metabolism is the global thermodynamic tax that the organism pays for its local order."*

In GFL, no structural synthesis, signal transduction, or biological transformation occurs without entropic dissipation. Any local reduction of entropy ($\Delta S_{\text{local}} < 0$) incurs an explicit, first-order metabolic cost integrated into stop-gates, loss functions, and optimization policies.

### 2.2. Genomic Data Governance & Sovereignty Mandate
Biological semantics inherently incorporate data governance dimensions:
- **Provenance Scope**: Immutable lineage tracking (`PUBLIC`, `CONTROLLED`, `CLINICAL`, `COMMERCIAL`, `RESTRICTED`).
- **Consent Scope**: Explicit ethical and regulatory boundaries (`RESEARCH_ONLY`, `CLINICAL_CARE`, `COMMERCIAL_USE`, `POPULATION_GENOMICS`).
- **Population Scope & Sensitivity**: Ancestry-stratified awareness, cohort boundaries, and equity checks to prevent European-ancestry bias propagation.
- **Data Sovereignty & Biosecurity**: Jurisdiction constraints (`EU`, `US`, `LOCAL_ONLY`) and biosecurity screening against dual-use toxins/pathogens.

### 2.3. The Epistemic Refinement Hypothesis (Representations as Priors)
In GFL, design candidates and causal assertions are epistemic belief priors rather than dogmatic truths: $P(\text{Claim} \mid \mathcal{E}_{\text{prior}})$.
- **Additive Non-Destructive Evidence**: New experimental evidence accumulates without overwriting historical provenance graphs.
- **Context Partitioning**: Divergent evidence across cell types or populations partitions claims into conditional equivalence classes rather than destructive overwrites.
- **Belief State Machine (Evidence DFA)**: Explicit lifecycle transitions: `SUPPORTED` $\to$ `CONTESTED` $\to$ `CONDITIONALLY_VALID` $\to$ `SUPERSEDED`.

---

## 3. System Architecture (Compiler Layers & Runtime)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GFL Workflow / Script (.gfl)                    │
│      (experiment, analyze, design, optimize, rules, hypothesis)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: PARSER & AST BUILDER (src/geneforgelang/core/parser.py)      │
│  - Declarative YAML-compatible syntax & biological DSL semantics       │
│  - Generates canonical AST (GFLAST, Experiment, Analysis, Design)      │
│  - Dynamic variable interpolation (${param})                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: SEMANTIC VALIDATOR & CAPABILITY-AWARE GATES                  │
│  (src/geneforgelang/core/semantic_validator.py)                        │
│  - Static type checking & biological compatibility enforcement         │
│  - Entity resolution across ontologies (HGNC, GO, ChEBI, UniProt)      │
│  - Symbolic Hypothesis Validation (SEMANTIC009, SEMANTIC010)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: IO CONTRACTS & GEOMETRIC TENSORS (BioTorch Contracts)        │
│  - IOContract (FASTQ, BAM, VCF, CSV, JSON, TENSOR, CUSTOM)             │
│  - TensorContract: standardized shapes, invariant_dimensions,          │
│    coordinate_frames (SE(3), SO(3), local_residue_frame)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: CAUSAL GRAPHS & MULTISCALE TOPOLOGY ENGINE                   │
│  - CausalTransitionNode: PHENOTYPIC -> CELLULAR -> MOLECULAR -> ATOMIC │
│  - Causal transition graphs with empirical CRISPR co-dependency gates  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: DECOUPLED AMPUTABLE SATELLITE PLUGINS (ADR-001 / ADR-0003)   │
│  Dynamic discovery via Python entry-points:                            │
│                                                                        │
│  ├── ClawBio Plugin (Biological stress-testing & resilience)           │
│  ├── AlphaGenome Atlas Plugin (AVI Score across 18 modalities, motifs) │
│  ├── DepMap CRISPR Plugin (Functional co-dependency & stop-gates)      │
│  └── RFOptimization Plugin (Near-Miss candidate rescue & AF3/RF3/Boltz)│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Canonical Type Structures (`src/geneforgelang/core/gftypes.py`)

GFL Core centralizes all data contracts in immutable, serializable structures:

1. **Data Types & Biological Sequences**:
   - `DataType`: `FASTA`, `FASTQ`, `BAM`, `SAM`, `VCF`, `TENSOR`, `DISTANCE_MATRIX`, `BACKBONE_FRAMES`, `CONTACT_MAP`, `SEQUENCE_EMBEDDING`, `ATTENTION_MAP`.
   - `IOContract`: Validates input and output contracts across blocks with static pre-execution compatibility checks.
   - `TensorContract`: Enforces coordinate frames and dimension invariance for structural biology AI models.

2. **Causal & Epistemic Structures**:
   - `CausalLevel`: Biological abstraction scales (`PHENOTYPIC`, `CELLULAR`, `MOLECULAR`, `ATOMIC`).
   - `CausalTransitionNode`: Formal node in a multiscale causal graph carrying immutable evidence provenance.
   - `CoDependencyTier`: CRISPR functional dependency strength (`HIGH`, `MODERATE`, `WEAK`, `NONE`).
   - `DepMapCoDependency`: Broad DepMap CRISPR co-dependency score with statistical stop-gate (`is_significant`).

3. **Candidate Lifecycle & Decision Boundary Rescue (RFOptimization)**:
   - `CandidateStatus`: `VALIDATED`, `NEAR_MISS`, `REJECTED`, `OPTIMIZED`.
   - `ConsensusModel`: `AF3`, `RF3`, `BOLTZ`, `PROTEIN_MPNN`, `LIGAND_MPNN`.
   - `MultiModelConsensus`: Independent tri-model screening ($iPAE < 2.5, iPTM > 0.8$, minimum confidence) preventing single-predictor overfitting.
   - `RescuePolicy`: Parameterizes gradient-guided MCMC mutations and discrete structure-recycling resampling.

4. **Genomic Foundation Model Annotations (AlphaGenome)**:
   - `AviModality`: 18 additive biological modalities (Splicing, AlphaMissense, ChIP-TF, DNASE, Histone marks).
   - `AviScore`: Unified variant impact metric for 9 billion SNVs across coding and non-coding regions.
   - `RegulatoryMotifAnnotation`: Disruption metrics for $>2,500$ TF motifs discovered via TF-MoDISco-lite.

---

## 5. Decoupled Satellite Plugin Ecosystem

In compliance with **ADR-001** and **ADR-0003**:
- The lightweight core (`geneforgelang-core`) contains zero heavy deep-learning dependencies (no PyTorch, TensorFlow, JAX, or RoseTTAFold in core).
- Plugins are distributed as independent satellite packages with their own `pyproject.toml` registered through Python entry points:

```toml
[project.entry-points."geneforgelang.plugins"]
alphagenome = "gfl_plugin_alphagenome.plugin:AlphaGenomePlugin"
depmap = "gfl_plugin_depmap.plugin:DepMapPlugin"
rfo = "gfl_plugin_rfo.plugin:RFOptimizationPlugin"
clawbio = "gfl_plugin_clawbio.plugin:ClawBioPlugin"
```

### Isolation & Resilience Principles
1. **Full Amputability**: Uninstalling any plugin never breaks core parsing or AST validation.
2. **Graceful Fallback**: If an optional plugin is absent, the validator issues actionable guidance or directs to containerized alternatives.
3. **Scientific Rigor**: Synthetic mocking/stubbing of biological databases or APIs is strictly prohibited in publication pathways. Real biological data and empirical verification are required.

---

## 6. Language & Development Standards (Protocol /neuroia)

1. **Mandatory English Standard**: English is strictly required for all source code, docstrings, inline comments, commit messages, and official documentation.
2. **Branch Isolation**: All developments take place in feature branches (`feature/...`), never committed directly to `main`.
3. **Atomic Commits**: Structured conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`).
4. **Mandatory Continuous Self-Documentation**: Every substantive development must immediately update:
   - `docs/architecture.md`
   - `docs/index.md`
   - `docs/geneforgelang/plugins/PLUGIN_ECOSYSTEM.md` or `docs/geneforgelang/features/<feature>.md`
   - `CHANGELOG.md`
   - `README.md`
5. **Pull Request Protocol**: Verified PRs submitted via `gh pr create` with comprehensive descriptions.

