# Changelog

All notable changes to GeneForgeLang (GFL) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Regulatory Genomics Dual-Head Contracts (BPNet, AtacWorks & MIT 6.874)**:
  - Formalized `RegulatoryProfileContract` decoupling global count magnitude (`CountHeadContract`) from base-resolution spatial distribution (`ProfileHeadContract`), solving the spatial information collapse when reducing genomic signal to scalars.
  - Implemented exact Multinomial Profile negative log-likelihood (NLL) and Jensen-Shannon Divergence (JSD) analytical loss functions matching MIT 6.874 Lecture 7 empirical values ($NLL_{P1} \approx 22.3$, $NLL_{P2} \approx 160.9$).
  - Added `SignalModality` distinguishing de novo sequence prediction (`DE_NOVO_SEQUENCE_DIRECT`) from experimental signal denoising (`SIGNAL_DENOISED_ENRICHED` e.g. AtacWorks) and raw empirical assays.
  - Enforced the Epistemic Barrier invariant in `EnhancedSemanticValidator`: prohibits asserting `VALIDATED_MECHANISM` without confirmed orthogonal empirical validation (`orthogonal_validation_confirmed: true`).
  - Added canonical example in `examples/features/regulatory_genomics_dual_head_profile.gfl` and documentation in `docs/geneforgelang/features/regulatory_genomics_dual_head_contracts.md`.
  - Added unit test suite in `tests/unit/test_regulatory_genomics_contracts.py` (100% passing).
- **Viral Interactome Complexes & AlphaGenome Locus Linking (AlphaFold DB Pandemic Portal & DeepMind 2026)**:
  - Added `ViralInteractomeComplexContract` and `ViralInteractomeType` enum formalizing quaternary viral-host and intra-viral complexes across 2,812 proteomes (8,028 high-confidence all-vs-all dimeric interactions).
  - Added `AlphaGenomeLocusLink` bridging quaternary viral complex interfaces with host receptor genomic variants (1-based `chr:pos:ref>alt` AlphaGenome Atlas format).
  - Enhanced `EnhancedSemanticValidator` with semantic validation for `complexes` blocks (subunits validation, `iplddt_threshold`, `iptm_threshold`, and strict AlphaGenome variant format checking).
  - Added canonical example in `examples/features/viral_interactome_pandemic_complexes.gfl` and documentation in `docs/geneforgelang/features/viral_interactome_complexes.md`.
  - Added unit test suite in `tests/unit/test_viral_interactome_complexes.py` (100% passing).
- **Prompteina Text-Conditioned All-Atom Protein & Binder Design (Baker Lab / IPD & Ai2 2026)**:

  - Formalized `NaturalLanguageConditioningContract` capturing macro-topology, active-site interaction coordinates, negative design constraints, and classifier-free guidance scales.
  - Added `TextConditionedDesignContract` for end-to-end de novo binder generation and structural scaffolding from natural language descriptions.
  - Registered `"prompteina"` and `"Prompteina"` as authorized generative design models and tools in `EnhancedSemanticValidator`.
  - Added `_validate_prompt_conditioning` semantic rules enforcing positive guidance scale and inference step budgets.
  - Added canonical example in `examples/features/prompteina_gm2a_binder_design.gfl` for GM2A neurodegenerative disease binder design.
  - Added feature documentation in `docs/geneforgelang/features/prompteina_text_conditioned_design.md` and unit tests in `tests/unit/test_prompteina_design.py` (100% passing).
- **Epigenetic Deconvolution & cfDNA Fragmentomics Foundation Contracts (Pleiades Architecture)**:

  - Formalized `EpigeneticDeconvolutionContract` and `FragmentomicsModality` enum for whole-epigenome foundation model deconvolution from liquid biopsy plasma cfDNA.
  - Expanded `DecisionContract` to natively accept `target_tissue` and `cfdna_methylation_profile` parameters for fast calibrated System 1 gating.
  - Registered `"pleiades"`, `"pleiades-biodecision"`, and `"pleiades-7b"` in `EnhancedSemanticValidator` tool catalog, and authorized `"epigenetic_deconvolution"` and `"fragmentomics"` analysis strategies.
  - Added canonical example in `examples/features/epigenetic_deconvolution_cfdna.gfl` and documentation in `docs/geneforgelang/features/epigenetic_deconvolution_cfdna.md`.
  - Added unit test suite in `tests/unit/test_epigenetic_deconvolution_cfdna.py` (100% passing).
- **AlphaEvolve Program Evolution & Autonomous Protocol Foundry (DeepMind / Google Cloud 2026)**:

  - Added `ProgramEvolutionContract` formalizing evolutionary optimization of code representations, liquid-handler pipetting schedules, and heuristic algorithms via LLM mutation engines guided by deterministic fitness evaluators.
  - Added `AlphaEvolve` and `ProgramEvolution` strategies to `EnhancedSemanticValidator` with strict domain constraints (`population_size > 0`, `generations > 0`, `0.0 <= elitism_rate <= 1.0`, non-empty `seed_program`).
  - Added canonical example in `examples/features/alphaevolve_protocol_optimization.gfl` and documentation in `docs/geneforgelang/features/alphaevolve_program_optimization.md`.
  - Added unit test suite in `tests/unit/test_alphaevolve_program_optimization.py` (100% passing).
- **DNA Typewriter Continuous Cellular Lineage Recording (Science 2026 - Yu et al.)**:

  - Implemented `tape_recorder` first-class AST construct and `TapeRecorderContract` based on *Science* 2026 (DOI: 10.1126/science.ael0508).
  - Added `CassetteArchitecture` enum (`tandem_pegRNA_insertional`, `base_editor_accumulation`, `crispr_homing_barcode`, `prime_editing_tape`).
  - Added `ReadoutModality` enum (`targeted_amplicon_dna_seq`, `single_cell_rna_seq_expression`, `multiplex_amplicon_seq`).
  - Added continuous recording capacity calculations (`total_recording_capacity_hours`) and feasibility verification (`can_accommodate_duration_hours`).
  - Added `LineageNode` phylogenetic representation tracking embryonic cellular generations, sequential tape state barcodes, and temporal commitment points.
  - Registered `dna_typewriter` and `targeted_amplicon_dna_seq` in `EnhancedSemanticValidator` tool catalog and compatibility matrix.
  - Added canonical example in `examples/features/dna_typewriter_embryo_lineage.gfl` and documentation in `docs/geneforgelang/features/dna_typewriter_lineage_recording.md`.
  - Added comprehensive unit test suite in `tests/unit/test_tape_recorder_lineage.py` (100% passing).
- **BioDecision-4B & System 1 Fast Calibrated Gating Engine (Qwen3.5-4B + LoRA Tev1 Recipe)**:
  - Added first-class support for `BioDecision-4B` as the canonical biomedical System 1 decision engine.
  - Implemented `DecisionContract` formal IO contract with deterministic latency budgets (`latency_budget_ms <= 50.0`) and empirical calibration bounds (`calibration_error_max <= 0.08`, benchmarked at $ECE = 0.068$).
  - Added `DecisionStrategy.SYSTEM_1_CALIBRATED`, `DecisionStrategy.BIODECISION_SINGLE_FORWARD`, and `DecisionStrategy.SYSTEM_1_FAST`.
  - Added `DecisionMode` (`CHOICE`, `BINARY`, `SCORE`) for discrete multi-class selection, binary gates, and continuous probability alignment.
  - Added `DecisionOutcome` tracking top predictions, ambiguity detection margins, empirical ECE, latency, and automated escalation triggers.
  - Integrated `decision` root block in `GFLAST` and `EnhancedSemanticValidator`.
  - Registered `biodecision-4b` as an authorized tool and analysis engine in `EnhancedSemanticValidator`.
  - Implemented `BioDecisionPlugin` in `src/geneforgelang/plugins/biodecision_plugin.py` with temperature-scaled softmax, ECE verification, and sub-50ms execution profiles.
  - Added canonical example in `examples/features/biodecision_clinical_trial_gating.gfl` and documentation in `docs/geneforgelang/features/biodecision_system1_gating.md`.
  - Added unit test suite in `tests/unit/test_biodecision_system1_gating.py` (100% passing).
- **Measurement-Consistent Structural Ensembles, 5-Model Co-folding Consensus & Physics Refinement (Nature Methods / Nature Biotechnology 2026)**:
  - Expanded `ConsensusModel` to include `CHAI_1 = "chai1"` and `PROTENIX = "protenix"` alongside AlphaFold3, RoseTTAFold3, and Boltz-1.
  - Implemented 5-model cross-validation in `MultiModelConsensus` with strict confidence gating.
  - Added `ExperimentalRestraintsContract` and `RestraintType` enum (`NMR_NOE`, `CRYO_EM_MAP`, `XL_MS`, `SAXS_ENVELOPE`, `EPR_DEER`) to steer AI structural diffusion toward measurement-consistent conformational ensembles.
  - Added `RunsNPosesMetric` implementing protein-ligand pose evaluation gates (RMSD $\le 2.0\text{ \AA}$, clash score $\le 10.0$).
  - Added `LigandConditionedPocketContract` formalizing allosteric and cryptic pocket transitions (apo collapsed vs. holo induced).
  - Added `PhysicsRefinementPolicy` for molecular mechanics energy minimization (OpenMM / Amber14SB) eliminating steric clash artifacts in complex receptor co-folding predictions.
  - Registered `chai1`, `protenix`, `openmm`, and `runs_n_poses` as validated tools and generative models in `EnhancedSemanticValidator`.
  - Added canonical example in `examples/features/measurement_consistent_gpcr_cofolding.gfl` and comprehensive documentation in `docs/geneforgelang/features/structural_ensembles_and_cofolding.md`.
- **Tangermeme Cis-Regulatory Logic & Context-Bound Claims Primitives (Nature Methods 2026 - ADR-0003)**:
  - Formally integrated Tangermeme (*Schreiber J. et al., Nature Methods 2025/2026*) sequence-to-function (S2F) post-training interpretation engine.
  - Implemented **Context-Bound Claims** representation preserving biological truth boundaries: $\text{Evaluated Claim} \iff (\text{Claim}, \text{ContextState}, \text{Provenance})$.
  - Implemented decoupled sequence manipulation and attribution execution with DeepLIFT/SHAP convergence delta auditing.
  - Implemented pure, deterministic **Recursive Variable-Length Seqlet Caller** with discrete convolution null distributions and diagonal subspan significance filtering ($P_{i,j} = \max(P_{i,j}, P_{i-1, j+1})$).
  - Implemented seqlet motif annotation via `tomtom-lite` and cis-regulatory syntax extraction (symmetric/asymmetric pairwise co-occurrence matrices $P \in \mathbb{Z}^{n,m,m}$ and spatial spacing distributions).
  - Added core plugin adapter in `src/geneforgelang/plugins/tangermeme_plugin.py` and decoupled amputatable satellite plugin `gfl-plugin-tangermeme`.
  - Registered `tangermeme` as an authorized analysis tool in `EnhancedSemanticValidator`.
  - Added canonical example in `examples/features/tangermeme_cis_regulatory_logic.gfl` and comprehensive documentation in `docs/geneforgelang/features/tangermeme_cis_regulatory_logic.md`.
- **Security Policy & Automated AI Vulnerability Auditing (Anthropic OSS Scanner Integration)**:
  - Added comprehensive security policy (`SECURITY.md`) outlining supported versions, coordinated disclosure SLAs, and GitHub Private Vulnerability Reporting channels.
  - Formally authorized opt-in AI security scanner integrations including Anthropic OSS Scanner (Claude 3.5 Sonnet / Opus) with automated empirical proof-of-concept (PoC) validation and direct remediation PRs.
- **De Novo Catalytic Motif & Enzyme Design Layer (AlphaProtein Novo Synergy - ADR-ARCH-001)**:
  - Added `CatalyticResidueRole` enum (`NUCLEOPHILE`, `GENERAL_ACID`, `GENERAL_BASE`, `TRANSITION_STATE_STABILIZER`, `OXYANION_HOLE`, `ELECTROPHILE`, `COFACTOR_COORDINATOR`).
  - Added `CatalyticResidue` dataclass specifying residue identity, chain, target interaction atom (e.g., `OG`, `NE2`, `OD1`), and ideal coordinates.
  - Added `CatalyticMotif` dataclass declaring multi-residue active-site geometry (e.g. classical Ser-His-Asp triad), spatial distance bounds, and max active-site RMSD tolerances ($\le 0.8\text{ \AA}$).
  - Added `SubstrateLigandContainer` dataclass for transition-state analogs and substrate SMILES with reactive atom indices.
  - Added `EnzymeDesignContract` formal IO contract specifying enzyme family, catalytic motif geometry, and substrate transition-state distance constraints ($\le 3.5\text{ \AA}$).
  - Preserved strict architectural boundary between GFL (observational contracts and syntax) and GeneForge (kinetic solver, energy barrier minimization, and scaffolding engine).
- **Deterministic Replay Contracts & Retroelement Architecture (Anti-Stochasticity Gates)**:
  - Added `RetroelementType` enum (`ARRAY_ASSOCIATED_RT`, `RETRON`, `GROUP_II_INTRON`, `DGR`, `CRISPR_ASSOCIATED_RT`, `VIRAL_RT`).
  - Added `RetroelementArchitecture` dataclass formalizing reverse transcriptase domain ranges, catalytic triad verification (`YADD`, `YMDD`, `LGDD`), and flanking repeat arrays.
  - Added `ExhaustiveCoverageContract` enforcing 100% continuous base scanning across sequence contigs to prevent LLM agent context-window drift.
  - Added `DeterministicReplayContract` binding agent discoveries to cryptographic verification hashes ($seed \times candidate \times checksum$), guaranteeing 100% reproducible re-discovery across independent agent runs (overcoming the stochastic discovery loss observed in Anthropic Mythos ART experiments).
- **Non-Coding Regulatory Variant Interpretation & ClinVar Resolution (`gfl-plugin-alphagenome`)**:
  - Added `ClinVarSignificance` enum (`PATHOGENIC`, `LIKELY_PATHOGENIC`, `UNCERTAIN_SIGNIFICANCE`, `BENIGN`, etc.) with `is_vus` helper.
  - Added `TissueRegulatoryEffect` dataclass capturing tissue-specific epigenomic delta tracks (DNase, RNA-seq, H3K27ac, contact maps) and disrupted transcription factors.
  - Added `NonCodingRegulatoryContract` formal IO contract resolving non-coding Variants of Uncertain Significance (VUS) across target vs. control tissue ontologies (e.g. Brain cortex `UBERON:0000955` vs Liver `UBERON:0002107`).
  - Extended `VariantImpact` with `resolves_non_coding_vus` epistemic property, tissue effect lists, and ClinVar status.
  - Updated `gfl-plugin-alphagenome` (`AlphaGenomePlugin`) to evaluate tissue-specific regulatory impact and resolve non-coding VUS candidates.
- **Jev & AnyJev Discrete Decision Architecture (`gfl-plugin-jev`)**:
  - Added `DecisionStrategy` enum (`PERMUTATION_INVARIANT_LOGITS`, `CALIBRATED_TEMPERATURE`, `EXACT_MATCH_PRIOR`, `ENSEMBLE_MARGINALIZED`).
  - Added `DecisionOption`, `DecisionOutcome`, and `DecisionContract` dataclasses for fast Neural System 1 discrete arbitration.
  - Implemented decoupled satellite plugin `gfl-plugin-jev` (`JevDecisionPlugin`) providing permutation-invariant logit evaluation, temperature calibration, ambiguity escalation gates, and fast candidate pre-screening to prevent unnecessary GPU consumption before heavy System 2 structural runs (e.g. AlphaFold3/RoseTTAFold3).
- **Biosynthetic Gene Cluster & Megasynthase Domain Architecture (`gfl-plugin-bgc`)**:
  - Added `BiosyntheticDomainType` enum representing modular enzymatic domains (PKS: `KS`, `AT`, `KR`, `DH`, `ER`, `ACP`, `TE`; NRPS: `CONDENSATION`, `ADENYLATION`, `THIOLATION`, `EPIMERIZATION`, `CYCLIZATION`).
  - Added `MegasynthaseDomain`, `MegasynthaseModule`, and `BGCAssemblyContract` dataclasses for multi-domain enzyme complexes (~2,500+ AA).
  - Implemented decoupled satellite plugin `gfl-plugin-bgc` (`BGCPlugin`) validating assembly invariants, carrier domain presence, chain-termination release, and scoring cross-domain transitions inspired by Keasling Lab / gLM2 (bioRxiv 2026).
- **RFOptimization & Multi-Model Consensus Rescue (`gfl-plugin-rfo`)**:
  - Added `CandidateStatus` enum (`VALIDATED`, `NEAR_MISS`, `REJECTED`, `OPTIMIZED`) and `ConsensusModel` enum.
  - Added `MultiModelConsensus` dataclass enforcing cross-model consensus ($iPAE < 2.5, iPTM > 0.8$) across independent models (AF3, RF3, Boltz1).
  - Added `RescuePolicy` dataclass and alternating gradient-guided MCMC with structure recycling in `RFOptimizationPlugin`.
- **Broad DepMap CRISPR Co-Dependency (`gfl-plugin-depmap`)**:
  - Added `DepMapCoDependency` dataclass with correlation scoring, p-values, and `CoDependencyTier` (`HIGH`, `MODERATE`, `WEAK`, `NONE`).
  - Added epistemic stop-gate in `DepMapPlugin` that halts execution when functional co-dependency is null or non-significant.
- **Multiscale Causal Transition Graphs**:
  - Added `CausalTransitionNode` dataclass with biological level stratification (`PHENOTYPIC`, `CELLULAR`, `MOLECULAR`, `ATOMIC`).
- **BioTorch Geometric AI & Tensor Contracts**:
  - Added `TensorContract` defining standardized tensor shapes, invariant dimensions, and coordinate frames ($SE(3)$, $SO(3)$, `local_residue_frame`).
  - Added tensor data types: `TENSOR`, `DISTANCE_MATRIX`, `BACKBONE_FRAMES`, `CONTACT_MAP`, `SEQUENCE_EMBEDDING`, `ATTENTION_MAP`.
- **Google DeepMind AlphaGenome Atlas Integration (`gfl-plugin-alphagenome`)**:
  - Added `AviScore` with support for 18 additive biological modalities (Splicing, AlphaMissense, ChIP-TF, DNASE).
  - Added `RegulatoryMotifAnnotation` for TF-MoDISco-lite discovered motifs.
  - Added live querying against Google DeepMind Science API.
- **Axiomatic Constitution & Governance**:
  - Added Bio-Thermodynamic Metabolic Tax Axiom (`CONSTITUTION.md`).
  - Added Genomic Data Governance & Sovereignty Mandate (`CONSTITUTION.md`).
  - Added Epistemic Refinement Hypothesis (Representations as Priors).
- Container-Based Plugin Execution:
  - Implemented container image discovery through `gfl.plugin_containers` entry points
  - Added `ContainerExecutor` for Docker-based plugin execution
  - Modified `PluginRegistry` to store and retrieve container image associations
  - Updated `GFLExecutionEngine` to automatically use containers when available
  - Added automatic volume mounting for file I/O in containers
  - Implemented fallback to local execution when Docker is unavailable
  - Added `containers` optional dependency for Docker integration
  - Enhanced plugin examples with container entry points
- Symbolic Reasoning Capabilities:
  - Implemented `rules` block for conditional biological relationships
  - Implemented `hypothesis` block for scientific hypothesis expression
  - Implemented `timeline` block for temporal orchestration
  - Implemented `pathways` and `complexes` blocks for biological entity definitions
  - Added entity reference validation in experiment parameters (e.g., pathway(UreaCycle))
  - Added hypothesis reference validation in experiment and analysis blocks
  - New error codes for undefined hypothesis and entity references
  - Comprehensive documentation for symbolic reasoning features

## [1.0.0] - 2025-08-31

### Added
- Advanced AI Workflow Syntax Extensions:
  - Extended `optimize` block to support Active Learning strategy with required nested keys
  - Extended `design` block to support inverse_design with required nested keys
  - Implemented new `refine_data` block for data refinement workflows
  - Implemented new `guided_discovery` block that reuses existing validation logic
- IO Contracts System:
  - Defined IO Contract data structures in `gfl/types.py`
  - Added IO Contract validation to experiment and analyze blocks
  - Implemented static compatibility checking between block outputs and inputs
  - Added new error codes for IO Contract validation
- Type System & Schema Registry:
  - Created SchemaLoader class to parse external schema definition files
  - Extended parser to recognize `import_schemas` directive
  - Integrated schema registry into semantic validator
  - Updated contract validation logic to use schema registry
  - Added error codes for schema validation
- Core Language Features:
  - Design block type definition with all required fields and validation
  - Optimize block type definition with search space, strategy, and execution components
  - Parameter injection mechanism for `${...}` syntax in nested experiments
  - With_priors block type definition and validation
- Validation System:
  - Enhanced semantic validator with rich error reporting
  - Location tracking, error codes, and suggested fixes
  - Backward compatibility with legacy validation API
- Documentation:
  - Comprehensive documentation for optimize block with scientific examples
  - Documentation for design block with genomic use cases
  - Documentation for with_priors clause with statistical modeling examples

### Changed
- Updated root structure validation to recognize new top-level blocks
- Enhanced error handling system with source locations, error codes, severity levels, and suggested fixes
- Improved parser to support schema import directives

### Fixed
- Type errors in `gfl/types.py` and `gfl/semantic_validator.py`
- Validation issues with parameter injection syntax
- Compatibility checking between different data types in IO contracts

## [0.1.0] - 2025-08-15

### Added
- Initial release of GeneForgeLang
- Basic GFL syntax with experiment, analyze, simulate, and branch blocks
- YAML-based parser
- Semantic validation for core language constructs
- Basic error handling system

### Changed

### Fixed

---
