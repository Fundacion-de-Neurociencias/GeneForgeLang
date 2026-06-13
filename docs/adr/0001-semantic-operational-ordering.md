# ADR 0001: Semantic Operational Ordering and Bounded Convergence

## Status
Proposed

## Context
In Phase 4 and 5 of the epistemic contract fabric design, we introduced constraint propagation (invalidation bridge) and conflict resolution. We originally posited that the execution of these operations should guarantee "path-independence" or strict confluence.

However, in a biological epistemic runtime, operations are intrinsically non-commutative. For example:
- `Conflict Resolution` followed by `Invalidation` might preserve an epistemic dispute (if both contracts survive invalidation).
- `Invalidation` followed by `Conflict Resolution` might eliminate the dispute entirely if one contract is invalidated prior to resolution.

Enforcing strict equality across these different execution paths would require introducing artificial rules that distort the denotational semantics of the language. Instead, GeneForgeLang must formally embrace non-commutative operations while ensuring they behave predictably within the semantic bounds of the epistemic lattice.

## Decision
1. **Relaxation of Confluence**: We abandon the requirement for strict global path-independence.
2. **Admissible Operational Ordering**: We define a formal operational precedence loop for the runtime:
   1. **Constraint Propagation** (Invalidation Bridge)
   2. **Conflict Resolution**
   3. **Temporal Stress Evaluation**
   4. **Convergence Stabilization**
3. **Bounded Convergence to Semantic Equivalence**: We prove that, under the admissible ordering, any configuration of the epistemic graph converges to a specific, bounded semantic equivalence class without falling into infinite cyclic degradation or orphan states. Different execution paths may yield different specific terminal states, but they must land in the same equivalence class or strictly stabilize.

## Consequences
- The runtime execution engine must rigorously follow the Admissible Operational Ordering to avoid generating non-deterministic garbage states.
- The next step requires refactoring the `ContradictionState` from a flat Enum into a **product lattice** (separating truth support, stability, and resolution) to mathematically express these equivalence classes properly.
