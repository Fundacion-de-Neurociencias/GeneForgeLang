# 🧬 GeneForgeLang

> **The Symbolic Language for Biological Reasoning**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Notice.** Research software. Not a medical device, not for clinical use, and not legal or regulatory advice.

## What is GeneForgeLang?

GeneForgeLang (GFL) is a domain-specific language for describing biological design workflows. A GFL document is YAML with typed blocks (`design`, `optimize`, `experiment`, `analyze`, ...). The Python library parses and validates these documents and offers a plugin system for tools that act on them.

**Status.** GFL is under active development and has no published release yet. The documented public API and the `gfl` command-line tool do not work from an installed package in this version (see [Quick Start](#quick-start)). The language features listed below describe the language design; check the [feature documentation](docs/index.md) for what the current parser accepts.

## Language Capabilities

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

### **Domain Extensions (experimental)**

The parser also accepts domain blocks for regulatory genomics, protein structure, single-cell regulation, biosecurity watermarking, lakehouse references and wet-lab dispatch (for example `alphagenome2:`, `protok:`, `single_cell_regulation:`, `biosecurity_watermark:`, `bioc_on_ice:` and `autonomous_execution:`). Each block is described in its [feature guide](#feature-guides--technical-specifications). These guides describe the block schema and the validation GFL performs; they are not benchmarks of the external models or services they name. Components that return simulated or stub output are listed by `geneforgelang.provenance.list_simulated_components()` and warn on first use.

### **Interactive DNA Helix Viewer (`GF-HelixView`)**

`geneforgelang.visualization.dna_helix_viewer` renders a self-contained HTML/SVG view of a DNA locus with codon translation, exon boundaries, known-variant tracks and SpCas9 PAM sites ([feature guide](docs/geneforgelang/features/dna_helix_viewer.md)).

### **Local Execution**

- **🛡️ Data stays local by default**: the parser and validator run on your machine and send no data to a cloud service. Optional engines that reach a remote service (for example the `bioc_on_ice` lakehouse reader or a remote model endpoint) only do so when a workflow asks for them; their feature guides say so.
- **🔒 Security Policy**: Coordinated vulnerability reporting via [SECURITY.md](SECURITY.md) with gitleaks secret scanning in CI and Bandit as a pre-commit hook.

## 🌐 Open-Source and Universal
GeneForgeLang is an **open-source project** dedicated to the entire scientific community. While it serves as the foundation for the GeneForge platform, its design and evolution are governed by universal biological principles, not by any specific commercial or execution environment.

*   **Universal Semantic Authority**: GFL defines the biological world independently of how it is executed.
*   **Open to Everyone**: Anyone can implement a GFL-compatible runtime or contribute to the language specifications.
*   **Decoupled Architecture**: Formal separation between Language Specification, Semantic Validation, and Execution Runtimes.

## 📜 Formal Specifications
To ensure consistency across the ecosystem, GFL maintains a set of formal specifications:
*   **[Architectural Directive](docs/architecture/ARCHITECTURAL_DIRECTIVE.md)**: The foundational decoupling mandate.
*   **[RFC Process](docs/rfc/README.md)**: Formal procedure for language evolution.
*   [Causal Semantics](docs/spec/causal_semantics.md): Rules for biological transformations.
*   [Biological State Space](docs/spec/state_space.md): Structural definition of the biological world.
*   [Instruction Set](docs/spec/instruction_set.md): Primitive biological operations.
*   [Execution Contract](docs/spec/execution_contract.md): Boundary between language and runtimes.
*   [Versioning Policy](docs/spec/versioning_policy.md): How the language evolves.
- **Type Safety**: Strong typing system with comprehensive validation
- **Plugin Architecture**: Extensible system for custom tools and algorithms
- **Web Interface**: Modern web UI for workflow creation and management
- **CLI Tools**: Comprehensive command-line interface for automation
- **API Integration**: RESTful API for programmatic access
- **Container Execution**: Reproducible execution using Docker containers

## 🧪 Example: BRCA1 gRNA Discovery (Illustrative simulation)

The [GFL Genesis example](examples/real_project/README.md) shows how a guided-discovery workflow for CRISPR gRNA candidates against BRCA1 is written in GFL. Its execution script draws every on-target and off-target score from `np.random.beta`: the numbers in its outputs are random scores, not a validation, and say nothing about real guide efficiency or safety. The accompanying [draft manuscript](examples/real_project/Manuscript_GeneForge_v2_Beta.md) is labelled the same way.

## Quick Start

### Installation

GeneForgeLang is not yet published on PyPI. Install it from source:

```bash
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang
pip install -e .

# Optional extras: web, cli, ml, containers, staging, lsp, dev
pip install -e ".[cli]"
```

The core library runs on Python 3.9 or newer. The `web`, `ml` and `dev` extras pin releases with security fixes (`torch`, `transformers`, `fastapi`, `starlette`, `aiohttp`, `black`), and those releases need Python 3.10 or newer: on Python 3.9 these extras install none of them.

### Basic Usage - Protein Design and Optimization

This is the target Python API. The top-level import below does not work in this version; feature F010 adds it. The workflow text itself parses and validates with the current parser.

<!-- does not run yet: F010 -->
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
    print(f"Done: {result['design']['count']} proteins generated")
```

### Command Line Interface

The `gfl` command does not start in this version (feature F015 tracks the fix). These are the intended commands:

```bash
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

```gfl
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

```gfl
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  constraints:
    - length(50, 150)
    - synthesizability > 0.8
  count: 10
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    ph: "range(6.5, 8.0)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: expression_level
  budget:
    max_experiments: 50
  run:
    experiment:
      tool: protein_assay
      type: expression_measurement
      params:
        temp: "${temperature}"
        ph: "${ph}"
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

```text
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
│   ├── permutation_baseline.py # Phylo shuffled-sequence signal auditor
│   └── api.py                  # Public programmatic Python API
├── visualization/              # Interactive visualization instruments (GF-HelixView)
│   └── dna_helix_viewer.py
├── plugins/                    # Extensible plugin architecture (BioPython, BLAST, GATK)
├── web/                        # Web visualization interface
├── cli/                        # Command-line interface (`gfl parse`, `gfl view dna`)
└── utils/                      # Shared schema registries and lakehouse utilities
```

## Plugin System

A plugin subclasses `BaseGFLPlugin` and implements `process`:

```python
from typing import Any

from geneforgelang.plugins.base import BaseGFLPlugin


class CustomAnalysisPlugin(BaseGFLPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.name = "custom_analysis"
        self.description = "Example analysis plugin"

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        # Custom analysis logic
        return {"result": "analysis_complete", "input_keys": sorted(data)}


plugin = CustomAnalysisPlugin()
print(plugin.process({"sequence": "MKTAYIAKQR"}))
```

Registering a plugin with `geneforgelang.plugins.plugin_registry.register_plugin` does not work in an installed package in this version: the registry module imports `src.geneforgelang`, which only resolves from a source checkout. Feature F010 fixes this.

## Web Interface (Not working!)

Launch the web interface for interactive workflow development:

```bash
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

### Public API contract

Clients may rely on the surface declared in [`docs/spec/public_contract.json`](docs/spec/public_contract.json): the functions of `geneforgelang.core.api`, the error types and codes, the grammar version and an evidence label per function (`execute` and the `infer` functions are labelled `simulated`). It is generated from the code, versioned with SemVer, and checked in CI. See [`docs/spec/API_CONTRACT.md`](docs/spec/API_CONTRACT.md).

Every plugin and connector shipped in this package is simulated or a stub (random or canned output). Their results carry a `provenance` label, they warn on first use, and `execute()` refuses them unless you pass `allow_simulated=True`. `OpenMedConnector` gives no privacy guarantee. `geneforgelang.provenance.list_simulated_components()` lists them.

## Development

### Setup Development Environment

```bash
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

```text
GeneForgeLang/
├── src/geneforgelang/    # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
├── resources/            # Dev tools, scripts, ...
└── pyproject.toml        # Project configuration
```

### Conformance suite

`tests/conformance_suite/` holds `.gfl` cases with an `expected.json` each. Run them against the real parser and validator from the repository root:

```bash
python -m geneforgelang.conformance tests/conformance_suite
```

Today 9 of 36 cases pass and 27 are listed as known failures, because the validator does not implement those constructs yet. See [tests/conformance_suite/README.md](tests/conformance_suite/README.md).

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
| | Permutation Baseline Gate (`shuffled_control`) | [`permutation_baseline_gate.md`](docs/geneforgelang/features/permutation_baseline_gate.md) |
| | Multi-Modal SynthID Bio Watermarking | [`biosecurity_watermark.md`](docs/geneforgelang/features/biosecurity_watermark.md) |
| **Tooling & Visualization** | GF-HelixView Dynamic 2.5D DNA Helix Explorer | [`dna_helix_viewer.md`](docs/geneforgelang/features/dna_helix_viewer.md) |
| | Graphify Static AST & Grammar Knowledge Graph | [`graphify_static_grammar_index.md`](docs/geneforgelang/features/graphify_static_grammar_index.md) |

## License

This project is licensed under the MIT License - see the [license](license) file for details.

## Citation

If you use GFL in your research, please cite:

```bibtex
@software{geneforgelang2025,
  title={GFL: A Professional DSL for Genomic Workflows},
  author={GFL Development Team},
  year={2025},
  version={1.0.0}
}
```

## Support

- [GitHub Issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues) - Bug reports, questions and feature requests
- [Documentation](docs/index.md) - Guides and reference in this repository

---

**GFL** - Open-source language for genomic workflow specification
