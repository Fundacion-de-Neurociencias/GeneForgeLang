# Phase 5.6 Representational Stress Audit

## Scope

This audit targets the internal semantic kernel, not the ESM adapter layer or
external evidence interoperability.

It answers:

```text
Does the internal semantics preserve valid distinctions under adversarial composition?
```

## Boundary

The audit exercises:

- product-lattice canonicalization
- semantic equivalence
- adversarial meet and join composition
- mutation stress across lattice dimensions
- illegal representational collapse detection

It does not import or evaluate external adapters, protein evidence syntax,
foundation model payloads, or provider-specific metadata.

## Legitimate Collision Rule

The equivalence relation is defined in `semantic_equivalence.py`:

```text
x ~ y iff every explicit product-lattice coordinate is identical.
```

The current lattice has no quotient rules. Therefore, two distinct coordinates
must not canonicalize to the same representation. Any future relaxation must be
introduced by changing the equivalence relation first, then updating this audit.

## Generated Stress Tiers

The audit uses only generative parameters from `fixtures/semantic/audit_config.json`.

- Tier A enumerates the full product lattice.
- Tier B samples adversarial sequences of meet and join operations.
- Tier C mutates lattice coordinates and composes them against boundary states.

No hand-authored semantic cases are encoded in the config.

## Output

The runner writes structured evidence only:

```text
representational_audit_report.json
```

Schema:

```json
{
  "rsi": 0.0,
  "fpcr": 0.0,
  "illegal_collapses": [],
  "monotonicity_breaches": [],
  "canonicalization_failures": [],
  "freeze_decision": "PASS"
}
```

## Freeze Gate

PASS requires:

- `rsi >= 0.999`
- `fpcr == 0.0`
- no illegal collapses
- no monotonicity breaches
- no canonicalization failures

FAIL blocks semantic closure. The next branch must be:

```text
fix/semantic-lattice-collapse
```
