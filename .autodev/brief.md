# Brief: GeneForgeLang (GFL), as found on 2026-10-18

Claims are tagged OBSERVED (seen in code, git or a command), INFERRED (deduced from observations) or ASSUMED (not checked). Paths are relative to the repository root. "chain" means the tip of the stacked feature-branch chain (`feature/viral-interactome-complexes`, commit 1b72405). "main" means `origin/main` (630059c, 2026-06-15).

## What it is
- OBSERVED: a public, MIT-licensed Python package `geneforgelang` (src layout, setuptools, Python >= 3.9) in the GitHub org Fundacion-de-Neurociencias. It provides a YAML-based workflow language for biological design (parser, validator, inference engine), about 65 typed contract dataclasses (`src/geneforgelang/core/gftypes.py`), a plugin registry, a CLI (`gfl`, `geneforgelang`), an LSP server (`src/gfl_lsp`) and two FastAPI apps.
- OBSERVED: the product is the chain, not main. The chain has 45 commits over main across ~26 feature branches, never merged; main has 31 commits not in the chain (carlosgoro's formalization-v2 merge and ruff/pytest fixes). A simulated merge gives 3 conflicts: CONSTITUTION.md, PROTOCOL.md and the conformance runner location (`resources/tools/dev/` on main, `scripts/` on the chain).
- OBSERVED: GeneForge (private) does not import GFL at runtime; its tests use `geneforgelang.core.gftypes` contracts that exist only on the chain.

## Component status
| Component | Path | Status | Evidence |
|---|---|---|---|
| Parser, validator | `src/geneforgelang/core/{parser,validator,advanced_validator}.py` | real | OBSERVED; tested |
| Working API | `src/geneforgelang/core/api.py` | real | OBSERVED: only importable API |
| Documented public API | `geneforgelang.{api,types,contracts}`, `from geneforgelang import parse` | dead/broken | OBSERVED: `__init__.py` lists `parse`, `validate`, `execute`, `infer` in `__all__` without importing them; `api/` holds only `gfl_service.py` |
| `export_evidence_graph` | `src/geneforgelang/__init__.py` | stub | OBSERVED: returns a constant dict |
| Contract dataclasses | `src/geneforgelang/core/gftypes.py` | real (chain only) | OBSERVED |
| Inference engine | `src/geneforgelang/core/enhanced_inference_engine.py` | unknown | ASSUMED; excluded from mypy |
| Builtin protein generator, optimizer | `src/geneforgelang/plugins/builtin/{protein_generator,simple_optimizer}.py` | simulated | scout: random output |
| AlphaGenome, AlphaFold | `src/geneforgelang/plugins/{alpha_genome,alphafold}.py`, `gfl-plugin-alphagenome/` | stub | scout |
| DepMap plugin | `gfl-plugin-depmap/gfl_plugin_depmap/plugin.py` | simulated | scout: 5 hardcoded pairs |
| BioDecision | `src/geneforgelang/plugins/biodecision_plugin.py` (chain) | simulated | OBSERVED: docstring and `DEFAULT_BENCHMARK_ECE = 0.068` claim calibration; scout: logits from a hash |
| OpenMed connector | `src/geneforgelang/ir/external/openmed_connector.py` | simulated | OBSERVED: md5-derived entities, `"privacy_cleared": True` constant (line 246) |
| Conformance runner | `scripts/conformance_runner.py` (chain), `resources/tools/dev/conformance_runner.py` (main) | simulated | OBSERVED: `actual = expected # Mocking success` |
| BRCA1 "validation" | `examples/real_project/execute_genesis_real.py` | simulated | OBSERVED: scores from `np.random.beta` (lines 41-42) |
| Plugin registry | `src/geneforgelang/plugins/plugin_registry.py` | broken | OBSERVED: discovers only group `gfl.plugins` (line 755); 6 of 7 in-repo plugin packages register under `geneforgelang.plugins`; scout: imports the deleted `gfl` module |
| LSP server | `src/gfl_lsp/` | dead | OBSERVED: `from gfl.api import parse, validate` |
| CLI | `src/geneforgelang/cli/commands.py` | real, fragile | scout: crashes on Windows cp1252; nested ImportError fallbacks |
| FastAPI apps | `src/geneforgelang/web/server.py` (main), `src/geneforgelang/api/gfl_service.py` (chain) | real, insecure | OBSERVED: `allow_origins=["*"]`; no auth dependency |
| In-repo plugin packages | `gfl-plugin-{alphagenome,bgc,causal-evidence,clawbio,depmap,jev,rfo}/` (chain) | mixed | OBSERVED |
| Apps | `applications/` (Gradio, translator) | unknown | ASSUMED demo apps |

## Packaging, versions, quality
- OBSERVED: versions disagree: pyproject and `__init__` 1.0.0; README badge 2.0.0-beta; `get_api_info` 0.1.0 (scout); tags v0.2.0-v0.2.4 and v2025.06-initial-stable. Not on PyPI, but README shows a PyPI badge and `pip install geneforgelang`. CITATION.cff DOI `10.1101/2024.08.31.geneforgelang` is malformed.
- OBSERVED: `ruff.toml` (line length 120, many ignores) and `pyproject [tool.ruff]` (line length 100) conflict; ruff.toml wins. `quality.yml` runs black/isort/flake8 against ruff's rules. `ci-pipeline.yml` runs `ruff check . --fix`, which repairs instead of failing. `protect-main.yml` checks parent count only. Actions are not SHA-pinned.
- OBSERVED: pytest.ini (asyncio_mode=auto, --strict-config) overrides pyproject's pytest config and needs pytest-asyncio, which no extra declares.
- Scout: the chain collects 1050 tests; ruff reports 90 errors on the chain and 1 on main. The independence guard in quality.yml greps a path that does not exist.
- OBSERVED: main tracks `CONTRIBUTING.MD` and `CONTRIBUTING.md` (case collision).

## Security and data
- OBSERVED: `.devcontainer/.env` is tracked on main and the chain (since 2025-09 per scout). Not read. Treated as compromised.
- OBSERVED: `resources/tools/genetics/genetic_risk_predictor.pkl` is tracked on main (not on the chain). Pickle loading executes code; provenance unknown.
- OBSERVED: `EVIDENCE_MATRIX.md` (chain) discusses ADNI and NACC variables (APOE4, MMSE, CDRSB). Both datasets are under DUAs.
- OBSERVED: main is unprotected (scout); agent commits appear as "Fundación de Neurociencias <admin@fneurociencias.org>" (87 of 157 commits since 2026-01-01) and "Usuario <usuario@example.com>".

## Public text
See `spec/claims-inventory.md`. README, manuscript, whitepaper, CHANGELOG, SECURITY.md and CITATION.cff contain claims without evidence.
