# gfl-plugin-clawbio

> GFL plugin adapters wrapping [ClawBio](https://github.com/ClawBio/ClawBio) bioinformatics skills.
> **Amputatable by design** — [ADR-0003](../GeneForgeLang/docs/adr/0003-extension-orthogonality.md) compliant. Score: 23/25.

## What this is

This package bridges [GeneForgeLang](https://github.com/GeneForgeLang/GeneForgeLang)
(the biological DSL) with [ClawBio](https://github.com/ClawBio/ClawBio)
(the bioinformatics skill library).

It wraps 4 ClawBio skills as GFL `GeneratorPlugin` adapters:

| GFL Tool ID | ClawBio Skill | Domain |
|---|---|---|
| `clawbio_pharmgx` | `pharmgx-reporter` | Pharmacogenomics |
| `clawbio_crispr_screen` | `crispr-screen-triage` | Functional genomics |
| `clawbio_rnaseq_de` | `rnaseq-de` | Transcriptomics |
| `clawbio_gwas_lookup` | `gwas-lookup` | Population genomics |

## Installation

```bash
# Plugin only (ClawBio optional)
pip install gfl-plugin-clawbio

# Plugin + ClawBio runtime
pip install 'gfl-plugin-clawbio[clawbio]'
```

## Usage in GFL

### PharmGx Reporter

```yaml
experiment:
  tool: clawbio_pharmgx
  type: analysis
  contract:
    inputs:
      raw_genome: {type: TEXT, attributes: {format: "23andme_v5"}}
    outputs:
      pharmacogenomic_report: {type: JSON}
  params:
    input_file: "patient_genome.txt"
```

### CRISPR Screen Triage

```yaml
analyze:
  strategy: variant
  data: guide_counts.csv
  thresholds:
    depletion_zscore_cutoff: -2.0
    min_guides_per_gene: 3
  contract:
    inputs:
      guide_counts: {type: CSV}
    outputs:
      hit_report: {type: JSON}
```

### RNA-seq Differential Expression

```yaml
analyze:
  strategy: differential
  data: count_matrix.csv
  thresholds:
    padj: 0.05
    log2fc_abs: 1.5
  contract:
    inputs:
      count_matrix: {type: CSV}
      sample_metadata: {type: CSV}
    outputs:
      de_results: {type: CSV}
```

### GWAS Lookup

```yaml
experiment:
  tool: clawbio_gwas_lookup
  type: analysis
  params:
    rsid: "rs429358"
    databases: [gwas_catalog, open_targets, gtex_v8]
```

## Architecture

```
gfl-plugin-clawbio/
├── gfl_plugin_clawbio/
│   ├── _clawbio_runner.py   ← ONLY file that touches ClawBio (via subprocess)
│   ├── pharmgx.py           ← PharmGxPlugin(GeneratorPlugin)
│   ├── crispr_screen.py     ← CrisprScreenPlugin(GeneratorPlugin)
│   ├── rnaseq_de.py         ← RnaseqDEPlugin(GeneratorPlugin)
│   └── gwas_lookup.py       ← GwasLookupPlugin(GeneratorPlugin)
└── governance.json          ← ADR-0003 score: 23/25 ✅
```

**Constitutional guarantee (ADR-0003):**
- `geneforgelang.*` never imports this package
- This package never imports `geneforgelang.core`, `.semantic`, or `.governance`
- ClawBio is called via subprocess only — never via Python import
- `pip uninstall gfl-plugin-clawbio` removes the plugin completely, zero residue

## Graceful degradation

If ClawBio is not installed, all plugins return a `DesignCandidate` with:
```json
{"status": "clawbio_not_installed", "install_hint": "pip install 'gfl-plugin-clawbio[clawbio]'"}
```

The GFL core never crashes. The plugin loads. The workflow fails gracefully.

## Running tests

```bash
# From the GeneForgeLang repo (GFL must be installed)
pip install -e /path/to/GeneForgeLang
pip install -e /path/to/gfl-plugin-clawbio

cd gfl-plugin-clawbio
pytest tests/ -v
```

## ADR-0003 Governance Score

| Dimension | Score | Max |
|---|---|---|
| Irreducibility Depth | 4 | 5 |
| Ontological Neutrality | 5 | 5 |
| Provider Abstraction Purity | 5 | 5 |
| Primitive Necessity | 4 | 5 |
| Sunsetability Confidence | 5 | 5 |
| **Total** | **23** | **25** |

Decision threshold: 20. **Status: APPROVED (Normal Review Queue).**

## License

MIT — same as ClawBio and GeneForgeLang.
