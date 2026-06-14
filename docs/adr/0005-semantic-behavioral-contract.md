# ADR-0005: Semantic Behavioral Contract Stability

## Status
Accepted

## Context
ADR-0004 established the **Structural Public Contract** of GeneForgeLang, guaranteeing that the surface API (exports, modules, types) remains stable and strictly governed. However, a language can perfectly respect its structural boundary while simultaneously breaking downstream consumers by altering the *meaning* or *observable behavior* of its constructs.

For example, if an internal change alters the normalization sequence such that `PROTEIN("TP53")` yields a different AST structure, or if extension lowering order changes, the semantic invariants are broken even though the imports are valid. This covert semantic drift undermines GFL's reliability as an institutional standard.

## Decision
We establish the **Semantic Behavioral Contract Stability System**. This system elevates behavioral invariants to the level of constitutional law, verified through automated replay against frozen snapshots.

### 1. Constitutional Semantic Invariants
The following behaviors are declared structurally invariant for any given major release:
*   **Parse Determinism**: The same `.gfl` source file must yield the exact same AST structure and canonical hash on every parse.
*   **Normalization Idempotence**: Normalizing an already normalized AST must yield the identical AST (`normalize(normalize(AST)) == normalize(AST)`).
*   **Canonicalization Stability**: The cryptographic hash of a canonicalized AST must not change across minor/patch versions.

### 2. Semantic Snapshots Corpus
A corpus of "golden fixtures" representing the constitutional semantic space (e.g., syntax normalization, extension lowering, parser determinism) will be maintained in `src/geneforgelang/governance/semantic_snapshots/`.
*   These are not standard unit tests. They are constitutional anchors.
*   The exact AST representation and canonical hashes for these fixtures are frozen in `golden_ast_hashes.json`.

### 3. Replay Certification (The Merge Gate)
All pull requests must pass the `semantic_replay.py` certification. This system parses the golden fixtures and verifies that the resulting AST shapes, normalizations, and canonical hashes strictly match the frozen snapshots.
Any failure indicates an unauthorized semantic mutation.

### 4. Semantic Evolution
Semantic evolution is possible but must be explicit. Changes to the semantic behavioral contract require an explicit rebuild of the snapshots via `snapshot_generator.py` and must be justified in a GFL-RFC, typically triggering a major version bump.

## Consequences
*   **Positive**: Downstream consumers (like GeneForge) can trust not just the API, but the fundamental behavior and structural outputs of the language. It provides absolute protection against accidental semantic drift.
*   **Negative**: Introduces rigidity to internal parser/normalizer refactoring. Any refactoring must preserve the exact canonical output of the AST, or go through a rigorous review process.
