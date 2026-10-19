# F001 contract review

**Verdict: ACCEPT WITH CHANGES**

Reviewed: `.autodev/contracts/F001.md` (draft), the F001 entry in `.autodev/features.json`, `.autodev/spec/quality-bar.md` (QB-7, QB-12) and `.autodev/project.toml`, on branch `autodev/F001` @ 164e7df.

I checked these facts directly, without opening `.devcontainer/.env`:
- The gitleaks v8.24.3 `linux_x64` SHA-256 in the contract (`9991e0b2...e29c`) matches the official `gitleaks_8.24.3_checksums.txt`.
- `actions/checkout` tag `v4.2.2` resolves to `11bd71901bbe5b1630ceea73d27597364c9af683` (`git ls-remote`).
- The upstream `.pre-commit-hooks.yaml` at v8.24.3 defines hook `gitleaks` (`language: golang`, entry `gitleaks git --pre-commit --redact --staged --verbose`). It also defines `gitleaks-system` and `gitleaks-docker`.
- Upstream rule `aws-access-token` has regex `(AKIA|...)[A-Z0-9]{16}`, `Entropy: 3`, and an allowlist for `.+EXAMPLE$`. The run-time `A-Z2-7` generator in item 6 matches it.
- A1 holds. `genetic_risk_predictor`, `genetic_predictor` and `train_dummy_model` are only referenced inside the two scripts that will be deleted. `pyproject.toml` packages only `geneforgelang*`, so `resources/` is not shipped. No `Unpickler`, `read_pickle`, `allow_pickle`, `torch.load`, `dill` or `yaml.load(` in any `.py`.
- A2 holds for Python. The only credential-like env var read is `GOOGLE_API_KEY` (`src/geneforgelang/web/apps/translator_app/app.py:8`, `resources/tools/dev/gfl_translator_app.py:29`). `devcontainer.json` has no `--env-file`, and no `.devcontainer` yml/json/sh mentions `env_file` or `dotenv`.
- A5 holds. A baseline run on 164e7df gave exactly 857 passed, 2 failed, 22 skipped, 5 xfailed. The two failures are the ones the contract names.
- Tools on this machine: pre-commit 4.3.0 (global) and 4.7.0 (`.venv`), WSL, and the Docker CLI (daemon not running). No `go`, `gitleaks` or `act`.

## Required changes

1. **Fix the base and the scan range (they are wrong today).**
   - 164e7df is not `main`. It is the tip of `autodev/integration`. `origin/main` is 630059c. Local `main` points at fb180d5, an unrelated line of history (merge-base 4d4c9ea).
   - Because of this, `git log main..HEAD` currently lists 34 commits, most of them old team history.
   - Item 5 must use a fixed range: `164e7df..HEAD` (or `$(git merge-base origin/main HEAD)..HEAD` if the PR branch is recut).
   - Correct the "Branch:" line to say what the branch really comes from.

2. **Keep `.autodev/` out of the public PR.**
   - `.autodev/` is tracked on `autodev/integration` (commit 11529ee adds 15 files) and therefore on `autodev/F001`. This contradicts `publish_autodev_state = false` for a public repo.
   - The contract also edits tracked `.autodev/next-steps.md` and `progress.md`, and adds `.autodev/spec/secret-rotation.md`, which it calls "local". If committed on this branch, the rotation list would be published by the PR to `main`.
   - The contract must say how the PR head excludes `.autodev/`. For example: cut the PR branch from `origin/main` and carry only the non-`.autodev` changes, or keep `.autodev/` edits uncommitted.
   - Add a Done-means item: `git diff --name-only origin/main...<pr-head> -- .autodev` prints nothing.

3. **The guard blocks several Done-means commands, and it may block the implementation step too.**
   - The autodev guard rejects any Bash command that contains `.env`. I hit it while reviewing.
   - Items 1, 2 and 3 cannot be run as written by an agent evaluator. Neither can the implementation step `git rm --cached .devcontainer/.env`.
   - The contract must say one of the following:
     - (a) the owner runs the `git rm --cached` command (queued as an owner action), or the owner grants an explicit, recorded, scoped guard exception for that one command and for reading `.devcontainer/.env.example`; and
     - (b) the checks in items 1-3 are written into `tests/security/test_repository_hygiene.py` so the evaluator verifies them by running pytest. That means `git ls-files` filters, `git check-ignore` over synthetic paths, and a parse of `.env.example`, without ever reading the secret file.
   - Do not plan to get around the guard with obfuscated command strings.

4. **Make item 2 deterministic.** Replace "contains only comments and `NAME=` lines" with this assertion:
   - every non-blank line matches `^(#.*|[A-Z_][A-Z0-9_]*=)$`; and
   - the set of names is exactly `{GOOGLE_API_KEY, PYTHONPATH, GFL_ENV}`.

5. **Add a Done-means item for the `.gitleaks.toml` allowlist.** The feature says "allowlist limited to test fixtures", but no item checks it.
   - **Static check (in the hygiene test):** `[extend] useDefault = true`; exactly one allowlist with only `paths`, a single regex anchored to `tests/fixtures/secrets/`; no `regexes`, `stopwords`, `commits` or global allowlist.
   - **Dynamic check (in the throwaway clone):**
     - the run-time fake key under `tests/fixtures/secrets/` is not reported, while the same key elsewhere is;
     - run this in both `gitleaks dir` and `gitleaks git` modes, because path matching differs (in `dir` mode reported paths are prefixed with the scanned directory, so a `^tests/...` anchor can silently never match).

6. **Item 6: the fallback does not satisfy the acceptance text.**
   - The acceptance requires the commit to be "blocked by the pre-commit hook". Running the raw binary with `gitleaks git --pre-commit --staged` does not exercise the hook configuration.
   - Keep `pre-commit run gitleaks` as the primary path. A4 (golang bootstrap without a system Go) can be tested on this machine, since there is no `go` and pre-commit 4.x is installed.
   - If A4 is falsified, the fallback must still go through pre-commit, for example `pre-commit try-repo https://github.com/gitleaks/gitleaks gitleaks-system --ref v8.24.3` with the checksum-verified binary on PATH. Then record that the configured `gitleaks` id needs Go, or switch the config to `gitleaks-system` with a note.
   - Also require:
     - **Positive control:** the same hook passes on a clean staged change.
     - **Clean evidence:** the log shows the `gitleaks` hook itself as Failed with `RuleID: aws-access-token`. With `git commit`, the other hooks (mypy `--strict`, poetry-check, local pytest) can fail for unrelated reasons and give a false "blocked".

7. **Item 7: the local fallback cannot run as written on the evaluator's machine.**
   - The workflow downloads a `linux_x64` binary. Git Bash on Windows cannot execute it, `act` is absent and the Docker daemon is down.
   - Name the execution environment: WSL (available) or `docker run ubuntu` if the daemon is started.
   - State that the fallback proves the script logic only, and that the hosted run stays an open owner-gated item. The feature is not "passes: true" until the owner accepts that, or the hosted run exists.

8. **Item 7: say exactly where the hash lives.**
   - The SHA-256 must be a literal in `secret-scan.yml` (for example `echo "<sha>  gitleaks_8.24.3_linux_x64.tar.gz" | sha256sum -c -`).
   - It must not be read at run time from the `checksums.txt` of the same release. That only re-proves TLS and adds no pinning.
   - The hygiene test should assert the literal hash and the exact versioned URL.

9. **Scope the "every `uses:` pinned" test to the new workflow.**
   - `ci-pipeline.yml` uses floating tags (`actions/checkout@v4`, `setup-python@v4`, `cache@v3`, `upload-artifact@v4`), and F003 owns it.
   - The test must check `.github/workflows/secret-scan.yml` only. Otherwise it fails on `main`, or tempts the implementer to edit an out-of-scope file.

10. **CI config trust.**
    - On `pull_request`, `--config .gitleaks.toml` comes from the PR head. A PR can widen the allowlist and pass its own scan.
    - Either load the config from the base commit (`git show "$BASE_SHA:.gitleaks.toml"`, falling back to the default config if it is absent), or document the gap and add `.gitleaks.toml` and `.pre-commit-config.yaml` to the PR's flagged sensitive files with a request to add them to `sensitive_paths`.
    - Also pass event SHAs to the script through `env:` rather than inline `${{ }}` in `run:`.
    - Handle the push case where `before` is all zeros or no longer reachable after a force-push: fall back to a tree scan and do not fail spuriously.

11. **QB-12 is not covered by any Done-means item.** Add:
    - every commit subject in the PR range follows Conventional Commits 1.0 (listed or commitlint output);
    - the PR draft flags every sensitive file touched: `.github/workflows/secret-scan.yml`, the `.devcontainer/.env` removal, and `.pre-commit-config.yaml`/`.gitleaks.toml` per item 10.

12. **Item 12: define "no new failures" by test id, not by count.**
    - The set of failing node ids must be a subset of the two named baseline ids. `test_lru_eviction` is timing-dependent, so counts alone can hide a swap.
    - Lint: `ruff check tests/security` exits 0, and `ruff check src tests` reports no more errors than at 164e7df.

13. **Item 9: replace the ambiguous grep.** `[A-Za-z0-9+/_-]{24,}` matches ordinary repository paths and URLs, so its result needs judgement. Use one of:
    - forbid paths and URLs in the doc, so any match fails; or
    - state the rule as "gitleaks over the file exits 0, and no line contains a `=` or `:` followed by a value", which is checkable.
    - The feature acceptance says "names services and owners only". Make the doc's sections match that wording: service, what rotating means, who.

## Deviations

- **Checksum-verified gitleaks binary instead of `gitleaks/gitleaks-action` pinned by SHA: ACCEPTED,** on condition of required changes 8 and 10. A6 is correct: the action requires a `GITLEAKS_LICENSE` for organization accounts. A version-pinned URL plus a literal SHA-256 is an immutable reference to the exact artifact, which is what the Pinned-Dependencies practice asks for. The only `uses:` (checkout) is SHA-pinned and verified above. Record the deviation in the PR body under "Why".
- **Deleting `genetic_predictor.py` and `train_dummy_model.py` instead of stubbing: ACCEPTED.** Nothing references them. They are outside the shipped package. They were non-functional (path `tools/genetics/...` relative to the wrong root, and a feature-count mismatch), and they present random data as "genetic risk" output. The ADR must name both deleted scripts, not only the `.pkl`.

## Assumptions

- **A1:** correct (verified).
- **A2:** correct for `.py`. It is limited to Python, so state that the rotation doc tells the owner to rotate every key in the file whatever the code reads. The contract already does.
- **A3:** falsifiable, untested until item 4 runs. If it fails and a real secret is found, the scope grows. Say that a new real secret is a stop-and-ask-owner event, not something to fix silently.
- **A4:** falsifiable, plausible for pre-commit 4.x, and testable here (no system Go). See required change 6 for what to do if it is false.
- **A5:** correct (verified: same counts and the same two node ids).
- **A6:** correct.

## Acceptance coverage

| Feature acceptance item | Covered by | Gap |
|---|---|---|
| `ls-files` clean | Item 1 | Required change 3 |
| gitleaks `detect --no-git` on the head, plus hook and CI block a fake key | Items 4, 6, 7 | `gitleaks dir` is the v8.24 equivalent of `detect --no-git`; say so. Required changes 6 and 7 |
| CI pinned by SHA and listed as a required check | Items 7, 8 | Item 8 should use the exact status-check context GitHub will report (the job name `gitleaks` unless `name:` is set), not the UI label `secret-scan / gitleaks` |
| Rotation doc | Item 9 | Required change 13 |
| ADR | Item 10 | Add joblib and the deleted scripts |
| PR body | Item 13 | Required changes 2 and 11 |

## Optional suggestions

- Both translator apps tell users to "Create a .env" in the working directory, which is the repo root. Consider a root-level `.env.example` as well, or make the comment in `.devcontainer/.env.example` say where `load_dotenv()` looks.
- Add `tests/security/__init__.py`. The other test subpackages have one, and it avoids basename collisions. Skip the hygiene tests when not run inside a git checkout (for example from an sdist).
- The hygiene test could also flag `gitleaks:allow` inline markers outside `tests/fixtures/secrets/`, a common bypass.
- Broaden item 11's grep to `Unpickler`, `pd.read_pickle`, `allow_pickle=True`, `torch.load`, `dill`, `cloudpickle` and `shelve`. All are absent today, so it costs nothing, and it backs the ADR's "code-executing serialization" wording.
- Add a CHANGELOG entry under "Security"/"Removed" (Keep a Changelog) for the pickle and script removal and the new scan.
- Store the evidence logs (pre-commit block, CI-script block and pass, gitleaks clean runs) under `.autodev/evidence/F001/`, with the fake key redacted (`--redact` is in the hook entry; use it in every manual run too).
