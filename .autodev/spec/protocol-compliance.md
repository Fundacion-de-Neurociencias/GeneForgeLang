# NeuroIA protocol compliance

Protocol: `C:/Users/usuario/AutonomousClaude/products/neurodiagnoses/protocols/PROTOCOLO_BUENAS_PRACTICAS_NEUROIA.md` (Spanish), including the annex "ANEXO NEUROIA – DESARROLLO AUTÓNOMO SUPERVISADO (autodev)", approved 2026-10-18. Where the annex and the protocol differ, the stricter rule applies.

## Language mapping
The repository's own rule is English-only for code, docs, commits and PRs. autodev PRs therefore use the English equivalents of the protocol's PR sections:

| Protocol (Spanish) | PR section (English) |
|---|---|
| Qué hace | What it does |
| Por qué | Why |
| Cómo reproducir | How to reproduce |
| Impacto en resultados | Impact on results |

Recorded in `project.toml` `[collaboration] pr_sections`. Each PR also lists the sensitive files it touches (annex A.3.3).

## Clauses
| Clause | Requirement (summary) | Status | Action |
|---|---|---|---|
| §2 Structure | README, LICENSE, .gitignore, src/, tests/, docs/decisions/ | met (partly) | `license` lowercase; data/ and results/ exist; no change needed now |
| §3, §"Reglas" 1 Branches | Never work on main; feature/fix branches | gap (repo): agents pushed a 26-branch chain, never merged | autodev uses `autodev/*` (annex A.2); integrate the chain via F005-F009 |
| §4 Commits | Conventional commit types | met for autodev | commitlint check in F005 |
| §5, A.3.3 PR template | Four sections; no self-approval | gap (repo): 15 open PRs, none with human review | autodev PRs use the mapped sections |
| §"Reglas" 4 main protected | Require PR, checks, review; no force push | gap | F003 prepares settings; owner applies (permissions change) |
| CI obligatorio, §7.2 | Each PR runs install, lint, tests, secret scan; failing CI blocks merge | gap: CI auto-fixes lint, does not gate | F003 |
| §6 Reproducibility | Pinned versions, explicit parameters, seeds | gap: open version ranges; random examples without seeds | F004, F011; lockfile for CI (F003) |
| §7.1 Pre-commit secret scan | gitleaks blocks commits with secrets | gap | F001 |
| §7.3 AI/agent security tests | Prompt-injection and tool-abuse tests | n/a for the library today (no agent runtime); revisit if LLM features are added | none |
| §7.5 HITL | Human approval for deletes, permissions, sensitive actions | met by autodev guard | approvals logged in the hub audit log |
| §7.6 Runtime protection, rate limiting | For deployed systems | gap only if FastAPI apps are kept | F016 |
| §7.8, §11 Credentials | Never in git; rotation after incidents | gap: `.devcontainer/.env` tracked | F001; rotation by owner; history purge is an owner gate |
| §8 Data | No dummy datasets or simulations as evidence | gap: random BRCA1 "validation", simulated components | F002, F004, F008 |
| §8.1 Real-data integrity | Every claim traces to real evidence; no fake fallbacks | gap | F002, F004, F006 |
| §8 (DUA) 1-4 | No third-party data without registered DUA; no redistribution; paper gate | unknown: `EVIDENCE_MATRIX.md` (ADNI/NACC) | Legal review before it lands (F009, Needs owner) |
| §10 Minimum testing | A test that the pipeline runs; tests for parsing | met (1050 tests on chain) but unverified in CI | F003 |
| §11 Decisions | `docs/decisions/` with Context/Decision/Consequences | partial: `docs/decisions/` has one record; ADRs live in `docs/adr/` | New decisions go to `docs/decisions/`; F009 reconciles the two folders |
| §12, "Documentación mínima" | Update README, CHANGELOG, docs/architecture.md | partial | Every autodev PR updates CHANGELOG |
| A.2 Branches | `autodev/` prefix; never touch team branches; check overlap first | met by configuration | Overlap with `feature/PDN_feature-GFP` recorded in spec/team.md |
| A.3.1 Independent verification | Separate session verifies; evidence in `.autodev/evidence/` | met by autodev design | none |
| A.3.2 Human review | Every change to main via PR reviewed by a person other than the author; the owner may be that person | met by configuration (`min_human_reviews = 1`, merge authority owner) | none |
| A.4 Sensitive changes | CI/CD, deploy, infra and `core/` need 2 human reviews, one from the Coordination, unless the owner grants a written exception | **gap**: config sets `sensitive_min_reviews = 1` per owner decision 7; Coordination (Raquel Riera) is not active on GFL | Owner decides: record a standing written exception for GFL in the audit log, or name a second reviewer. Until then, each sensitive PR asks for the exception explicitly |
| A.5 Publication | Production only from a `vX.Y.Z` tag with owner approval; post-release check | met by configuration (`release_requires_tag = true`) | F012 (PyPI is the "production" of a library) |
| A.6 Traceability | Hash-chained audit log; each cycle records where it stopped | met by the hub | none |
| A.7 Documentation | Truthful public text; stale docs proposed for removal with approval | gap | F002, F009 |
| A.8 Monthly metrics | % changes by autodev, first-pass approvals, post-merge errors, reverts, review time, cost | not yet applicable | hub report once PRs flow |
| A.9 Never | No deploy/merge/delete/permission/external message without approval; no simulated data as evidence; no secrets or patient data; no protocol edits | met by guard (`forbidden_paths` include `.devcontainer/.env`, `**/*.pkl`) | none |

## Proposed amendment (for the owner, not applied)
The annex A.4 two-review rule cannot be met on GFL while only one other human (María) is active and the Coordination does not review GFL. Proposed wording, in the protocol's language, for the owner to approve or reject:
> "En repositorios con un único colaborador humano activo, la Dirección puede sustituir la segunda revisión de cambios sensibles por su propia aprobación explícita, registrada en el registro de auditoría."
