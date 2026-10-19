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

## 2026-10-19: build, F002 attempt 2 (feedback 1)
- dcaec97: README Plugin System example rewritten against the real API (`geneforgelang.plugins.base.BaseGFLPlugin`, implements `process`); it states that `plugin_registry.register_plugin` fails in an installed package because the registry imports `src.geneforgelang` (F010). Support section: readthedocs and Discussions links (both 404) replaced by `docs/index.md`. Manuscript and final report: "revolutionary", "real-world application(s)" and "executed on the GeneForge WebApp" reworded as simulated examples.
- Guard widened: `test_readme_python_block_runs` runs every unmarked README python block that uses geneforgelang in `python -I` from an empty temp dir; README denylist adds the two dead URLs; report denylist adds the three phrases. Test file reformatted with ruff format (it was not formatted before).
- Verified: the widened guard fails 4 tests on 17fd3e5 (`attempt2-guard-on-17fd3e5.log`) and passes 94 on head; full suite, lint and language check in `attempt2-checks.txt`.
- Inventory: C21 (plugin example) and C22 (support links) added as fixed. Contract: D11-D14 added under "Attempt 2".
- Still needs owner: Zenodo DOI (A2), D10 deviation from acceptance item 1, PR approval. Release gate: `.autodev/` must not reach public main.
- Next: `/autodev:verify F002` in a separate session.

## 2026-10-19: verify F002 - PASS (attempt 2)
- Independent evaluator at 4d6acff. 953 passed, 22 skipped, 5 xfailed; ruff clean; claims guard 94 passed on head, 29 failed on origin/main, 4 failed on 17fd3e5 (exactly the feedback-1 items); language check 0 findings.
- README plugin example runs with `python -I` from an empty dir (exit 0); the register_plugin caveat holds; all README external links answer 200; cffconvert valid; Zenodo DOI 302.
- Governance auditor: nothing blocking for verify. Release gate: `.autodev/` must not reach public main.
- Open for the owner at the PR: Zenodo DOI (A2), D10 deviation from acceptance item 1, PR approval. Non-blocking wording left in the bannered manuscript (F009).
- Correction (same day): the PASS above was wrong. Acceptance items 1 (literal "every row fixed") and 6 (owner approval) are not met, and the evaluator rule requires every item. Verdict changed to FAIL, `passes` back to false. Code needs no change; see contracts/F002-feedback-2.md (owner/planner decisions).

## 2026-10-19: sprint F002 (after feedback 2) - no build, blocked on owner
- Read `contracts/F002-feedback-2.md`: every code-level check passed at 4d6acff; the FAIL rests on acceptance item 1 (literal "every row fixed") and item 6 (owner approves the PR).
- No code change made. Item 1 needs an edit to `features.json`, which the builder may not make, or pulling C15-C20 work from F004/F006/F008/F009/F011 into F002, which is out of scope. Item 6 is the owner's decision.
- Baseline on 7e23933 with the project commands: `pytest tests` 953 passed, 22 skipped, 5 xfailed; `ruff check src tests` clean. Source unchanged since 4d6acff (`git diff --stat 4d6acff HEAD -- . ':!.autodev'` empty).
- Recorded both decisions under "Needs owner" in `next-steps.md`, with the recommended wording for item 1.
- Next: owner/planner amends item 1 and the owner approves the PR; then `/autodev:verify F002`. Do not run `/autodev:sprint F002` again before that.

## 2026-10-19: verify F002 - FAIL (feedback 3)
- Independent evaluator at 8b3556f. Source unchanged since 4d6acff. 953 passed, 22 skipped, 5 xfailed; ruff clean; claims guard 94 passed (`verify3-checks.txt`).
- FAIL only on acceptance items 1 (inventory: 12 fixed, 4 prevented, 6 open; wording not amended) and 6 (no owner approval). See contracts/F002-feedback-3.md.
- Governance auditor: nothing blocking. `.autodev/` must stay out of any PR to public main.
- Next: owner decisions; no further sprint or verify until they are recorded.
## 2026-10-19: build, F018 (restore a truthful green suite)
- Baseline at cf67007: 2 failed, 857 passed, 22 skipped, 5 xfailed (`.autodev/evidence/F018/baseline-before.log`).
- Root causes and fixes (contract `.autodev/contracts/F018.md`, evaluator review `F018-review.md`):
  - `test_lru_eviction`: LRU ordered by `time.time()`, which ties at 15.625 ms resolution on CPython 3.11/Windows and fell back to insertion order. `IntelligentCache` now stamps a per-cache monotonic `CacheEntry.access_seq` on every put and hit; `LRUEvictionPolicy` evicts the lowest.
  - `test_find_similar_entities`: cosine similarity of parallel vectors rounded to 1.0000000000000033. `_cosine_similarity` now clamps to [-1, 1]. The test had been skipped in CI with a false "requires network access" reason, which hid the failure; the skip is removed.
  - Same fixes already exist on team branch `origin/feature/PDN_feature-GFP`; field name and semantics match (contract, Coordination).
- Tests added: `test_lru_eviction_independent_of_clock_resolution` (frozen clock), `test_find_similar_entities_returns_known_genes_in_unit_range`, `test_cosine_similarity_parallel_vectors_hit_bounds_exactly` (9 scales), `test_cosine_similarity_random_vectors_within_bounds`.
- Evidence (`.autodev/evidence/F018/`): `suite-after.log` (CI unset, -rA: 871 passed, 22 skipped, 5 xfailed, exit 0); `oracle-old-code.log` (new tests against cf67007 product code: 10 failed, 1 passed); `repeat.log` (20/20 runs of both original tests pass); `lint-before.txt` (1 finding, I001) vs `lint-after.txt` (0); `lint-repo-wide.txt` (exit 0); `diff-checks.log` (test diff, config untouched, integration is fast-forward).
- Findings for later features: `OpenMedConnector` is a mock with hardcoded embeddings and a fictitious `base_url` (G9, F002); TTL expiry uses wall-clock `time.time()` rather than `time.monotonic()`.
- Owner gate: `core/performance.py` is a sensitive path; the PR needs owner review.
- Next: independent verification (`/autodev:verify F018`).

## 2026-10-19: verify, F018 - PASS
- Independent evaluator at b5dbe76. Verdict: `.autodev/evidence/F018/verdict.json`.
- Full suite (CI unset and CI=true): 871 passed, 22 skipped, 5 xfailed, exit 0 (`verify-suite.log`, `verify-checks.txt`). Both originally failing tests pass, 20/20 repeats.
- New regression tests fail against the pre-fix product code (12 failed, `verify-oracle.txt`). Tests diff removes only the false CI skip; no config or conftest change. Ruff clean (changed files and repo-wide). Language check: 0 findings.
- Governance auditor: 0 blocking. Notes: publish only the product/test commits, never `.autodev/`; `core/performance.py` is a sensitive path (owner review gate).
- Next: F001.

## 2026-10-19: build, F002 attempt 3 (amended acceptance item 1)
- The planner amended item 1: in-scope rows `fixed`; rows owned by later features `prevented` and naming the feature. C15-C20 were still `open`.
- `tests/docs/test_public_claims.py`: new `test_owned_claim_absent`, one guard per C15-C20 claim. Absent claims (C15 version drift, C16, C20 truth-audit doc) are plain guards; present claims (C15 1.0.0 vs Beta, C17 privacy flag, C18 mocked conformance, C19 readthedocs URL, C20 PR description doc) are strict xfails naming F011/F004/F006/F011/F009, so they fail the suite when the owner removes the claim until the marker is dropped.
- Inventory: 0 rows `open` (14 fixed, 8 prevented). Contract: D15-D17 under "Attempt 3".
- Verified: injection makes the 3 plain guards fail, removing C17 makes its strict xfail XPASS -> fail (`evidence/F002/attempt3-owned-guards.log`); full suite 968 passed, 22 skipped, 10 xfailed; ruff clean (`attempt3-checks.txt`).
- Still needs owner: PR approval (item 6), Zenodo DOI (A2).
- Next: `/autodev:verify F002` in a separate session.
