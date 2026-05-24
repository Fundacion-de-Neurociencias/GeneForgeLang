# Temporal Perturbation Semantics

GeneForgeLang models temporal perturbation as a semantic execution primitive. Timing is part of
the biological meaning of a perturbation, not an adapter feature and not a sequence-token
representation.

The temporal layer is backend-agnostic and contains:

- `TemporalPerturbationIR`
- activation, dwell, dissociation, pulse and gate operators
- `facilitated_dissociation` as a first-class primitive
- temporal perturbation composition
- cross-scale temporal compilation
- temporal constraint validation
- `TemporalCapabilityProvider` for optional backend capabilities

## Core principle

The effect of a biological perturbation can depend on activation profile, dwell regime,
dissociation mode, rebound expectation and causal timing constraints. GeneForgeLang keeps those
semantics in the core runtime and lets adapters provide only instrumental estimates.

## Example

```python
from geneforgelang.temporal import facilitated_dissociation, sequential, activate

schedule = sequential(
    activate("IL2R", profile="gated"),
    facilitated_dissociation("IL2R", timed_release="brief"),
)
```

This expresses temporal control over receptor occupancy without importing any model-specific
ontology, tokenizer or backend.
