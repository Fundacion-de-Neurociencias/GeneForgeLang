# Loci Block Conformance Tests

## Purpose

These tests validate the implementation of the `loci` block, which defines genomic regions and their coordinates. The loci block is fundamental to spatial genomic reasoning as it establishes the coordinate system for all spatial predicates.

## Test Cases

### 01_valid_definition.gfl
**Purpose**: Test basic valid locus definition
**Expected**: Should parse and validate successfully
**Description**: Defines a simple locus with chromosome, start, end coordinates and basic elements

### 02_invalid_missing_chromosome.gfl
**Purpose**: Test validation of missing required chromosome field
**Expected**: Should be rejected by semantic validator
**Description**: Locus definition missing the required chromosome field

### 03_invalid_missing_start.gfl
**Purpose**: Test validation of missing start coordinate
**Expected**: Should be rejected by semantic validator
**Description**: Locus definition missing the required start field

### 04_invalid_missing_end.gfl
**Purpose**: Test validation of missing end coordinate
**Expected**: Should be rejected by semantic validator
**Description**: Locus definition missing the required end field

### 05_invalid_coordinate_types.gfl
**Purpose**: Test validation of incorrect coordinate data types
**Expected**: Should be rejected by semantic validator
**Description**: Start and end coordinates are strings instead of integers

### 06_multiple_loci.gfl
**Purpose**: Test multiple locus definitions in single block
**Expected**: Should parse and validate successfully
**Description**: Multiple loci with different chromosomes and coordinate ranges

### 07_complex_elements.gfl
**Purpose**: Test complex element definitions within loci
**Expected**: Should parse and validate successfully
**Description**: Locus with multiple elements of different types (promoter, enhancer, gene)

### 08_edge_coordinates.gfl
**Purpose**: Test edge cases for coordinate validation
**Expected**: Should parse and validate successfully
**Description**: Loci with minimal coordinate ranges and boundary conditions

## Validation Rules

### Required Fields
- `id`: Unique identifier for the locus
- `chromosome`: Chromosome name (string)
- `start`: Start coordinate (integer, 1-based)
- `end`: End coordinate (integer, 1-based)

### Optional Fields
- `elements`: List of genomic elements within the locus

### Coordinate Validation
- Start coordinate must be positive integer
- End coordinate must be positive integer
- End coordinate must be >= start coordinate
- Chromosome names should follow standard format (chr1, chr2, chrX, chrY, chrM)

### Element Validation
- Each element must have `id` and `type` fields
- Element types should be valid (promoter, enhancer, gene, etc.)
- Element coordinates should fall within the locus bounds (if specified)

## Expected Behavior

### Parser
- Accept valid YAML syntax for loci definitions
- Reject malformed YAML or invalid structure
- Handle multiple loci in single block

### Semantic Validator
- Validate required fields are present
- Check coordinate data types and ranges
- Validate element definitions within loci
- Generate appropriate error messages for invalid configurations

### Engine Implementation
- Store locus definitions in coordinate system
- Enable spatial queries against loci
- Support coordinate-based spatial predicates
- Handle coordinate transformations and calculations

## Success Criteria

A successful loci implementation should:
1. Parse all valid test cases without errors
2. Reject all invalid test cases with clear error messages
3. Support multiple loci with different chromosomes
4. Validate coordinate ranges and data types
5. Enable spatial queries using locus definitions
6. Handle complex element hierarchies within loci
