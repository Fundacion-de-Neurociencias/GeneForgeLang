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

- **Declarative Syntax**: Clean, readable YAML-based workflow definitions
- **Type Safety**: Strong typing system with comprehensive validation
- **Interactive Multi-Omic Visualizer**: Real-time dynamic B-DNA helix scanner with reading frame translation, frameshift alerts, ClinVar variant tracks, and CRISPR PAM detection (`gfl view dna`)
- **Plugin Architecture**: Extensible system for custom tools and algorithms
- **Web Interface**: Modern web UI for workflow creation and management
- **CLI Tools**: Comprehensive command-line interface for automation
- **API Integration**: RESTful API for programmatic access
- **Container Execution**: Reproducible execution using Docker containers

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

```
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

### Protein Design

```
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

GFL follows a modular architecture:

```
src/geneforgelang/
├── core/           # Core language functionality
│   ├── parser.py   # YAML/GFL parser
│   ├── validator.py # Semantic validation
│   ├── gftypes.py    # Type system
│   └── api.py      # Public API
├── visualization/  # Interactive visualization instruments (GF-HelixView)
│   └── dna_helix_viewer.py
├── plugins/        # Plugin system
├── web/           # Web interface
├── cli/           # Command-line tools
└── utils/         # Shared utilities
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
