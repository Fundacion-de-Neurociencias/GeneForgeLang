# GFL CONSTITUTION: Structural Decoupling and Governance

## 1. The Fundamental Mandate
GeneForgeLang (GFL) is the **sole authority** for defining the symbolic representation of biological reality. This distinction is structural and mandatory, as detailed in the **[Architectural Directive](docs/architecture/ARCHITECTURAL_DIRECTIVE.md)**.

*   **GFL = The Constitution**: Defines the rules, semantics, and state space.
*   **GeneForge = The Executive**: Executes the rules, performs inference, and optimizes the state in practice.
*   **CAL = The Judiciary**: Arbitrates between interpretations and empirical evidence.

## 2. Delineation of Responsibilities

### 🧾 GeneForgeLang (GFL Repository)
The GFL repository is responsible for the **Legislative Authority** of the biological world:
*   **Causal Semantics**: What constitutes a valid biological transformation.
*   **Biological State Space**: Formal structure and canonical biological types.
*   **Instruction Set**: Primitive operations and composition rules.
*   **Formal Validity**: Structural constraints and invariants.
*   **Evolution**: Governance, versioning, and RFC processes for the language.

### 🧬 GeneForge (Runtime Implementation)
GeneForge acts as the **Executive Authority** within the world defined by GFL:
*   **Execution**: Running GFL instructions in a simulated or real-world environment.
*   **Inference**: Causal reasoning and learning from real data.
*   **Arbitration**: Practical application of CAL layers.
*   **Runtime Optimization**: Efficient processing of the GFL state.

## 3. The Structural Boundary
> **GFL defines the rules. GeneForge detects when the rules are insufficient.**

To avoid **Epistemological Collapse**, GeneForge must NEVER:
1.  Define or modify the semantics of the language.
2.  Decide on causal validity rules outside the GFL specification.
3.  Act as the judge of the standard governance.

### 4. Interaction Protocol
1.  **Execution**: GeneForge executes GFL scripts according to the current GFL Specification.
2.  **Detection**: If GeneForge detects a biological case that is not expressible or is inconsistent within GFL, it must NOT modify its internal logic to "fix" the language.
3.  **Feedback Loop**: The GeneForge team must propose a **GFL-RFC** (Request for Comments) following the **[RFC Process](docs/rfc/README.md)**.
4.  **Formalization**: GFL evaluates, versions, and releases the updated specification.
5.  **Synchronization**: GeneForge updates its runtime to support the new GFL version.

## 5. Universal Open Source Commitment
GFL is a universal standard. While GeneForge is its primary reference runtime, GFL must remain open to any third-party implementation. No feature in GFL shall be designed to exclusively benefit GeneForge at the expense of general biological expressiveness.
