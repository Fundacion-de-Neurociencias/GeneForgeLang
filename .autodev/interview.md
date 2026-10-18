# Owner interview and decisions

## 2026-10-18: onboarding decisions (binding)
Recorded from the owner's answers in the hub chat (Spanish), restated in English with the same meaning.

1. **Secrets.** Treat the tracked env files as exposed.
   - Remove them from the tree, add a .gitignore guard, and add secret scanning (gitleaks) in pre-commit and in CI.
   - Give the owner a rotation list that names services, never values. Agents may not read the file. The owner, or whoever manages those accounts, rotates the keys.
   - Purging history in the public repo needs a force-push and a separate owner approval. It is queued as an owner decision and is never done automatically.
2. **Public text.** Correct it now, as a PR the owner approves. Remove, or relabel as "illustrative simulation", every claim without evidence: the README validation section, the manuscript, the whitepaper claims, the PyPI badge and install line, the version, the DOI and the SECURITY claims.
3. **Role of GFL.** First a usable open library: installable from PyPI, with one coherent version and a small, stable, tested public API that works for GeneForge and for third parties. The formal-standard work (specification, conformance) comes after, backed by real code.
4. **Simulated components.** Label them as simulation in code and outputs, and disconnect them from any decision or public text. Each one is replaced by a real implementation only when access exists and an oracle test proves it.
5. **Legal and clinical.**
   - Add clear "not legal advice / not for clinical use" notices.
   - Remove such claims from public text.
   - List what a patent lawyer and a regulatory expert must review. Agents never decide those questions.
6. **Integration.** The newest chain is the product. Integrate it in reviewable slices, GFL first. Before that: clean the junk, get tests and CI green, protect main.
   - Coordinate with María: her PDN branch overlaps the chain in about 10 files. Decide with her whether it lands before or after the chain.
   - Reconcile main's 31 commits.
7. **Review.** The owner approves each slice (merge authority: owner).
   - On PRs that touch their work, ask María and Carlos for an opinion through PR review requests or comments. Do not block on them.
   - Configuration: `[collaboration] mode = "team"`, `merge_authority = "owner"`, `min_human_reviews = 1`, `[team] reply_to_reviews = true`.

## 2026-10-18: quality directive (binding, all products)
"No demos. Professional, high-quality products. 'It works' is not enough; aim for the best standards and the best architecture: excellence, not just passing tests."
Applied as: `spec/quality-bar.md` (standards, each with its check); every feature has at least one acceptance item that names the standard; root-cause redesigns with migration paths (facade API, provenance contract, plugin protocol) are preferred over patches.

## Open questions for the owner (not yet asked)
Listed in `next-steps.md` under "Needs owner".

## Plan approval
Pending. The lead engineer presents the plan; the owner's "sí" is recorded here with its date.

## 2026-10-18 owner approval of the plan
- **Approved:** "Por lo demás ok, adelante". Work starts with GeneForgeLang.
- **Scope clarification from the owner:** he sees GeneForge as part of GeneForge Ecosystem, a child directory. Technically, GeneForge is a git submodule with its own GitHub repository and history, so autodev keeps two workspaces (`geneforge-ecosystem`, `geneforge`). It treats them as one product, "GeneForge" (hub `products/geneforge`), and reports on them together to the owner.
- **Sensitive-change reviews (NeuroIA protocol annex A.4):** the owner chose "Mi sí basta, con excepción registrada". His approval is the required human review for sensitive paths. The exception is recorded in the audit log for each sensitive PR. Carlos or María are asked for a non-blocking second opinion.
