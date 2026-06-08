# GFL Policy Feedback Update Layer (PFUL)

## 1. Introduction: The Learning Loop
The PFUL completes the GFL architectural cycle by providing a formal mechanism for self-correction. It ensures that the system doesn't just record its conflicts (ERC) and act on them (RCC), but also **learns** from the outcomes of those actions to refine future decision policies.

## 2. The Feedback Cycle
PFUL operates as a continuous four-stage loop:

1.  **Outcome Observation**: Captures the empirical result of an action taken via an RCC projection.
2.  **Policy Audit**: Compares the result against all branches of the original `IRREDUCIBLE` tension.
3.  **Attribution**: Identifies whether the error was due to a faulty model (GeneForge), biased evidence (OpenMed), or an incomplete formalization (GFL).
4.  **Policy Update**: Adjusts the weights and contextual priorities in CAL and GeneForge for future projections.

## 3. Feedback Primitives

### 📉 3.1 Projection Failure
Occurs when a `LOCAL_COLLAPSE` decision (Path A) leads to an outcome that validates the non-selected branch (Path B).
*   *Action*: Decrease the "Epistemic Trust" weight for the source that advocated for Path A in that specific context.

### 📈 3.2 Policy Reinforcement
Occurs when the selected projection leads to the predicted biological state.
*   *Action*: Increase the "Operational Confidence" for the specific context-filter used in the collapse.

### 🧪 3.3 Structural Divergence
Occurs when the outcome contradicts **all** branches of the original tension.
*   *Action*: Mandatory trigger for a **GFL-RFC**. This indicates a "Blind Spot" in the language specification itself.

## 4. Adjustment of the ERC/RCC Hierarchy
Learning through PFUL results in updates to:
*   **CAL Weights**: Real-time adjustment of which observation providers are more reliable for specific biological domains.
*   **GeneForge Heuristics**: Fine-tuning of the "Decision Projection" logic (e.g., "In liver cells, trust Axis 1 evidence over Axis 2 simulation").

## 5. Learning Traceability
Every policy update must be registered as a **`LEARNING_EVENT`**:
*   `trigger_collapse_id`: Link to the original RCC decision.
*   `outcome_evidence_id`: Link to the Axis 3/OpenMed observation of the result.
*   `delta`: The specific change made to the arbitration policy (e.g., `Weight +0.05 for OpenMed-NER-01`).
*   `rationale`: Scientific explanation of why the update was necessary.

## 6. Standard Compliance for Learning Systems
A GFL-compliant learning system must:
*   Maintain an immutable log of all learning events.
*   Allow "Policy Rollbacks" if an update leads to systematic semantic degradation.
*   Report "High-Divergence Zones" where the system's learning loop is failing to achieve consistency.
