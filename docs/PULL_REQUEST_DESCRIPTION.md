# Pull Request: GFL Formalization and Structural Decoupling

## 🎯 Summary
This PR implements the formalization of **GeneForgeLang (GFL)** as the independent, universal source of truth for biological semantics. It establishes a clear structural boundary between the language specification (Legislative/GFL) and the execution runtime (Executive/GeneForge).

## 🚀 Key Changes

### ⚖️ Governance & Constitution
*   **[CONSTITUTION.md](CONSTITUTION.md)**: Establishes the mandatory decoupling between GFL and GeneForge. GFL defines the biological reality; GeneForge executes it.
*   **[TRANSFER_MEMORANDUM.md](TRANSFER_MEMORANDUM.md)**: Formal record of the transfer of conceptual direction to the GFL repository.

### 📜 Formal Specifications (`docs/spec/`)
We have introduced a set of formal specifications to govern the language:
*   **causal_semantics.md**: Rules for valid biological transformations and invariants.
*   **state_space.md**: Formal structure of the multi-layered Biological State Space.
*   **instruction_set.md**: Primitive biological operations and validation logic.
*   **execution_contract.md**: Boundary definition for any GFL-compatible runtime.
*   **versioning_policy.md**: Semantic versioning and community RFC process.

### 🌐 Documentation & Protocol
*   **README.md**: Updated to reflect GFL's role as an open-source universal standard.
*   **PROTOCOL.md**: Restored and adapted to the GFL repository.

## 🧱 Architectural Impact
This PR ensures that:
1.  **GFL defines what is biologically valid.**
2.  **GeneForge (and other runtimes) only execute what GFL defines.**
3.  The system remains scientifically consistent and portable across different implementations.

## ✅ Verification
*   All new markdown files have been validated for structure and internal linking.
*   Changes are pushed to `feature/gfl-formalization-v2` following the NeuroIA protocol.

---
**Branch**: `feature/gfl-formalization-v2`
**Reference**: [NeuroIA Protocol Verified]
