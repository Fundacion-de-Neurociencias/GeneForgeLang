# GFL Versioning and Evolution Policy (Draft v0.1)

## 1. Semantic Versioning for Biology
GFL follows a strict Semantic Versioning (SemVer) approach (`MAJOR.MINOR.PATCH`), but applied to biological semantics:

*   **MAJOR**: Breaking changes to the core grammar, biological state structure, or fundamental causal rules. (e.g., removing a primitive type).
*   **MINOR**: Additive changes that don't break backward compatibility (e.g., a new instruction, a new canonical biological type).
*   **PATCH**: Documentation fixes, validator performance improvements, or bug fixes in the reference implementation.

## 2. Evolution Process (The GFL-RFC)
To maintain its status as an open-source project "open to everyone", GFL adopts an RFC (Request for Comments) process:
1.  **Proposal**: Anyone can submit a GFL-RFC (in `docs/rfc/`) proposing a semantic change.
2.  **Community Review**: Discussion period for ecosystem impact (GeneForge, researchers, third-party developers).
3.  **Formalization**: Once approved, the change is integrated into the core specification files (`docs/spec/`).

## 3. Runtime Compatibility Guarantee
Runtimes (like GeneForge) must declare which GFL version they support.
*   **Forward Compatibility**: GFL 1.2 runtimes should be able to execute GFL 1.1 scripts.
*   **Graceful Degradation**: If a script uses a feature from GFL 1.3 that a 1.2 runtime doesn't understand, the runtime must fail with a clear `UNSUPPORTED_SEMANTIC` error rather than producing an incorrect biological result.

## 4. Decoupling from GeneForge Release Cycle
GFL releases are independent of GeneForge WebApp or GeneForge Core updates. This ensures that the biological language can evolve at the pace of scientific discovery, not software product roadmap.
