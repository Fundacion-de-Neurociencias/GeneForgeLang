---
title: 'GeneForgeLang: A Symbolic Language for Genetic Reasoning, Editing, and Simulation'
tags:
  - synthetic biology
  - gene editing
  - symbolic language
  - bioinformatics
  - AI-driven design
authors:
  - name: Manuel Menéndez González
    orcid: 0000-0002-5218-0774
    affiliation: "1"
affiliations:
 - index: 1
   name: Universidad de Oviedo, Spain
   ror: 006gksa02
date: 24 May 2025
bibliography: paper.bib
---

# Summary

**GeneForgeLang (GFL)** is a symbolic language designed to represent, analyze, and simulate biomolecular processes with unprecedented clarity, granularity, and logical reasoning. GFL allows scientists and AI models to interact through a shared grammar that can describe genetic modifications, transcriptional regulation, protein folding, therapeutic edits, and pathway simulation.

Originally conceived to address the limitations of existing descriptive formats (e.g., FASTA, SBOL, ProForma) and programming languages used in synthetic biology, GFL enables representation of **DNA, RNA, and protein constructs**, **mutation provenance**, **therapeutic delivery**, and **feedback systems**. Its formal grammar and parser support AI-enhanced interpretation, bidirectional translation from scientific literature, and automatic simulation of molecular logic.

Although it is currently used in the context of precision medicine and neurogenetics, GFL is fully extensible to domains like **crop engineering**, **antibiotic resistance**, **pandemic vaccine design**, and **synthetic metabolic pathways**.

# Statement of need

With the rise of CRISPR, base editors, and programmable RNA therapies, biomedical science has entered an era of **complex multilayered interventions**. Yet, most researchers still describe their designs through prose, diagrams, or Python scripts—lacking a **semantic, symbolic, and machine-interpretable layer**.

GFL solves this gap by providing a **compact, modular, and logically expressive language** capable of:

- Describing point mutations and large edits with provenance and intent
- Representing epigenetic states and post-translational modifications
- Encoding delivery routes, dosages, and tissue-specific expression
- Enabling feedback loops, probabilistic reasoning, and pathway logic
- Being parsed, validated, and simulated by LLMs and bioinformatics pipelines

## Related work

GFL builds upon conceptual and technical precedents:

- SBOL [@Galdzicki2014] provides semantic interoperability but lacks reasoning syntax
- GenoCAD [@GenoCAD] enables modular design but not dynamic or clinical modeling
- ProForma [@LeDuc2022] formalizes proteoforms but is protein-only and lacks logic
- Eugene [@Eugene2009] focuses on device constraints, not biological complexity

GFL merges these paradigms into a **unified language for describing biological reality**, particularly suited for AI interaction, therapeutic prototyping, and knowledge extraction.

# Software description

GFL includes the following components:

## Grammar (`grammar.md`)

A formal specification of the language, defining symbols for:

- Structural abstraction: linear, secondary, tertiary, quaternary (`~`, `:`, `^`, `*`)
- Molecular types: DNA, RNA, protein (`d`, `r`, `p`)
- Logic: conditionals, hypotheses, effects, simulation
- Entities: mutations, edits, delivery vectors, omics pathways

## Syntax (`syntax.md`)

An EBNF-based definition of GFL syntax, ensuring:

- Valid sequence of symbolic elements
- Metadata handling via `{}` blocks
- Nested expressions for control logic
- Compatibility with Markdown and plaintext editors

## Parser (`parser.py`)

A Python script that:

- Validates GFL statements
- Parses into structured JSON
- Detects semantic errors (e.g., transcription of a protein)
- Supports conversion to SBOL, FASTA, ProForma

## GitHub repository

All components and examples are hosted under MIT license at:
👉 [https://github.com/Fundacion-de-Neurociencias/GeneForgeLang](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)

# Use cases and examples

## 1. Prime Editing for CFTR F508del (Cystic Fibrosis)

```gfl
~d:CFTR[MUT:SOM:DEL:F508@codon508]
EDIT:Prime(INS:TTC@exon10){pegRNA=CFTR_PE, target=CFTR}
DELIV(mRNA+LNP@IV){target_cells=Pulmonary_Epithelium}
TIME(0d):DELIV(...)
TIME(7d):EFFECT(↑CFTR_protein@apical_membrane)
```

## 2. miR-21-mediated Drug Resistance in Breast Cancer

```gfl
PATHWAY: ↑miR-21 → INHIBIT(miR-21 → ~r:PTEN_mRNA) → ↓^p:PTEN → ↑^p:AKT
EDIT:Anti-miRNA(miR-21_ASO){delivery=intratumoral}
SIMULATE: {Drug=Doxorubicin, AntagomiR} OUTCOME: ↑Apoptosis
```

## 3. CAR-T Design for HER2+ Tumors

```gfl
~d:CAR_HER2 - ^p:Dom(scFv_anti-HER2) - ^p:Dom(CD28_costim) - ^p:Dom(CD3zeta)
TRANSLATE(~r:CAR_HER2_mRNA → ^p:CAR_HER2_protein){cell=T_cell}
INTERACT(CAR_HER2 / HER2){via=immunological_synapse}
EFFECT(↑Tumor_Lysis, ↑T_cell_Persistence)
```

# Acknowledgements

GFL is promoted by **Fundación de Neurociencias**. Special thanks to the scientific community for contributing edge cases, ontological structures, and design critiques.

# References
