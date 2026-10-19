# Next steps (living plan)

Curated by the owner's direction, evolve retrospectives and Claude. The runner's state snapshot reads it.
This is an endless cycle, so the list is never empty. Keep it ranked and short.

## Now
- Owner reviews and approves the onboarding plan (roadmap Phase 0-3, features F001-F016).
- F001: built on `autodev/F001` (2026-10-19); verify FAIL 1 (scope) fixed by reverting the out-of-scope commit; waiting for `/autodev:verify F001` again. Then the owner approves pushing a PR branch cut from `origin/main` with the product commits only (draft in `contracts/F001-pr.md`), so the hosted `gitleaks` run exists.
- F002: correct public claims (README, manuscript, whitepaper, CHANGELOG, SECURITY, CITATION) with not-for-clinical-use / not-legal-advice notices; PR for the owner to approve.

## Next
- F003: one CI that gates PRs; one lint config; branch-protection settings for main (owner applies or approves).
- F004: provenance contract; label and disconnect simulated components on main.
- F005: reconcile main's 31 commits with the chain; integration plan by slices.
- F006: honest conformance runner.

- Proposed feature (needs owner/planner to add it to the backlog): fix the 2 baseline test failures at their root cause - LRU victim chosen by `time.time()` ties at Windows clock resolution (`core/performance.py`), mock cosine similarity outside [0, 1] (`ir/external/openmed_connector.py`). A tested fix exists in commit 3e9f9ec on `autodev/F001` (reverted there as out of scope). Both files are on María's branch: agree with her whether it lands on her branch or after it.

## Later
- F007-F009: integrate the chain in slices (owner approves each).
- F010-F012: public API facade, unified version, publish readiness (TestPyPI dry run is an owner gate).
- F013-F016: plugin entry-point group, GeneForge consumer contract, cross-platform CLI, FastAPI apps.
- Phase 3: specification and conformance work backed by real code.

## Needs owner
- **F001 blocked by a red baseline (decide now).** The Stop gate needs a green suite. Verify rejected the root-cause fix for the 2 pre-existing failures as out of F001's scope (María's files, sensitive `core/**`). Choose one: (a) approve the fix `3e9f9ec` inside F001 (record the approval; the generator cherry-picks it back and it joins the PR); or (b) add a separate feature with a higher priority than F001 for the baseline fixes, coordinated with María, and run it first. Recommendation: (b), with María's agreement, because it keeps the security PR free of library changes.
- **Key rotation (now).** F001 listed the services in `spec/secret-rotation.md` (Google API key for Gemini, plus anything else in the file). The owner or the account managers rotate every credential in the file. Agents never read the file.
- **History purge (separate decision, never run by an agent).** Removing `.devcontainer/.env` (and the deleted `.pkl`) from the public history needs `git filter-repo` plus a force-push to `main` and every branch that contains it, and every collaborator must re-clone. Recommended only after rotation, because the old values are already public and may be in forks. Decide: purge / do not purge.
- **Required checks and sensitive paths (with F003).** Add the status-check context `gitleaks` (workflow `.github/workflows/secret-scan.yml`) as required on `main`. Add `.gitleaks.toml` and `.pre-commit-config.yaml` to `[collaboration] sensitive_paths` in project.toml (`.github/workflows/**` is already there).
- **Pre-commit config (finding from F001).** The existing `poetry-check` hook clones the poetry repository, which fails on Windows without `core.longpaths` ("Filename too long"), and the project is not a Poetry project. F003 should drop it or fix it.
- **María's branch (PDN, `feature/PDN_feature-GFP`).** Decide with María whether it lands before or after the chain. Recommendation: after slice 1, rebased by her with our help, because the chain is larger and already reconciled.
- **EVIDENCE_MATRIX.md (ADNI/NACC variables).** Legal review before it enters the public repo. Recommendation: keep it out until the review is done.
- **Patent and regulatory review.** A patent lawyer and a regulatory expert review the items in `spec/ecosystem.md` ("Expert review list"). Agents do not decide.
- **Version number** for the first PyPI release. Recommendation: 0.3.0, which continues the v0.2.x tags and signals a pre-1.0 API.
- **FastAPI apps.** Keep them as a secured optional extra, or remove them from the library. Recommendation: remove from the library; GeneForge does not use them.
- **Zenodo DOI** in whitepaper.md (10.5281/zenodo.15493559): confirm it is ours and current.
- **Contact identities.** Confirm a monitored package contact email (pyproject says team@geneforgelang.org) and the security contact in SECURITY.md.
- **Bot identity.** Agent commits appear as "Fundación de Neurociencias <admin@…>". Recommendation: a dedicated bot account so agent and human work are distinguishable.
- **External plugins** in "GeneForgeLang Ecosystem" (gatk, samtools, biopython-tools, clawbio, causal-evidence, tangermeme, CRISPR plugins): where they should live, and whether blast (corrupt) is retired.
