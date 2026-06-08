# GFL Epistemic Resolution Contract (ERC)

## 1. Introduction: The Principle of Non-Resolution
The ERC is not a "decision engine" that forces coherence; it is a **formal contract for conflict representation**. Its primary goal is to ensure that the system never "silently decides" between incompatible sources of truth. 

**Core Mandate**: If a conflict cannot be deterministically resolved via the priority hierarchy, it must be **preserved as a first-class citizen** in the state space.

## 2. Epistemic States
Every collision between GFL (Language), GeneForge (Model), and Observation (Evidence) must result in one of three states:

### 🟢 2.1 RESOLVABLE (Priority Protocol)
Conflicts resolved by the fixed hierarchy of authority:
1.  **GFL Semantic Invariants** (Legislative Truth)
2.  **GeneForge Core** (Executive Simulation)
3.  **Observation Providers** (Empirical Evidence)
*   *Action*: The lower-priority source is superseded, and the resolution is logged.

### 🟡 2.2 CONTEXTUAL (Scoped Priority)
Conflicts where priority depends on specific metadata (e.g., Axis 1 clinical data).
*   *Action*: The system applies context-specific rules defined in the `Grounding` layer.

### 🔴 2.3 IRREDUCIBLE (Preserved Tension)
Conflicts where neither source can be discarded (e.g., a formal GFL invariant contradicts a high-rigor OpenMed observation).
*   **MANDATORY RULE**: The system **PROHIBITS** silent resolution.
*   *Action*: Create a **`Non-Resolved Tension`** node. 
*   *Result*: The GFL state remains in a superposition of conflicting truths, forcing downstream consumers to acknowledge and handle the ambiguity.

## 3. The Role of CAL (Causal Arbitration Layer)
Under the ERC, CAL is stripped of its "universal judge" role. It becomes a **Conflict Registrar**:
1.  **Detection**: Identifies collisions between sources.
2.  **Classification**: Assigns the collision to one of the 3 Epistemic States.
3.  **Registration**: Logs the conflict with its full provenance.
4.  **Preservation**: Ensures that `IRREDUCIBLE` tensions are not pruned during optimization or inference.

## 4. Conflict Traceability
Every conflict registration must contain:
*   `collision_id`: Unique identifier.
*   `state`: [RESOLVABLE | CONTEXTUAL | IRREDUCIBLE].
*   `sources`: List of conflicting evidence/formalisms.
*   `resolution_path`: The ERC rule applied (or `NONE` for Irreducible).
*   `version`: Conflicts are versioned to track the evolution of the tension.

## 5. Standard Compliance
A GFL-compliant system must:
*   Identify all semantic collisions.
*   Reject any "silent decision" that bypasses the ERC hierarchy.
*   Expose `IRREDUCIBLE` tensions to the user/consumer as a formal part of the biological state.
