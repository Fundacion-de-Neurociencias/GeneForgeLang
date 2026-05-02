# GFL Epistemic Resolution Contract (ERC)

## 1. Introduction
The Epistemic Resolution Contract (ERC) establishes the formal hierarchy of authority and the deterministic rules for resolving conflicts between different sources of truth within the GFL ecosystem. It prevents "semantic leakage" and ensures that every resolution is traceable and scientifically justifiable.

## 2. Hierarchy of Epistemic Precedence

| Priority | Source | Role | Authority Type |
| :--- | :--- | :--- | :--- |
| **1 (Highest)** | **GFL Specifications** | Semantic Invariants | Legislative (Biological Truth Space) |
| **2** | **GeneForge Core** | Causal Inference | Executive (Simulated/Estimated Reality) |
| **3 (Lowest)** | **Observation Providers** | Empirical Evidence | Observational (Noisy Projections) |

## 3. Conflict Resolution Logic

### 3.1 GFL vs. Observation (OpenMed)
*   **Rule**: If an observation contradicts a GFL Semantic Invariant, the observation is **REJECTED** as "Invalid Projection".
*   **Action**: Record as `INVALID_OBSERVATION` with the specific invariant ID violated.
*   **Exception**: If the observation is high-rigor (Axis 1), it may trigger a **GFL-RFC** to update the language.

### 3.2 GeneForge (Model) vs. Observation (OpenMed)
*   **Rule**: If the causal model contradicts empirical evidence, the conflict is **PRESERVED**.
*   **Action**: Mark as **"Biological Tension"** node. This indicates a potential gap in the model or a specific pathology not captured by the general rule.
*   **Learning**: These tension nodes are the primary fuel for structural learning in GeneForge.

### 3.3 GFL vs. GeneForge (Model)
*   **Rule**: The model must never violate GFL Invariants.
*   **Action**: If a simulated state violates an invariant, the simulation is halted as `SEQC_ERROR` (Semantic Error).
*   **Resolution**: Requires a change in the model's parameters or a GFL-RFC if the invariant is found to be too restrictive for real-world biology.

## 4. Formalization of Uncertainty: "Irreducible Tension"
The system must not force coherence where it doesn't exist.
*   A conflict is **IRREDUCIBLE** if neither the model nor the evidence can be discarded with absolute certainty.
*   **Representation**: The system emits a `TENSION_STATE` with multiple probability distributions, forcing the consumer to acknowledge the ambiguity.

## 5. Override Conditions
An override can only be performed via an **Explicit Epistemic Lock**:
*   `SEMANTIC_LOCK`: Forces the model to ignore noisy observations.
*   `EVIDENCE_LOCK`: Forces the system to accept an observation as truth (e.g., in Axis 1 clinical cases), marking the model as "INCONSISTENT_WITH_CASE".

## 6. Traceability and Falsification
Every resolution decision must be logged with:
1.  **Conflict ID**: Unique identifier for the collision.
2.  **ERC Rule**: The specific rule applied (e.g., `ERC-3.1`).
3.  **Residual Tension**: The remaining uncertainty after resolution.
4.  **Falsification Trace**: What evidence would be needed to reverse this decision.
