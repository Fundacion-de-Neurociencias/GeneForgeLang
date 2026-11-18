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

## Case format

Every case is a pair of files next to each other:

- `NN_name.gfl`: the input document.
- `NN_name.expected.json`: `{"status": "valid" | "invalid", "codes": ["SEMANTIC001", ...]}`.
  `invalid` means parsing raises (reported as the code `SYNTAX_ERROR`) or the validator reports at least one error. `codes` are reason codes that must all appear among the reported ones; an empty list checks the status only.

A `.gfl` file without an expectation, an expectation without a `.gfl` file, and a malformed expectation are errors, not skips.

The expectations record what each case documents (its header comment or description), not what the validator currently returns.

## Running

From the repository root:

```bash
python -m geneforgelang.conformance tests/conformance_suite --junit conformance-report.xml
```

The runner (`src/geneforgelang/conformance.py`) calls the real `geneforgelang.core.api.parse` and `validate` and compares the result with `expected.json`. The command exits `0` only when no case fails, errors, or passes while listed as a known failure; it exits `1` otherwise and `2` when the suite directory is missing. CI runs it in the `Conformance` workflow and publishes the JUnit report as an artifact.

Cases that fail today are listed in `known_failures.json` (`reason` and `tracking` for each). They are reported as `KNOWN-FAILURE` on every run and appear as skipped in the JUnit report. A listed case that starts to pass makes the run fail (`UNEXPECTED-PASS`), so remove its entry in the same change that fixes the validator.

## Current result

Measured on 2026-11-16 with `python -m geneforgelang.conformance tests/conformance_suite`: 36 cases, 9 pass, 27 known failures, 0 unexpected failures.

- 27 known failures. The validator does not implement `loci`, `simulate`, spatial predicates, large-scale editing operations or the Locityper schema, rejects the v1.2.0 `pathways` and `hypothesis` samples, and has no rule for the three core-semantics codes (`INVALID_SEQUENCE`, `VIABILITY_VIOLATION`, `AMBIGUOUS_TARGET`). Each entry in `known_failures.json` names the validator codes observed.
- 9 passes, and only one of them is meaningful evidence of validation: `v1.2.0/timeline/01_simple_chronology.gfl` (valid). The other eight expect `invalid` without a reason code, and the validator rejects those documents for an unrelated reason (for example `SEMANTIC006`, no recognised main block). They pass on status alone and do not show that the intended rule exists.
- The `tracking` field points to the log entry that records the gap. No GitHub issue exists yet for these gaps.

## Contributing

New tests should follow the naming convention `NN_test_name.gfl` where NN is a sequential number, and each test should include a clear description of what it's validating.

Each subdirectory contains its own README.md with specific information about the tests it contains.
