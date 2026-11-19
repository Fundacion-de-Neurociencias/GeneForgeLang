# ADR 0003: Extension Sunsetability and Core Non-Contamination

## Status
Proposed

## Context
GeneForgeLang is an open-source language, not a closed internal pipeline. Its
architecture must survive external contributors, forks, and third-party
extensions without relying on private cultural discipline.

ADR-0002 established syntactic minimality and proof burden inversion. The next
failure mode is harder to detect: extensions that appear optional but quietly
become required by the core runtime, parser, lattice, contradiction machinery,
or semantic ontology.

If an extension cannot be removed without breaking the core language, it has
ceased to be an extension. It has become hidden language semantics.

## Decision
All extensions must satisfy Extension Sunsetability.

1. **No core-to-extension imports**

   Core language packages must not import from `geneforgelang.extensions`.
   Extension dependencies must point outward from optional extension code, not
   inward from the language kernel.

2. **No extension-to-semantic runtime dependencies**

   Extensions must not import semantic runtime modules, lattice modules,
   contradiction machinery, inference engines, compiler behavior, or primitive
   ontology modules. They may define syntax, metadata carriers, structural
   validation, and provider-neutral adapter contracts.

3. **No runtime hooks**

   Extensions must not register hidden hooks into parser core, inference
   execution, contradiction resolution, lattice transitions, or ontology
   registries.

4. **Clean removal property**

   Removing an extension package must not change baseline parser behavior,
   semantic ontology, epistemic state algebra, contradiction behavior, or
   compiler semantics.

5. **Governance scoring**

   Language governance checks must report a compliance score over reduction
   rigor, provider neutrality, primitive necessity, semantic contamination risk,
   and sunsetability. Scores below the blocking threshold fail CI.

## Consequences
- Extensions remain opt-in and amputable.
- Provider integrations cannot become implicit dependencies of the language
  kernel.
- Reviewers can reject extensions that pass syntax tests but fail architectural
  sunsetability.
- The governance audit becomes the executable constitution for language growth.
