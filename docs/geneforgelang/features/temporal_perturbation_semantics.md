# Temporal Perturbation Semantics

GeneForgeLang models temporal perturbation as a semantic execution primitive. Timing is part of
the biological meaning of a perturbation, not an adapter feature and not a sequence-token
representation.

The core purpose is not to describe time. The core purpose is to test whether a perturbation remains
causally coherent under temporal stress.

The temporal layer is backend-agnostic and contains:

- `TemporalPerturbationIR`
- activation, dwell, dissociation, pulse and gate operators
- `facilitated_dissociation` as a first-class primitive
- temporal perturbation composition
- cross-scale temporal compilation
- temporal constraint validation
- temporal stability testing under activation, dwell, dissociation and rebound stress
- `TemporalCapabilityProvider` for optional backend capabilities

## Core principle

The effect of a biological perturbation can depend on activation profile, dwell regime,
dissociation mode, rebound expectation and causal timing constraints. GeneForgeLang keeps those
semantics in the core runtime and lets adapters provide only instrumental estimates.

The runtime can stress a schedule by delaying activation, extending dwell, changing release mode or
amplifying rebound. The resulting `TemporalStabilityReport` gives a stability score, sensitivity
profile and invariant failures.

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

```python
from geneforgelang.temporal import TemporalExecutionRuntime, facilitated_dissociation

runtime = TemporalExecutionRuntime()
report = runtime.test_temporal_stability(facilitated_dissociation("IL2R"))
```

This tests whether the temporal regime is robust under timing perturbations.
