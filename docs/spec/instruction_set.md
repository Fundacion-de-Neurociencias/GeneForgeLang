# GFL Biological Instruction Set (Draft v0.1)

## 1. Core Instructions
Instructions are the primitive operations that modify the Biological State Space.

### Modification Primitives:
*   `SUBSTITUTE(ref, alt, pos)`: Change a base or residue.
*   `INSERT(seq, pos)`: Add a sequence at a position.
*   `DELETE(pos, len)`: Remove a sequence.
*   `INVERT(pos, len)`: Reverse a sequence segment.

### Logic Primitives:
*   `IF(condition) THEN { instructions }`: Conditional execution based on state.
*   `WHEN(event) TRIGGER { instructions }`: Event-driven transformations.
*   `CONSTRAINT(expression)`: Enforce a biological invariant.

## 2. Instruction Composition
Instructions can be composed into **Macros** and **Protocols**:
*   `MACRO`: A reusable set of instructions (e.g., `CRISPR_KO`).
*   `PROTOCOL`: A sequence of instructions with temporal checkpoints (`TIME(n)`).

## 3. Validation Rules
Before an instruction set is committed, it must pass the **GFL Semantic Validator**:
1.  **Syntactic Check**: Grammar and type correctness.
2.  **Causal Check**: Does the instruction violate any "Allowed Causal Relations"?
3.  **Feasibility Check**: Is the instruction physically possible within the current `Cellular` context?

## 4. Execution Atomicity
Instruction blocks within a `TRANSACTION` boundary must succeed or fail as a single unit, preventing inconsistent biological states.
