# F001 feedback 1 (verify, 2026-10-19): FAIL

Verified head: 881f7d9. Evidence: `.autodev/evidence/F001/verdict.json`, `.autodev/evidence/F001/verify/`.

What works: hygiene tests, ruff and the full suite are green; the workflow script, run verbatim in WSL against `origin/main` + product commits (base without `.gitleaks.toml`), exits 0 with default rules; no secrets or `.autodev/` paths leak into the PR commits.

## Blocking

1. **Scope: commit 3e9f9ec (G2.2).**
   - Did: compared the branch diff with the contract.
   - Expected: no change under `src/geneforgelang/**` ("Does not change").
   - Happened: 3e9f9ec changes `core/performance.py` (LRU victim selection) and `ir/external/openmed_connector.py` (similarity score now in [0, 1]). `core/**` is a sensitive path, both files are on the teammate's in-flight branch, and no owner approval is recorded.
   - Fix: drop 3e9f9ec from F001. Propose the two fixes as a separate feature coordinated with the teammate, or record explicit owner approval. Restore item 13 to its original wording (failing ids are a subset of the 2 baseline ids).
2. **Stale PR draft (G5.1).**
   - Did: read `.autodev/contracts/F001-pr.md`.
   - Expected: claims that match the final head.
   - Happened: it says "No library code changes" and "873 passed, 2 failed"; the branch includes 3e9f9ec and the suite shows 878 passed, 0 failed. `10-11-pr-rehearsal.log` predates 3e9f9ec.
   - Fix: once the commit set is final, rerun the suite and the cherry-pick rehearsal on the PR head and update the draft (commit list, counts, impact).

## Open (not a code defect)

- The hosted run of `secret-scan.yml` does not exist. Per contract item 6, PASS needs the hosted run or the owner's acceptance of the local evidence.
