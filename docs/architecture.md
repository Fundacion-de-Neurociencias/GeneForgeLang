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

### 2.4. The Context-Bound Claims Principle (Tangermeme S2F Primitives)
> *"Claims are not globally true; biological claims are valid strictly under explicit contextual conditions."*

Through this architectural principle, GeneForgeLang is endowed with the constitutional capability to decipher **why and under what exact conditions a DNA sequence functions**, eliminating flat or generic assertions and enabling both human researchers and autonomous AI agents to operate on contextualized, testable, and falsifiable hypotheses.

GFL formally enforces the distinction between flat assertions and context-bound claims:
$$\text{Evaluated Claim} \iff (\text{Claim}, \text{ContextState}, \text{Provenance})$$
- **Claim**: The biological assertion (e.g. TF binding disruption, expression alteration).
- **ContextState**: Explicit experimental and epigenetic conditions (`species`, `cell_line_or_tissue`, `assay_type`, `target_factor`, `condition`).
- **Provenance**: Computational lineage and model confidence verification (`model_name`, `model_version_or_hash`, `attribution_method`, `convergence_delta_checked`).
- **Computational Engine**: Downstream interpretation is performed via decoupled sequence-to-function primitives (`gfl-plugin-tangermeme`), including recursive variable-length seqlet calling and pairwise motif syntax analysis ($P \in \mathbb{Z}^{n,m,m}$).

### 2.5. The Physics-AI Dialectic & Measurement-Consistent Ensembles
> *"AI guides physics by navigating the macroscopic conformational landscape; physics refines AI by enforcing microscopic thermodynamic conservation."*

GFL constitutionalizes the complementary roles of generative structural models (AlphaFold 3, Boltz-1, Chai-1, Protenix) and empirical physics/measurement restraints:
1. **Measurement-Consistent Conformational Ensembles**: Ground-state structural predictions are steered by sparse empirical data (`NMR_NOE`, `CRYO_EM_MAP`, `XL_MS`, `SAXS_ENVELOPE`) via `ExperimentalRestraintsContract`, eliminating unconstrained diffusion hallucinations and resolving measurement-consistent conformational ensembles.
2. **Ligand-Conditioned Cryptic Pockets**: Protein pockets exist in dynamic equilibrium; cryptic binding sites remain collapsed in uninduced (*apo*) states unless co-folded with cognate ligands (*holo* induced). GFL models this conditional transition via `LigandConditionedPocketContract`.
3. **Physics-Based Refinement as Epistemic Stop-Gate**: Co-folding predictions are evaluated under the *Runs N' Poses* benchmark (`RunsNPosesMetric`). In unrefined predictions of complex transmembrane receptors (e.g. GPCRs), steric collisions and strained geometries are resolved through molecular mechanics energy minimization (`PhysicsRefinementPolicy`), ensuring thermodynamic admissibility.

### 2.6. Fast Calibrated Gating & The BioDecision Dialectic (System 1 vs. System 2)
> *"Slow reasoning without calibrated probability is epistemic debt; fast routing without calibration bounds is reckless heuristic."*

In complex multi-agent scientific pipelines, evaluating candidate claims (*"Is this clinical endpoint statistically supported?"*, *"Does this extraction hallucinate?"*, *"Should this candidate proceed to full atomic co-folding?"*) using standard frontier autoregressive models (GPT-4o, Claude Opus, Gemini) creates a dual bottleneck: excessive latency (thousands of milliseconds of reasoning token generation) and uncalibrated verbal outputs devoid of deterministic mathematical thresholding.

GFL formally constitutionalizes **System 1 Fast Calibrated Gating** via `BioDecision-4B` (single forward pass architecture, Qwen3.5-4B + LoRA Tev1 recipe):
1. **Single Forward Pass Execution ($\le 50$ ms)**: Replaces autoregressive generation loops with direct logit projection over a constrained, discrete response space (`allowed_space`), cutting execution latency by $\sim 98\%$.
2. **Strict Calibration Error Bounds ($ECE \le 0.08$)**: Requires empirical calibration error verification ($ECE = 0.068$ on HaluBench/PubMedQA). Unambiguous probability gating ($P \ge \tau$, default $\tau = 0.85$) enables deterministic routing without stochastic context drift.
3. **Formal Decision Modes (`DecisionMode`)**:
   - `CHOICE`: Multi-class single selection from an admissible biological hypothesis space.
   - `BINARY`: Deterministic binary gate (`SUPPORTED` vs `CONTRADICTED`, `PASS` vs `FAIL`).
   - `SCORE`: Continuous calibrated confidence estimate $[0.0, 1.0]$.
4. **Epistemic Escalation Gate**: When ambiguity is detected ($P_{\text{top1}} - P_{\text{top2}} < \text{margin}$) or confidence drops below $\tau$, the contract deterministically triggers fallback escalation (`fallback_strategy: ESCALATE_TO_SYSTEM2`), seamlessly preserving deep reasoning rigor only when ambiguity warrants it.

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

3. **Candidate Lifecycle, 5-Model Consensus & Physics Refinement**:
   - `CandidateStatus`: `VALIDATED`, `NEAR_MISS`, `REJECTED`, `OPTIMIZED`.
   - `ConsensusModel`: `AF3`, `RF3`, `BOLTZ`, `CHAI_1`, `PROTENIX`, `PROTEIN_MPNN`, `LIGAND_MPNN`.
   - `MultiModelConsensus`: Independent 5-model cross-validation ($iPAE < 2.5, iPTM > 0.8$, confidence $\ge 0.80$) preventing single-architecture inductive bias.
   - `RunsNPosesMetric`: Evaluates protein-ligand co-folding pose accuracy (RMSD $\le 2.0\text{ \AA}$) and steric clash constraints ($\text{clash} \le 10.0$).
   - `ExperimentalRestraintsContract`: Injects NMR NOE, Cryo-EM map, or SAXS empirical distance and envelope constraints.
   - `LigandConditionedPocketContract`: Differentiates ligand-induced cryptic pocket opening vs. collapsed apo states.
   - `PhysicsRefinementPolicy`: Molecular mechanics (OpenMM, Amber14SB) energy minimization for steric clash elimination.
   - `RescuePolicy`: Parameterizes gradient-guided MCMC mutations and discrete structure-recycling resampling.

4. **Genomic Foundation Model Annotations (AlphaGenome & ClinVar Resolution)**:
   - `AviModality`: 18 additive biological modalities (Splicing, AlphaMissense, ChIP-TF, DNASE, Histone marks).
   - `AviScore`: Unified variant impact metric for 9 billion SNVs across coding and non-coding regions.
   - `RegulatoryMotifAnnotation`: Disruption metrics for $>2,500$ TF motifs discovered via TF-MoDISco-lite.
   - `ClinVarSignificance`: Clinical classification standard (`PATHOGENIC`, `LIKELY_PATHOGENIC`, `UNCERTAIN_SIGNIFICANCE`, `BENIGN`, etc.).
   - `TissueRegulatoryEffect`: Quantifies tissue-specific delta tracks (DNase, RNA-seq, H3K27ac, contact maps) and disrupted transcription factors.
   - `NonCodingRegulatoryContract`: Formal IO contract resolving non-coding Variants of Uncertain Significance (VUS) across target vs. control tissue ontologies (e.g. Brain cortex `UBERON:0000955` vs Liver `UBERON:0002107`).
   - `VariantImpact.resolves_non_coding_vus`: Epistemic predicate determining if a ClinVar VUS is promoted/clarified via high-impact regulatory disruption ($Phred \ge 20.0$).

5. **Deterministic Discovery & Retroelement Architecture (Anti-Stochasticity Gates)**:
   - `RetroelementType`: Taxonomy of non-canonical enzymes and mobile elements (`ARRAY_ASSOCIATED_RT` / ART, `RETRON`, `GROUP_II_INTRON`, `DGR`, `CRISPR_ASSOCIATED_RT`, `VIRAL_RT`).
   - `RetroelementArchitecture`: Formal structural contract defining reverse transcriptase domain boundaries, catalytic triad verification (`YADD`, `YMDD`, `LGDD`), and flanking repeat arrays.
   - `ExhaustiveCoverageContract`: Enforces full, continuous, non-fragmented base scanning ($100\%$ base coverage, sliding window/stride, dual-strand verification) preventing LLM agent context-window drift.
   - `DeterministicReplayContract`: Guarantees reproducible re-discovery across independent agent runs via cryptographic verification hashes ($seed \times candidate \times checksum$), preventing the "stochastic trap" observed in unstructured agent swarms (e.g., Anthropic Mythos ART discovery).

6. **De Novo Catalytic & Enzyme Design Layer (AlphaProtein Novo Synergy - ADR-ARCH-001)**:
   - *Constitutional Boundary*: GFL provides strict syntactic representation and observational contracts, strictly delegating active kinetic solvers, energy barrier optimization ($\Delta G^\ddagger$), and generative diffusion to the GeneForge runtime (`gf/simulation/catalytic_kinetics/` and `gf/models/catalytic_scaffolder.py`).
   - `CatalyticResidueRole`: Functional roles for active-site residues (`NUCLEOPHILE`, `GENERAL_ACID`, `GENERAL_BASE`, `TRANSITION_STATE_STABILIZER`, `OXYANION_HOLE`, `ELECTROPHILE`, `COFACTOR_COORDINATOR`).
   - `CatalyticResidue`: Container defining residue identity, chain, target interaction atom (e.g., `OG`, `NE2`, `OD1`), and ideal 3D coordinates.
   - `CatalyticMotif`: Multi-residue active site declaration (e.g. classical Ser-His-Asp triad), spatial distance bounds, and max active-site RMSD tolerances ($\le 0.8\text{ \AA}$).
   - `SubstrateLigandContainer`: Declarative container for transition-state analogs and substrate SMILES with reactive atom indices.
   - `EnzymeDesignContract`: Formal IO contract specifying enzyme family, catalytic motif geometry, and substrate transition-state distance constraints ($\le 3.5\text{ \AA}$).

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
bgc = "gfl_plugin_bgc.plugin:BGCPlugin"
jev = "gfl_plugin_jev.plugin:JevDecisionPlugin"
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
