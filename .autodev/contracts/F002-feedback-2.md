# F002 verification feedback 2 (2026-10-19)

Verdict: FAIL at 4d6acff. Evidence: `.autodev/evidence/F002/verdict.json`.

Every code-level check passes: full suite (953 passed), lint, claims guard (94 passed on head, 29 failed on origin/main, 4 on 17fd3e5), README plugin example runs, README links answer 200, cffconvert valid, DOI resolves, language check clean, governance auditor finds nothing blocking. No further code change is needed.

The FAIL comes from two acceptance items that only people can close:

1. **Acceptance item 1 (owner or planner).** It requires every row of `spec/claims-inventory.md` to be `fixed`. C6 and C11-C13 are `prevented`, and C15-C20 are `open` and assigned to F004, F006, F008, F009 and F011 (deviation D10 in the contract). Fix: amend the acceptance item in `features.json` to "rows in scope fixed; the rest prevented or assigned", or move those rows into scope.
2. **Acceptance item 6 (owner).** The owner approves the PR in chat before merge. Approving it is the owner's decision. Also confirm the Zenodo DOI (A2).

After both, re-run `/autodev:verify F002`. Release gate: exclude `.autodev/` from the PR to public main.
