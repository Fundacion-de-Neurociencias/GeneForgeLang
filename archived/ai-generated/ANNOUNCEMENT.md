# GeneForgeLang v1.0.0 Release Announcement

## 🎉 We're Excited to Announce the Release of GeneForgeLang v1.0.0! 🎉

We're thrilled to announce the official release of GeneForgeLang (GFL) v1.0.0, a major milestone in our journey to revolutionize genomic workflow automation. This release represents months of dedicated development and introduces groundbreaking features that position GFL as the most advanced and extensible genomic workflow language available.

## 🚀 What's New in v1.0.0

### Advanced AI Workflow Syntax
GFL v1.0.0 introduces powerful new syntax extensions that enable sophisticated AI-driven workflows:
- **Active Learning Optimization**: Enhanced optimize blocks with Active Learning strategy support
- **Inverse Design**: Extended design blocks for inverse design workflows
- **Data Refinement**: New refine_data blocks for intelligent data preprocessing
- **Guided Discovery**: Revolutionary guided_discovery blocks that combine generative design with active learning

### IO Contracts System
Data integrity is critical in genomic workflows. Our new IO Contracts system ensures compatibility between workflow blocks with:
- Static compatibility checking between block outputs and inputs
- Strong typing for genomic data with built-in validation
- Support for both built-in and custom data types

### Type System & Schema Registry
GFL is now more extensible than ever with our powerful Schema Registry:
- Define custom data types in external schema files
- Import schema definitions with the new `import_schemas` directive
- Use custom types in IO contracts for domain-specific validation

## 🧪 Key Features

### AI-Powered Workflows
- **Generative Design**: AI models for protein, DNA, and molecule generation
- **Intelligent Optimization**: Bayesian optimization, genetic algorithms, and active learning
- **Parameter Injection**: Dynamic parameter substitution with `${...}` syntax
- **Workflow Integration**: Seamless combination of design and optimization blocks

### Developer Experience
- **Enhanced Validation**: Rich error reporting with location tracking and suggested fixes
- **Backward Compatibility**: All existing workflows continue to work without modification
- **Comprehensive Documentation**: Complete guides and tutorials for all new features

## 🌟 Impact for the GeneForge Community

### For Researchers
- Accelerate discovery with AI-driven experimental design
- Reduce errors with automated data integrity checking
- Customize workflows for domain-specific requirements

### For Developers
- Extend GFL with custom data types and validation rules
- Build powerful plugins that integrate with the new workflow system
- Leverage improved tooling and error reporting

### For the Genomics Community
- Standardize genomic workflows with a powerful, extensible language
- Enable reproducible research with structured workflow definitions
- Foster collaboration through shared schema definitions and plugins

## 📚 Documentation & Resources

We've prepared comprehensive documentation to help you get started with GFL v1.0.0:

- [Complete Documentation](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)
- [Tutorial: Using Custom Schemas in IO Contracts](docs/tutorials/custom_schemas_io_contracts.md)
- [IO Contracts System Guide](docs/features/io_contracts.md)
- [Schema Registry Documentation](docs/features/schema_registry.md)
- [Guided Discovery Block Documentation](docs/features/guided_discovery.md)
- [Full Changelog](CHANGELOG.md)

## 🚀 Getting Started

To start using GFL v1.0.0, update your installation:

```bash
pip install --upgrade geneforgelang
```

Or if you're installing from source:

```bash
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang
pip install -e .
```

## 🙏 Acknowledgements

We want to thank the entire GeneForge community for their feedback, contributions, and support throughout the development of v1.0.0. Your input has been invaluable in shaping this release.

## 📣 Feedback and Support

We're excited to see what you'll build with GFL v1.0.0! Please share your experiences, report any issues, and suggest improvements through our [GitHub repository](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang).

For support, check out:
- [Documentation](https://fundacion-de-neurociencias.github.io/GeneForgeLang/)
- [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues)
- [GitHub Discussions](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions)

---

**GeneForgeLang Team**
*Empowering genomic research through structured workflows and AI-powered analysis*
