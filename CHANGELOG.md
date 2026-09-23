# Changelog

All notable changes to GeneForgeLang (GFL) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
