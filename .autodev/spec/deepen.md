# Deepen: "GFL as an open library other applications can depend on"

## 1. The professional's move
The field is **open-source Python library maintenance for scientific software** (the practice of projects such as Biopython, pydantic, attrs and the Scientific Python ecosystem).
A top maintainer would not start by adding syntax. They would:
- define the **public surface** explicitly, small and typed. Everything else is private. A compatibility promise (SemVer plus a deprecation policy) is enforced by a machine check, not by an ADR alone;
- make **the built artifact** the thing under test: install the wheel in a clean environment on every OS, rather than testing an editable checkout;
- treat **provenance and honesty** as part of the API. Results say whether they are measured, computed, simulated or a stub. Docs make no claim the tests do not back;
- make **downstream breakage visible before release**: consumer contract tests for known dependants (GeneForge), and an API diff against the last tag;
- **secure the supply chain**: Trusted Publishing, build attestations, pinned CI actions, secret scanning, no pickles;
- make **plugins a versioned protocol** with one discovery mechanism, tested from installed wheels.

## 2. The rawest material
- The **built wheel and sdist** (`python -m build`), and what `pip install` actually puts on disk; not the source tree.
- The **import graph** of `src/geneforgelang` and `python -X importtime` output.
- **Signatures extracted from code** (griffe), compared with ADR-0004, `docs/spec/API_CONTRACT.md` and `src/geneforgelang/governance/public_manifest.json`.
- **Installed entry points** (`importlib.metadata.entry_points()`) after installing each `gfl-plugin-*` wheel.
- **GeneForge's own import statements** (grep of its tests and bridges), not its docs.
- **CI logs** on a clean runner; not CHANGELOG's "100% passing".
- **PyPA specifications** (PEP 517/518/621, core metadata, PEP 561) and the PyPI Trusted Publishing docs.

## 3. Methods and tools
- Packaging: `build`, `twine check`, `check-wheel-contents`, `pyroma`; single version source (setuptools-scm or pyproject).
- API: `griffe check` (API diff against the last tag), a parametrized import test over the manifest, `mypy --strict`, PEP 561 `py.typed`, mkdocstrings reference with doctests.
- Architecture: `import-linter` contracts (facade → core → plugins; core never imports cli/web).
- Tests: pytest; Hypothesis property tests for the parser and validator; `mutmut` on core; an honest conformance runner with a meta-test.
- Supply chain: gitleaks, pip-audit, OpenSSF Scorecard checks, SHA-pinned actions, PyPI Trusted Publishing (OIDC), GitHub artifact attestations (SLSA build level 2).
- Cross-platform: CI matrix on ubuntu, windows and macos; Python 3.9-3.12.

## 4. External oracles
| Oracle | What it proves | Feature |
|---|---|---|
| Clean-venv install of the built wheel, then `from geneforgelang import parse, validate` and `gfl --help`, on 3 OSes | The library is usable as shipped | F010, F012, F015 |
| `griffe check` against the last tag | No unannounced breaking change (SemVer) | F010, F011 |
| Downstream consumer smoke test (GeneForge's imports and fields) | Dependants keep working | F014 |
| Plugin wheels installed in a clean venv appear in the registry | Plugin discovery works for third parties | F013 |
| `twine check` and the TestPyPI dry run (owner gate) | The package meets PyPI's metadata rules | F011, F012 |
| gitleaks and pip-audit in CI; Scorecard checks | Supply-chain hygiene | F001, F003 |
| Conformance meta-test with a wrong expectation | The conformance suite can fail | F006 |
| Claims test over public text | Public text matches the evidence | F002 |

## Restated task
Ship GFL as a library whose **built wheel** installs in a clean environment on Linux, Windows and macOS. It exposes a small typed public API (`parse`, `validate`, `geneforgelang.api/.types/.contracts`), checked against the manifest and against the last tag with an API diff. GeneForge's imports are pinned by a consumer contract test. Plugins are discovered from installed wheels through one entry-point group. Every result carries provenance, and simulated output is labelled. Releases use Trusted Publishing from tags with attestations, after owner approval.
Acceptance is the oracles above, run in CI. "Tests pass in the dev checkout" is not acceptance.
