# GFL RFC 002: Integrating OpenMed Privacy Layer

*   **Proposer**: GFL Core Team
*   **Status**: PROPOSED
*   **Created**: 2026-05-02
*   **GFL Version Target**: v2.2.0

## 🎯 Summary
This RFC proposes the formal adoption of `OpenMed/privacy-filter-nemotron` as the reference model for the **GFL Privacy Layer** within the **Observation Interface (GOIS)**.

## 🧬 Scientific Motivation
Clinical observations (Axis 3) are essential for grounding GFL biological models. However, direct ingestion of clinical data poses significant privacy risks. By integrating a specialized clinical de-identification model, we can enable safe, automated processing of real-world medical evidence.

## 📜 Semantic Specification
The Privacy Layer acts as an intermediate filter in the `GOIS.IngestionPipeline`:
1.  **Ingestion**: Receives raw clinical data.
2.  **Filtering**: Executes `privacy-filter-nemotron` to detect and mask PII (Names, IDs, Dates, Locations).
3.  **Anonymization**: Replaces PII with generic placeholders or synthetically consistent alternates.
4.  **Emission**: Emits a `CLEAN_OBSERVATION` to the GFL state.

## 🧱 Backward Compatibility
This is a **MINOR** (additive) change. It introduces a new optional (but recommended) security step for clinical pipelines.

## ⚙️ Implementation Impact
*   **GeneForge**: Will implement a plugin to call the OpenMed privacy API or local model.
*   **MRI**: Will validate that any clinical observation block has a `privacy_cleared: true` metadata flag.

## 🚫 Alternatives Considered
*   **Rule-based filtering**: Rejected due to low recall in unstructured clinical text.
*   **General-purpose LLMs**: Rejected due to high hallucination risk and potential data leakage.

## ⚠️ Unresolved Questions
*   Should the privacy layer be mandatory for ALL phenotype events, or only those from clinical sources?
