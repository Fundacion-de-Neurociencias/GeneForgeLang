# GFL Observation Interface Spec (GOIS)

## 1. Introduction
The GFL Observation Interface (GOIS) defines how external empirical evidence (Axis 3) is mapped to the formal biological state (Axis 2) defined in GFL. This interface ensures that GFL remains a pure language while allowing integration with heterogeneous data sources like clinical reports, sensors, and experimental datasets.

## 2. The Evidence Boundary
Observations are **not** biological truth; they are **projections** of a hidden biological state.
*   **Axis 2 (Biological)**: The formal symbolic state defined by GFL.
*   **Axis 3 (Observational)**: The raw data and structured evidence (e.g., OpenMed extractions).

## 3. Observation Types
GOIS defines the following observation primitives:
*   `PHENOTYPE_EVENT`: A structured observation of a clinical or physiological state.
*   `EVIDENCE_NODE`: A link to a raw data source (e.g., a PDF, a FASTQ file, a clinical report).
*   `QUALIFIED_STATEMENT`: A clinical assertion with an associated confidence score and source authority.

## 4. Mapping Protocol (Evidence → State)
Observations are integrated into GFL via **Observation Adapters**:
1.  **Extraction**: Raw data (e.g., clinical text) is processed by external models (e.g., OpenMed NER).
2.  **Structuralization**: Entities are mapped to GFL Biological Entities ($E$).
3.  **Tension Resolution**: If an observation conflicts with a biological invariant, it is recorded as a **Semantic Tension** node, not as a state update.

## 5. Privacy and Sovereignty
All observations passing through GOIS must adhere to the **Privacy Protocol**:
*   **PII Filtering**: Mandatory removal of Personally Identifiable Information before the observation is committed to the GFL state.
*   **Local Processing**: Preference for edge-side observation processing to maintain data sovereignty.

## 6. Role of GOIS in the Ecosystem
*   **GeneForge**: Uses GOIS to feed its inference engine with real-world observations.
*   **OpenMed**: Acts as a primary **Observation Provider** for clinical and biomedical entities.
*   **Conformance Suite**: Uses GOIS to inject adversarial clinical cases for stress-testing.
