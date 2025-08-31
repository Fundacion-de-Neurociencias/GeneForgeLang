# Changelog

All notable changes to GeneForgeLang will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-30

### Added

#### 🎯 Stable & Typed API
- **Complete typed API** with dataclasses and TypedDict for AST structures
- **Backward compatible** with 0.1.x APIs while adding new typed interfaces
- **Semantic versioning** with strict API contract (`api_version = "2.0.0"`)
- **Overloaded functions** supporting both typed and untyped modes
- **Enhanced validation** with detailed `ValidationResult` objects
- **Improved inference** with structured `InferenceResult` objects

#### 📋 Enhanced Schema & Validation
- **Comprehensive JSON Schema** for GFL with examples and validation rules
- **Schema-based validation** using jsonschema library
- **Format-specific validation** for GFL conventions and best practices
- **Multi-level validation** (errors, warnings, info)
- **Tool-type compatibility checks** for experimental configurations
- **Sequence validation** for guide RNAs and other genomic sequences

#### 📦 PyPI-Ready Packaging
- **Production-ready pyproject.toml** with full metadata and classifiers
- **Multiple optional dependencies** organized by use case:
  - `[schema]` - JSON schema validation
  - `[apps]` - Demo applications
  - `[ml]` - Machine learning stack
  - `[dev]` - Development tools
  - `[qa]` - Quality assurance tools
  - `[test]` - Testing frameworks
  - `[docs]` - Documentation tools
- **Entry points** for plugin discovery and external integrations
- **Proper version management** with semantic release support

#### 🔧 Enhanced CLI Tools
- **gfl-parse**: Parse GFL files with multiple output formats (JSON, YAML, repr)
- **gfl-validate**: Comprehensive validation with schema checking
- **gfl-infer**: Run inference with configurable models
- **gfl-schema**: Display and validate against JSON schema
- **gfl-info**: System and API information display
- **Rich argument parsing** with detailed help and examples
- **Multiple output formats** and file output support

#### 🔌 Advanced Plugin System
- **Entry point discovery** using `importlib.metadata`
- **Lazy plugin loading** for improved performance
- **Plugin metadata** and validation support
- **Base plugin class** (`BaseGFLPlugin`) for consistent interfaces
- **Plugin registry** with automatic discovery and error handling
- **External plugin support** via pyproject.toml entry points

#### ⚙️ Comprehensive CI/CD
- **Multi-platform testing** (Linux, Windows, macOS)
- **Python version matrix** (3.10, 3.11, 3.12, 3.13)
- **Quality gates** with ruff, black, mypy, bandit, safety
- **Coverage reporting** with codecov integration
- **Build and packaging tests** for PyPI readiness
- **Nightly builds** to catch dependency issues early

#### 🛠️ Developer Experience
- **Pre-commit hooks** for code quality enforcement
- **Comprehensive .gitattributes** for cross-platform consistency
- **Security configurations** for sensitive file handling
- **Type checking** with mypy strict mode
- **Code formatting** with black and ruff
- **Documentation standards** with pydocstyle

#### 🔄 MCP Integration
- **Supermemory MCP integration** for cross-platform AI context sharing
- **Setup automation** for easy MCP configuration
- **Demo applications** showing practical MCP usage
- **Documentation** for integrating with Claude, ChatGPT, Cursor, etc.

### Changed

#### API Improvements
- **Enhanced error messages** with location information and error codes
- **Consistent return types** across all API functions
- **Better type hints** with proper overloads and literals
- **Improved documentation** with comprehensive examples

#### Code Quality
- **Stricter type checking** with mypy configuration
- **Enhanced security** with bandit and safety checks
- **Better test organization** with pytest markers and fixtures
- **Improved logging** with structured messages and levels

#### Performance
- **Lazy loading** for optional dependencies and plugins
- **Efficient plugin discovery** with caching mechanisms
- **Memory optimization** for large AST processing
- **Faster CI** with parallel job execution

### Fixed

#### Parser & Validation
- **Robust YAML parsing** with better error handling
- **Consistent AST structure** across different input formats
- **Validation edge cases** for complex experimental configurations
- **Plugin loading failures** with graceful degradation

#### Cross-Platform
- **Line ending consistency** with comprehensive .gitattributes
- **Path handling** for Windows/Unix compatibility
- **Encoding issues** with UTF-8 enforcement
- **Build reproducibility** across different environments

### Documentation

#### New Documentation
- **API Reference** (`docs/API_REFERENCE.md`) with comprehensive examples
- **Migration Guide** for upgrading from 0.1.x to 0.2.x
- **Plugin Development Guide** for external plugin authors
- **MCP Integration Guide** for AI platform setup

#### Improved Documentation
- **README.md** updated with new features and examples
- **Type annotations** in all public APIs
- **Docstring improvements** with Google-style formatting
- **Code examples** for all major use cases

### Dependencies

#### Added
- `typing-extensions>=4.0` for Python < 3.11 compatibility
- `jsonschema>=4.0` for schema validation (optional)
- Development tools: mypy, ruff, black, bandit, safety, pytest-cov

#### Updated
- Minimum Python version: 3.10+ (was 3.9+)
- PyYAML: 6.0+ (stricter version requirement)
- Optional dependencies with better version constraints

## [0.1.0] - Previous Release

### Added
- Basic GFL parser with YAML syntax
- Simple validation framework
- Demo applications with Gradio
- Plugin system foundation
- Initial CI setup

---

## Migration Notes

### From 0.1.x to 0.2.x

The 0.2.x release is **fully backward compatible** with 0.1.x APIs. However, we strongly recommend migrating to the new typed API for better development experience:

```python
# Old (0.1.x) - still works
from gfl.api import parse, validate
ast = parse(gfl_text)
errors = validate(ast)

# New (0.2.x) - recommended
from gfl.api import parse, validate
ast = parse(gfl_text, typed=True)
result = validate(ast, detailed=True)
```

### Breaking Changes

- **Minimum Python version**: Now requires Python 3.10+ (was 3.9+)
- **Import changes**: Some internal modules reorganized (public API unchanged)
- **Optional dependencies**: Some features now require explicit installation of extras

### Upgrade Steps

1. **Update Python**: Ensure you're using Python 3.10 or later
2. **Reinstall package**: `pip install geneforgelang[schema,test]`
3. **Update imports**: Use new typed API where possible
4. **Run tests**: Verify your code works with new version
5. **Update CI**: Use new quality tools and matrix testing

For detailed migration instructions, see `docs/API_REFERENCE.md`.
