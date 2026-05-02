# GFL Resolution Consumption Contract (RCC)

## 1. Introduction: From Philosophy to Operation
The RCC defines the rules for consuming and "collapsing" the `IRREDUCIBLE` tensions preserved by the ERC. It acknowledges that while GFL maintains structural ambiguity for scientific rigor, downstream systems (e.g., GeneForge, Clinical Dashboards) often require a single path to act.

## 2. The Principle of Decision Projection
Downstream systems do not "resolve" a GFL tension; they **project** a decision based on a specific operational context.
*   **The State**: Remains `IRREDUCIBLE` and ambiguous in the core GFL graph.
*   **The Projection**: A temporary, context-bound "collapse" of the state for a specific action (e.g., "Run Simulation Path A").

## 3. Consumption Categories

### 🧪 3.1 Research/Simulation Consumption (Axis 2)
*   **Rule**: Mandatory preservation of tension.
*   **Requirement**: The system must simulate **all** branches of the irreducible tension.
*   **Output**: Multi-modal probability distributions.

### ⚕️ 3.2 Clinical/Decision Consumption (Axis 1 & 3)
*   **Rule**: Permitted context-bound collapse.
*   **Requirement**: If an action is required (e.g., therapy recommendation), the system may select the highest-confidence branch.
*   **Audit**: The decision must be explicitly marked as a `LOCAL_COLLAPSE` and linked to the source `TENSION_NODE`.

## 4. Rules of Collapse (The "Non-Violation" Clause)
A downstream system may only collapse an irreducible tension if:
1.  **Safety First**: An immediate action is required for system/patient safety.
2.  **Contextual Locking**: The consumer specifies a `CONTEXT_FILTER` (e.g., "Assume Invariant X is dominant for this specific query").
3.  **No Back-Propagation**: The local decision **MUST NOT** modify the underlying GFL state. The tension remains open for all other consumers.

## 5. Traceability of the Collapse
Every consumed decision must register a `COLLAPSE_LOG`:
*   `source_tension_id`: Link to the irreducible ERC node.
*   `consumer_id`: The system making the decision (e.g., `GeneForge-Engine-01`).
*   `rationale`: Why the specific branch was chosen (e.g., "Max Likelihood", "Clinical Safety").
*   `epistemic_cost`: A metric of how much biological detail was lost in the collapse.

## 6. Standard Compliance for Consumers
A GFL-compliant consumer must:
*   Declare itself as a "Tension-Aware" or "Tension-Collapsing" system.
*   Never treat a `LOCAL_COLLAPSE` as a "Biological Truth".
*   Provide a way for the end-user to "unfold" the collapse and see the underlying irreducible tension.
