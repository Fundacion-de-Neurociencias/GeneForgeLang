# GFL Causal Semantics Specification (Draft v0.1)

## 1. Introduction
This document defines the formal rules for causal transformations within the GeneForgeLang (GFL) ecosystem. GFL is the sole authority for defining how biological state evolves.

## 2. Valid Transformations
A transformation is considered valid in GFL if it satisfies the following criteria:
*   **Symbolic Traceability**: Every change must be representable as a symbolic instruction.
*   **Directionality**: Transformations must follow biological causality (e.g., DNA → RNA → Protein).
*   **Conservation of Identity**: A biological entity must maintain its symbolic identifier throughout a transformation unless explicitly re-characterized.

## 3. Structural Constraints
*   **Ontological Alignment**: Transformations must map to valid biological processes defined in the GFL Ontology.
*   **Non-Resolution Principle**: Conflicts between observational evidence (Axis 3) and molecular state (Axis 2) must be preserved as "Tension" nodes rather than forced to a single value.
*   **Boundary Integrity**: Edits within a cell-type context cannot leak into unrelated cellular contexts without a defined transport/pathway bridge.

## 4. Biological Invariants
GFL runtime must ensure that the following invariants are never violated:
1.  **Genome Integrity**: Base sequences must remain valid according to the IUPAC standard.
2.  **Causal Closure**: No biological effect can exist without a symbolic cause (even if the cause is marked as `UNKNOWN`).
3.  **Hierarchy Preservation**: Modifying a domain (`^d`) must respect the parent protein (`^p`) structure.

## 5. Causal Validity Domains
Valid transformations are scoped by "Validity Domains" (e.g., `CLINICAL_VALIDITY`, `RESEARCH_PROJECTION`). A transformation may be valid in one domain but invalid in another.
