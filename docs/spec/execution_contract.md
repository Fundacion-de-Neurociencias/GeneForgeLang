# GFL Execution Contract (Draft v0.1)

## 1. Principles of Decoupling
GeneForgeLang (GFL) is a platform-agnostic symbolic language. Its execution contract defines the expected behavior of *any* runtime that claims GFL compatibility.

*   **Runtime Independence**: GFL specifications are independent of any specific software implementation (e.g., GeneForge, custom simulators, or laboratory automation systems).
*   **Agnostic Interpretation**: A GFL script must describe "what" biological change happens, while the runtime determines "how" to simulate or execute it within its specific context.

## 2. Interpretation vs. Execution
*   **Interpretation (GFL Core)**: The process of validating the symbolic logic, checking causal consistency, and resolving macros into primitive instructions. This is handled by GFL itself.
*   **Execution (External Runtime)**: The process of mapping GFL instructions to specific actions (e.g., updating a probabilistic model, generating a CRISPR guide, or controlling a liquid handler).

## 3. The Runtime Boundary (GeneForge and Others)
GeneForge is the **reference runtime** for GFL, but it is not the only one.

| Layer | Responsibility | Authority |
| :--- | :--- | :--- |
| **GFL Specification** | Definition of biological world and rules | **GFL Community** |
| **GFL Validator** | Semantic and structural verification | **GFL Core** |
| **GeneForge Runtime** | Inference, clinical reasoning, and simulation | **GeneForge Team** |
| **Third-Party Runtime** | Custom implementation (e.g., benchling, synthace) | **External Developers** |

## 4. Conformance Requirements
Any system claiming GFL-Native status must:
1.  Pass the GFL Standard Conformance Suite.
2.  Respect all "Biological Invariants" defined in the GFL Causal Semantics.
3.  Support the "Biological Instruction Set" without modifying its semantic meaning.

## 5. Extensibility
Runtimes may extend GFL via the **Plugin System**, but these extensions must not break the core language compatibility. If a feature is generally useful, it should be proposed for inclusion in the GFL core specification.
