# Roadmap: GeneForgeLang

"Launch" for GFL means: version X.Y.Z is on PyPI, installs from the wheel in a clean environment on Linux, Windows and macOS, and exposes a small typed public API that GeneForge and third parties use, guarded by an API diff and a consumer contract test. Public text claims nothing the evidence does not support.

Every phase meets `spec/quality-bar.md`. The owner approves each PR to main.

## Phase 0: urgent hygiene (F001-F004)
Goal: the public repository stops leaking and stops overclaiming; main becomes a gated branch.
- F001: tracked secrets and the pickle removed; gitleaks in pre-commit and CI; rotation list for the owner. The history purge is a separate owner decision.
- F002: public claims corrected; not-for-clinical-use / not-legal-advice notice; claims test.
- F003: one CI that gates PRs; one lint config; branch-protection settings for main (owner applies).
- F004: provenance contract; simulated components on main labelled and disconnected from decisions.
Exit: main is protected, CI is a required check, gitleaks is clean, the claims test passes, and the owner has the rotation list.

## Phase 1: integration of the chain, with green CI (F005-F009)
Goal: the newest chain is on main, in reviewable slices, with nothing simulated presented as real.
- F005: reconcile main's 31 commits with the chain (3 known conflicts, CONTRIBUTING case collision); integration plan by slices. Order relative to María's PDN branch decided with her.
- F006: conformance runner compares real results.
- F007: slice 1, core language and contracts.
- F008: slice 2, plugins and plugin packages, simulated ones labelled.
- F009: remaining slices; open PRs closed or superseded; ruff errors at zero. EVIDENCE_MATRIX.md only after legal review.
Exit: the chain tip is contained in main; CI is green; every simulated component carries provenance.

## Phase 2: working public API and a PyPI release (F010-F012, F014, F015)
Goal: a library others can depend on.
- F010: public facade (`parse`, `validate`, `api`, `types`, `contracts`), import tests that match the docs, import-linter boundaries, API snapshot.
- F011: one version and PEP 621 metadata (owner picks the number; recommendation 0.3.0).
- F014: GeneForge consumer contract test.
- F015: cross-platform CLI.
- F012: release workflow with Trusted Publishing and attestations; TestPyPI dry run, then PyPI, each an owner gate.
Exit: the "launch" definition above holds.

## Phase 3: plugins, then specification and conformance (F013, F016, later)
- F013: one plugin entry-point group and a versioned plugin protocol; plugin authoring guide.
- F016: FastAPI apps removed or secured (owner decides).
- Later: home for the external plugins; replace stubs with real integrations only when access exists and an oracle test proves them; then the formal specification and the conformance suite as a standard, backed by the real implementation (owner decision 3).
