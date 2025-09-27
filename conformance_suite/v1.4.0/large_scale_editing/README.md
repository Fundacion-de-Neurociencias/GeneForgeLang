# Large Scale Editing Tests v1.4.0

## Overview

These tests validate the new large-scale genomic editing operations introduced in GFL v1.4.0. These capabilities enable molecular engineers to describe insertions, deletions, and inversions of substantial genomic regions within structured operation blocks.

## Test Cases

### 01_delete_operation.gfl
**Purpose**: Validates the `delete` operation for removing large genomic regions
- Tests deletion of repeated sequences (FXN GAA repeat expansion)
- Validates proper locus identification and removal simulation
- Ensures hypothesis testing works after deletion operations

### 02_insert_operation.gfl
**Purpose**: Validates the `insert` operation for adding therapeutic sequences
- Tests insertion of external sequences at safe harbor loci
- Validates sequence reference resolution from external files
- Ensures proper targeting of genomic locations for integrations

### 03_invert_operation.gfl
**Purpose**: Validates the `invert` operation for reversing genomic regions
- Tests inversion of promoter regions
- Validates that inverted sequences maintain proper modeling
- Ensures downstream effects can be simulated after inversions

## Expected Behavior

A compliant GFL execution engine should:
- Parse `delete`, `insert`, and `invert` operations without errors
- Resolve all sequence and locus references correctly
- Simulate the large-scale genomic changes appropriately
- Execute downstream hypothesis validation on modified genomes

## Implementation Notes

These operations use the `bridge_editor` tool context and are designed to work with:
- Existing locus definitions and coordinate systems
- External sequence files via proper path resolution
- Integration with hypothesis testing frameworks
- Maintenance of genomic referential integrity
