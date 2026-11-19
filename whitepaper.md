# GeneForgeLang (GFL): A Symbolic Language for Rational Bio-Design

> **Notice.** Research software. Not a medical device, not for clinical use, and not legal or regulatory advice.

> **Status of this document.** This whitepaper was published on Zenodo on 2025-05-23 (DOI below) and describes the original vision for GFL. This repository copy has been corrected: claims of clinical use were removed, and every notation or interoperability feature that the current parser does not implement is marked "proposed, not implemented". The implemented language is the YAML-based syntax documented in [docs/index.md](docs/index.md).

## Executive Summary

GeneForgeLang (GFL) is a symbolic, cross-modality language designed to bridge molecular biology, genome editing research and AI-driven reasoning. It aims at a compact, structured and interpretable representation of DNA, RNA and protein elements, from raw sequences to regulatory logic, epigenetic states and editing interventions. GFL addresses the lack of a unified symbolic system for encoding, reasoning about and simulating molecular edits in research and synthetic-biology contexts.

## 1. Problem Statement

Modern bioinformatics pipelines are fragmented:

* DNA sequences are stored in flat sequence and annotation formats that lack functional logic.
* Genome editing tools (e.g., CRISPR, base editors) require ad hoc protocols.
* Experimental data are not symbolically formalized.
* There's no standard language to bridge **editing logic**, **regulatory design** and **intervention modeling**.

## 2. GeneForgeLang: Core Capabilities

### 🧠 Logical Encoding of Biology (proposed, not implemented)

* Causal logic: `if A then B`, `MOT(x) = degradation`
* Temporal modeling: `TIME(n): EDIT(...)`
* Conditional hypotheses: `HYPOTHESIS: if MUT(...) → EFFECT(...)`

The implemented parser expresses rules, hypotheses and timelines as YAML blocks (`rules`, `hypothesis`, `timeline`); see the feature documentation.

### 🧬 Multimodal Symbolism (proposed, not implemented)

* `~d`, `:r`, `^p`, `*p`: layers for DNA, RNA, protein, complexes
* Modules: motifs, domains, mutations, edits, metadata
* Pathways: `PATHWAY: ARG → CPS1 → OTC`

### ⚙️ AI Compatibility and Interoperability (proposed, not implemented)

* Promptable syntax for LLMs and generative protein models
* Translation to and from SBOL, FASTA, GenBank and ProForma

## 3. Use Cases

### 3.1 Gene Therapy Research

* Design of base editing plans for CPS1, OTC and CFTR mutations
* Simulation of multiple edit strategies
* Evaluation of delivery systems and time-course outcomes

### 3.2 Synthetic Regulatory Engineering

* ARE/NFE2L2 synthetic enhancers via transcription factor logic
* Modular macros: reusable regulatory elements (proposed, not implemented)

### 3.3 Interpretable Intervention Plans

* Symbolic, human-readable encoding of CRISPR interventions in research designs
* Interpretable molecular intervention plans for review by domain experts

## 4. Implementation Roadmap

### Phase 1 – Language Core

* YAML-based grammar, parser, semantic validator and test suite (implemented)
* Integration with generative AI models (in progress)

### Phase 2 – Tooling

* Web-based editor
* YAML/JSON export of designs
* Integration with sequence generators and validators

### Phase 3 – Ecosystem Interoperability (proposed, not implemented)

* SBOL/GenBank/FASTA exporters
* Plugins for design tools or a CLI bridge

## 5. Comparison with Existing Standards (proposed, not implemented)

The GFL column describes design goals of the proposed notation, not features of the current release.

| Feature                 | GFL (proposed)       | SBOL             | GenBank         | ProForma        |
| ----------------------- | -------------------- | ---------------- | --------------- | --------------- |
| Symbolic logic          | Proposed             | ❌ No             | ❌ No            | ❌ No            |
| Cross-modality          | Proposed: DNA/RNA/protein | ✅ DNA parts | ❌ Sequence only | ✅ Proteins only |
| AI-readability          | Proposed             | ⚠️ Partial       | ❌ No            | ✅ Yes           |
| Macros and reuse        | Proposed             | ⚠️ Template only | ❌ No            | ❌ No            |
| Temporal representation | Proposed: TIME(x)    | ❌ No             | ❌ No            | ❌ No            |

## 6. Call to Action

GFL is open-source, modular and designed to evolve with community input. We are seeking collaborators to:

* Test GFL on real research workflows and report gaps
* Build plugins for design tools (e.g. Benchling, CRISPResso)
* Contribute to libraries of reusable workflow blocks

## 7. License and Acknowledgements

Developed by Fundación de Neurociencias
Lead: Dr. Manuel Menéndez González
License: MIT
Website: [https://github.com/Fundacion-de-Neurociencias/GeneForgeLang](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)
📄 DOI

The original version of this whitepaper is published on [Zenodo](https://doi.org/10.5281/zenodo.15493559) and citable as:

Menéndez González, M. (2025). *GeneForgeLang: A Symbolic Language for Rational Bio-Design and Clinical Genomic Engineering*. Fundación de Neurociencias. https://doi.org/10.5281/zenodo.15493559
