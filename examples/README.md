# GFL Examples

This directory contains example GFL workflows demonstrating the language syntax and capabilities.

## simple_workflow.gfl

A basic example showing:
- Protein sequence design using a generator plugin
- Parameter optimization using search strategies
- Workflow variable substitution

## Running Examples

```python
from gfl.api import parse, validate, execute

# Load and parse a GFL file
with open('examples/simple_workflow.gfl', 'r') as f:
    gfl_code = f.read()

ast = parse(gfl_code)
errors = validate(ast)

if not errors:
    result = execute(ast)
    print("Workflow completed successfully!")
else:
    print(f"Validation errors: {errors}")
```

## Plugin Requirements

The examples use these plugins:
- `ProteinVAEGenerator`: Simple protein sequence generator (maps to SimpleProteinGenerator)
- `BayesianOptimization`: Parameter optimization (maps to SimpleOptimizer)

These are baseline implementations provided for demonstration. For production use, integrate established computational biology tools through the plugin system.
