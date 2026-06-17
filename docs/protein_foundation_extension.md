# Protein Foundation Model Extension

## Scope

This extension adds syntax-layer interoperability for protein foundation model
evidence references. It is not a semantic extension and is not wired into the
GeneForgeLang compiler core.

Supported metadata constructs:

```text
PROTEIN("TP53")
SEQUENCE("MEEPQSDPSV...")
EMBEDDING_REF("esm")
STRUCTURE_CONFIDENCE(0.82)
PLAUSIBILITY_SCORE(0.74)
```

## Syntax And Semantics Separation

The extension parses and normalizes references into metadata-only nodes:

- `ProteinNode`
- `SequenceNode`
- `EmbeddingReferenceNode`
- `EvidenceScoreNode`

These nodes do not modify the semantic lattice, epistemic state algebra,
contradiction resolution, primitive causal ontology, inference semantics, or
compiler core logic.

## Metadata-Only Role

Protein foundation model outputs are external annotations. They may identify a
protein, carry a sequence, point to an embedding provider, or attach a numeric
evidence score. They must not be interpreted as causal claims.

The parser rejects phrases that attempt causal inference, semantic completion,
or rule synthesis from embeddings.

## GeneForge ESM Adapter Contract

`esm_bridge.py` validates payloads from the GeneForge ESM evidence adapter using
the following required fields:

- `sequence_embedding`
- `structure_confidence`
- `neighborhood_hits`
- `plausibility_score`
- `source_model`
- `provenance`

The provenance must explicitly declare:

- `semantic_mutation: false`
- `causal_completion: false`

This keeps interoperability limited to external evidence linking.
