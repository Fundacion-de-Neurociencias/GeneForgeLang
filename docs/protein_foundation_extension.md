# Protein Foundation Model Evidence Extension

The protein evidence extension adds syntax-layer interoperability for protein
foundation model outputs such as ESM embeddings. It is deliberately isolated
from GeneForgeLang semantic ontology, epistemic state algebra, contradiction
resolution, causal primitives, inference semantics, and compiler core logic.

## Scope

Supported syntax:

```gfl
PROTEIN("TP53")
SEQUENCE("MEEPQSDPSV...")
EMBEDDING_REF("esm")
MODEL_STRUCTURE_CONFIDENCE(0.82)
EMBEDDING_SCORE(0.41)
```

The syntax normalizes into canonical metadata nodes only:

- `ProteinNode`
- `SequenceNode`
- `EmbeddingReferenceNode`
- `EvidenceScoreNode`

These nodes carry external evidence annotations, structural metadata, and
reference links. They do not assert biological causality, derive hypotheses, or
modify any semantic lattice state.

## Separation From Semantics

The extension is not wired into the core parser, compiler, semantic runtime, or
ontology registry. Consumers must opt in by importing
`geneforgelang.extensions.protein_evidence`.

Allowed operations:

- evidence annotation
- structural metadata attachment
- external reference linking

Rejected operations:

- inferred causal claims
- semantic completion
- rule synthesis from embeddings

## ESM Adapter Contract

`foundation_bridge.py` provides the provider-neutral bridge for protein
foundation model outputs. `esm_bridge.py` is the ESM-specific adapter layer over
that generic bridge and preserves these functions:

- `validate_embedding_schema(payload)`
- `import_embedding(payload)`
- `export_to_geneforge_adapter()`

Accepted payloads may include protein identifiers, sequences, embedding vectors
or references, provider/model names, explicitly model-scoped scores, metadata,
and external references. The bridge rejects payload fields that attempt to
encode causal claims, semantic completions, epistemic status, truth support, or
synthesized rules.

The adapter output is a serializable extension AST marked with
`semantic_role: metadata_only`, preserving the invariant:

```text
Semantic ontology unchanged.
```
