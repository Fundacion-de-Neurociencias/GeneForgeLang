# Baseline audit: GeneForgeLang (2026-10-18)

Read-only. Scope: the chain tip (1b72405) with origin/main (630059c) as baseline. Scores per `quality/DIMENSIONS.md`: 0 absent or harmful, 1 ad hoc, 2 in place and partly verified, 3 verified and guarded in CI. Profile: public open-source research library and CLI, local-only, customer-facing.
Limitation: pytest and ruff were not run by the planner, to avoid writing caches into the read-only worktree. Counts come from the scout (1050 tests collected; 90 ruff errors on the chain, 1 on main).

| # | Dimension | Score | Evidence |
|---|---|---|---|
| D1 | Product coherence & dead ends | 1 | `gfl_lsp` imports the deleted `gfl` module; `export_evidence_graph` is a constant stub in `__init__`; documented modules `api`/`types`/`contracts` do not exist; two FastAPI apps unused by GeneForge; loose root scripts (`demo_ir.py`, `main.py`); `scripts/fix_joss_issues.py`, `cleanup_script.py`; status docs in `docs/` (`END_TO_END_TRUTH_AUDIT.md`, `PULL_REQUEST_DESCRIPTION.md`); external plugin blast is corrupt |
| D2 | User journeys & UX | 0 | The first documented journey (`pip install geneforgelang`, `from geneforgelang import parse`) fails at both steps; CLI crashes on Windows cp1252 |
| D3 | Correctness & tests | 1 | 1050 tests collect on the chain, but no CI gate has run them on the chain; conformance runner hard-codes success (`actual = expected`); CHANGELOG "100% passing" unbacked; pytest config split between pytest.ini and pyproject; pytest-asyncio needed but undeclared |
| D4 | Security | 0 | `.devcontainer/.env` tracked in a public repo since 2025-09; `genetic_risk_predictor.pkl` on main (unsafe deserialisation, unknown provenance); `allow_origins=["*"]` and no auth in `web/server.py`, no auth in `api/gfl_service.py`; no secret scanning; actions not SHA-pinned; main unprotected |
| D5 | Privacy & data protection | 1 | Library stores no personal data; OpenMed connector claims `privacy_cleared: True` without a filter; genetic data only in examples |
| D6 | Regulatory & legal | 0 | Clinical claims (README "Clinical Relevance", whitepaper "Clinical-Grade", manuscript "clinical translation") with no intended-use statement or disclaimer; ADNI/NACC variables in a public file (`EVIDENCE_MATRIX.md`) without recorded DUA review; MIT license present |
| D7 | Scientific & model validity | 0 | BRCA1 "validation" from `np.random.beta`; BioDecision "ECE 0.068" from hash logits; DepMap 5 hardcoded pairs; random generator and optimizer; simulated outputs unlabelled, against NeuroIA §8.1 |
| D8 | CI/CD & release | 1 | Three workflows: `ci-pipeline.yml` runs `ruff check . --fix` (never fails on fixable errors); `quality.yml` runs black/isort/flake8, which conflict with ruff, and an independence guard on a missing path; `protect-main.yml` only counts merge parents; no build or release job; versions disagree (1.0.0, 2.0.0-beta, 0.1.0, v0.2.x tags); not on PyPI |
| D9 | Reliability & observability | 1 | Local library; `print` used in library code paths; logging not structured. N/A for uptime and backups (local-only) |
| D10 | Performance & cost | N/A | Local library; `core/performance.py` exists but no budgets. Revisit if import time becomes a problem (heavy optional deps) |
| D11 | Accessibility | N/A | No UI in scope (Gradio apps in `applications/` are demos) |
| D12 | Dependencies & supply chain | 1 | Open lower-bound ranges only; no lockfile for CI; no Dependabot/Renovate config observed; pre-commit hooks pinned to old revs (ruff v0.1.9); no SBOM |
| D13 | Documentation | 1 | Extensive docs, ADRs and mkdocs site (`gh-pages` branch), but README instructions fail, versions disagree, ADR-0004/API_CONTRACT describe modules that do not import, and decisions are split between `docs/adr/` and `docs/decisions/` |
| D14 | Developer experience & reproducibility | 1 | Makefile, devcontainer, pre-commit exist; but the devcontainer ships a tracked `.env`; `make dev-install` installs `[all]` (torch); duplicate lint configs; CONTRIBUTING.MD/.md case collision on main breaks checkouts on Windows/macOS |
| D15 | Architecture & maintainability | 1 | No enforced boundaries; `core/gftypes.py` holds ~65 dataclasses in one module; registry and LSP depend on a deleted package; nested ImportError fallbacks hide breakage; 26-branch unmerged chain |
| D16 | Feedback loop & product analytics | 1 | GitHub issues only; no download metrics (not published); no release hypotheses |
| D17 | Content, i18n & discoverability | 1 | Public README and whitepaper overclaim; mixed Spanish content (EVIDENCE_MATRIX.md, workflow comments) against the English-only rule |
| D18 | Synergy & integration | 0 | GeneForge pins GFL two contradictory ways and imports contracts that exist only on the chain; plugin entry-point group split (`gfl.plugins` vs `geneforgelang.plugins`), so 6 of 7 in-repo plugins are never discovered |
| D19 | Ecosystem & obligations | 0 | No registry of relations; ADNI/NACC DUA status unknown; external services (AlphaGenome, AlphaFold, DepMap, OpenMed, UniProt, LLM providers) unregistered; pickle of unknown provenance; no disclaimers |

## Top findings (ranked)
1. **Secrets in a public repo** (D4, critical): `.devcontainer/.env` tracked since 2025-09. Rotate (owner), remove, guard (F001). History purge is an owner gate.
2. **Simulated results presented as validated or clinical** (D7, D6, critical): README, manuscript, whitepaper, BioDecision, OpenMed, conformance runner (F002, F004, F006, F008).
3. **No working public API and no package** (D2, D18, high): the documented imports fail; not on PyPI; four versions (F010, F011, F012).
4. **The product is not on main, and main is unguarded** (D8, high): 26-branch chain unmerged, 31 divergent commits on main, no protection, CI that cannot fail (F003, F005, F007-F009).
5. **Unsafe artifact** (D4, high): `.pkl` of unknown provenance on main (F001).
6. **Plugin discovery broken** (D18, D15, medium): entry-point group split; registry and LSP import a deleted module (F013).
7. **Insecure HTTP apps** (D4, medium): CORS `*`, no auth (F016).
8. **Third-party dataset content in public text** (D19, D6, medium): ADNI/NACC variables in `EVIDENCE_MATRIX.md`; legal review before publishing (Needs owner).
9. **Windows breakage** (D14, medium): cp1252 CLI crash; CONTRIBUTING case collision (F015, F005).

## What raises each critical dimension by one level
- D4 0→1: F001 merged and the keys rotated. 1→2: F003 (gitleaks, pip-audit in CI). 2→3: branch protection with required checks plus F016.
- D7 0→1: F002 and F004. 1→2: F006 and F008. 2→3: provenance tests and the claims test required in CI.
- D18 0→1: F013. 1→2: F010. 2→3: F014 running in CI.
- D19 0→1: `system/relations.json` drafted from `spec/ecosystem.md`; owner answers on the unknowns.
