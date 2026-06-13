# ADR 0003: Extension Orthogonality under Excision

## Status
Proposed

## Context
As GeneForgeLang scales as an open-source biological DSL, there is an inherent risk that extensions (which bridge external scientific APIs like ClinVar, UniProt, ESM) will inadvertently bleed into and contaminate the core language semantics. Superficial static checks (e.g., "no file imports X") are fragile against future architectural expansions and adversarial creativity.

We must establish a rigorous, mathematically auditable boundary to guarantee that extensions are strictly amputable without altering the language's core foundation.

## Decision: Formal Extension Orthogonality

We mandate the principle of **Extension Orthogonality under Excision**. We define this not as an informal guideline ("extensions should be removable"), but as a formal, verifiable property of the codebase.

An extension $E$ is defined as mathematically and architecturally valid if and only if the following four properties hold:

1. **Semantic Invariance under Removal:**
   $$\mathcal{S}(\text{Core}) = \mathcal{S}(\text{Core} \cup E) \setminus \mathcal{S}(E)$$
   The base semantic rules, algebra, and mathematical operations of the core language remain completely invariant under the excision of $E$. The existence of $E$ must not mutate the core's operational semantics.

2. **Decoupled Semantic Transitions:**
   $$\forall \tau \in \text{Transitions}(\text{Core} \cup E), \quad \tau \text{ depends on } E \implies \tau \notin \text{Transitions}(\text{Core})$$
   No core state-space transition or runtime constraint propagation can depend on constructs, methods, or states introduced by $E$.

3. **Closure Proof Preservation (Lattice Integrity):**
   The removal of $E$ must preserve all lattice closure, idempotence, and commutativity properties. The proof checks implemented in the core algebraic test suite (`test_closure.py`) must execute and pass without $E$.

4. **Parser Completeness for Base Grammar:**
   The removal of $E$ must preserve the parsing completeness and correctness of the base grammar. The base parser must successfully parse, validate, and normalize core GFL programs without any dependency on $E$'s AST nodes or grammar rules.

## Enforcement Mechanism

To transform these properties into a hard CI/CD gate, we implement a hybrid verification pipeline:

### 1. Level 1 — Hard Mechanical Gate (Deterministic Block)
Implemented in `architectural_audit.py` as a blocking pre-push validation (`make constitutional`):
- **Core Contamination Check:** Computes the full transitive dependency closure of the codebase using AST. It blocks any import path (direct or transitively through intermediaries) from `extensions/*` to the core zones:
  * `semantic.lattice`
  * `semantic.conflict`
  * `semantic.constraints`
  * `semantic.runtime`
- **Reverse Contamination Check:** Prohibits any import from the core compiler or `semantic/*` into any module in `extensions/*`. No exceptions.
- **Physical Excision Simulation:** Automates the physical excision of each extension from the source tree, runs the core semantic test suites (`tests/unit/semantic`) and parser base tests (`tests/unit/test_parser.py`) in an isolated subprocess, and validates that all tests pass before restoring the extension directory. Any test failure under excision results in immediate merge rejection.

### 2. Level 2 — Structured Governance Scoring (Review Assist)
An assessment model that scores each extension's architectural profile across five dimensions (0 to 5 points each) declared in its `governance.json`:
- **Irreducibility Depth (0-5):** Does the justification prove the structural impossibility of implementing the feature inside the core or standard metadata structures?
- **Ontological Neutrality (0-5):** Does the extension avoid sneaking covert, non-generic semantics into the language?
- **Provider Abstraction Purity (0-5):** Does the extension compile directly to a neutral intermediate representation (IR), separating API details from compiler logic?
- **Primitive Necessity (0-5):** Does it add genuine, necessary formal expressiveness rather than convenient syntactic sugar?
- **Sunsetability Confidence (0-5):** How cleanly can the extension be amputated without leaving vestigial residues or requiring core modifications?

**Decision Thresholds:**
- **Score < 15:** Automatic rejection (Mechanical Block).
- **Score 15–20:** Mandatory Reviewer Escalation (Requires detailed human oversight and manual sign-off by the core language team).
- **Score > 20:** Normal Review (Standard OSS review queue).

## Consequences
- The language core remains mathematically pristine, provable, and decontaminated.
- The open-source community can scale scientific extensions infinitely without risking core language regression or metric-oriented optimization (Goodhart's Law).
- The transition between mechanical verification and human epistemic review is explicitly separated, avoiding both metric teocracy and manual review fatigue.
