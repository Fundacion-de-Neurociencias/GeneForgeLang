# Progress log

Append-only. One entry per session: date, phase, feature, what changed, what is next.

## 2026-10-18: onboarding (planning)
- Phase: onboard, steps 2-4. No code changed; nothing committed by the planner.
- Wrote the contract and plan in `.autodev/`: project.toml, brief, interview, next-steps, intended use, deepen, ecosystem, claims inventory, protocol compliance, team, quality bar, roadmap, baseline audit, and 16 features (F001-F016), validated against the schema.
- Evidence came from the read-only chain worktree (`~/.autodev/scan/geneforgelang`, tip 1b72405) and origin/main (630059c), plus the cross-repo discovery.
- Not run: the test suite and ruff (running them would write caches into the read-only worktree). Test and lint counts are the scout's.
- Next: owner reviews and approves the plan; then F001 (secrets) and F002 (public claims).

## 2026-10-19: build, F001 (secrets, pickle, gitleaks)
- Branch `autodev/F001` from `autodev/integration` @ 164e7df. Contract `contracts/F001.md`, reviewed by the evaluator (`contracts/F001-review.md`, ACCEPT WITH CHANGES; all 13 changes folded in), plus one amendment during build.
- Product commits (no `.autodev/` path; the PR branch can be cut from `origin/main` by cherry-picking them): `e793288` untrack `.devcontainer/.env` (via `git rm --cached`, never opened), add `.env.example` with names only, ignore rules, delete the `.pkl` and its loader/generator, ADR `docs/decisions/20261019-no-pickle-artifacts.md`; `2cec236` `.gitleaks.toml`, pre-commit hook gitleaks v8.24.3, `.github/workflows/secret-scan.yml` (checkout pinned by SHA, binary checked by a literal SHA-256, config read from the PR base), `tests/security/test_repository_hygiene.py` (16 tests); `11b9118` allowlist the exact public value `nferruz/ProtGPT2`.
- Amendment: gitleaks over the HEAD export found one `generic-api-key` false positive (`tokenizer_name="nferruz/ProtGPT2"` in `src/geneforgelang/models/advanced_models.py`, a public Hugging Face id). Fixed with one anchored literal in the allowlist. A code edit was rejected because every chain branch edits that file, and a `.gitleaksignore` entry was rejected because it is bound to the line number.
- Verified (logs in `evidence/F001/`, harness scripts in `evidence/F001/scripts/`):
  - gitleaks reports no leaks on the HEAD export and on `164e7df..HEAD`.
  - The allowlist skips a fake key only under `tests/fixtures/secrets/`, in both `dir` and `git` modes. A non-allowlisted `tokenizer_name` value is still reported.
  - pre-commit hook (Linux/WSL, no system Go): passes a clean change; blocks a fake AWS key with `aws-access-token`; `git commit` is blocked.
  - The workflow `run:` blocks, run verbatim in WSL, give the expected exit code in 7 of 7 scenarios. These include a PR that widens its own allowlist (still blocked) and pushes whose `before` is all zeros or unreachable.
  - Full suite: 873 passed, 2 failed, 22 skipped, 5 xfailed. The failing ids are exactly the 2 baseline ids. ruff: 1 error at both 164e7df and HEAD; `tests/security` is clean.
  - PR rehearsal on `origin/main`: cherry-pick is clean, with 0 `.autodev/` paths.
- Known limitations:
  - The hosted GitHub run of `secret-scan.yml` does not exist yet. Pushing is an owner gate.
  - The pre-commit golang bootstrap on Windows was not shown to work: it failed with MAX_PATH under the very long scratchpad `PRE_COMMIT_HOME` (`05a-*.log`). A default `~/.cache/pre-commit` is much shorter but was not tested.
  - History still contains the secret file and the pickle.
- Findings for other features:
  - Baseline failures (files on María's branch, not touched): `test_lru_eviction` picks its victim from `time.time()` ties at Windows clock resolution; `test_find_similar_entities` gets a negative mock cosine similarity.
  - The `poetry-check` pre-commit hook fails to clone on Windows ("Filename too long"), and the project uses setuptools, not Poetry (F003).
  - The dev postgres password is hardcoded in `.devcontainer/docker-compose.yml` (local default).
  - The autodev guard matches `.env` inside commit-message text; use `git commit -F`.
- Owner: rotate the credentials (`spec/secret-rotation.md`), decide on the history purge, make `gitleaks` a required check, and add `.gitleaks.toml` and `.pre-commit-config.yaml` to `sensitive_paths` (all in next-steps.md).
- Next: `/autodev:verify F001` in a separate session.
