# Changelog

All notable changes to GeneForgeLang (GFL) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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