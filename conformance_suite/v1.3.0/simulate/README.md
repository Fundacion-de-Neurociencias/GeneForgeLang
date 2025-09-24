# Simulate Block Conformance Tests

## Purpose

These tests validate the implementation of the enhanced `simulate` block, which enables what-if reasoning and in silico experiments based on spatial genomic rules. The simulate block is the key component for testing hypotheses without performing actual experiments.

## Test Cases

### 01_simple_simulation.gfl
**Purpose**: Test basic spatial simulation with rule application
**Expected**: Should parse successfully and apply rules correctly
**Description for GF Engine**: "The reasoning engine must apply the RelocationPenaltyRule and determine that the gene activity is 'low_or_off'."

### 02_simulation_no_matching_rule.gfl
**Purpose**: Test simulation where action doesn't trigger any rules
**Expected**: Should parse successfully with no rule application
**Description for GF Engine**: "The reasoning engine must not infer any state changes."

### 03_complex_multi_rule_simulation.gfl
**Purpose**: Test simulation with multiple rules and dependencies
**Expected**: Should parse successfully and apply rules in correct order
**Description**: Complex scenario with multiple rules affecting different elements

### 04_simulation_with_contact_check.gfl
**Purpose**: Test simulation involving Hi-C contact data
**Expected**: Should parse successfully and evaluate 3D contact conditions
**Description**: Simulation that depends on 3D chromatin contact information

### 05_invalid_simulation_missing_action.gfl
**Purpose**: Test validation of simulate block missing action field
**Expected**: Should be rejected by semantic validator
**Description**: Simulate block missing required action field

### 06_invalid_simulation_missing_query.gfl
**Purpose**: Test validation of simulate block missing query field
**Expected**: Should be rejected by semantic validator
**Description**: Simulate block missing required query field

### 07_edge_case_null_action.gfl
**Purpose**: Test simulation with null action (baseline query)
**Expected**: Should parse successfully and query current state
**Description**: Simulation that queries current state without performing actions

### 08_complex_nested_simulation.gfl
**Purpose**: Test complex nested simulation scenarios
**Expected**: Should parse successfully and handle complex dependencies
**Description**: Multiple simulations with interdependent rules and elements

## Simulation Engine Features

### Action Types
- `move(element, destination)`: Hypothetically move element to new location
- `set_activity(element, level)`: Hypothetically change element activity level
- `null`: No action (baseline query)

### Query Types
- `get_activity(element)`: Query element activity level
- `get_activity(element, level)`: Query element activity with specific level

### Rule Application
- Rules are applied based on spatial conditions
- Dependencies are resolved in correct order
- Activity levels are inferred from rule consequences

## Validation Rules

### Required Fields
- `name`: Unique identifier for the simulation
- `action`: Hypothetical action to perform (can be null)
- `query`: List of queries to evaluate

### Optional Fields
- `description`: Human-readable description of the simulation
- `parameters`: Additional simulation parameters

### Action Validation
- Move actions must specify valid element and destination
- Activity actions must specify valid element and level
- Null actions are valid for baseline queries

### Query Validation
- Queries must specify valid element references
- Activity queries can specify target levels
- Query results should be returned in consistent format

## Expected Behavior

### Parser
- Accept valid simulate block syntax
- Handle complex action and query structures
- Reject malformed simulation definitions

### Semantic Validator
- Validate required fields are present
- Check element references exist
- Validate action and query structures
- Generate appropriate error messages

### Simulation Engine
- Execute hypothetical actions without modifying original state
- Apply spatial rules based on modified state
- Evaluate queries and return results
- Handle rule dependencies and conflicts
- Support complex nested scenarios

## Success Criteria

A successful simulate implementation should:
1. Parse all valid test cases without errors
2. Reject all invalid test cases with clear error messages
3. Execute hypothetical actions correctly
4. Apply spatial rules based on modified state
5. Evaluate queries and return accurate results
6. Handle rule dependencies and conflicts appropriately
7. Support complex nested simulation scenarios
8. Maintain original state integrity during simulation
9. Provide consistent query result formats
10. Handle edge cases and boundary conditions

## Integration with Spatial Reasoning

The simulate block integrates with:
- **Loci definitions**: For coordinate-based spatial queries
- **Spatial predicates**: For rule condition evaluation
- **Rule engine**: For consequence inference
- **Hi-C data**: For 3D contact evaluation
- **Activity system**: For state management and queries

## Performance Considerations

Simulation performance depends on:
- Number of rules to evaluate
- Complexity of spatial predicates
- Hi-C data query performance
- Rule dependency resolution
- Query result aggregation

## Error Handling

The simulation engine should handle:
- Missing element references
- Invalid action parameters
- Rule evaluation failures
- Query execution errors
- State inconsistency issues
- Dependency resolution conflicts
