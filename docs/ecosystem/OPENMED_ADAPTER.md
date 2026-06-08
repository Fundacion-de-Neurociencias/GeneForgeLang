# GFL Ecosystem: OpenMed Adapter Spec

## 1. Role of OpenMed
OpenMed serves as an external **Observation Provider** for the GFL ecosystem. It provides the statistical and clinical context necessary to ground GFL biological models in real-world evidence.

## 2. Interface Points

### 🧠 2.1 Entity Extraction (NER)
OpenMed models translate unstructured clinical text into structured GFL entities.
*   **Reference Model**: `OpenMed/openmed-clinical-ner` (Cancer, Genetics, Oncology).
*   **Input**: Clinical reports, discharge summaries.
*   **Output**: `PHENOTYPE_EVENT` nodes mapped to Axis 2 identifiers.

### 🛡️ 2.2 Privacy Layer
OpenMed's de-identification models act as a gatekeeper for GOIS.
*   **Reference Model**: `OpenMed/privacy-filter-nemotron`.
*   **Function**: Automated PII filtering of clinical observations.
*   **Compliance**: GDPR/HIPAA-ready pipelines.

### 🧪 2.3 Adversarial Data Injection
OpenMed's synthetic medical datasets are used to stress-test the GFL formalism.
*   **Datasets**: `OpenMed/SynthVision` (VQA), `OpenMed/Medical-Reasoning-SFT-Mega`.
*   **Usage**: The **GFL Conformance Suite** uses these datasets to generate complex biological hypotheses.

## 3. Implementation Boundary
> **OpenMed is an Observer, GFL is the Ground Truth.**

*   **No Semantic Authority**: OpenMed cannot define new biological invariants or instructions.
*   **Observation-Only**: OpenMed data is always treated as `OBSERVATION` type, which can be refuted by higher-rigor biological evidence (Axis 2).

## 4. Technical Mapping
| OpenMed Component | GFL Integration Point |
| :--- | :--- |
| **NER (Biomedical)** | `EntityRegistry` mapping |
| **Privacy Filter** | `GOIS.IngestionPipeline` |
| **Synthetic QA** | `ConformanceSuite.AdversarialTests` |
| **Reasoning Datasets** | `SemanticValidator.ConsistencyPressure` |
