# Public API contract

GeneForgeLang publishes the surface its clients (GeneForge, PharmaOracle, third parties) may rely on. The machine-readable contract is [`public_contract.json`](public_contract.json). It is generated from the code and is never edited by hand. This page states the rules.

GFL is a research tool. It is not for clinical use and gives no legal advice.

## What the contract covers

- The ten public functions of `geneforgelang.core.api`: name, parameters (name, kind, annotation, default) and return annotation.
- The public error types: `EnhancedValidationError`, `EnhancedValidationResult`, `ErrorSeverity`, `ErrorCategory`, `ErrorCodes` (every error code and its value), `GFLSyntaxError` and `ExecutionError`.
- The grammar: `grammar_version`, the top-level constructs `parse()` accepts, and what `parse()` returns for each conformance sample of that version. Conformance directories above `grammar_version` describe constructs the validator does not implement yet; they are listed as `unimplemented_suites`.
- An evidence label for every function: `computed` (deterministic result) or `simulated` (not measured; see the reason in the snapshot). `measured` and `stub` are valid labels too. A function with no label fails the build.

Anything else is private, including the CLI output layout, the web apps and the plugin internals. The facade `geneforgelang.parse` is planned (feature F010); when it lands it joins this contract.

## Versions

`CONTRACT_VERSION` (in `src/geneforgelang/public_contract.py`) follows SemVer:

| Change against the last accepted contract | Bump |
|---|---|
| Removed or renamed name, parameter, error code, enum member or construct; changed default, annotation or return type; new required parameter; lowered evidence label | MAJOR |
| New name, optional parameter, error code, construct; raised evidence label | MINOR |
| No surface change | PATCH or none |

Evidence order, weakest to strongest: `stub`, `simulated`, `computed`, `measured`. A bump of `GRAMMAR_VERSION` needs a contract bump of at least the same level.

Every surface change also needs a `Contract X.Y.Z` line in `CHANGELOG.md`.

## Working with the contract

Run these from the repository root:

```
python -m geneforgelang.public_contract --check          # the snapshot equals the code
python -m geneforgelang.public_contract --write          # regenerate after an intended change
python -m geneforgelang.public_contract --against REF    # bump and changelog rules against a git ref
python -m geneforgelang.public_contract --check-tag vX.Y.Z   # tag equals pyproject.toml and __version__
```

To change the surface on purpose: change the code, raise `CONTRACT_VERSION` as the table says, add the changelog line, run `--write`, commit the snapshot. The pull request workflow `.github/workflows/contract.yml` runs `--check` and `--against origin/main`; on a `vX.Y.Z` tag it also runs `--check-tag`, so a tag and the package metadata cannot disagree.

Tests: `tests/contract/test_public_contract.py`.
