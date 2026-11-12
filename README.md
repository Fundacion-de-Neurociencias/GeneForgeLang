# 🧬 GFL v2.0 Beta

> **The Symbolic Language for Biological Reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0--beta-blue.svg)](.)
[![PyPI](https://img.shields.io/pypi/v/geneforgelang.svg)](https://pypi.org/project/geneforgelang/)

## **GFL v2.0 Beta - Multi-Omic Reasoning Language**

**Open-source domain-specific language for computational biology** that integrates multi-omic data with spatial genomic reasoning for biological discovery and design.

## What is GFL v2.0?

GFL v2.0 is a **next-generation domain-specific language** for computational biology that enables researchers to reason across multiple omics layers while maintaining spatial genomic context. Building on declarative workflow capabilities, v2.0 introduces comprehensive multi-omic integration, spatial genomic reasoning, and guided discovery frameworks.

> ⚡ **Fundamental Bio-Thermodynamic Pillar**:
> *"Metabolism is the global thermodynamic tax that the organism pays for its local order."*
> In GFL, metabolic cost and global entropic dissipation are first-order constraints against any local entropy reduction or biological order synthesis.

## 🚀 **New in v2.0 - Multi-Omic Capabilities**

### **Multi-Omic Integration**

- **🧬 Transcripts Block**: Define transcript structures with exon annotations
- **🔬 Proteins Block**: Annotate proteins with functional domains
- **⚗️ Metabolites Block**: Chemical formula support with database integration
- **🔗 External Identifiers**: UniProt, RefSeq, ChEBI, HMDB, KEGG integration

### **Spatial Genomic Reasoning**

- **📍 Genomic Loci**: Define named genomic regions with coordinates
- **🎯 Spatial Predicates**: `is_within`, `distance_between`, `is_in_contact`
- **🧩 3D Chromatin**: Hi-C integration for spatial interactions
- **📐 Context-Aware Rules**: Spatial constraints in biological reasoning

### **Advanced Discovery Engine**

- **🔄 Guided Discovery**: Iterative learning and candidate optimization
- **⚙️ Capability-Aware**: Engine compatibility across deployment scenarios
- **📋 Rule-Based Logic**: Complex biological constraint expression
- **🎭 Simulation Framework**: What-if analysis and hypothesis testing

### **Structural Bio-AI, Consensus & Borderline Rescue**

- **⚗️ De Novo Catalytic Motif & Enzyme Design (AlphaProtein Novo Synergy)**: Observational syntactic contracts for active-site catalytic triad geometry (`SER:OG`, `HIS:NE2`, `ASP:OD1`), transition-state substrate containers, and spatial distance tolerances ($\le 3.5\text{ \AA}$) strictly preserving GFL's observational boundary while enabling GeneForge's kinetic and scaffolding engines
- **🔁 Deterministic Replay & Retroelement Mining (Anti-Stochasticity Gates)**: Cryptographic verification contracts ($seed \times checksum$) and continuous base-level sequence coverage ($100\%$ sliding window) guaranteeing reproducible re-discovery of Array-associated Reverse Transcriptases (ART) and mobile elements across autonomous agent swarms (overcoming the Anthropic Mythos stochasticity trap)
- **🧬 Non-Coding Regulatory Variant Interpretation (ClinVar + AlphaGenome)**: Tissue-specific regulatory triage resolving non-coding Variants of Uncertain Significance (VUS) across target vs. control tissue ontologies (e.g. Brain cortex vs Liver) with AVI scores and epigenomic disruption tracks
- **⚡ Jev & AnyJev Fast Decision Pre-Screening**: Training-free, permutation-invariant discrete option selection and calibrated confidence gating (Neural System 1) before escalating to formal biological arbitrament (System 2)
- **🔬 BGC & Megasynthase Assembly Lines**: Multi-domain modular enzyme complex validation (PKS, NRPS, hybrid megasynthases, ~2,500+ AA) to explore non-natural chemical space (e.g. $\delta$-valerolactam nylon precursors) inspired by gLM2
- **🎯 RFOptimization & Near-Miss Rescue**: Classification of borderline candidates (`NEAR_MISS`) and alternating gradient-guided simulated MCMC mutations + discrete resampling
- **⚖️ 5-Model Consensus Screening & Runs N' Poses Gate**: Cross-model validation across AlphaFold 3, RoseTTAFold 3, Boltz-1, Chai-1, and Protenix with pose gating ($iPAE < 2.5, iPTM > 0.8$, RMSD $\le 2.0\text{ \AA}$) to prevent co-folding hallucinations
- **🧲 Measurement-Guided Ensembles & Physics Refinement**: Steers generative diffusion models via empirical sparse restraints (NMR NOE, Cryo-EM, SAXS) and resolves steric clashes in complex receptors (GPCRs) via OpenMM force field energy minimization
- **🔍 Ligand-Conditioned Cryptic Pockets**: Dynamic modeling of allosteric and cryptic pockets transitioning from collapsed apo states to open holo states upon probe binding
- **📐 BioTorch Tensor Contracts**: Formal geometry and tensor representations with coordinate frames ($SE(3)$, $SO(3)$, `local_residue_frame`) and invariant dimensions
- **🛑 DepMap CRISPR Stop-Gates**: Empirical epistemic stopping gates based on Broad DepMap Public co-dependency and statistical significance
- **🔬 Google DeepMind AlphaGenome**: 18-modality unified variant impact scoring (AVI Score) and regulatory motif disruption analysis
- **🍊 Tangermeme Cis-Regulatory Logic & Seqlet Syntax (Nature Methods)**: Decoupled sequence-to-function interpretation, recursive variable-length seqlet calling, and context-bound claims preserving formal conditions ($\text{Claim}, \text{ContextState}, \text{Provenance}$). Empowers researchers and AI agents to decipher why and under what exact conditions a DNA sequence functions, eliminating generic assertions in favor of contextualized, falsifiable hypotheses.
- **🧠 Distributed Biological Reasoning & Perturbation Atlas (Sun et al. / Shi et al. / OpenAI / Scripps)**: High-throughput whole-brain in vivo Perturb-seq screen contracts (`perturbation_atlas:`, 7.7M cells, 1,947 disease genes) with unary agent swarm allocation, paralog phenotypic dissonance detection (*Grin2a* vs *Grin2b* opposition), causal disease transition synthesis, and `ReasoningAtlasCompiler` for epistemic causality graph generation.
- **🛡️ Multi-Modal Biosecurity Watermarking & AI Provenance (SynthID Bio / Nature 2026 / DeepMind)**: Cross-dogma function-preserving biological watermarking (`biosecurity_watermark:`, `synth_provenance:`) spanning proteins ($k$-mer context hashing, green-list logit biasing, $g$-value and $z$-score detection with $p < 10^{-5}$), coding DNA (100% synonymous wobble-base watermarking with zero phenotypic alteration, human Codon Adaptation Index $\text{CAI} \ge 0.80$, and cryptic splice motif avoidance), and stable mRNA therapeutics. Protects biological intellectual property and prevents AI slop database contamination.
- **🧬 Carbon-X Frontier Genomic Foundation LLM (`HuggingFaceBio/Carbon-X`)**: Deep whole-genome DNA understanding and locus-level reasoning (`genomic_llm:`, `carbonx:`) powered by 14.8B parameters, hybrid 6-mer DNA tokenization (5,515 vocab entries), and a 40,960 token context window ($\approx 245\text{ kb}$ of contiguous DNA). Enables interactive "Chat with DNA", regulatory motif discovery, variant consequence explanation, and synthetic promoter design with local, privacy-preserving execution on Apple Silicon (M4 Max Metal GPU acceleration).
- **✨ ProTok Unified Multimodal Protein & Genomic Tokenizer (Harvard / Rajpurkar Lab / arXiv:2610.18481)**: Unifies protein sequence (1D), backbone 3D spatial geometry (direct PDB/AlphaFold Cartesian coordinate quantization), and functional ontologies (Enzyme Commission EC, Gene Ontology GO, CATH) into a single discrete residue vocabulary (`protok:`, `unified_protein_stream:`). Powered by Multi-Codebook Vector Quantization ($3.14\times 10^6$ composite states) and Codebook Group Dropout ($0.939$ lDDT on CATH 4.2, $0.695$ zero-shot EC level 1 precision, $52\%$ de novo backbone designability), plus structural biosecurity watermarking with exact binomial $p$-value detection. Includes **4 Bidirectional GFL–ProTok Cross-Synergies**: (1) `GenTokTokenizer` ($16,384$ trimodal DNA $\times$ 3D Chromatin Topology $\times$ Epigenetic states), (2) Central Dogma causal variant propagation (`DNA codon` $\rightarrow$ `ProTok conformation` $\rightarrow$ `clinical decision`), (3) Grammar-Constrained Decoding Masks ($>99.999\%$ search-space pruning), and (4) Isomorphic 3-Axis Diagnostic Projection ([Feature Guide](docs/geneforgelang/features/protok_unified_residue_stream.md)).
- **🗺️ Graphify Static Knowledge Graph & Grammar Indexing (Graphify-Labs / Tree-sitter AST)**: Deterministic, queryable knowledge graph spanning all Python compiler internals, AST contracts, and user-facing `.gfl` genetic programs (`graph.json`, `graph.html`, `GRAPH_REPORT.md`). Reduces agent context window consumption by **>240x (99.6% token reduction)**, unifies 6,459 nodes and 11,198 edges, maps architectural God Nodes (`EnhancedSemanticValidator`), and provides automated static grammar auditing (`scripts/audit_gfl_grammar_graph.py`, `scripts/gfl_ast_to_graphify.py`) ([Feature Guide](docs/geneforgelang/features/graphify_static_grammar_index.md)).
- **🌊 Mesoscopic DNA Breathing & Transcription Factor Coupling (USC / Rohs Lab / Bioinformatics Advances 2026)**: Transient base-pair thermal unpairing dynamics and opening bubble profiling (`dna_dynamics:`, `breathing:`) powered by an analytical Peyrard-Bishop-Dauxois (PBD) statistical mechanics solver coupled with canonical pentamer DNA shape parameters (MGW, Roll, HelT, ProT). Models the physical code of gene regulation, distinguishing between `RIGID_SHAPE_DOMINATED` factors (where breathing disrupts major groove recognition) and `BREATHING_ASSISTED` pioneer factors (where thermal opening lowers the free energy barrier for TBP/Cas9/intercalation), enabling quantitative non-coding VUS binding delta predictions ($\Delta\Delta G_{\text{binding}}$) ([Feature Guide](docs/geneforgelang/features/dna_breathing_mesoscopic_dynamics.md)).
- **🔬 Single-Cell Immune Regulation & Dynamic Cell States (TenK10K Paradigm / Garvan / Nature 2026)**: Population-scale single-cell functional genomics (`single_cell_regulation:`, `sc_regulation:`, `cellular_context:`) grounded in Phase 1 of TenK10K (Cuomo, Spenceley, Tanudisastro et al., Powell & MacArthur; 1,925 individuals, >5M cells, 28 PBMC lineages). Elevates GFL beyond static bulk eQTLs to: (1) **Cell-Type Specificity** across 28 Cell Ontology (`CL:`) immune lineages (50% of eQTLs are cell-type specific, enriched in distal enhancers $>20\text{ kb}$ from TSS); (2) **Continuous Cell-State Interaction Kinetics** ($\beta_{\text{eff}}(s) = \beta_0 + \gamma \cdot s$) modeling activation/cytotoxicity gradients; (3) **Cell Abundance QTLs (`caQTLs`)** modulating sublineage differentiation under simplex conservation; and (4) **Bayesian Colocalization Gating** ($PP_4 \ge 0.80$) matching GWAS autoimmune/neurological loci to causal single-cell transcripts ([Feature Guide](docs/geneforgelang/features/single_cell_immune_regulation_tenk10k.md)).
- **🤖 Autonomous Wet-Lab Protocol Execution & Synthesizability Engine (AutoDNA / Nature 2026 Synergy)**: Bridges declarative genetic programming with physical in vitro execution (`autonomous_execution:`, `wet_lab_dispatch:`, `laboratory_protocol:`) grounded in AutoDNA (*Nature*, 2026; Ledford, Chen, Wu et al.; DOI: `10.1038/d41586-026-03552-8`). Unifies 4 core pillars: (1) **SiLA 2 & AutoDNA Multi-Instrument Compilation** across synthesizers, thermocyclers, liquid handlers, and sequencers; (2) **Biophysical Synthesizability Gates** enforcing enzymatic TdT homopolymer limits ($\le 4\text{ bp}$), GC composition ($40\%\text{--}60\%$), and secondary hairpin free energy ($\Delta G_{\text{hairpin}} > -8.0\text{ kcal/mol}$); (3) **Biosecurity Air-Gap & Cryptographic Dispatch Tokens** (automated select agent toxin screening and SHA-256 execution authorization signatures); and (4) **Closed-Loop Telemetry & Causal Epistemic Refinement** reconciling physical NGS sequencing reads and step-wise yields ($\ge 97.7\%$) to promote in silico hypotheses to `EMPIRICAL_VERIFIED` ([Feature Guide](docs/geneforgelang/features/autonomous_wet_lab_autodna_synergy.md)).
- **🧊 Cloud-Native Biological Lakehouse & Frozen Annotations (`bioc-on-ice` / Sean Davis 2026)**: Language-agnostic, zero-download biological lakehouse integration (`bioc_reference:`, `lakehouse_reference:`, `bioc_on_ice:`) grounded in Bioconductor on Ice (*`bioc-on-ice`*, Sean Davis 2026; 100 GB, ~4B rows, 81 tables across 7 schemas: `annotation`, `clinical`, `ontology`, `reference`, `provenance`, `raw`, `resource`). Unifies: (1) **Epistemic Release Pinning** (binding GFL protocols to frozen snapshots e.g. `2026-11-08` or `latest` with SHA-256 table integrity audits); (2) **Zero-Download HTTP Range Pushdown Execution** via DuckDB HTTPFS (`read_parquet('https://...')`) and PyArrow streaming dataset readers without multi-gigabyte monolithic downloads; (3) **Lakehouse Ground Truth Resolution** for Ensembl/NCBI genes (*GZMB*, *KRAS*, *TP53*, *TREM2*, *IL2RA*), transcripts, and ontology CURIE validation (`CL:`, `GO:`, `HP:`, `DOID:`, `UBERON:`); and (4) **Dual-Mode Offline Fallback** with local manifest caching (`~/.cache/geneforgelang/bioc_on_ice/`) and curated reference registry ([Feature Guide](docs/geneforgelang/features/bioc_on_ice_lakehouse_reference.md)).
- **🎯 AlphaGenome 2 Dedicated 1 Mb Cell-Specific Gene Regulation & Epigenetic Imputation (Google DeepMind 2026)**: Cell-type-specific locus-scale programming (`alphagenome2:`, `ag2_locus:`, `cellular_regulation_1mb:`) grounded in AlphaGenome 2 (Gayoso, Mottram et al., DeepMind, November 2026). Unifies: (1) **Dedicated 1 Mb Sequence Context** focusing 100% of transformer capacity on a single cellular state rather than diluting over thousands of bulk tissues; (2) **Zero-Shot Generalization via Scarce scRNA-seq** (from just 50–100 cells without retraining); (3) **Cross-Modality Imputation** predicting chromatin accessibility (ATAC/DNase), histone marks (H3K27ac), and single-cell **5mC DNA methylation** without wet-lab assay costs; (4) **SOTA Distal Enhancer-to-Gene Mapping** across up to 1 Mb with distance-decay contact modeling; and (5) **Pre-Flight Compilation Gating** protecting client API quotas and Google Cloud budgets ([Feature Guide](docs/geneforgelang/features/alphagenome2_cellular_regulation_1mb.md)).
- **🧬 FineDNA Sovereign Biocomputing & Closed-Loop RLVR Compiler (FineDNA / Qwen3-14B Synergy 2026)**: On-premise frontier biological reasoning and interactive RLVR code generation (`finedna:`, `finedna_circuit:`, `finedna_task:`) grounded in FineDNA (514B biological mid-training tokens, 200k SFT conversations, 100k RL tasks for environments, reaching **GPT-Sol 6.1 performance** on open weights). Unifies: (1) **100% Sovereign Air-Gapped Execution** running locally on Apple Silicon Mac Studio or private GPU clusters with strict compile-time protection against external IP leakage (`air_gapped: true`); (2) **Closed-Loop Interactive RLVR Compilation** using GFL as the deterministic reward oracle to catch syntax/thermodynamic errors and self-correct with SHA-256 cryptographic proof tokens; (3) **Zero Marginal Token Cost** eliminating recurring cloud API fees for biopharma screening; and (4) **RLVR Benchmark Dataset Exporter** allowing enterprise clients to format proprietary assays into FineDNA training environments ([Feature Guide](docs/geneforgelang/features/finedna_sovereign_biocomputing.md)).

### **Privacy-Preserving Bio-Skills & Governance**

- **🧬 Local Bioinformatics**: High-precision analysis running 100% locally
- **✅ Scientific Reproducibility**: Automatic generation of Reproducibility Packages (hashes, timestamps, versions)
- **🧠 Clinical Neuro-Skills**: Specialized skills for PharmGx, Geriatric Risk, and NutriGx
- **🛡️ Data Sovereignty & Biosecurity**: Provenance, Consent, Jurisdiction, and Population equity tracking as first-class language semantics
- **🔒 Security Policy & Continuous AI Scanning**: Coordinated vulnerability reporting via [SECURITY.md](SECURITY.md) with support for automated AI security auditing (Anthropic OSS Scanner) and Bandit static analysis gates

### **🧬 Interactive Visualization & Dynamic DNA Helix Explorer (`GF-HelixView`)**

- **Dynamic B-DNA Double Helix (SVG 2.5D)**: Physical geometry rendering of the right-handed B-DNA double helix (10 base pairs per turn, pitch 3.4 nm, rise 0.34 nm, major groove 2.2 nm, minor groove 1.2 nm) with explicit sugar-phosphate backbones and Watson-Crick hydrogen bonding ($A=T$ with 2 H-bonds vs $G\equiv C$ with 3 H-bonds).
- **Reading Head & Interactive Scrubber**: Dynamic scanning across loci (1 to $N$ bp) with speed controls ($0.5\times$ to $5\times$), keyboard navigation (`ArrowLeft`, `ArrowRight`, `Space`), and real-time physical metrics.
- **Dynamic Codon Translation & Frameshift Disruption Alerts**: Real-time 3-frame translation from nucleotide triplets to amino acids, with live detection and alerting of open reading frame disruptions and premature termination codons (PTC).
- **Exon & Splicing Architecture Overlays**: Canonical donor (`GT`, 5' ss) and acceptor (`AG`, 3' ss) boundary identification, reading phase tracking (Phase 0, 1, 2), and quick-jump navigation across exons.
- **ClinVar & Known Variant Tracks**: Pathogenicity classification badges (Pathogenic, Likely Pathogenic, VUS, Benign), HGVS nomenclature, molecular consequences, and direct jump-to-mutation controls.
- **Epigenomics (5hmC) & CRISPR PAM Scanner**: Methylated CpG dinucleotide overlays and automated SpCas9 PAM window scanning (`NGG` motif with 20-nt guide alignment and -3 nt cleavage marker).
- **Zero-Dependency Portable HTML5/SVG Export**: Self-contained single-file HTML applications (~40 KB) that run offline in any modern browser without CDN, NPM, or external runtime requirements.

## Key Features

- **Declarative Genetic Syntax**: Clean, readable, mathematically sound YAML-based biological workflow definitions with strict 2-space indentation.
- **Sovereign Biological AI & Air-Gapped Compliance**: Native on-premise execution with FineDNA-14B and Carbon-X 14.8B on local workstations (Apple Silicon Mac Studio / NVIDIA GPUs), strictly rejecting public cloud egress when `air_gapped: true`.
- **Closed-Loop RLVR Verification & Proofs**: Interactive compiler self-correction emitting deterministic reward scores and cryptographic SHA-256 verification tokens.
- **Dedicated Locus-Scale (1 Mb) Regulation**: AlphaGenome 2 integration dedicating 100% of transformer context to a single cell state, cross-modal 5mC methylation imputation, and distal enhancer-promoter contact modeling.
- **Cloud-Native Biological Lakehouse**: Bioconductor on Ice (`bioc-on-ice`) integration querying 81 frozen Parquet tables (~4B rows, 100 GB) via DuckDB HTTPFS pushdown without multi-gigabyte local downloads.
- **Physical DNA Mechanics & Breathing**: Mesoscopic Peyrard-Bishop-Dauxois (PBD) thermal bubble opening dynamics and pioneer transcription factor binding prediction.
- **Autonomous Wet-Lab Dispatch & Synthesizability Gates**: AutoDNA SiLA 2 multi-instrument compilation, automated enzymatic TdT homopolymer checks, and biosecurity screening.
- **Multimodal Protein & Residue Tokenization**: ProTok unified 1D sequence, 3D Cartesian geometry, and functional ontology codebooks with Central Dogma causal propagation.
- **Interactive Multi-Omic Visualizer (`GF-HelixView`)**: Real-time dynamic B-DNA 2.5D helix scanner with 3-frame translation, frameshift alerts, ClinVar variant tracks, and CRISPR PAM detection (`gfl view dna`).
- **Extensible Plugin Ecosystem**: Interoperable plugins for BioPython, BLAST, GATK, Samtools, and custom analytical pipelines.

## 🧪 **Scientific Validation - BRCA1 gRNA Discovery**

GFL has been validated through a comprehensive experiment discovering optimal gRNA candidates for CRISPR gene editing:

### **Results Summary**

- **🏆 Best Candidate**: BRCA1_gRNA_4_02
- **📈 Combined Score**: 89.7% efficiency
- **🎯 On-Target**: 84.8% efficiency with only 3.0% off-target risk
- **⚡ Discovery Time**: 24 seconds for 50 candidates across 5 cycles

### **Scientific Impact**

- **Clinical Relevance**: BRCA1 is critical for cancer research
- **Safety Focus**: <30% off-target risk across all top candidates
- **Efficiency**: >80% on-target activity for top 10 candidates
- **Reproducibility**: Complete workflow documented and open-source

Scientific manuscript available in the examples directory.

## Quick Start

### Installation

```
# Basic installation
pip install geneforgelang

# With web interface
pip install geneforgelang[web]

# With CLI tools
pip install geneforgelang[cli]

# With container support
pip install geneforgelang[containers]

# Full installation
pip install geneforgelang[all]
```

### Basic Usage - Protein Design and Optimization

```python
from geneforgelang import parse, validate, execute

# Simple GFL Workflow Example
workflow = """
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  count: 10
  length: 100
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    pH: "range(6.0, 8.0)"
    concentration: "range(10, 100)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: efficiency
  budget:
    max_experiments: 20
  run:
    experiment:
      tool: protein_assay
      type: efficiency_measurement
      params:
        temp: "${temperature}"
        pH: "${pH}"
        conc: "${concentration}"
"""

# Parse and validate
ast = parse(workflow)
errors = validate(ast)

if not errors:
    print("GFL file successfully validated")

    # Execute workflow
    result = execute(ast)
    #print(result)
    print(f"Done!: {result['design']['count']} proteins generated")
"""

# Parse and validate
ast = parse(workflow)
errors = validate(ast)

if not errors:
    # Execute workflow
    result = execute(ast)
    print(f"Editing efficiency: {result['efficiency']:.2%}")
```

### Command Line Interface

```
# Parse a workflow
gfl parse workflow.gfl

# Validate a workflow
gfl validate workflow.gfl

# or both!
gfl parse workflow.gfl --validate

# Execute a workflow
gfl infer workflow.gfl

# View and interact with a DNA locus from a GFL protocol
gfl view dna examples/dmd_gene_helix_viewer.gfl --open

# View directly from a FASTA file specifying gene and active coordinate
gfl view dna --fasta locus.fasta --gene DMD --coord 161 --output viewer.html --open

# Get help (or check full options)
gfl --help
gfl -h
```

## Workflow Examples

### CRISPR Gene Editing

```yaml
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: BRCA1
    guide_rna: GCACTGCCATGGAGGAGCCG
    cell_line: HEK293T

analysis:
  type: off_target_prediction
  algorithm: cas_offinder
  params:
    max_mismatches: 3

validation:
  type: experimental
  replicates: 3
  controls: [negative, positive]
```

### Sovereign Biocomputing & RLVR Verification (FineDNA-14B)

```yaml
finedna_circuit:
  contract_id: "FineDNA-TREM2-Microglia-Rescue-01"
  task_type: "crispr_circuit_design"
  prompt: "Synthesize an HDR repair construct to rescue loss-of-function TREM2 variant R47H in human microglia."
  target_locus: "chr6:41126000-41131000"
  inference_config:
    endpoint_url: "http://localhost:8000/v1"
    model_name: "FineDNA-14B"
    air_gapped: true

verifiable_dna:
  task_id: "TREM2-RLVR-Verification-01"
  domain: "sequence_localization"
  ground_truth_reference: "12-35:+"
  reward_success: 1.0
  localization_contract:
    contract_id: "loc_trem2_exon2_hdr"
    query_pattern: "GAATTCATGCGATCG"
    target_sequence: "NNNNNNNNNNNGAATTCATGCGATCGNNNNNNNNNN"
    mode: "exact_match"
```

### Cell-Specific 1 Mb Epigenetic Regulation & Enhancer Triage (AlphaGenome 2)

```yaml
alphagenome2:
  contract_id: "ag2_microglia_trem2_1mb"
  locus_window_1mb: "chr6:40626000-41626000"
  genome_build: "GRCh38"
  cellular_context:
    cell_type_curie: "CL:0000129"
    cell_type_name: "microglial cell"
    conditioning_mode: "cell_ontology_curie"
  impute_modalities:
    - "chromatin_accessibility"
    - "dna_methylation_5mc"
  enhancer_gene_linking:
    target_gene_id: "ENSG00000095977"
    enhancer_locus: "chr6:41129500-41130500"
    min_contact_probability: 0.75
    max_distance_bp: 150000
```

### Cloud-Native Lakehouse Query (Bioconductor on Ice / DuckDB)

```yaml
bioc_reference:
  contract_id: "bioc_gzmb_grch38_lakehouse"
  release_version: "2026-11-08"
  genome_build: "GRCh38"
  backend: "duckdb_httpfs"
  query:
    schema_name: "annotation"
    table_name: "ensembl_genes"
    filter_criteria:
      gene_symbol: "GZMB"
    limit: 10
  target_gene_symbol: "GZMB"
```

### Protein Design

```yaml
design:
  entity: ProteinSequence
  objective:
    maximize: stability
    target: therapeutic_protein
  constraints:
    - length: [50, 150]
    - synthesizability: ">0.8"
  count: 10

optimize:
  search_space:
    temperature: [25, 42]
    ph: [6.5, 8.0]
  strategy: bayesian_optimization
  objective:
    maximize: expression_level
  budget:
    max_experiments: 50
```

## 🧬 Interactive DNA Helix Explorer (`GF-HelixView`)

GeneForge introduces a high-fidelity, interactive B-DNA double helix explorer that bridges biophysical structure with multi-omic annotation tracks.

### Declarative GFL Protocol

Define a visualization contract directly in your `.gfl` file with strict 2-space indentation:

```yaml
dna_viewer:
  name: "dmd_exons44_51_helix"
  target_gene: "DMD"
  genomic_range: "chrX:31,180,000-31,210,000"
  conformation: "b_dna"
  active_coordinate: 161
  dna_sequence: "ATGAAGATGAGGACCAGGTC...TTTAA"
  tracks:
    - "exons"
    - "reading_frames"
    - "clinvar_variants"
    - "epigenetics_5hmc"
    - "crispr_pam_sites"
  exons:
    - exon_number: 44
      start_coord: 1
      end_coord: 148
      phase: 0
      donor_splice_boundary: "GT"
      acceptor_splice_boundary: "AG"
    - exon_number: 45
      start_coord: 149
      end_coord: 324
      phase: 1
      donor_splice_boundary: "GT"
      acceptor_splice_boundary: "AG"
  variants:
    - coordinate: 161
      variant_id: "VCV000000001"
      clinical_significance: "pathogenic"
      molecular_consequence: "frameshift_variant"
      hgvs_cdna: "c.6438delT"
      hgvs_protein: "p.Phe2147LeufsTer3"
      notes: "Exon 45 deletion disruption; dystrophin reading frame altered"
  epigenetic_marks:
    - coordinate: 42
      modification_type: "5hmC"
      strand: "+"
  crispr_pam_sites:
    - coordinate: 88
      pam_motif: "NGG"
      guide_sequence: "GATGAAGATGAAGATGAAGA"
      target_strand: "+"
```

### CLI Commands

Launch and export interactive helix viewers directly from the terminal:

```bash
# Generate and open viewer from a GFL protocol
gfl view dna examples/dmd_gene_helix_viewer.gfl --open

# Generate from a FASTA file specifying gene and active coordinate
gfl view dna --fasta locus.fasta --gene DMD --coord 161 --output locus_viewer.html --open
```

Explore the compiled human *DMD* reference visualization in [`visualizations/dmd_exons44_51_helix.html`](visualizations/dmd_exons44_51_helix.html) and full documentation in [`docs/geneforgelang/features/dna_helix_viewer.md`](docs/geneforgelang/features/dna_helix_viewer.md).

## Architecture

GFL follows a modular, capability-driven compiler architecture:

```
src/geneforgelang/
├── core/                       # Core language and specialized domain engines
│   ├── parser.py               # YAML/GFL AST parser
│   ├── validator.py            # Enhanced semantic validation & security gates
│   ├── gftypes.py              # Domain type system & AST contract definitions
│   ├── finedna_engine.py       # FineDNA sovereign inference & RLVR compiler environment
│   ├── alphagenome2_engine.py  # AlphaGenome 2 dedicated 1 Mb regulation & 5mC imputation
│   ├── bioc_ice_engine.py      # Bioconductor on Ice DuckDB HTTPFS lakehouse client
│   ├── wet_lab_engine.py       # AutoDNA SiLA 2 dispatch & enzymatic TdT synthesis gates
│   ├── dna_breathing_engine.py # Peyrard-Bishop-Dauxois mesoscopic DNA breathing solver
│   ├── protok_engine.py        # ProTok unified multimodal residue vocabulary
│   ├── carbonx_engine.py       # Carbon-X 14.8B genomic LLM & 6-mer tokenizer
│   ├── single_cell_engine.py   # TenK10K continuous cell-state kinetics & caQTLs
│   ├── watermark_engine.py     # SynthID Bio biological watermarking engine
│   └── api.py                  # Public programmatic Python API
├── visualization/              # Interactive visualization instruments (GF-HelixView)
│   └── dna_helix_viewer.py
├── plugins/                    # Extensible plugin architecture (BioPython, BLAST, GATK)
├── web/                        # Web visualization interface
├── cli/                        # Command-line interface (`gfl parse`, `gfl view dna`)
└── utils/                      # Shared schema registries and lakehouse utilities
```

## Plugin System

GFL supports custom plugins for extending functionality:

```
from geneforgelang.plugins import BasePlugin

class CustomAnalysisPlugin(BasePlugin):
    name = "custom_analysis"
    version = "1.0.0"

    def execute(self, params: dict) -> dict:
        # Custom analysis logic
        return {"result": "analysis_complete"}

# Register plugin
from geneforgelang.plugins import register_plugin
register_plugin(CustomAnalysisPlugin())
```

## Web Interface (Not working!)

Launch the web interface for interactive workflow development:

```
gfl web --host 0.0.0.0 --port 8080
```

Features:

- Visual workflow editor
- Real-time validation
- Execution monitoring
- Result visualization

## API Reference

### Core Functions

- `parse(text: str) -> Dict`: Parse GFL text into AST
- `validate(ast: Dict) -> List[str]`: Validate AST semantics
- `execute(ast: Dict) -> Dict`: Execute workflow
- `infer(model, ast: Dict) -> Dict`: Run ML inference

## Development

### Setup Development Environment

```
# Clone repository
git clone <repository-url>
cd <repository-directory>

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Project Structure

```
GFL/
├── src/geneforgelang/    # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
├── resources/            # Dev tools, scripts, ...
└── pyproject.toml        # Project configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [User Guide](docs/guides/user-guides/) - Complete usage documentation
- [API Reference](docs/geneforgelang/api.md) - Detailed API documentation
- [Architecture](docs/dev/decisions/organization.md) - System design and decisions
- [Examples](examples/) - Practical workflow examples

### Feature Guides & Technical Specifications

| Category | Capability | Specification & Guide |
| :--- | :--- | :--- |
| **Foundation Models & Reasoning** | FineDNA Sovereign Biocomputing & RLVR | [`finedna_sovereign_biocomputing.md`](docs/geneforgelang/features/finedna_sovereign_biocomputing.md) |
| | Carbon-X 14.8B Genomic Foundation LLM | [`carbonx_genomic_llm.md`](docs/geneforgelang/features/carbonx_genomic_llm.md) |
| | ProTok Unified Multimodal Residue Vocabulary | [`protok_unified_residue_stream.md`](docs/geneforgelang/features/protok_unified_residue_stream.md) |
| | Distributed Perturbation & Reasoning Atlas | [`perturbation_atlas.md`](docs/geneforgelang/features/perturbation_atlas.md) |
| **Regulation & Dynamics** | AlphaGenome 2 Dedicated 1 Mb Cell-Specific Regulation | [`alphagenome2_cellular_regulation_1mb.md`](docs/geneforgelang/features/alphagenome2_cellular_regulation_1mb.md) |
| | Mesoscopic DNA Breathing & PBD Dynamics | [`dna_breathing_mesoscopic_dynamics.md`](docs/geneforgelang/features/dna_breathing_mesoscopic_dynamics.md) |
| | Single-Cell Immune Regulation (TenK10K) | [`single_cell_immune_regulation_tenk10k.md`](docs/geneforgelang/features/single_cell_immune_regulation_tenk10k.md) |
| | Tangermeme Cis-Regulatory Logic & Seqlets | [`tangermeme_cis_regulatory_logic.md`](docs/geneforgelang/features/tangermeme_cis_regulatory_logic.md) |
| **Lakehouse & Big Data** | Bioconductor on Ice (`bioc-on-ice`) Lakehouse | [`bioc_on_ice_lakehouse_reference.md`](docs/geneforgelang/features/bioc_on_ice_lakehouse_reference.md) |
| **Wet-Lab & Biosecurity** | Autonomous Wet-Lab Protocol Execution (AutoDNA) | [`autonomous_wet_lab_autodna_synergy.md`](docs/geneforgelang/features/autonomous_wet_lab_autodna_synergy.md) |
| | Verifiable DNA Computation & RLVR Oracles | [`verifiable_dna_computation.md`](docs/geneforgelang/features/verifiable_dna_computation.md) |
| | Multi-Modal SynthID Bio Watermarking | [`biosecurity_watermark.md`](docs/geneforgelang/features/biosecurity_watermark.md) |
| **Tooling & Visualization** | GF-HelixView Dynamic 2.5D DNA Helix Explorer | [`dna_helix_viewer.md`](docs/geneforgelang/features/dna_helix_viewer.md) |
| | Graphify Static AST & Grammar Knowledge Graph | [`graphify_static_grammar_index.md`](docs/geneforgelang/features/graphify_static_grammar_index.md) |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use GFL in your research, please cite:

```
@software{geneforgelang2025,
  title={GFL: A Professional DSL for Genomic Workflows},
  author={GFL Development Team},
  year={2025},
  version={1.0.0}
}
```

## Support

- GitHub Issues - Bug reports and feature requests
- Discussions - Community support
- [Documentation](https://geneforgelang.readthedocs.io) - Comprehensive guides

---

**GFL** - Open-source language for genomic workflow specification
