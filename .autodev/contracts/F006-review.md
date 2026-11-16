# F006 contract review (evaluator, contract only, verbatim)

Contract review for F006 (contract only; I did not check the implementation).

Gaps:
1. Issue links. The acceptance item says failing cases are "listed as known failures with issue links". The contract puts GitHub issues out of scope and points `tracking` at a `progress.md` entry. That is a deviation from the acceptance item with no link anywhere. Either create the issues or add a Done-means item saying the report lists the tracking reference per known failure. The evaluator should treat this as a stated deviation, not a pass. The CI report is also unverified, because the item 8 check only parses the YAML and checks the exit-code handling.
2. Item 1 grep scope. It covers `src resources scripts`, but the acceptance wording is "in the runner". The command also has no explicit exit-code expectation (grep returning 1 means no matches). The contract admits the guard's own string in `tests/` is the only match, which is fine because `tests/` is not scanned. Add `tools` for completeness.
3. Item 2. "valid JUnit with 27 skipped" has no check method (the XML parse and the skipped count). It also hard-codes the counts 9/27 on the assumption that they hold on a clean checkout. Say that the run is done from a clean checkout and that the counts come from the real validator.
4. Item 3. The evidence log is required but there is no command or path (`.autodev/evidence/F006/`). Name the exact meta-test command, with the venv python and the repo root as cwd, that produces the log.
5. Item 4. It lacks exact commands for the two mutations (editing `known_failures.json`, restoring it, and expecting exit 1 and the `FAIL` or `UNEXPECTED-PASS` label). Confirm these are covered by tests as well as by manual runs.
6. Item 5. Five failure modes, but it names no tests and no command for each. Exit 2 for a missing directory is stated only in prose.
7. Item 6. It does not state the new test count, or that `.venv/Scripts/python.exe` is used for the full suite. The baseline "1078 passed / 24 skipped / 9 xfailed" is not tied to a command.
8. Item 7. `ruff format --check` is limited to "the new files", and the mypy or pyright type check is missing. The acceptance item requires type hints, so add a type-check command (for example `mypy src/geneforgelang/conformance.py`).
9. Item 8. A YAML parse does not prove the job works. Add an actual run of the same step locally, with the report written and the runner's exit code propagated. Also state whether the artifact upload runs with `if: always()`.
10. "Importable typed runner with its own unit tests" is only partly covered. Item 6 covers the tests, but there is no Done-means item for `import geneforgelang.conformance` from the .venv, or for unit tests of `evaluate`, `matches` and `load_expected` separately from the CLI-level tests.
11. The Verification channel is CLI only, which is acceptable. Item 8, the CI workflow, cannot be run for real without a push, so mark it as an owner gate.

Verdict: NEEDS REVISION. Items 1 to 7 are mostly checkable through the CLI, but the issue-link deviation, the missing type check, and the missing explicit commands for items 3 to 5 and 8 should be fixed before implementation is judged.

## How the contract folds these remarks in

- 1: stated as a deviation in the contract (`## Known deviations`); the report lists `tracking` per known failure. Not closed here: opening GitHub issues is outward-facing and queued by the guard.
- 2: grep covers `src resources` (the directories `scripts/` and `tools/` do not exist on this branch) and expects exit 1 (no match).
- 3, 4, 5, 6, 8 (type check), 9 (local run), 10: exact commands added to the contract; their output is `evidence/F006/commands.txt`. Items 4 and 5 are also covered by tests (`TestKnownFailures`, `TestRunSuite`, `TestCommand`), and `evaluate`, `matches` and `load_expected` have their own unit tests (`TestEvaluate`, `TestMatches`, `TestLoadExpected`).
- 7: full-suite command and counts are recorded in progress.md after the run.
- 11: the GitHub run of `conformance.yml` is an owner gate (push and merge).
