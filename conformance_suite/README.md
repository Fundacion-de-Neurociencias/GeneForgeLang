# GFL Conformance Test Suite

## Overview

The GFL Conformance Test Suite is a comprehensive collection of `.gfl` scripts designed to validate the compatibility and correctness of any GFL execution engine implementation. This suite serves as an executable specification for the GeneForgeLang language, ensuring that all implementations adhere to the defined language features and behaviors.

## Purpose

1. **Accelerate GF Development**: Provide the GeneForge team with a standardized test suite to validate their execution engine implementation.
2. **Executable Contract**: Define a binding, executable contract between the language specification and any engine that wants to implement it.
3. **Long-term Quality Asset**: Become a fundamental part of our release process for all future versions of GFL.

## Structure

The test suite is organized by GFL version, with each version containing tests for specific language features:

- `v1.2.0/` - Tests for GFL v1.2.0 features including timeline, rules/hypothesis, and contracts/schemas
  - `timeline/` - Tests for chronological execution features
  - `rules_and_hypothesis/` - Tests for hypothesis validation and rule-based reasoning
  - `contracts_and_schemas/` - Tests for entity resolution and pathway references
- `v1.3.0/` - Tests for GFL v1.3.0 features including loci management, spatial predicates, and simulation capabilities
  - `loci/` - Tests for genomic locus definition and validation
  - `spatial_predicates/` - Tests for spatial relationship testing between genomic elements
  - `simulate/` - Tests for genomic change simulation and hypothesis testing
- `v1.4.0/` - Tests for GFL v1.4.0 features including large-scale genomic editing operations
  - `large_scale_editing/` - Tests for delete, insert, and invert operations on large genomic regions
- `v1.5.0/` - Tests for GFL v1.5.0 features including genomic haplotyping with Locityper
  - `locityper_haplotyping/` - Tests for haplotype panel references, Locityper analysis, and genotyping schemas

## Usage

To validate a GFL execution engine:

1. Run all test scripts in the suite against your engine implementation
2. Compare the output with the expected results documented in each test
3. Ensure all tests pass for full conformance

## Contributing

New tests should follow the naming convention `NN_test_name.gfl` where NN is a sequential number, and each test should include a clear description of what it's validating.

Each subdirectory contains its own README.md with specific information about the tests it contains.
