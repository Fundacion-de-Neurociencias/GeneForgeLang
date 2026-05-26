# ADR-002: Epistemic Runtime Refoundation

## Status

Proposed

## Context

GeneForgeLang must not become another biology DSL or a frontend for genomic foundation models.
External systems such as Carbon, OpenMed, ESMFold, AlphaFold and ClinVar must remain capability
providers, not semantic authorities.

The strategic direction is a biological epistemic runtime: a kernel that models evidence,
uncertainty, causal invalidation, provenance, constraints, perturbations, compressibility and
agent-safe execution.

## Decision

Introduce an additive architecture:

- `semantic/` owns epistemic and semantic contracts.
- `adapters/` implements external capabilities only.
- Carbon enters only as `CarbonCapabilities`.
- The semantic kernel includes provenance, temporal validity, contradiction tracking, epistemic
  state transitions, perturbation algebra, latent geometry, scale compilation and agent
  checkpoints.

The existing IR v1 remains compatible and unchanged.

## Consequences

This prevents model lock-in and avoids Carbon-shaped biology. The kernel can survive future
foundation models, symbolic engines and causal backends.

The runtime must protect the core from ontology creep. Domain-specific disease, pathway, clinical
or dataset semantics belong in higher layers, not the kernel.

## Constraint propagation

Constraints are first-order executable structures in the semantic kernel. A constraint violation is
not only a local validation error: it can propagate downstream through a `ConstraintGraph` and
degrade epistemic belief states.

The kernel supports operational constraint kinds such as reachability, monotonicity, bounded
uncertainty, topological integrity and identifiability. These are abstract epistemic invariants, not
hardcoded biological entities.

## Verification

The initial implementation is covered by `tests/unit/semantic/test_refoundation.py` and preserves
existing IR behavior through the existing IR unit tests.
