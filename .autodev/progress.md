# Progress log

Append-only. One entry per session: date, phase, feature, what changed, what is next.

## 2026-10-18: onboarding (planning)
- Phase: onboard, steps 2-4. No code changed; nothing committed by the planner.
- Wrote the contract and plan in `.autodev/`: project.toml, brief, interview, next-steps, intended use, deepen, ecosystem, claims inventory, protocol compliance, team, quality bar, roadmap, baseline audit, and 16 features (F001-F016), validated against the schema.
- Evidence came from the read-only chain worktree (`~/.autodev/scan/geneforgelang`, tip 1b72405) and origin/main (630059c), plus the cross-repo discovery.
- Not run: the test suite and ruff (running them would write caches into the read-only worktree). Test and lint counts are the scout's.
- Next: owner reviews and approves the plan; then F001 (secrets) and F002 (public claims).

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
