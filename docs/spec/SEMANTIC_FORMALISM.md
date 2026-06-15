# GFL Semantic Formalism: The Mathematical Basis of Biological Truth

## 1. Introduction
To achieve epistemological independence, GeneForgeLang (GFL) must be defined not by its implementation (GeneForge), but by a formal mathematical structure. This document provides the symbolic mapping of GFL to formal logic.

## 2. The Biological State Space (BSS)
The Biological State Space is defined as an algebraic structure $B = (E, R, \Sigma)$ where:
*   $E$: The set of Biological Entities (Genes, Proteins, Cells).
*   $R$: The set of typed Causal Relations ($R \subseteq E \times T \times E$, where $T$ is the set of relation types).
*   $\Sigma$: The set of state-defining predicates (e.g., $EXPRESSED(e), MUTATED(e)$).

## 3. Instruction Semantics
A GFL Instruction $I$ is a state transition function $f_I: B \to B'$.
*   **Consistency Requirement**: A transition is valid if and only if $B'$ does not violate any global invariants $\Lambda$.
*   **Atomic Transformations**: Instructions are atomic; they either complete fully or leave the state unchanged.

## 4. Formal Invariants ($\Lambda$)
Invariants are expressed as logical predicates over the state space $B$.
*   **IUPAC Integrity**: $\forall s \in Sequences, VALID\_IUPAC(s)$.
*   **Causal Closure**: $\forall e \in \Delta E, \exists c \in E: CAUSES(c, e)$.

## 5. Ambiguity Resolution
Structural ambiguity occurs when a GFL script $S$ maps to multiple possible state transitions $\{f_{S,1}, f_{S,2}, \dots, f_{S,n}\}$.
*   **Standard Rule**: A GFL-MRI must detect and reject any $S$ where $n > 1$ unless an explicit arbitration layer is provided.

## 6. Grounding
Every entity $e \in E$ must be uniquely identified by a URI pointing to an external authority (e.g., `https://identifiers.org/hgnc:11998` for TP53). This ensures that the "Truth Space" is anchored in existing biological knowledge.
