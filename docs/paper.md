---
title: 'GeneForgeLang: A Domain-Specific Language for Genomic Workflows with AI-Powered Analysis'
tags:
  - synthetic biology
  - gene editing
  - domain-specific language
  - bioinformatics
  - AI-driven design
  - CRISPR
authors:
  - name: Manuel Menéndez González
    orcid: 0000-0002-5218-0774
    affiliation: "1"
affiliations:
 - index: 1
   name: Universidad de Oviedo, Spain
   ror: 006gksa02
date: 19 September 2025
bibliography: paper.bib
---

# Summary

**GeneForgeLang (GFL)** is a domain-specific language designed to represent, analyze, and simulate genomic workflows with unprecedented clarity, granularity, and AI-powered analysis capabilities. GFL allows scientists and AI models to interact through a shared grammar that can describe genetic modifications, CRISPR guide RNA design, therapeutic edits, and pathway optimization.

Originally conceived to address the limitations of existing descriptive formats and programming languages used in synthetic biology, GFL enables representation of **CRISPR gRNA designs**, **gene editing workflows**, **protein engineering processes**, and **experimental optimization strategies**. Its formal grammar and parser support AI-enhanced interpretation, bidirectional translation from scientific literature, and automatic simulation of molecular logic.

GFL is particularly well-suited for applications in **precision medicine**, **CRISPR optimization**, **protein design**, and **synthetic biology workflows**.

# Statement of need

With the rise of CRISPR technologies, base editors, and programmable RNA therapies, biomedical science has entered an era of **complex multilayered interventions**. Yet, most researchers still describe their designs through prose, diagrams, or general-purpose programming languages—lacking a **semantic, symbolic, and machine-interpretable layer** specifically designed for genomic workflows.

GFL solves this gap by providing a **compact, modular, and logically expressive language** capable of:

- Describing CRISPR gRNA designs with efficiency and specificity predictions
- Representing gene editing workflows with provenance and intent
- Encoding experimental optimization strategies and parameter spaces
- Enabling feedback loops, probabilistic reasoning, and pathway logic
- Being parsed, validated, and executed by AI models and bioinformatics pipelines

## Related work

GFL builds upon conceptual and technical precedents:

- SBOL [@Galdzicki2014] provides semantic interoperability but lacks reasoning syntax
- GenoCAD [@Czar2009] enables modular design but not dynamic or clinical modeling
- ProForma [@LeDuc2022] formalizes proteoforms but is protein-only and lacks logic
- Eugene [@Bilitchenko2011] focuses on device constraints, not biological complexity

GFL merges these paradigms into a **unified language for describing genomic workflows**, particularly suited for AI interaction, therapeutic prototyping, and knowledge extraction.

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

## Plugin System

GFL features an advanced plugin system that allows integration of specialized tools for:

- **CRISPR gRNA design and evaluation**: On-target efficiency prediction using DeepHF-based models, off-target risk assessment using CFD-based algorithms
- **Protein engineering**: Sequence generation using VAE and transformer-based models
- **Experimental optimization**: Bayesian optimization and active learning strategies
- **Pathway simulation**: Computational modeling of biological pathways

The plugin system implements a robust registry with automatic discovery, dependency management, and lifecycle hooks. Plugins can be registered via entry points or direct registration, ensuring seamless integration of third-party tools.

## Execution Engine

GFL includes a powerful execution engine that orchestrates complex genomic workflows by dispatching to appropriate plugins based on workflow block types and configurations. The engine supports:

- **Design blocks**: Generation of biological entities (proteins, DNA, RNA, small molecules) using specialized AI/ML models
- **Optimize blocks**: Intelligent experimental design using advanced optimization algorithms
- **Analyze blocks**: Integration of analysis tools for evaluating experimental results

## API and CLI

GFL provides both a comprehensive Python API and command-line interface for:

- Parsing and validating GFL workflows
- Executing complex genomic workflows
- Managing plugins and dependencies
- Batch processing of multiple workflows

## GitHub repository

All components and examples are hosted under MIT license at:
👉 [https://github.com/Fundacion-de-Neurociencias/GeneForgeLang](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang)

# Use cases and examples

## 1. CRISPR gRNA Optimization for TP53 Gene Editing

```gfl
# Optimized CRISPR gRNA design for TP53 gene editing
guided_discovery:

  # Generate candidate gRNAs
  design_params:
    design_type: "combinatorial_generation"
    combinatorial_generation:
      target_gene: "TP53"
      target_gene_id: "ENSG00000141510"
      reference_genome: "GRCh38"
      pam_sequence: "NGG"
      candidates_per_cycle: 1000
    output: generated_grna_candidates

  # Active learning to select the best candidates
  active_learning_params:
    strategy: "active_learning"
    active_learning:
      acquisition_function: "multi_objective_expected_improvement"
      experiments_per_cycle: 50
    surrogate_model: "RandomForestRegressor"

  # Multi-objective optimization
  objective:
    maximize: "on_target_score"   # Predicted by DeepHF-based plugin
    minimize: "off_target_risk"   # Predicted by CFD-based plugin

  # Stopping criteria
  budget:
    max_cycles: 20
    convergence_threshold: 0.005

  # Evaluation using integrated plugins
  run:
    analyze:
      tool: "gfl-crispr-evaluator" # Orchestrates on-target and off-target scorers
      input: generated_grna_candidates
      output: evaluated_grna_scores
      contract:
        inputs:
          generated_grna_candidates:
            type: "GRNA_Sequence_List"
        outputs:
          evaluated_grna_scores:
            type: "GRNA_Evaluation_Table"

  # Final output
  output: top_tp53_grnas
```

## 2. Protein Sequence Design using AI Models

```gfl
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
    minimize: aggregation_propensity
  constraints:
    - length(50, 200)
    - gc_content(0.4, 0.6)
  count: 10
  output: designed_proteins
```

## 3. Experimental Optimization for CRISPR Efficiency

```gfl
optimize:
  search_space:
    temperature: range(25, 42)
    guide_concentration: range(10, 100)
  strategy:
    name: BayesianOptimization
  objective:
    maximize: efficiency
  budget:
    max_experiments: 20
  run:
    experiment:
      tool: CRISPR_cas9
      params:
        temp: ${temperature}
        conc: ${guide_concentration}
```

# Acknowledgements

GFL is promoted by **Fundación de Neurociencias**. Special thanks to the scientific community for contributing edge cases, ontological structures, and design critiques. We also thank the reviewers from the Journal of Open Source Software for their valuable feedback that significantly improved the quality and scientific accuracy of this work.

# References
