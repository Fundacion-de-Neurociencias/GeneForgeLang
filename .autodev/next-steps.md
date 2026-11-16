# Next steps (living plan)

Curated by the owner's direction, evolve retrospectives and Claude. The runner's state snapshot reads it.
This is an endless cycle, so the list is never empty. Keep it ranked and short.

## Now
- F006 REWORK (top priority, review of PR 25, 2026-11-16): the conformance suite passes vacuously. 8 of 9 "pass" cases (v1.3.0/loci/02-05, simulate/05-06, spatial_predicates/06-07) expect `{"status":"invalid","codes":[]}`, which `matches` (src/geneforgelang/conformance.py:136) checks by status only, and the validator rejects them for the same unrelated reason it rejects their valid twins (SEMANTIC006 / SEMANTIC002 / SEMANTICTYPE001). Reproduction: copy `v1.3.0/loci/01_valid_definition.gfl` over `02_invalid_missing_chromosome.gfl`: the suite still reports 9 pass, 0 fail. Fix: every invalid case must carry the specific reason code it targets and the runner must compare codes; a case whose valid twin is a known failure cannot count as pass; add a mutation test proving the suite fails when a case file is replaced. Also reword the contract workflow note: it triggers on pull_request and push to main.
- Owner reviews and approves the onboarding plan (roadmap Phase 0-3, features F001-F016).
- F001: built on `autodev/F001` (2026-10-19). Every reproducible item passed in verify 3. The hosted `secret-scan.yml` run is now an owner gate that does not block the feature (contract amendment, 2026-10-19). Next: `/autodev:verify F001`.
- F002: correct public claims (README, manuscript, whitepaper, CHANGELOG, SECURITY, CITATION) with not-for-clinical-use / not-legal-advice notices; PR for the owner to approve.

## Next
- F003: one CI that gates PRs; one lint config; branch-protection settings for main (owner applies or approves).
- F004: provenance contract; label and disconnect simulated components on main. Scope from the 2026-11-15 delta: `OpenMedConnector` mock behind a real-looking endpoint, `llm_planner.py:64` entity-keyed branch, unsourced MYC figures and the "ensures reliable execution in production" sentence in the manuscript (`.autodev/reviews/2026-11-15-delta.md`).
- F005: reconcile main's 31 commits with the chain; integration plan by slices.
- F006: honest conformance runner.

- Proposed feature (needs owner/planner to add it to the backlog): fix the 2 baseline test failures at their root cause - LRU victim chosen by `time.time()` ties at Windows clock resolution (`core/performance.py`), mock cosine similarity outside [0, 1] (`ir/external/openmed_connector.py`). A tested fix exists in commit 3e9f9ec on `autodev/F001` (reverted there as out of scope). Both files are on María's branch: agree with her whether it lands on her branch or after it.

## Later
- F007-F009: integrate the chain in slices (owner approves each).
- F010-F012: public API facade, unified version, publish readiness (TestPyPI dry run is an owner gate).
- F013-F016: plugin entry-point group, GeneForge consumer contract, cross-platform CLI, FastAPI apps.
- Phase 3: specification and conformance work backed by real code.

## Needs owner
- **Upstream delta 2026-11-15: data-use terms.** ALPHAGENOME, ENSEMBL and UNIPROT are used in code and docs with no data-use registry (`project.toml` `[ecosystem] registries = []`). Provide the terms for each, or confirm that no shipped path uses them. Agents cannot supply legal terms. Details: `.autodev/reviews/2026-11-15-delta.md`.
- **Upstream delta 2026-11-15: history and rotation.** `.devcontainer/.env` is still in history (removed from tracking upstream). Confirm rotation of anything it held, then decide the purge (see the history purge item below).
- **F001 hosted CI run (owner gate, does not block verification).** Approve publishing a PR branch cut from `origin/main` with `e793288 2cec236 11b9118` (draft in `contracts/F001-pr.md`), so the hosted `secret-scan.yml` run exists and proves the workflow itself.
- **Red baseline (lesson 19).** The 2 baseline failures below still make the Stop gate block every session. Recommendation: add the baseline-fix feature (under "Next") at the top of the backlog, coordinated with María. The 2 red baseline tests do not block F001 (item 13 allows them); their fix stays the separate proposed feature under "Next".
- **Guard requests 20261019-054021-32d1c2 and 20261019-054350-fb3e87.** Reject both: the first is a cleanup of a throwaway clone that is not needed; the second is a false positive on text inside a JSON file.
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
- **F002: approve the PR (acceptance item 6).** Item 1 was amended by the planner; attempt 3 marks C15-C20 `prevented` with guards. After `/autodev:verify F002` passes, only the owner's approval remains.
- **Contact identities.** Confirm a monitored package contact email (pyproject says team@geneforgelang.org) and the security contact in SECURITY.md.
- **Bot identity.** Agent commits appear as "Fundación de Neurociencias <admin@…>". Recommendation: a dedicated bot account so agent and human work are distinguishable.
- **External plugins** in "GeneForgeLang Ecosystem" (gatk, samtools, biopython-tools, clawbio, causal-evidence, tangermeme, CRISPR plugins): where they should live, and whether blast (corrupt) is retired.
