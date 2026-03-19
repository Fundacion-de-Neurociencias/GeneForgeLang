# Contracts and Schemas Tests

## Purpose

These tests validate the entity resolution and pathway reference features of GFL v1.2.0. The contracts and schemas construct allows users to define entities and reference them symbolically in other parts of the workflow.

## What is Tested

1. **Entity Definition**: The ability to define named entities such as pathways with lists of components
2. **Symbolic Reference Resolution**: The ability to resolve symbolic references like `pathway(TestPathway)` to their defined values
3. **Parameter Passing**: The correct passing of resolved entity values to tools and plugins

## Test Files

- `01_entity_resolution.gfl` - Basic entity resolution and pathway reference test
- (Additional tests would be added here as the suite expands)

## Expected Behavior

A conformant GFL engine should:
1. Parse entity definitions (pathways, contracts, schemas) and store them for later reference
2. Resolve symbolic references to defined entities when encountered in tool parameters
3. Pass the resolved entity values correctly to the target tools/plugins
4. Handle entity references in various contexts (parameters, conditions, etc.)
