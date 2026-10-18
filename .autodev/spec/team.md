# People and process: GeneForgeLang

## People
| Person | Identity in git | Areas | Last active | Role for autodev |
|---|---|---|---|---|
| Manuel Menéndez (owner) | Manuel Menéndez, manuelmenendezgonzalez | product direction; early roadmap branches (2025) | 2025-06 in git; active as owner | Product developer; approves every slice and every irreversible step |
| María Alonso Vega | mariaalonsovega (two emails: fneurociencias.com and .org) | `feature/PDN_feature-GFP`, repository reorganization, `check-src` | 2026-10-15 | Only active human. Asked for an opinion on PRs that touch her files; not blocking |
| Carlos Gómez | carlosgoro | CI, lint, tools; main's 31 commits (formalization-v2 merge, ruff/pytest fixes) | 2026-06-15 | Asked for an opinion on CI and on the reconciliation PR; not blocking |
| Sara Pérez | Sara, saraperez-cyber | imports fixes, project structure | 2026-05 | Inactive; informed only |
| Agents (unattributed) | "Fundación de Neurociencias <admin@fneurociencias.org>", "Usuario <usuario@example.com>" | the whole chain (~26 branches) | 2026-10-17 | Not a reviewer. Recommend a distinct bot identity |
| Raquel Riera (Coordination, per protocol) | not seen in GFL history | scientific validation | n/a | Needed for annex A.4 unless the owner grants an exception |

## Active branches that autodev must respect
- `feature/PDN_feature-GFP` (María, based on main, 2026-10-15). Overlaps the chain in about 10 files, including `src/geneforgelang/core/execution.py`, `src/geneforgelang/plugins/plugin_registry.py`, `src/geneforgelang/ir/external/openmed_connector.py`, `CONSTITUTION.md` and `PROTOCOL.md`. autodev does not edit these files outside the planned slices. Before/after-chain order: decided by the owner with María.
- The chain (`feature/*` from `feature/agentic-genomics-causal-validation` to `feature/viral-interactome-complexes`) is the product; autodev integrates it and does not add new commits to those branches.
- Stale branches (`refactor/*`, `roadmap-phase-*`, `gh-pages`, etc.): untouched; candidates for cleanup only with owner approval.

## Open pull requests
15 open PRs (#7-#21). #10-#21 conflict with each other or with main; none has a human review. They are superseded by the slice PRs (F007-F009) and closed only with a comment linking the replacement.

## Review flow (configured)
1. autodev works on `autodev/*` branches and integrates on `autodev/integration`.
2. An independent verifier session checks each feature; evidence goes to `.autodev/evidence/`.
3. A PR to main with the sections What it does / Why / How to reproduce / Impact on results, and the sensitive files touched.
4. Review requests to María and/or Carlos when their areas are touched; autodev replies to their comments (`reply_to_reviews = true`) but does not wait on them.
5. The owner approves the merge in chat (`merge_authority = "owner"`, `min_human_reviews = 1`).
6. Releases only from `vX.Y.Z` tags, with owner approval.

## Where plans live
- Living plan: `.autodev/next-steps.md`. Product view: hub `products/geneforge/`.
- Team plans outside git (Drive): unknown; ask the owner if there is a GFL plan folder.
