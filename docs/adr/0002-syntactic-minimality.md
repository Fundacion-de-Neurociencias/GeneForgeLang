# ADR 0002: Syntactic Minimality and Extension Discipline

## Status
Proposed

## Context
GeneForgeLang is adding interoperability layers for evidence contracts, epistemic
lattices, temporal stress, constraint propagation, conflict algebra, and protein
foundation model outputs. These capabilities are useful only if the core
language remains small, compositional, and semantically disciplined.

The main architectural risk is no longer only semantic leakage into the
epistemic runtime. It is syntactic inflation: adding many narrowly scoped
constructs that could have been represented by existing primitives or by a
provider-neutral intermediate representation.

If unchecked, syntactic inflation turns GeneForgeLang from a compact scientific
language into a catalog of feature-specific constructs.

## Decision
All future extensions must pass a Semantic Minimality Audit before merge.

1. **No causal semantics in extensions**

   Extensions must not introduce causal claims, inference rules, contradiction
   policies, epistemic state transitions, ontology terms, or compiler behavior.
   They may carry syntax, metadata, references, and structural annotations only.

2. **Irreducibility requirement**

   Every new syntactic construct must demonstrate that it is not reducible to an
   existing primitive or provider-neutral metadata form without formal loss. If
   it is reducible, the construct must not be added.

3. **Provider-specific syntax compiles to provider-neutral IR**

   Provider-specific adapters may exist at the edge, but their output must
   normalize into provider-neutral extension IR. Provider names may appear as
   metadata, not as semantic categories.

4. **Aggressive AST primitive minimization**

   Extensions must minimize canonical AST node types. New node classes require
   justification that an existing node cannot represent the construct without
   ambiguity or loss of validation guarantees.

5. **No score promotion**

   Model scores, embedding scores, confidence values, or latent-space measures
   must never promote themselves into `TruthSupport`, `EpistemicStatus`,
   causal validity, contradiction state, or semantic confidence.

6. **Invariant tests are merge gates**

   Extensions that parse external evidence must include tests proving semantic
   null-effect against the lattice, ontology, epistemic state algebra, and rule
   synthesis boundaries.

## Consequences
- New extension proposals must include a short minimality section explaining
  why each construct is necessary.
- Provider adapters such as ESM integrations must remain thin wrappers over
  provider-neutral extension contracts.
- Syntax that can be represented as `ExternalEvidenceReference`-style metadata
  should not receive a dedicated node unless validation would otherwise become
  ambiguous.
- The phrase "Semantic ontology unchanged" becomes an explicit release
  invariant for syntax-layer interoperability work.
