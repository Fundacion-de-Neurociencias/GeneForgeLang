# Contributing to GeneForgeLang

## Workflow for Language Evolution (Protocolo /neuroia)
1. **Branch Isolation**: Never commit directly to `main`. Create a feature branch: `feature/<feature-name>` or `feat/<feature-name>`.
2. **Implementation**: Implement in this repo: parser/AST (`src/geneforgelang/core/`), validator/interpreter, and decoupled plugins (`gfl-plugin-*`).
3. **Automated Verification**: Run the relevant test suite and ensure zero regressions across `tests/unit/`.
4. **Mandatory Documentation Policy (Regla Obligatoria)**:
   - Every substantive development (new types, AST blocks, contracts, plugins, mathematical or biological primitives) **MUST be documented immediately upon creation** in the existing official documentation files:
     - `docs/architecture.md`: Compiler layers, runtime, data flows, and axiomatic invariants.
     - `docs/index.md`: Master index and links to new capabilities.
     - `docs/geneforgelang/plugins/PLUGIN_ECOSYSTEM.md`: Satellite plugin catalog and entry points.
     - `docs/geneforgelang/features/<feature>.md`: Dedicated feature specification.
     - `CHANGELOG.md`: Detailed entry under `[Unreleased]`.
     - `README.md`: High-level summary of capabilities.
5. **Pull Request**: Push branch to origin and open a PR against `main` via `gh pr create`.
6. **Release**: Bump version in `pyproject.toml` (semver), tag release, publish to PyPI, and notify downstream consumers (GeneForge).

## Code Quality & Architecture Guarantees
- **ADR-001**: Clean boundary between GFL (legislative, types, semantics) and GeneForge (executive runtime).
- **ADR-0003**: Amputability and orthogonality. Satellite plugins must remain decoupled packages using entry-points without polluting GFL core dependencies.
- **Scientific Rigor**: No mock data or simulated responses in validation gates. Real biological data and empirical verification are strictly required.
