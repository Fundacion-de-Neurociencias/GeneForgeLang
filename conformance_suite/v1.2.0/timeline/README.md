# Timeline Tests

## Purpose

These tests validate the temporal execution features of GFL v1.2.0. The timeline construct allows users to define when actions should occur relative to a starting time point (T0).

## What is Tested

1. **Chronological Ordering**: Events must execute in temporal order (T0, T+1h, T+2h) regardless of their declaration order in the script
2. **Time Expression Parsing**: Various time expressions should be correctly interpreted
3. **Action Execution**: Actions associated with time points should execute correctly

## Test Files

- `01_simple_chronology.gfl` - Basic chronological ordering test
- (Additional tests would be added here as the suite expands)

## Expected Behavior

A conformant GFL engine should:
1. Parse all timeline events and their associated time expressions
2. Sort events chronologically regardless of declaration order
3. Execute actions at each time point in the correct sequence
4. Maintain state between time points as appropriate
