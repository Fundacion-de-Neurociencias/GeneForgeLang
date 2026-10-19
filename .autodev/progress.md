# Progress log

Append-only. One entry per session: date, phase, feature, what changed, what is next.

## 2026-10-18: onboarding (planning)
- Phase: onboard, steps 2-4. No code changed; nothing committed by the planner.
- Wrote the contract and plan in `.autodev/`: project.toml, brief, interview, next-steps, intended use, deepen, ecosystem, claims inventory, protocol compliance, team, quality bar, roadmap, baseline audit, and 16 features (F001-F016), validated against the schema.
- Evidence came from the read-only chain worktree (`~/.autodev/scan/geneforgelang`, tip 1b72405) and origin/main (630059c), plus the cross-repo discovery.
- Not run: the test suite and ruff (running them would write caches into the read-only worktree). Test and lint counts are the scout's.
- Next: owner reviews and approves the plan; then F001 (secrets) and F002 (public claims).

## 2026-10-19: build, F002 (public claims)
- Baseline was red (2 failed, 857 passed): LRU tie on the Windows clock and a cosine rounding error. Fixed in 0a7a97b by applying the identical hunks from `origin/feature/PDN_feature-GFP` (María Alonso Vega); ruff I001 import order also fixed. Suite then green.
- Contract `.autodev/contracts/F002.md` drafted, reviewed by the evaluator (`F002-review.md`, 14 remarks, all folded in), committed in 3c96d54.
- 5363af4: README (validation numbers, PyPI badge and install lines, version badge, clinical and unsupported claims removed; notice; install from source; top-level import and `gfl` CLI marked as not working; code fences tagged; Protein Design example now validates; manuscript and license links fixed), whitepaper (clinical claims removed, unimplemented notation labelled "proposed, not implemented", status note), CITATION.cff (404 bioRxiv DOI removed; Zenodo DOI under identifiers), real_project manuscript, final report and README (simulation banners, claims removed), `execute_genesis_real.py` (docstrings and printed labels only), docs/index.md notice, four docs pages install from source, one schema title ("Clinical-Grade" dropped).
- New guard: `tests/docs/test_public_claims.py` (93 tests).
- Verified (logs in `.autodev/evidence/F002/`): claims test 93 passed on the branch and 28 failed on origin/main 630059c (d8-*.log); full suite `952 passed, 22 skipped, 5 xfailed`; ruff clean; language check 0 non-English segments; `cffconvert --validate` passes; Zenodo DOI 302, removed bioRxiv DOI 404 (d6-citation-doi.log); script AST identical apart from strings (d5-ast-check.log); smoke run exit 0 in a temp dir with `results/` untouched (d5-smoke-run.log; matplotlib and pandas are not in the project venv, so it ran with `uv run --with`).
- Inventory: C1-C5, C7-C10, C14 fixed; C6, C11-C13 prevented (not on main); C15-C20 open with their features.
- Needs owner: confirm the Zenodo DOI (A2); confirm the D10 deviation from acceptance item 1 (rows owned by other features); approve the PR (owner decision 2).
- Findings for other features: the README Quick Start does not run (`from geneforgelang import parse` fails; `plugin_registry.py` imports `src.geneforgelang`; the `gfl` script fails) -> F010/F015. `docs/index.md` links to a missing `SECURITY_ADVISORY.md` and README links to readthedocs (C19) -> F009/F011. The example script needs matplotlib and pandas, which no extra declares. The README feature lists (multi-omic blocks, spatial predicates) were not checked against the parser -> F009/F010.
- Next: `/autodev:verify F002` in a separate session.

## 2026-10-19: verify F002 - FAIL (feedback 1)
- Independent evaluator at 17fd3e5. Lint clean; 952 passed, 22 skipped, 5 xfailed; claims guard 93 passed on head, 28 failed on origin/main; cffconvert valid; Zenodo DOI 302; script AST unchanged, smoke run exit 0.
- FAIL on G8.2/QB-8: README plugin example imports names that do not exist and is unmarked; README links readthedocs and Discussions, both 404.
- Governance auditor: nothing blocking for a merge into autodev/integration; .autodev/ must not reach public main.
- Next: F002 attempt 2 with contracts/F002-feedback-1.md.
