# Contributing to GeneForgeLang

## Workflow for Language Evolution
1. Open an Issue (Language Change Request) describing motivation, syntax/semantics, examples.
2. Implement in this repo: parser/AST, validator/interpreter, and tests.
3. Update docs/spec/examples.
4. Bump version in pyproject.toml (semver), tag release, publish to PyPI.
5. Notify GeneForge to update dependency.

## Code Quality
- Keep public API stable where possible; document breaking changes.
- Add tests for all new grammar/semantics.
- CI must pass before merging.

## Release Process
- Update [project].version.
- Create annotated tag X.Y.Z.
- CI publishes to PyPI when tag is pushed (requires PYPI_API_TOKEN).
