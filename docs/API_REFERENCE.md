# GeneForgeLang API Reference

This document provides comprehensive documentation for the GeneForgeLang (GFL) stable API. The API follows semantic versioning and provides both typed and untyped interfaces.

## API Version: 2.0.0

**Compatibility**: Backward compatible with 0.1.x APIs
**Package Version**: 0.2.0+

## Overview

The GFL API provides three main functions for working with genomic workflow specifications:

- **`parse()`**: Convert GFL source code to AST
- **`validate()`**: Check AST for semantic correctness
- **`infer()`**: Run probabilistic reasoning on AST

All functions support both typed and untyped modes for maximum flexibility.

## Core Functions

### parse()

Parse GFL source code into an Abstract Syntax Tree (AST).

#### Signatures

```python
# Typed mode (recommended)
def parse(text: str, *, typed: Literal[True]) -> GFLAST: ...

# Untyped mode (backward compatible)
def parse(text: str, *, typed: Literal[False] = False) -> Dict[str, Any]: ...
```

#### Parameters

- **`text`** (str): GFL source code in YAML-style syntax
- **`typed`** (bool, optional): If True, return typed `GFLAST` object; if False, return `Dict[str, Any]`. Default: False

#### Returns

- **Typed mode**: `GFLAST` object with full type safety and IDE support
- **Untyped mode**: `Dict[str, Any]` for backward compatibility

#### Raises

- **`ValueError`**: If the input cannot be parsed

#### Examples

```python
from gfl.api import parse

# Untyped mode (backward compatible)
ast_dict = parse("""
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
""")

# Typed mode (recommended for new code)
ast_typed = parse("""
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
""", typed=True)

# IDE autocomplete works with typed mode!
print(ast_typed.experiment.tool)  # "CRISPR_cas9"
print(ast_typed.experiment.params.target_gene)  # "TP53"
```

### validate()

Validate an AST for semantic correctness.

#### Signatures

```python
# Detailed mode (recommended)
def validate(ast: Union[GFLAST, Dict[str, Any]], *, detailed: Literal[True]) -> ValidationResult: ...

# Simple mode (backward compatible)
def validate(ast: Union[GFLAST, Dict[str, Any]], *, detailed: Literal[False] = False) -> List[str]: ...
```

#### Parameters

- **`ast`**: AST to validate (either `GFLAST` or `Dict[str, Any]`)
- **`detailed`** (bool, optional): If True, return detailed `ValidationResult`; if False, return `List[str]`. Default: False

#### Returns

- **Detailed mode**: `ValidationResult` with categorized errors, warnings, and info
- **Simple mode**: `List[str]` with error messages (empty list if valid)

#### Examples

```python
from gfl.api import parse, validate

ast = parse("experiment:\n  tool: CRISPR_cas9\n  type: gene_editing")

# Backward compatible mode
errors = validate(ast)
if errors:
    print(f"Found {len(errors)} errors")
    for error in errors:
        print(f"  - {error}")

# Detailed mode (recommended)
result = validate(ast, detailed=True)
if not result.is_valid:
    print("Validation failed:")
    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")
```

### infer()

Run probabilistic post-processing with a provided model.

#### Signatures

```python
# Detailed mode (recommended)
def infer(model, ast: Union[GFLAST, Dict[str, Any]], *, detailed: Literal[True]) -> InferenceResult: ...

# Simple mode (backward compatible)
def infer(model, ast: Union[GFLAST, Dict[str, Any]], *, detailed: Literal[False] = False) -> Dict[str, Any]: ...
```

#### Parameters

- **`model`**: Model with `predict(features: Dict[str, Any]) -> Dict[str, Any]` method
- **`ast`**: AST to run inference on
- **`detailed`** (bool, optional): If True, return detailed `InferenceResult`; if False, return `Dict[str, Any]`. Default: False

#### Returns

- **Detailed mode**: `InferenceResult` with predictions, confidence, and metadata
- **Simple mode**: `Dict[str, Any]` for backward compatibility

#### Examples

```python
from gfl.api import parse, infer
from gfl.models.dummy import DummyModel

ast = parse("experiment:\n  tool: CRISPR_cas9\n  type: gene_editing")
model = DummyModel()

# Backward compatible mode
results = infer(model, ast)
print(results["predictions"])

# Detailed mode (recommended)
result = infer(model, ast, detailed=True)
print(f"Confidence: {result.confidence}")
print(f"Predictions: {result.predictions}")
```

## Convenience Functions

### parse_file()

Parse GFL file and return AST.

```python
def parse_file(file_path: str, *, typed: bool = False) -> Union[GFLAST, Dict[str, Any]]:
```

#### Parameters

- **`file_path`** (str): Path to GFL file
- **`typed`** (bool, optional): If True, return `GFLAST`; if False, return `Dict[str, Any]`. Default: False

#### Examples

```python
from gfl.api import parse_file

# Parse file in typed mode
ast = parse_file("experiment.gfl", typed=True)
```

### validate_file()

Parse and validate GFL file.

```python
def validate_file(file_path: str, *, detailed: bool = False) -> Union[List[str], ValidationResult]:
```

#### Parameters

- **`file_path`** (str): Path to GFL file
- **`detailed`** (bool, optional): If True, return `ValidationResult`; if False, return `List[str]`. Default: False

#### Examples

```python
from gfl.api import validate_file

# Validate file with detailed results
result = validate_file("experiment.gfl", detailed=True)
if result.is_valid:
    print("✓ File is valid")
```

### get_api_info()

Get API version and compatibility information.

```python
def get_api_info() -> Dict[str, str]:
```

#### Returns

Dictionary with API metadata:
- `version`: Package version
- `api_version`: API version (semantic versioning)
- `compatibility`: Compatibility information
- `typed_support`: Typed API support level
- `schema_version`: JSON schema version

#### Examples

```python
from gfl.api import get_api_info

info = get_api_info()
print(f"GFL API Version: {info['api_version']}")
```

## Type System

### Core Types

#### GFLAST

The main typed AST representation.

```python
@dataclass
class GFLAST:
    experiment: Optional[Experiment] = None
    analyze: Optional[Analysis] = None
    simulate: Optional[bool] = None
    branch: Optional[Branch] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Experiment

Represents an experimental design.

```python
@dataclass
class Experiment:
    tool: str
    type: ExperimentType
    params: ExperimentParams = field(default_factory=ExperimentParams)
    strategy: Optional[str] = None
```

#### Analysis

Represents an analysis configuration.

```python
@dataclass
class Analysis:
    strategy: AnalysisStrategy
    data: Optional[str] = None
    thresholds: AnalysisThresholds = field(default_factory=AnalysisThresholds)
    filters: List[str] = field(default_factory=list)
    operations: List[AnalysisOperation] = field(default_factory=list)
```

### Validation Types

#### ValidationResult

Detailed validation results.

```python
@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
```

#### ValidationError

Individual validation message.

```python
@dataclass
class ValidationError:
    message: str
    location: Optional[str] = None
    severity: Literal["error", "warning", "info"] = "error"
    code: Optional[str] = None
```

### Inference Types

#### InferenceResult

Detailed inference results.

```python
@dataclass
class InferenceResult:
    predictions: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## Migration Guide

### From 0.1.x to 0.2.x

The 0.2.x API is fully backward compatible with 0.1.x, but adds new typed interfaces.

#### Old Code (0.1.x)

```python
from gfl.api import parse, validate, infer

ast = parse(gfl_text)
errors = validate(ast)
results = infer(model, ast)
```

#### New Code (0.2.x - Recommended)

```python
from gfl.api import parse, validate, infer

# Use typed API for better IDE support
ast = parse(gfl_text, typed=True)
result = validate(ast, detailed=True)
inference = infer(model, ast, detailed=True)

# Access with full type safety
if result.is_valid:
    print(f"Confidence: {inference.confidence}")
```

## Error Handling

### Common Exceptions

- **`ValueError`**: Invalid input or configuration
- **`FileNotFoundError`**: File not found (file functions)
- **`ImportError`**: Missing optional dependencies

### Best Practices

```python
from gfl.api import parse, validate
from gfl.types import ValidationError

try:
    ast = parse(gfl_text, typed=True)
    result = validate(ast, detailed=True)

    if not result.is_valid:
        for error in result.errors:
            print(f"Validation error: {error}")
        return False

except ValueError as e:
    print(f"Parse error: {e}")
    return False
```

## Performance Considerations

### Memory Usage

- Typed mode uses slightly more memory due to dataclass overhead
- For large files, consider processing in chunks
- Use lazy plugin loading to reduce startup time

### Optimization Tips

```python
# Cache parsed ASTs for repeated validation
ast = parse(text, typed=True)
result1 = validate(ast, detailed=True)
result2 = some_other_validation(ast)

# Use untyped mode for simple scripts
if simple_use_case:
    ast = parse(text)  # Faster for one-off processing
```

## Version Compatibility

| GFL Version | API Version | Python | Features |
|-------------|-------------|--------|----------|
| 0.2.x       | 2.0.0       | 3.10+  | Full typed API, schema validation |
| 0.1.x       | 1.0.0       | 3.9+   | Basic API, dict-only |

## Support

- **Issues**: [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues)
- **Documentation**: [README.md](../README.md)
- **Examples**: [examples/](../examples/)
