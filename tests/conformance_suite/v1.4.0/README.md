# GFL Conformance Test Suite v1.4.0

## Overview

This version of the GFL Conformance Test Suite introduces support for large-scale genomic editing operations using the new bridge editing syntax. These tests validate the implementation of insertions, deletions, and inversions of large genomic regions within the `operation` block context.

## New Features

- **Large-Scale Deletions**: Tests for removing large genomic regions using the `delete` operation
- **Large-Scale Insertions**: Tests for integrating therapeutic sequences at specific loci using the `insert` operation
- **Large-Scale Inversions**: Tests for flipping genomic regions using the `invert` operation

## Structure

- `large_scale_editing/` - Tests for the new large-scale genomic editing capabilities
  - Bridge editor operations that can manipulate entire genomic blocks
  - Support for sequence reference resolution
  - Locus-based targeting for precise genomic interventions

## Usage

These tests validate that a GFL execution engine correctly:
1. Parses and understands the new operation syntax within `operation` blocks
2. Resolves sequence and locus references appropriately
3. Simulates large-scale genomic changes without errors
4. Maintains referential integrity across the genomic constructs

Run these tests during implementation to ensure your execution engine properly supports the new large-scale editing operations.
