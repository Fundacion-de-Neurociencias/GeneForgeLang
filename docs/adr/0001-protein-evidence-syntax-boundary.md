# ADR 0001: Protein Evidence Syntax Boundary

## Status

Accepted

## Context

GeneForgeLang needs to interoperate with external protein foundation model
evidence, including ESM-family outputs, without changing GeneForgeLang's causal
ontology or inference semantics.

The risk is semantic drift: embeddings or plausibility scores could be treated
as causal claims, inferred mechanisms, disease likelihoods, or generated rules.
That would violate the language boundary where GeneForgeLang describes
structure and metadata but does not invent biology.

## Decision

Add a syntax-layer extension under
`src/geneforgelang/extensions/protein_evidence/`.

The extension allows metadata constructs only:

- `PROTEIN("...")`
- `SEQUENCE("...")`
- `EMBEDDING_REF("esm")`
- `STRUCTURE_CONFIDENCE(x)`
- `PLAUSIBILITY_SCORE(x)`

These constructs normalize to metadata-only AST nodes:

- `ProteinNode`
- `SequenceNode`
- `EmbeddingReferenceNode`
- `EvidenceScoreNode`

The ESM bridge validates the external GeneForge adapter payload shape and
rejects semantic boundary violations, including these fields anywhere in a
payload:

- `pathogenicity_prediction`
- `causal_effect`
- `inferred_mechanism`
- `disease_likelihood`

## Prohibitions

The extension must not:

- modify the semantic lattice
- modify epistemic state algebra
- alter contradiction resolution
- add primitive causal ontology terms
- change inference semantics
- change compiler core logic
- synthesize rules from embeddings
- infer likely pathogenic effects
- complete causal mechanisms

## Preserved Invariants

Parsing ESM-linked syntax preserves semantic invariance:

```text
S_old = S_new
```

for the semantic lattice, causal primitives, contradiction resolution, and
inference semantics.

The extension is an interoperability contract only. Protein foundation model
outputs remain external metadata annotations.
