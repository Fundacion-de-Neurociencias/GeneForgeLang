# GFL Conformance Suite v1.3.0 - Spatial Genomic Reasoning

## Overview

This conformance suite validates the implementation of GFL v1.3.0 spatial genomic reasoning capabilities. It provides comprehensive test cases for the new features that enable spatial genomic awareness and reasoning.

## New Features Tested

### 1. Loci Block (`loci/`)
Tests the genomic coordinate and region definition capabilities:
- Valid locus definitions with chromosome, start, end coordinates
- Element definitions within loci
- Invalid configurations and error handling

### 2. Spatial Predicates (`spatial_predicates/`)
Tests the spatial genomic predicate system:
- `is_within(element, locus)` - Check if element is within genomic region
- `distance_between(element_a, element_b)` - Calculate genomic distance
- `is_in_contact(element_a, element_b, hic_map)` - Check 3D chromatin contact
- Complex logical combinations and edge cases

### 3. Enhanced Simulate Block (`simulate/`)
Tests the what-if reasoning and simulation capabilities:
- Spatial simulation with hypothetical actions
- Rule-based inference and activity determination
- Complex scenarios with multiple rules and dependencies

## Test Structure

Each test directory contains:
- **Positive tests**: Valid GFL scripts that should execute successfully
- **Negative tests**: Invalid GFL scripts that should be rejected by the validator
- **Edge cases**: Boundary conditions and complex scenarios
- **README.md**: Detailed explanation of test purposes and expected behaviors

## Expected Behavior

### For GeneForge Engine Implementation

The GeneForge engine should:

1. **Parse correctly**: All positive tests should parse without syntax errors
2. **Validate properly**: Negative tests should be caught by the semantic validator
3. **Execute accurately**: Spatial predicates should evaluate correctly based on genomic coordinates
4. **Reason logically**: Simulation engine should apply rules and infer consequences
5. **Handle dependencies**: Check that all feature dependencies are satisfied

### For Validation

- **Syntax validation**: Parser should accept valid syntax and reject invalid syntax
- **Semantic validation**: Validator should catch semantic errors and missing dependencies
- **Capability validation**: Validator should warn about unsupported features on different engine types

## Usage

### Running Individual Tests

```bash
# Test loci functionality
gfl validate conformance_suite/v1.3.0/loci/01_valid_definition.gfl

# Test spatial predicates
gfl validate conformance_suite/v1.3.0/spatial_predicates/01_is_within_pass.gfl

# Test simulation
gfl validate conformance_suite/v1.3.0/simulate/01_simple_simulation.gfl
```

### Running Full Suite

```bash
# Validate all v1.3.0 tests
gfl validate conformance_suite/v1.3.0/

# Run with specific engine capabilities
gfl validate --engine-type=advanced conformance_suite/v1.3.0/
```

## Test Categories

### Positive Tests (Should Pass)
- `01_*` files: Basic valid functionality
- `02_*` files: Advanced valid functionality
- `03_*` files: Complex valid scenarios

### Negative Tests (Should Fail)
- `invalid_*` files: Various invalid configurations
- `missing_*` files: Missing required fields
- `type_*` files: Incorrect data types

### Edge Cases
- `edge_*` files: Boundary conditions
- `complex_*` files: Complex scenarios
- `dependency_*` files: Feature dependency tests

## Implementation Notes

### Spatial Genomic Coordinates
- All coordinates are 1-based (standard genomic convention)
- Chromosome names follow standard format (chr1, chr2, chrX, chrY, chrM)
- Coordinate ranges are inclusive (start ≤ position ≤ end)

### Spatial Predicates
- `is_within` checks if an element's coordinates fall within a locus
- `distance_between` calculates linear genomic distance (not 3D distance)
- `is_in_contact` requires Hi-C data file reference

### Simulation Engine
- Actions are hypothetical and don't modify the original state
- Rules are applied in dependency order
- Activity levels follow predefined scale (low, medium, high, etc.)

## Dependencies

This conformance suite requires:
- GFL v1.3.0 parser with spatial genomic support
- Enhanced semantic validator with capability checking
- Spatial reasoning engine with rule evaluation
- Hi-C data integration capabilities (for contact-based predicates)

## Success Criteria

A successful implementation should:
1. **Parse all positive tests** without syntax errors
2. **Reject all negative tests** with appropriate error messages
3. **Execute spatial predicates correctly** based on coordinate logic
4. **Apply rules accurately** in simulation scenarios
5. **Generate appropriate warnings** for unsupported engine capabilities

## Contributing

When adding new test cases:
1. Follow the naming convention: `[number]_[description].gfl`
2. Include clear comments explaining the test purpose
3. Add corresponding negative test cases where applicable
4. Update this README with new test descriptions
5. Ensure tests are atomic and focused on specific functionality

This conformance suite ensures that GFL v1.3.0 spatial genomic reasoning capabilities are implemented correctly and consistently across different engine versions.
