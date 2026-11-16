# Changelog

All notable changes to GeneForgeLang (GFL) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Contract 1.1.0: provenance contract for simulated output:
  - New `geneforgelang.provenance` module: `Provenance` (`kind` of `measured`, `computed`, `simulated` or `stub`, plus `source` and `version`), `SimulatedComponentWarning`, `SimulatedInputError` and `list_simulated_components()`
  - Every plugin and connector shipped with the library is labelled and warns on first use: `SimpleProteinGenerator`, `SimpleOptimizer`, `AlphaGenomePlugin`, `OpenMedConnector`, `ProteinVAEGenerator`, `MoleculeTransformerGenerator` and `BayesianOptimizer`
  - `execute()` takes the optional parameter `allow_simulated` (default `False`). **Behaviour change:** without it, a plugin or intermediate result labelled `simulated` or `stub` raises `SimulatedInputError`. Every shipped plugin is one of these, so a default call that used one now raises. Pass `allow_simulated=True` to accept the output knowingly; the result then carries `provenance` with kind `simulated`
  - `OpenMedConnector.deidentify_clinical_note()` returns `privacy_cleared: False`. The connector never applied a privacy filter, so the previous constant `True` was wrong. The result now says that no privacy guarantee is provided; `get_entity_knowledge()` reports its `source` as `OpenMed (stub)`
  - `geneforgelang.plugins.alphafold` is now an alias of `geneforgelang.plugins.alpha_genome` (it held a diverging copy of the same stub)

### Security
- Raised the minimum versions of optional dependencies that had known HIGH or CRITICAL advisories (OSV.dev scan of 2026-10-21):
  - `ml` extra: `torch>=2.10.0`, `transformers>=5.10.0`
  - `web` extra: `fastapi>=0.133.0`, `starlette>=1.3.1`, `aiohttp>=3.14.4`
  - `dev` extra: `black>=26.10.1`
  - The `web` extra now declares `python-multipart>=0.0.31`, which `web/server.py` needs for `UploadFile` and which was missing
  - These releases require Python 3.10 or newer, so the pins carry the marker `python_version >= '3.10'`. The core library still installs on Python 3.9; the `web`, `ml` and `dev` extras add these packages only on 3.10+

### Added
- Published API contract for clients (Contract 1.0.0, grammar 1.2.0):
  - `docs/spec/public_contract.json` is generated from the code by `python -m geneforgelang.public_contract --write`
  - CI fails when a public name, signature, error code or grammar construct changes without a `CONTRACT_VERSION` bump and a `Contract X.Y.Z` line here
  - Release tags `vX.Y.Z` must equal the `pyproject.toml` version and `geneforgelang.__version__`
  - Every public function carries an evidence label (`computed` or `simulated`)
  - `get_api_info()` now reports the contract and grammar versions instead of a fixed `0.1.0`
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
