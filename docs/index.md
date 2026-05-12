# GeneForgeLang Documentation Index

> **The Symbolic Language for Biological Reasoning**

Welcome to the official documentation for GeneForgeLang (GFL). This index provides easy navigation to all documentation resources.

## Getting Started

**New to GeneForgeLang?** Start here:

- [Installation Guide](guides/user-guides/installation.md) — Install GFL and dependencies
- [Quick Start](guides/user-guides/quickstart_user.md) — Your first workflow in 5 minutes
- [Comprehensive Tutorial](guides/user-guides/tutorial.md) — Step-by-step guide to GFL concepts

## User Guides

Practical guides for using GeneForgeLang:

| Guide | Purpose |
|-------|---------|
| [CLI Reference](guides/geneforgelang/cli.md) | Command-line interface documentation |
| [API Reference](guides/geneforgelang/api.md) | Python API for programmatic access |
| [Custom Schemas & IO Contracts](guides/user-guides/custom_schemas_io_contracts.md) | Define data structures and contracts |

---

## Core Features & Capabilities

Learn about GFL's powerful features:

### Workflow Components

- [Design Block](geneforgelang/features/design_block.md) — Generate biological entities
- [Optimize Block](geneforgelang/features/optimize_block.md) — Parameter optimization and tuning
- [Data Staging](geneforgelang/features/data_staging.md) — Manage workflow inputs/outputs
- [Refine Data](geneforgelang/features/refine_data.md) — Post-processing and data refinement

### Analysis & Reasoning

- [Symbolic Reasoning](geneforgelang/features/symbolic_reasoning.md) — Bayesian and rule-based reasoning
- [Schema Registry](geneforgelang/features/schema_registry.md) — Type definitions and validation
- [With Priors Clause](geneforgelang/features/with_priors_clause.md) — Bayesian prior integration
- [IO Contracts](geneforgelang/features/io_contracts.md) — Contract-based data validation

### Specialized Features

- [Guided Discovery](geneforgelang/features/guided_discovery.md) — AI-powered workflow optimization
- [Container Execution](geneforgelang/features/container_execution.md) — Docker container integration
- [Spatial Genomic Capabilities](geneforgelang/features/spatial_genomic_capabilities.md) — 3D genome analysis
- [Locityper Haplotyping](geneforgelang/features/locityper_haplotyping.md) — HLA/KIR genotyping
- [Epigenetic Editing](geneforgelang/features/epigenetic_editing.md) — CRISPR-based epigenetic modifications
- [Capability-Aware Validator](geneforgelang/features/capability_aware_validator.md) — Context-aware validation

### Advanced Topics

- [Enhancer Module Specification](geneforgelang/features/Enhancer_Module_Spec.md) — Regulatory element design

---

## Plugin Ecosystem

Extend GFL with plugins:

### Overview & Architecture

- [Plugin Ecosystem Overview](geneforgelang/plugins/plugins_overview.md) — Plugin system architecture
- [Plugin Ecosystem Documentation](geneforgelang/plugins/PLUGIN_ECOSYSTEM.md) — Complete plugin guide

### Core Plugins

Available in `geneforgelang/plugins/core_plugins/`:

- BLAST — Sequence similarity searches
- GATK — Genomic variant analysis
- SAMtools — Sequence manipulation
- And more...

### Genesis Plugins

Available in `geneforgelang/plugins/genesis_plugins/`:

- On-Target Scoring — CRISPR efficiency
- Off-Target Scoring — CRISPR risk
- Evaluator — Combined scoring
- Visualizer — Results visualization

### Creating Custom Plugins

- [Creating Plugins Guide](guides/dev-guides/creating_plugins.md) — Build your own plugins

---

## Development

For developers and contributors:

### Architecture & Design

- [Organizational Architecture](dev/decisions/organization.md) — System organization
- [Design Ontology](dev/decisions/ontology.md) — Core concepts and relationships
- [Design History](dev/decisions/HISTORY.md) — Evolution of design decisions

### Deployment & Operations

- [Deployment Guide](guides/dev-guides/DEPLOYMENT_GUIDE.md) — Production deployment

---

## Additional Resources

- **Examples**: See [examples/](../examples/) directory for workflow examples
- **Schema**: [schema/](../schema/) contains JSON schemas and type definitions
- **Source Code**: [src/](../src/) contains the main GeneForgeLang implementation

---

## External Links

- [GitHub Repository](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang) — Source code
- [Security Policy](../SECURITY_ADVISORY.md) — Security information
- [Contributing Guide](../CONTRIBUTING.md) — How to contribute
- [License](../LICENSE) — MIT License

---

## Document Organization

```
docs/
├── INDEX.md (this file)
├── guides/
│   ├── user-guides/          # User-facing documentation
│   │   ├── installation.md
│   │   ├── quickstart_user.md
│   │   ├── tutorial.md
│   │   └── custom_schemas_io_contracts.md
│   └── dev-guides/           # Developer documentation
│       ├── creating_plugins.md
│       └── DEPLOYMENT_GUIDE.md
├── geneforgelang/                 # App documentation
|   ├── features/                 # Feature documentation
│   |   ├── design_block.md
│   |   ├── optimize_block.md
│   |   ├── symbolic_reasoning.md
│   |   ├── guided_discovery.md
│   |   └── ... (15 feature docs total)
│   ├── plugins/              # Plugin documentation
|   │   ├── plugins_overview.md
|   │   ├── PLUGIN_ECOSYSTEM.md
|   │   ├── core_plugins/
|   │   └── genesis_plugins/
|   ├── api.md
|   └── cli.md
└── dev/                      # Development resources
    ├── decisions/            # Architecture decisions
    │    ├── organization.md
    │    ├── ontology.md
    │    └── HISTORY.md
    └── reports/
```

---

*Last updated: April 2026*  
*GeneForgeLang - The Symbolic Language for Biological Reasoning*
