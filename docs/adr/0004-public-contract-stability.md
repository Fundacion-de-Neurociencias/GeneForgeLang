# ADR-0004: Public Contract Stability

## Status
Accepted

## Context
GeneForgeLang (GFL) is transitioning from being an implicitly governed internal framework component (used exclusively by GeneForge) to an independent, institutional open-source language standard. In its previous state, downstream consumers like GeneForge freely imported internal modules, models, and CLI tools, establishing unwritten contracts and tight architectural coupling.

This "monorepo culture" creates a drift where downstream convenience dictates upstream evolution. If GFL is to function as a public language, its API must be robust, stable, and sovereign. Ad-hoc imports and silent API expansions destroy backward compatibility and make constitutional evolution impossible.

## Decision
We establish the **Public Contract Stability System** to enforce API sovereignty through automated coercion. This decision mandates the following principles:

### 1. Public Contract Sovereignty
The public API surface of GFL is Sovereign. **Downstream convenience cannot justify upstream surface expansion.** The API is designed for structural semantic correctness, not to facilitate shortcuts in downstream systems like GeneForge.

### 2. Strict API Boundary
The only modules permitted for external consumption are:
*   `geneforgelang.api`
*   `geneforgelang.contracts`
*   `geneforgelang.types`

Any downstream system importing from `models`, `cli`, `core` (excluding `.api`), or `extensions` is structurally invalid.

### 3. Frozen Public Manifest
The public surface of GFL must be explicitly declared in a versioned `public_manifest.json` file. Any additive or breaking changes to the exported symbols, type signatures, or contracts must be reviewed by humans and cannot be silently regenerated.

### 4. Dual Boundary Enforcement
*   **Upstream (Level 1)**: GFL CI will enforce that the actual codebase exactly matches the `public_manifest.json`. Unapproved expansions will fail the build.
*   **Downstream (Level 2)**: GFL will distribute an automated AST auditor (`api_boundary_audit.py`) that downstream consumers must run to verify they are not leaking internal dependencies.

### 5. Formal Deprecation Protocol
A public symbol cannot be simply amputated. The lifecycle for removing an API is:
1.  **Notice**: The symbol is marked as `deprecated` in the `public_manifest.json`.
2.  **Grace Period**: The symbol emits warnings via the `api_boundary_audit.py` and at runtime for at least one major/minor version cycle.
3.  **Migration Path**: A documented alternative must be provided.
4.  **Sunset**: The symbol is removed in a major version release.

## Consequences
*   **Positive**: Downstream consumers can rely on GFL without fear of silent breakage. GFL can evolve its internal mechanics freely as long as the public API contract is honored.
*   **Negative**: Initial friction for systems like GeneForge that previously relied on "opportunistic imports" (this has already been resolved via the initial amputation phase). The GFL core team faces higher overhead when modifying the public API, as changes require explicit manifest updates and human review.
