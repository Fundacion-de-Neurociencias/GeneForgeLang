# Rules and Hypothesis Tests

## Purpose

These tests validate the hypothesis definition and validation features of GFL v1.2.0. The rules and hypothesis construct allows users to define logical relationships between conditions and link experimental execution to specific hypotheses.

## What is Tested

1. **Hypothesis Definition**: The ability to define hypotheses with ID, description, and logical conditions
2. **Hypothesis Linking**: The ability to link experimental execution to defined hypotheses using the `validates_hypothesis` field
3. **Rule Evaluation**: The correct interpretation and evaluation of logical rules (if/then conditions)

## Test Files

- `01_hypothesis_link.gfl` - Basic hypothesis linking test
- (Additional tests would be added here as the suite expands)

## Expected Behavior

A conformant GFL engine should:
1. Parse hypothesis definitions with all required fields (id, description, if/then conditions)
2. Associate experiments with hypotheses using the `validates_hypothesis` field
3. Maintain references between hypotheses and experiments for reporting and validation
4. Correctly evaluate logical conditions in hypothesis definitions
