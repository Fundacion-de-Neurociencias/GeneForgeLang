# GFL Biological State Space (Draft v0.1)

## 1. Structure of the GFL State
The GFL Biological State is a multi-layered symbolic graph representing the current understanding of a biological system.

### Layers:
*   **Layer D (DNA)**: Symbolic representation of genomic sequence, modifications, and structural variants.
*   **Layer R (RNA)**: Transcriptional state, splicing variants, and expression levels.
*   **Layer P (Protein)**: Proteomic state, post-translational modifications, and protein-protein interactions.
*   **Layer C (Cellular)**: Contextual metadata (cell type, organelle, environment).

## 2. Canonical Biological Types
GFL defines the following primitive types:
*   `GENE`: A functional unit of heredity.
*   `TRANSCRIPT`: An RNA molecule.
*   `POLYPEPTIDE`: A protein sequence.
*   `MUTATION`: A deviation from a reference state.
*   `EDIT`: A planned or executed modification.
*   `PATHWAY`: A sequence of causal interactions.

## 3. Allowed Causal Relations
Relations in the state space must be explicitly typed:
*   `REGULATES(A, B)`: A controls the expression or activity of B.
*   `INTERACTS(A, B)`: Physical or functional binding.
*   `DERIVES_FROM(A, B)`: A is a product of B (e.g., RNA derives from DNA).
*   `CAUSES(A, B)`: Strong causal link between state A and event B.

## 4. State Transitions
The state space is immutable; every "change" results in a new state version indexed by a `TRANSITION_VECTOR`. This allows for backtracking and counterfactual reasoning (e.g., "what if the edit failed?").
