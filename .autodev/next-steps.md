# Next steps (living plan)

Curated by the owner's direction, evolve retrospectives and Claude. The runner's state snapshot reads it.
This is an endless cycle, so the list is never empty. Keep it ranked and short.

## Now
- Owner reviews and approves the onboarding plan (roadmap Phase 0-3, features F001-F016).
- F001: remove `.devcontainer/.env` and the `.pkl` from the tree; gitleaks in pre-commit and CI; rotation list by service name.
- F002: correct public claims (README, manuscript, whitepaper, CHANGELOG, SECURITY, CITATION) with not-for-clinical-use / not-legal-advice notices; PR for the owner to approve.

## Next
- F003: one CI that gates PRs; one lint config; branch-protection settings for main (owner applies or approves).
- F004: provenance contract; label and disconnect simulated components on main.
- F005: reconcile main's 31 commits with the chain; integration plan by slices.
- F006: honest conformance runner.

## Later
- F007-F009: integrate the chain in slices (owner approves each).
- F010-F012: public API facade, unified version, publish readiness (TestPyPI dry run is an owner gate).
- F013-F016: plugin entry-point group, GeneForge consumer contract, cross-platform CLI, FastAPI apps.
- Phase 3: specification and conformance work backed by real code.

## Needs owner
- **Key rotation.** After F001 lists the services, the owner or the account managers rotate the keys. Agents never read the file.
- **History purge.** Removing `.devcontainer/.env` from the public history needs a force-push. Separate approval; recommended only after rotation, because the old values are already public.
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
