# IO Contracts Implementation Summary

This document summarizes the implementation of IO Contracts for GeneForgeLang (GFL), which enhances data integrity and workflow robustness by allowing static validation of data flow between GFL blocks.

## Features Implemented

### 1. IO Contract Data Structures

**File Modified:** `gfl/types.py`

**Enhancements:**
- Added `DataType` enum with common biological data formats (FASTA, FASTQ, BAM, SAM, VCF, etc.)
- Created `IOContract` dataclass to represent data type specifications
- Created `BlockContract` dataclass to represent input/output contracts for GFL blocks
- Added proper type annotations and serialization methods

### 2. New Error Codes

**File Modified:** `gfl/error_handling.py`

**Enhancements:**
- Added new error codes for IO Contract validation:
  - `SEMANTIC_INVALID_CONTRACT` - Invalid contract structure
  - `SEMANTIC_CONTRACT_MISMATCH` - Incompatible contract types
  - `SEMANTIC_MISSING_CONTRACT` - Missing required contract fields

### 3. Contract Validation for Experiment Blocks

**File Modified:** `gfl/semantic_validator.py`

**Enhancements:**
- Extended `_validate_experiment_block()` to validate IO contracts
- Added `_validate_io_contract()` method to validate contract structure
- Added `_validate_contract_section()` method to validate inputs/outputs sections
- Added `_validate_contract_definition()` method to validate individual contract definitions

### 4. Contract Validation for Analysis Blocks

**File Modified:** `gfl/semantic_validator.py`

**Enhancements:**
- Extended `_validate_analysis_block()` to validate IO contracts
- Reused existing contract validation methods

### 5. Static Compatibility Checking

**File Modified:** `gfl/semantic_validator.py`

**Enhancements:**
- Added `_store_block_contract()` method to store contracts in symbol table
- Added `_check_contract_compatibility()` method to validate compatibility between producer and consumer blocks
- Added `_are_contract_types_compatible()` method with type compatibility rules
- Added `_check_contract_attributes_compatibility()` method to validate attribute compatibility

## Code Structure Changes

### New Validation Methods
1. `_validate_io_contract()` - Validates IO contract structure
2. `_validate_contract_section()` - Validates contract sections (inputs/outputs)
3. `_validate_contract_definition()` - Validates individual contract definitions
4. `_store_block_contract()` - Stores block contracts for compatibility checking
5. `_check_contract_compatibility()` - Checks compatibility between blocks
6. `_are_contract_types_compatible()` - Checks type compatibility with rules
7. `_check_contract_attributes_compatibility()` - Checks attribute compatibility

### Updated Validation Methods
1. `_validate_experiment_block()` - Extended to validate IO contracts
2. `_validate_analysis_block()` - Extended to validate IO contracts
3. `_validate_blocks()` - Extended to store contracts for compatibility checking

## Example Usage

```yaml
experiment:
  tool: "sequence_aligner"
  type: "sequencing"
  input: raw_sequences
  output: aligned_reads
  contract:
    inputs:
      raw_sequences: 
        type: "FASTQ"
        attributes:
          layout: "paired-end"
    outputs:
      aligned_reads: 
        type: "BAM"
        attributes:
          sorted: true

analyze:
  strategy: "variant"
  input: aligned_reads
  output: variants
  contract:
    inputs:
      aligned_reads: 
        type: "BAM"
        attributes:
          sorted: true
          indexed: true
    outputs:
      variants: 
        type: "VCF"
```

## Compatibility Rules

The implementation includes built-in compatibility rules:
- FASTQ → FASTQ, TEXT
- FASTA → FASTA, TEXT
- BAM → BAM, SAM, BINARY
- SAM → SAM, BAM, TEXT
- VCF → VCF, TEXT
- CSV → CSV, TEXT
- JSON → JSON, TEXT

## Benefits

1. **Early Error Detection**: Contract mismatches are detected at validation time rather than runtime
2. **Improved Workflow Robustness**: Ensures data compatibility between workflow steps
3. **Better Documentation**: Contracts serve as explicit documentation of data expectations
4. **Enhanced Composability**: Blocks with compatible contracts can be easily composed
5. **Static Analysis**: Enables tooling for workflow analysis and optimization

## Backward Compatibility

All changes are backward compatible:
- Existing GFL files without contracts continue to work without modification
- Contract validation only occurs when contracts are explicitly defined
- Default behavior is preserved when contracts are not present