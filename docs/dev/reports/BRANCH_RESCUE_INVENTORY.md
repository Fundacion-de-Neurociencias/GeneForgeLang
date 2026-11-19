# Branch Rescue & Immutable Archive Inventory

This report documents the systematic audit and zero-loss rescue of unmerged branches against `main` (`fad8138`), ensuring that **no valuable code, architectural decision records (ADRs), or domain examples are lost**.

---

## 1. Rescued & Integrated into `main`

| Source Branch | Rescued Artifacts | Target Location on `main` |
| :--- | :--- | :--- |
| `origin/feature/PDN_feature-GFP` | `RFdiffusionPlugin` (updated with optional `torch` import, English comments, and `simulated` provenance metadata) + new unit tests | [`src/geneforgelang/plugins/rfdiffusion.py`](../../../src/geneforgelang/plugins/rfdiffusion.py), [`tests/unit/test_rfdiffusion_plugin.py`](../../../tests/unit/test_rfdiffusion_plugin.py) |
| `origin/feat/public-contract-stability` | `ADR-002-epistemic-runtime-refoundation.md`, `temporal_perturbation_semantics.md`, and 3 temporal GFL examples | [`docs/dev/decisions/ADR-002-epistemic-runtime-refoundation.md`](../decisions/ADR-002-epistemic-runtime-refoundation.md), [`docs/geneforgelang/features/temporal_perturbation_semantics.md`](../../geneforgelang/features/temporal_perturbation_semantics.md), [`examples/temporal/`](../../../examples/temporal/) |
| `origin/roadmap-phase-3` | Fundamental LLM + GFL integration principle | [`docs/LLM_GFL_Fundamental_Principle.md`](../../LLM_GFL_Fundamental_Principle.md) |
| Governance / Legal Sync | External data terms (`ALPHAGENOME`, `ENSEMBL`, `UNIPROT`) | [`docs/DATA_TERMS.md`](../../DATA_TERMS.md) |

---

## 2. Historical Branches Archived as Immutable Git Tags (`archive/*`)

Branches representing superseded snapshots (already consolidated into `main` via PR #28/#30/#31 or containing legacy directory layouts such as `Downloads/` or `.devcontainer/.env`) are preserved as immutable Git tags so their full commit history remains accessible without cluttering active development branches:

* `archive/autodev-integration` (`autodev/integration` — playbooks and `.autodev/` contracts `F001`–`F020`)
* `archive/autodev-publish` (`origin/autodev/publish`)
* `archive/docs-hvl-implementation-plan` (`origin/docs/hvl-implementation-plan`)
* `archive/feat-public-contract-stability` (`origin/feat/public-contract-stability`)
* `archive/feature-pdn-feature-gfp` (`origin/feature/PDN_feature-GFP`)
* `archive/feature-clawbio-stress-test` (`origin/feature/clawbio-stress-test`)
* `archive/feature-dynamic-dna-helix-viewer` (`origin/feature/dynamic-dna-helix-viewer`)
* `archive/feature-ppg-clinical-schema` (`origin/feature/ppg-clinical-schema`)
* `archive/refactor-repository-reorganization` (`origin/refactor/repository_reorganization`)
* `archive/refoundation-epistemic-runtime` (`origin/refoundation/epistemic-runtime`)
* `archive/roadmap-phase-2` (`origin/roadmap-phase-2`)
* `archive/roadmap-phase-3` (`origin/roadmap-phase-3`)
* `archive/separation-evidence-syntax` (`origin/separation-evidence-syntax`)
