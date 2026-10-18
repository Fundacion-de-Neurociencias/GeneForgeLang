# Intended use: GeneForgeLang (GFL)

## Statement
GeneForgeLang is open-source research software: a Python library and command-line tool for writing, parsing and validating structured descriptions of biological design and analysis workflows, and for exchanging them through typed contracts and plugins.

**It is not a medical device, is not for clinical use or diagnosis, and its outputs are not validated scientific results. Nothing in it is legal, patent or regulatory advice.** Components marked `simulated` or `stub` produce illustrative output only.

The same notice text must appear in README.md, docs/index.md and the package description (checked by `tests/docs/test_public_claims.py`, F002).

## Who uses it
- Now: the Fundación de Neurociencias team and GeneForge (sister product) as a dependency; anyone on GitHub (public repository).
- In 12 months: third-party researchers and tool builders installing it from PyPI; plugin authors; partners.

## Usage profile (`[usage]` in project.toml)
| Axis | Value | Notes |
|---|---|---|
| Audience | public-anonymous, partners | Public repo and package; partners via GeneForge |
| Business model | open-source, research | MIT license |
| Channels | library-sdk, cli; internal-http-api only while the FastAPI apps exist | F016 decides the apps |
| Data sensitivity | genetic, only where examples handle sequences or variants | The library stores no personal data |
| Regulatory | none | Valid only while the not-for-clinical-use statement holds and clinical claims are absent |
| Deployment | local-only | Runs on the user's machine |
| Tenancy | single-user | |
| Criticality | customer-facing | Public package; API stability matters to dependants |

## Primary use cases (ranked), each with its intended-use journey
1. **Validate a GFL workflow from Python.** `pip install geneforgelang` in a clean venv; `from geneforgelang import parse, validate`; parse a documented example; get a typed result and typed errors for an invalid file. Journey test: clean-venv wheel install plus smoke test (F010, F012).
2. **Validate from the command line.** `gfl validate example.gfl` on Linux, macOS and Windows; exit code 0 for valid, 1 for invalid. Journey test: CLI matrix in CI (F015).
3. **Depend on GFL contracts from another product (GeneForge).** Import the contract dataclasses from the public API and rely on their fields across minor releases. Journey test: consumer contract test (F014) plus API snapshot (F010).
4. **Extend GFL with a plugin.** Install a `gfl-plugin-*` wheel and see it discovered by the registry. Journey test: plugin discovery integration test (F013).

## Not intended
- Clinical decisions, diagnosis, treatment or patient counselling.
- Presenting simulated or stub outputs (random generators, AlphaGenome/AlphaFold stubs, DepMap fixture pairs, BioDecision scores, OpenMed connector) as measured or validated results.
- Processing identifiable patient data or third-party cohort data (ADNI, NACC) inside this public repository.
- Patentability, freedom-to-operate or regulatory conclusions.
- Running the bundled HTTP apps as an internet-facing service.
