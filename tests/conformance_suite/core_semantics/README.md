# GFL Core Semantics Conformance Suite

## 🎯 Purpose
This suite validates that GeneForgeLang (GFL) functions as a robust, scientifically falsifiable language. Unlike feature tests, these tests focus on the **underlying symbolic logic** and **biological consistency** of the language, regardless of which runtime (e.g., GeneForge) is executing it.

## 🧪 Test Categories

### 1. 🛡️ Invariants (`invariants/`)
Validates that GFL preserves fundamental biological rules.
*   **Genome Integrity**: Sequencing and base validity (IUPAC).
*   **Causal Closure**: No effect without a symbolic cause.
*   **Hierarchy Consistency**: Sub-entities must respect parent structure.

### 2. 🧩 Ambiguity Detection (`ambiguity/`)
Ensures GFL detects when a script has multiple possible biological interpretations.
*   **Coordinate Ambiguity**: Operations without explicit reference systems.
*   **Relational Conflict**: Conflicting causal links that aren't marked as "Tension".

### 3. 👹 Adversarial Robustness (`adversarial/`)
Validates that GFL rejects syntactically valid but semantically impossible constructs.
*   **The "Valid Syntax, Invalid Logic" test**: Correct GFL grammar but violates biological truth.
*   **Resource Violation**: Operations that require physically impossible states.

### 4. 🧬 Runtime Independence (`runtime_independence/`)
Ensures GFL remains decoupled from any specific implementation.
*   **No Runtime Leakage**: GFL must not contain blocks that only make sense to GeneForge.
*   **Deterministic Interpretation**: Different runtimes must reach the same semantic conclusion.

## 🚀 Usage
These tests should be executed by the **GFL Semantic Validator**. A passing test means the validator correctly identified the invariant violation, ambiguity, or invalid logic.
