# GFL Capability-Aware Validator

## Overview

The GFL Capability-Aware Validator is an enhanced semantic validator that checks not only if GFL code is syntactically and semantically correct, but also whether it's compatible with the target execution engine's capabilities. This prevents users from attempting to run scripts with features that aren't supported by their engine version.

## Key Features

### 1. Engine Capability Checking
- Validates GFL code against specific engine capabilities
- Generates warnings (not errors) for unsupported features
- Maintains backward compatibility with legacy GFL features

### 2. Feature Dependency Validation
- Checks if all required dependencies for a feature are supported
- Prevents execution of features with missing prerequisites
- Provides clear dependency information

### 3. Multiple Engine Types
- **Basic**: Core GFL features (experiment, analyze, design, optimize, branch, metadata)
- **Standard**: Most features up to v1.2.0 (includes rules, simulate, hypothesis, timeline)
- **Advanced**: All features including spatial genomic capabilities (v1.3.0)
- **Experimental**: Cutting-edge features and integrations

### 4. Spatial Genomic Feature Support
- Validates loci blocks for genomic coordinates
- Checks spatial predicates (is_within, distance_between, is_in_contact)
- Validates enhanced simulate blocks for what-if reasoning
- Supports Hi-C integration capabilities

## Usage

### Basic Usage

```python
from gfl.parser import parse_gfl
from gfl.semantic_validator import validate
from gfl.capability_system import get_engine_capabilities

# Parse GFL content
ast = parse_gfl(gfl_content)

# Validate with specific engine capabilities
basic_capabilities = get_engine_capabilities("basic")
result = validate(ast, engine_capabilities=basic_capabilities)

# Check for warnings
if result.warnings:
    for warning in result.warnings:
        print(f"WARNING: {warning.message}")
        if hasattr(warning, 'feature'):
            print(f"Feature: {warning.feature.value}")
```

### Using Engine Types

```python
from gfl.semantic_validator import validate_with_engine_type

# Validate for specific engine type
result = validate_with_engine_type(ast, "standard")

# Check results
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")
```

### Advanced Usage

```python
from gfl.semantic_validator import EnhancedSemanticValidator
from gfl.capability_system import GFLFeature

# Create custom capability set
custom_capabilities = {
    GFLFeature.EXPERIMENT_BLOCK,
    GFLFeature.ANALYZE_BLOCK,
    GFLFeature.LOCI_BLOCK,
    GFLFeature.SPATIAL_PREDICATES
}

# Validate with custom capabilities
validator = EnhancedSemanticValidator(
    file_path="my_script.gfl",
    engine_capabilities=custom_capabilities
)
result = validator.validate_ast(ast)
```

## Engine Capability Definitions

### Basic Engine
- Core workflow features
- Suitable for simple analysis and experiments
- No advanced reasoning or spatial capabilities

### Standard Engine
- All basic features
- Rules and hypothesis blocks
- Basic simulation capabilities
- Schema imports and data refinement

### Advanced Engine
- All standard features
- Spatial genomic capabilities (loci, spatial predicates)
- Enhanced simulation with what-if reasoning
- Hi-C integration support

### Experimental Engine
- All advanced features
- Cutting-edge integrations
- Cloud and external data source support
- Future experimental features

## Feature Definitions

### Core Features
- `EXPERIMENT_BLOCK`: Basic experiment execution
- `ANALYZE_BLOCK`: Data analysis and processing
- `DESIGN_BLOCK`: Design and optimization
- `OPTIMIZE_BLOCK`: Optimization algorithms
- `BRANCH_BLOCK`: Conditional execution
- `METADATA_BLOCK`: Metadata management

### Advanced Features
- `SIMULATE_BLOCK`: Basic simulation
- `RULES_BLOCK`: Rule-based logic
- `HYPOTHESIS_BLOCK`: Hypothesis management
- `TIMELINE_BLOCK`: Temporal reasoning

### Spatial Genomic Features (v1.3.0)
- `LOCI_BLOCK`: Genomic coordinate definitions
- `SPATIAL_PREDICATES`: Spatial genomic predicates
- `SPATIAL_SIMULATE`: What-if spatial reasoning
- `HIC_INTEGRATION`: 3D chromatin contact data

### Reasoning Features
- `REASONING_ENGINE_V1`: Advanced inference
- `WHAT_IF_SIMULATION`: Hypothetical scenario testing
- `SPATIAL_REASONING`: Spatial genomic reasoning

## Validation Results

### Warnings vs Errors
- **Errors**: Syntax, semantic, or structural issues that prevent execution
- **Warnings**: Capability issues that prevent execution on the target engine
- **Info**: Informational messages and suggestions

### Capability Warnings
```python
# Example warning
warning = GFLValidationWarning(
    message="Feature 'loci_block' is not supported by the target engine",
    feature=GFLFeature.LOCI_BLOCK,
    suggestion="Consider upgrading your GFL engine to support loci_block"
)
```

### Result Structure
```python
class EnhancedValidationResult:
    errors: List[str]           # Critical issues
    warnings: List[GFLValidationWarning]  # Capability warnings
    info: List[str]             # Informational messages
```

## Examples

### Example 1: Basic Engine Validation
```python
# GFL with spatial features
gfl_content = """
loci:
  - id: "GeneLocus"
    chromosome: "chr1"
    start: 1000000
    end: 1001000

rules:
  - id: "SpatialRule"
    if:
      - type: "is_within"
        element: "Promoter"
        locus: "GeneLocus"
    then:
      - type: "set_activity"
        element: "Gene"
        level: "high"
"""

# Validate with basic engine
result = validate_with_engine_type(parse_gfl(gfl_content), "basic")

# Expected warnings:
# - LOCI_BLOCK not supported
# - SPATIAL_PREDICATES not supported
# - Dependencies missing
```

### Example 2: Advanced Engine Validation
```python
# Same GFL content
result = validate_with_engine_type(parse_gfl(gfl_content), "advanced")

# Expected: No capability warnings
# All spatial genomic features supported
```

### Example 3: Custom Capabilities
```python
# Define minimal capabilities
minimal_capabilities = {GFLFeature.EXPERIMENT_BLOCK}

result = validate(ast, engine_capabilities=minimal_capabilities)

# Most features will generate warnings
```

## Integration with LSP

The capability-aware validator integrates with the GFL Language Server Protocol (LSP) to provide real-time capability checking:

- **Real-time warnings**: Show capability issues as users type
- **Engine selection**: Allow users to select target engine type
- **Feature suggestions**: Suggest alternatives for unsupported features
- **Dependency guidance**: Help users understand feature dependencies

## Best Practices

### 1. Always Specify Engine Type
```python
# Good
result = validate_with_engine_type(ast, "standard")

# Avoid
result = validate(ast)  # No capability checking
```

### 2. Handle Warnings Appropriately
```python
# Check for capability warnings
capability_warnings = [w for w in result.warnings if hasattr(w, 'feature')]
if capability_warnings:
    print("Script uses unsupported features:")
    for warning in capability_warnings:
        print(f"- {warning.feature.value}: {warning.message}")
```

### 3. Use Appropriate Engine Types
- **Development**: Use "experimental" for latest features
- **Production**: Use "standard" or "advanced" for stability
- **Legacy systems**: Use "basic" for maximum compatibility

## Future Enhancements

### Planned Features
1. **Dynamic Capability Detection**: Auto-detect engine capabilities
2. **Feature Migration Tools**: Help migrate scripts between engine versions
3. **Performance Impact Analysis**: Estimate execution performance
4. **Cloud Integration**: Validate cloud-specific features

### Research Applications
1. **Multi-Engine Workflows**: Support for heterogeneous execution environments
2. **Feature Versioning**: Track feature evolution across GFL versions
3. **Compatibility Matrices**: Comprehensive compatibility information
4. **Migration Assistance**: Automated migration between engine versions

## Conclusion

The GFL Capability-Aware Validator provides a robust foundation for ensuring GFL script compatibility across different execution engines. By generating warnings rather than errors for unsupported features, it maintains script validity while providing clear guidance on engine requirements.

This system enables the GFL ecosystem to evolve incrementally, with new features being introduced without breaking existing functionality, while providing clear migration paths for users who want to take advantage of new capabilities.
