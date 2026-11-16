# F020 contract review

Verdict on the contract: **acceptable with changes**. Most items can be checked through the real channel. Three gaps must be closed before verification.

## 1. Done-means concreteness
- D1: concrete. It gives a command and the expected result (0 HIGH/CRITICAL lines), and before/after evidence exists. OK.
- D2: the counts are concrete, but the exact commands are not written down: which venv path, which pytest invocation, the `uv pip compile` arguments (`--python-version 3.10/3.11`, which extras). Add them verbatim so the run can be repeated. **"The build passes" (acceptance 2) is not addressed at all.** Add `python -m build` (or `uv build`) plus `twine check` / a metadata check showing the markers in the wheel's `Requires-Dist`.
- D3: import plus `/health` 200 only shows that the modules import. See point 4.
- D4: "None left" needs a command. Run the scanner as in D1, and also run a resolved-environment audit (`pip-audit` or `uv pip compile` output fed to OSV) on the extras venv. A1 says the scanner reads only the floors, so D1 cannot prove anything about what actually gets installed.

## 2. `python_version >= '3.10'` markers
- The reasoning is sound, and PEP 508 semantics are correct: on 3.9 a marked requirement is simply dropped. It avoids a metadata and CI-matrix change. CI (`ci-pipeline.yml`) installs only `-e .`, so the extras are not exercised there anyway.
- **Hole: A3 ("nothing vulnerable is installed on 3.9") is unverified.** The unmarked web packages (`slowapi`, `uvicorn[standard]`, `httpx`) stay installable on 3.9. If any of them pulls `starlette` (or `fastapi`/`aiohttp`) transitively, a 3.9 user of `.[web]` gets an old vulnerable starlette with no floor at all. I believe slowapi uses starlette at runtime, but I have not confirmed whether it declares it as a dependency. Required: run `uv pip compile pyproject.toml --extra web --extra ml --extra dev --python-version 3.9` and show that no vulnerable torch, transformers, starlette, fastapi, aiohttp or black version appears. If one does, add `starlette<0; python_version < '3.10'`-style exclusions, or mark slowapi too.
- Functional consequence that is not documented: on 3.9, `.[web]` now installs slowapi and uvicorn without fastapi, and `.[ml]` installs no torch. The extras are silently broken on 3.9. That is acceptable as a choice, but it must be stated in the CHANGELOG/README ("web/ml extras require Python >= 3.10"). Marking the whole extra consistently would be cleaner.

## 3. Deviations from the acceptance text
- D-fastapi (0.133.0 rather than 0.109.1): justified. 0.109.1 does fix CVE-2024-24762, but it cannot coexist with starlette >= 1.3.1. The contract's PyPI checks (0.129.0 `<1.0.0`, 0.133.0 `>=0.40.0`) are cited, but no evidence file holds them. Save the PyPI JSON excerpts under evidence.
- D-black (26.10.1 rather than 26.3.1): plausible. The acceptance lists CVE-2026-31900/32274, while the contract cites a different GHSA. Record the scanner line that flagged `black==26.3.1` (A1 falsification) as evidence. Otherwise the deviation is asserted, not shown.
- D-multipart: reasonable and in scope, since it is needed for import.
- Acceptance 2, "manifests and lockfiles updated together": no lockfile exists, and the contract says so. OK. The build part is missing (see point 1).
- Acceptance 3, "breaking upgrades handled in the code with tests": the contract changes no code and adds no tests. That is defensible only if it is shown that no breaking API is used. See point 4.

## 4. Untested risk of torch 2.0 -> 2.15 and transformers 4 -> 5
- `enhanced_inference_engine.load_model` (lines ~298-327) calls `from_pretrained(..., torch_dtype=...)`. transformers 5 renamed `torch_dtype` to `dtype`. I am not certain whether 5.x still accepts the old name with a warning or rejects it. D3 only imports the module, so this path never runs.
- Also untested: `use_fast=True` / tokenizer backend changes in v5, and `torch.load` `weights_only=True` as the default since 2.6 (grep found no direct `torch.load`, which is good).
- `models/advanced_models.py` cannot import at all (missing `gfl`), so it gives no coverage either.
- Required: a smoke test that actually runs `load_model()` with a tiny local or cached model (e.g. `sshleifer/tiny-gpt2` or a randomly initialised config saved to tmp, so nothing is downloaded), plus one inference call, in the extras venv. Save it as evidence. If `torch_dtype` breaks, change the code and add a test. That is exactly what acceptance 3 asks for.
- `/health` 200 does not exercise any starlette 1.x or fastapi 0.163 behaviour beyond routing. Every other endpoint returns 503 (`gfl` missing), so the web upgrade is effectively unverified beyond import. Acceptable only because that defect predates the feature (it is correctly logged as a finding). Say this explicitly in `not_proved`.

## Missing items, summary
1. A build check (wheel/sdist) that shows the markers in the metadata.
2. A 3.9 resolution showing that no vulnerable transitive starlette, fastapi or aiohttp gets installed (validates A3).
3. A resolved-environment audit, beyond the floor-only scanner.
4. A `load_model()` plus inference smoke on transformers 5 / torch 2.15 (covers `torch_dtype`).
5. Evidence files for the PyPI checks behind D-fastapi and D-black.
6. A documentation note that the web/ml/dev pins need Python >= 3.10.
7. Exact commands written into D2.
