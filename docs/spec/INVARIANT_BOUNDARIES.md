# GFL Invariant Boundary Definition (IBD)

## 1. Introduction: The Limits of Adaptation
To maintain scientific rigor and prevent "post-hoc over-adjustment," GFL defines a strict boundary between its immutable formal core and its adaptive learning layers (PFUL). This ensures that learning improves performance without eroding the fundamental truth space.

## 2. The Immutable Core (Immutable)
The following components are **PROTECTED** and cannot be modified by any internal learning process or PFUL event. Changes to these items require a formal **GFL-RFC** and a new version release.

*   **GFL Constitution**: The fundamental mandate of structural decoupling.
*   **Semantic Invariants (P1)**: The core biological rules (e.g., IUPAC integrity, central dogma constraints).
*   **ERC Structural Rules**: The mandate of Non-Resolution for irreducible conflicts.
*   **Instruction Set**: The definition of primitive biological operations.

## 3. The Learning Sandbox (Mutable)
The PFUL layer is restricted to modifying only the following components. These are the "Operational Heuristics" of the system.

*   **CAL Epistemic Weights**: The trust scores assigned to various observation providers.
*   **RCC Decision Policies**: The heuristics used to select a branch for local decision projection.
*   **GeneForge Inference Parameters**: Probabilistic weights and confidence thresholds.
*   **Contextual Priority Rules**: The mapping of specific metadata to priority shifts.

## 4. Boundary Protection Rules
*   **No Circular Learning**: PFUL cannot justify a violation of an Immutable Invariant by claiming it as "learned truth."
*   **Invariant Override Prohibition**: If a learned policy contradicts an Immutable Invariant, the policy is **VOID**.
*   **Falsification Anchor**: Immutable Invariants serve as the ultimate anchors for falsification. If evidence consistently contradicts an invariant, the system must trigger an external `RFC`, never an internal `PFUL_UPDATE`.

## 5. Audit and Compliance
A GFL-compliant system must:
*   Enforce hardware-level or software-level read-only protection for the Immutable Core.
*   Provide a `BOUNDARY_AUDIT` report showing all PFUL modifications and verifying they stay within the Learning Sandbox.
*   Flag any attempt to "learn away" a foundational biological rule.
