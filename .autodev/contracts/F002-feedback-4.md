# F002 feedback 4 (verify 4, commit 5dcc4f3)

Verdict: FAIL on one point. Everything else passes: lint, the full suite (968 passed), the guard against origin/main (29 failures in 13 families), cffconvert, the DOI check, the language check, and the governance auditor (0 blocking).

1. **The strict xfail guards swallow errors, which breaks contract D16.**
   - What I did: in a scratch worktree of HEAD, I deleted `src/geneforgelang/ir/external/openmed_connector.py` and ran `pytest tests/docs/test_public_claims.py::test_owned_claim_absent`.
   - What I expected: a test error, or C17 XPASS (strict fails), so that F004 is forced to drop the marker and arm the guard.
   - What happened: `XFAIL [C17-privacy-cleared-F004] - C17 still present`. `FileNotFoundError` counts as the expected failure. Evidence: `.autodev/evidence/F002/verify4-owned-guards.log`, case 4.
   - Where to look: `tests/docs/test_public_claims.py:367` (`_owned_xfail`). Fix: `pytest.mark.xfail(strict=True, raises=AssertionError, ...)`. Optionally, decide what a missing file means in `_c17_no_unconditional_privacy_flag`.
   - Proof to attach: rerun case 4 and show that it is no longer reported as XFAIL.

Advisory, not blocking: exclude `.autodev/` from the PR to public main. Item 6 (owner approval) and the Zenodo DOI (A2) remain owner gates.
