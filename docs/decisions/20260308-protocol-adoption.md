# ADR 001: Adoption of the NeuroIA Best Practices Protocol

**Date**: 2026-03-08  
**Status**: Accepted  
**Author**: Antigravity (AI)  

## Context
The GeneForgeLang (GFL) repository has grown organically, accumulating multiple utility scripts at the root and lacking a standardized directory layout for data and results. To scale professionally and ensure the scientific reproducibility required by NeuroIA, it is necessary to formalize repository structure and workflows.

## Decision
We adopt the "NeuroIA Best Practices Protocol for Repositories v1.0". Implemented changes include:
1. Directory restructuring (`data/`, `results/`, `docs/decisions/`, etc.).
2. Relocation of utility scripts from root to `scripts/`.
3. CI/CD automation via GitHub Actions.
4. Protection of the `main` branch (disallowing direct commits).
5. Standardization of atomic commit conventions, English language mandate, and PR flows.

## Consequences
- **Positive**: Enhanced order, simplified onboarding, CI-guaranteed reproducibility, traceability of technical decisions.
- **Negative**: Increased initial workflow rigor for contributors.
- **Neutral**: Requirement to keep `docs/decisions/` continuously up to date for all architectural developments.
