# F018 contract review

**Verdict on the contract:** the root causes are plausible, and I confirmed both of them by experiment. All the "Done means" items can be run through the CLI and the isolated `.venv`, but D1, D4, D5, D6 and D7 need tighter wording before they can actually fail. D4 currently has an escape clause that makes it impossible to fail.

## Root-cause plausibility (checked against `cf67007` and the `.venv`, Python 3.11.15)

1. **LRU: plausible and confirmed.**
   - At `cf67007`, `LRUEvictionPolicy.select_victim` does `min(..., key=last_accessed)`, and `CacheEntry.touch()` and `put()` stamp `time.time()`.
   - In the `.venv`, `time.get_clock_info('time')` reports `GetSystemTimeAsFileTime()` with `resolution=0.015625`, and five consecutive `time.time()` calls returned the same value.
   - When the timestamps tie, `min` returns the first key in insertion order, which is `key1`. That matches the symptom in `baseline-before.log` (`None == 100`).
   - Calling it a product bug ("wrong on any platform within one tick") is fair. `time.time()` can also be adjusted (`adjustable=True`) and can go backwards, which supports the counter fix.
   - Note: from Python 3.13, CPython uses a precise clock on Windows. Pinning 3.11 is what makes the failure reproduce on this machine. Say so in the contract.
2. **Cosine: plausible and confirmed.**
   - The mock embeddings are constant vectors (`[0.1]*768`, `[0.2]*768`, `[0.3]*768`), so they are all parallel.
   - The old formula gives `1.0000000000000033` (TP53 vs BRCA1) and `1.0000000000000002` (TP53 vs KRAS), exactly as stated.
   - For an antiparallel pair, `[0.1]*768` vs `[-0.3]*768`, it gives `-1.0000000000000033`.
3. **Coordination claim: confirmed.**
   - `origin/feature/PDN_feature-GFP` has `access_seq: int = 0` (line 68), selects with `min(... access_seq)`, and clamps with `max(-1.0, min(1.0, similarity))` (line 158).
   - Add these two `git show ... | grep` commands to the contract as evidence, so the claim can be re-checked.

## Remarks on "Done means"

1. **Branch mismatch with the acceptance item.** The feature acceptance says "`commands.test` exits 0 on the **integration branch**". D1 says "on this branch". Rewrite: *"D1a: `commands.test` exits 0 at the feature HEAD. D1b: the same command exits 0 after merging the feature into `autodev/integration` (runner step, log saved to `suite-after-integration.log`)."*

2. **D1 can pass with tests silently skipped.**
   - `test_find_similar_entities` carries `@pytest.mark.skipif(os.getenv("CI") == "true", ...)`. If `CI=true` is set, a green suite proves nothing about that test.
   - Exit code 0 alone also does not rule out new skips.
   - Rewrite: *"D1: run with `CI` unset (`env -u CI uv run ... -rA`). The summary must show `0 failed`, `skipped == 22` and `xfailed == 5` (the baseline counts), and `passed >= 859 + N_new`. The `-rA` output must list both originally failing test IDs as `PASSED`."*

3. **The D2 grep has holes.**
   - `grep -E '^-[^-]'` misses deleted blank lines (`^-$`) and deleted lines that begin with `-`.
   - `git diff cf67007 -- tests/` compares against the working tree, not against the committed result.
   - Rewrite: *"`git diff --numstat cf67007...HEAD -- tests/` shows 0 in the deletions column for every file, and the only files listed are `tests/unit/test_performance.py` and `tests/unit/ir/test_external_connectors.py`."*

4. **D3 does not cover deselection through conftest or hooks.**
   - `tests/conftest.py` exists. Under D2 a change there would add lines only, so it would pass, yet it could add `collect_ignore` or a `pytest_collection_modifyitems` hook.
   - Rewrite: *"`git diff --quiet cf67007...HEAD -- pytest.ini pyproject.toml tests/conftest.py` exits 0, and `git diff cf67007...HEAD | grep -E '^\+.*(skip|xfail|deselect|importorskip|collect_ignore|collection_modifyitems)'` prints nothing."*

5. **D4 cannot fail as written.**
   - "or reason from the tie-break" lets the check pass on argument alone. "temp copy" is not specified.
   - The patch target is also ambiguous. `performance.py` does `import time`, so the patch must be `monkeypatch.setattr(performance.time, "time", lambda: 1000.0)`, which patches the global `time` module for the test's duration. That is acceptable, but say so.
   - The test only catches the old bug if the most recently accessed key is the first one inserted. Make that an explicit requirement.
   - Rewrite: *"D4: new test `test_lru_eviction_frozen_clock`. It patches `time.time` to a constant through `monkeypatch.setattr(performance.time, 'time', ...)`, puts k1 and k2, gets k1, puts k3, and asserts that k2 was evicted and k1 survives. Old-code oracle: `git worktree add <scratch>/old cf67007`, copy the new test file in, then run `PYTHONPATH=<scratch>/old/src uv run --no-project --python .venv python -m pytest <scratch>/old/tests/unit/test_performance.py::...frozen_clock -p no:cacheprovider`. This must exit 1, with the log saved to `.autodev/evidence/F018/oracle-old-lru.log`. The same test at HEAD must exit 0. Remove the worktree afterwards."* Also confirm that `PYTHONPATH` takes precedence over the editable install's `.pth` file: assert `performance.__file__` points into `<scratch>/old`.

6. **D5 has wrong or ambiguous bounds and no old-code oracle.**
   - "`0 <= sim <= 1` for parallel vectors" is too weak; it should require `== 1.0`.
   - "`== -1.0` bound respected for antiparallel" mixes up equality and a bound.
   - Rewrite: *"D5: for the pairs ([0.1]\*768, [0.3]\*768), ([0.1]\*768, [0.2]\*768) and ([1e-3]\*768, [1e3]\*768), `_cosine_similarity` returns exactly `1.0`. For ([0.1]\*768, [-0.3]\*768) it returns exactly `-1.0`. For random vectors, `-1.0 <= sim <= 1.0`. The test fails against `cf67007` through the same worktree oracle as D4 (log `oracle-old-cosine.log`); the old code gives `1.0000000000000033` and `-1.0000000000000033`."*
   - Note that `find_similar_entities` values fall in [0, 1] only because the mock embeddings are positive. The clamp guarantees [-1, 1], not [0, 1]. The contract should say this, so that nobody reads the existing assertion as a property of the product.

7. **D6 uses bare `pytest`, not the isolated `.venv`.** The reasoning about `--count` is fine. Rewrite: *"`for i in $(seq 20); do uv run --no-project --python .venv python -m pytest '<id1>' '<id2>' -q -p no:cacheprovider || exit 1; done 2>&1 | tee .autodev/evidence/F018/repeat.log`, with exit status 0 (use `set -o pipefail`)."* Repetition is a weak oracle on a fast clock, so make clear that D4 is the main proof and D6 is secondary.

8. **D7 has no concrete command or baseline.** The evaluator's rule "every deterministic check green" will clash with `commands.lint`, which is out of scope here (F007). Rewrite: *"D7: `ruff check --output-format concise <4 files>` at `cf67007` (via the worktree) and at HEAD. The set of findings at HEAD is a subset of the baseline set, saved to `lint-before.txt` and `lint-after.txt`. The repo-wide `commands.lint` result is recorded but not gating for F018 (F007 owns it)."* Without this, the evaluator will either fail F018 on inherited lint debt or ignore lint arbitrarily.

## Scope and assumptions

9. **"Does not change any public signature" vs the new `CacheEntry.access_seq` field.** `CacheEntry` is a public dataclass. Adding a field is compatible only if it is the last field and has a default. Rewrite: *"Adds `access_seq: int = 0` as the last field of `CacheEntry` (backward-compatible addition; positional construction unchanged)."* Also state whether a `put()` that overwrites an existing key counts as an access. It should; record that in the scope.

10. **A2 has no evidence command.** The search I ran found no consumers of `last_accessed`, `_cosine_similarity`, `LRUEvictionPolicy` or `CacheEntry(` outside `performance.py` and `openmed_connector.py`, apart from the one test. Rewrite A2/A3 as: *"`grep -rn 'last_accessed\|CacheEntry(\|_cosine_similarity' src tests` lists only the definitions, internal uses and the existing tests."*

11. **Owner gate is missing.** `src/geneforgelang/core/**` is listed under `sensitive_paths` in `project.toml`, so publishing this change needs the owner's review (`sensitive_min_reviews = 1`). Add an "Owner gates" section: *"PR touching `core/performance.py` requires owner review; prepared artifact: branch `autodev/F018` + PR text with the sections What it does / Why / How to reproduce / Impact on results."*

12. **Small points.**
    - The existing `skipif` reason is in Spanish ("Requiere acceso a red externa"), and it is also false: the connector is a mock and makes no network calls. Leave the test unchanged (D2), but record this under Out of scope as a G10/G9 finding for F002 or the translation feature.
    - "Impact" journeys are not listed. Add `## Impact`: callers of `IntelligentCache` in `core/` (the grammar parser's caching tests `test_grammar_parser.py::TestGrammarParserIntegration::test_performance_caching`) and the `TestPerformanceOptimizer` tests. The evaluator should re-run these explicitly.

Files reviewed:
- `C:/Users/usuario/.autodev/workspaces/geneforgelang/.autodev/contracts/F018.md`
- `C:/Users/usuario/.autodev/workspaces/geneforgelang/.autodev/features.json` (F018 entry, read-only)
- `C:/Users/usuario/.autodev/workspaces/geneforgelang/.autodev/evidence/F018/baseline-before.log`
- `src/geneforgelang/core/performance.py` and `src/geneforgelang/ir/external/openmed_connector.py` at `cf67007` (the working tree already has uncommitted changes to both; I did not review those)
