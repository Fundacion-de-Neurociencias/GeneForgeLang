# Spatial Predicates Conformance Tests

## Purpose

These tests validate the implementation of spatial genomic predicates that enable spatial reasoning about genomic elements and their relationships. Spatial predicates are the core of GFL v1.3.0's spatial genomic reasoning capabilities.

## Test Cases

### 01_is_within_pass.gfl
**Purpose**: Test `is_within` predicate that should evaluate to true
**Expected**: Should parse successfully and evaluate to true
**Description**: Element coordinates are within the specified locus bounds

### 02_is_within_fail.gfl
**Purpose**: Test `is_within` predicate that should evaluate to false
**Expected**: Should parse successfully and evaluate to false
**Description**: Element coordinates are outside the specified locus bounds

### 03_distance_between.gfl
**Purpose**: Test `distance_between` predicate with distance calculation
**Expected**: Should parse successfully and calculate correct distance
**Description**: Calculate genomic distance between two elements and use in rule evaluation

### 04_is_in_contact.gfl
**Purpose**: Test `is_in_contact` predicate with Hi-C data reference
**Expected**: Should parse successfully and check 3D contact
**Description**: Check if two elements are in 3D contact using Hi-C contact map

### 05_complex_logical_conditions.gfl
**Purpose**: Test complex logical combinations of spatial predicates
**Expected**: Should parse successfully and evaluate complex conditions
**Description**: Multiple spatial predicates combined with AND, OR, NOT operators

### 06_invalid_predicate_missing_fields.gfl
**Purpose**: Test validation of spatial predicates with missing required fields
**Expected**: Should be rejected by semantic validator
**Description**: Spatial predicate missing required element or locus parameters

### 07_invalid_predicate_unknown_type.gfl
**Purpose**: Test validation of unknown spatial predicate types
**Expected**: Should be rejected by semantic validator
**Description**: Spatial predicate with unknown or invalid type

### 08_edge_case_same_coordinates.gfl
**Purpose**: Test edge cases with elements at same coordinates
**Expected**: Should parse successfully and handle edge cases
**Description**: Elements with identical coordinates and boundary conditions

## Spatial Predicates

### is_within(element, locus)
**Purpose**: Check if a genomic element is within a specified locus
**Parameters**:
- `element`: ID of the genomic element to check
- `locus`: ID of the locus to check against
**Logic**: Returns true if element's coordinates fall within locus bounds
**Use Case**: Verify elements are in their expected genomic locations

### distance_between(element_a, element_b)
**Purpose**: Calculate linear genomic distance between two elements
**Parameters**:
- `element_a`: ID of the first genomic element
- `element_b`: ID of the second genomic element
**Logic**: Returns distance in base pairs (can be used with threshold comparisons)
**Use Case**: Check if elements are within specified distance ranges

### is_in_contact(element_a, element_b, hic_map)
**Purpose**: Check if two elements are in 3D chromatin contact
**Parameters**:
- `element_a`: ID of the first genomic element
- `element_b`: ID of the second genomic element
- `hic_map`: Path to Hi-C contact map file
**Logic**: Queries Hi-C data to determine 3D contact probability
**Use Case**: Verify elements are in physical contact despite linear distance

## Validation Rules

### Required Fields
- All spatial predicates must have `type` field specifying predicate type
- `is_within`: Requires `element` and `locus` fields
- `distance_between`: Requires `element_a` and `element_b` fields
- `is_in_contact`: Requires `element_a`, `element_b`, and `hic_map` fields

### Logical Operators
- `AND`: Both conditions must be true
- `OR`: At least one condition must be true
- `NOT`: Condition must be false
- Parentheses for grouping logical operations

### Coordinate Validation
- Elements must have valid coordinates within their loci
- Distances must be calculated correctly based on genomic coordinates
- Hi-C maps must be valid file references

## Expected Behavior

### Parser
- Accept valid spatial predicate syntax
- Handle complex logical combinations
- Reject malformed predicate definitions

### Semantic Validator
- Validate required fields for each predicate type
- Check element and locus references exist
- Validate Hi-C map file references
- Generate appropriate error messages for invalid predicates

### Engine Implementation
- Evaluate spatial predicates based on coordinate data
- Calculate genomic distances accurately
- Query Hi-C data for contact information
- Apply logical operators correctly
- Handle edge cases and boundary conditions

## Success Criteria

A successful spatial predicates implementation should:
1. Parse all valid test cases without errors
2. Reject all invalid test cases with clear error messages
3. Evaluate `is_within` predicates correctly based on coordinates
4. Calculate `distance_between` accurately
5. Query Hi-C data for `is_in_contact` evaluations
6. Apply logical operators in correct precedence order
7. Handle edge cases and boundary conditions appropriately
8. Support complex nested logical expressions
