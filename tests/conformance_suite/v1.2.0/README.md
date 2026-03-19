# GFL Conformance Test Suite - v1.2.0

## Overview

This directory contains conformance tests for GFL v1.2.0, which introduces advanced symbolic reasoning and temporal execution features. These tests validate the implementation of new language constructs including timeline-based execution, hypothesis validation, and entity resolution.

## Feature Areas

### Timeline (`timeline/`)
Tests for chronological execution features where actions must be executed in temporal order regardless of their declaration order in the script.

### Rules and Hypothesis (`rules_and_hypothesis/`)
Tests for hypothesis definition and validation, ensuring engines can link experimental execution to defined hypotheses.

### Contracts and Schemas (`contracts_and_schemas/`)
Tests for entity resolution and pathway references, validating that engines can properly resolve symbolic references to defined entities.

## Test Naming Convention

Tests follow the pattern `NN_test_name.gfl` where:
- `NN` is a sequential number (01, 02, 03, etc.)
- `test_name` is a descriptive name of what is being tested

Each test file includes a description comment explaining what aspect of the feature is being validated.

## Expected Results

Each test file should document the expected output or behavior. Implementations should produce equivalent results to be considered conformant.
