# GeneForgeLang Repository Organization

This document describes the organization of the GeneForgeLang repository following the recommended structure.

## Core Library Components (✅ Commit Obligatory)

### Source Code (gfl/)
The core GFL library source code is located in the [gfl/](gfl/) directory, including essential modules:
- [error_handling.py](gfl/error_handling.py) - Error handling and validation result classes
- [parser.py](gfl/parser.py) - YAML parser for GFL documents
- [schema_loader.py](gfl/schema_loader.py) - Schema registry and loading functionality
- [semantic_validator.py](gfl/semantic_validator.py) - Semantic validation of GFL ASTs
- [types.py](gfl/types.py) - Type definitions and utilities

### Official Documentation (docs/)
Documentation is organized in the [docs/](docs/) directory:
- [features/](docs/features/) - Feature-specific documentation
- [tutorials/](docs/tutorials/) - Step-by-step tutorials
- Key documents: [API_REFERENCE.md](docs/API_REFERENCE.md), [PLUGIN_ECOSYSTEM.md](docs/PLUGIN_ECOSYSTEM.md), etc.

### Library Tests (tests/)
Comprehensive test suite in the [tests/](tests/) directory:
- Unit tests in [tests/unit/](tests/unit/)
- Integration tests in [tests/integration/](tests/integration/)
- Test files: [test_advanced_validation.py](test_advanced_validation.py), [test_io_contracts.py](test_io_contracts.py), [test_schema_registry.py](test_schema_registry.py)
- Test data: [test_advanced_syntax.gfl](test_advanced_syntax.gfl), [test_custom_types.yml](test_custom_types.yml), [test_io_contracts.gfl](test_io_contracts.gfl), [test_schema_registry.gfl](test_schema_registry.gfl)

### Maintenance Scripts (scripts/)
Maintenance tools in the [scripts/](scripts/) directory:
- [pre_release_check.py](scripts/pre_release_check.py) - Pre-release validation
- [release.ps1](scripts/release.ps1) and [release.sh](scripts/release.sh) - Release automation scripts

## Example Projects (✅ Commit Recommended)

### GFL Genesis Project (examples/gfl-genesis/)
A comprehensive example project demonstrating advanced GFL capabilities:
- Main workflow: [genesis.gfl](examples/gfl-genesis/genesis.gfl)
- Custom plugins in [plugins/](examples/gfl-genesis/plugins/) directory
- Schema definitions in [schemas/](examples/gfl-genesis/schemas/) directory
- Project documentation in [docs/](examples/gfl-genesis/docs/) directory
- Planning documents in [docs/planning/](examples/gfl-genesis/docs/planning/) directory

### Simple Examples (examples/)
Basic examples in the [examples/](examples/) directory:
- Simple workflows: [example1.gfl](examples/example1.gfl), [example2.gfl](examples/example2.gfl)
- Specialized examples: [example_crispr_optimization.gfl](example_crispr_optimization.gfl), [example_protein_design.gfl](example_protein_design.gfl)

## Internal Development Files (❌ Ignore)

The following internal development artifacts are excluded from version control via [.gitignore](.gitignore):
- Implementation summary files: `*_SUMMARY.md`
- Temporary files and build artifacts
- Cache directories and compiled Python files

## Directory Structure

```
.
├── gfl/                        # Core library source code
├── docs/                       # Official documentation
│   ├── features/               # Feature documentation
│   └── tutorials/              # Step-by-step tutorials
├── tests/                      # Library test suite
├── scripts/                    # Maintenance scripts
├── examples/                   # Example projects and workflows
│   ├── gfl-genesis/            # Comprehensive example project
│   │   ├── genesis.gfl         # Main workflow definition
│   │   ├── plugins/            # Custom plugins
│   │   ├── schemas/            # Schema definitions
│   │   ├── docs/               # Project documentation
│   │   │   └── planning/       # Planning documents
│   │   └── ...                 # Other project files
│   └── ...                     # Simple examples
├── .gitignore                  # Git ignore rules
└── ...                         # Other repository files
```

This organization maintains a clean separation between the core GFL library and example projects, making it easy for users to understand the structure and find what they need.