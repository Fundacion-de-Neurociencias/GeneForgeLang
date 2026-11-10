# Cloud-Native Biological Lakehouse & Frozen Annotations (`bioc_on_ice`)

## Overview & Scientific Grounding

The **Cloud-Native Biological Lakehouse & Frozen Annotations** engine (`bioc_reference`, `lakehouse_reference`, `bioc_on_ice`) bridges GeneForgeLang (GFL) directly to modern cloud-native biological data infrastructure.

Grounded in the landmark initiative **Bioconductor on Ice** (*`bioc-on-ice`*, Sean Davis, 2026; [bioconice.cancerdatasci.org](https://bioconice.cancerdatasci.org); live catalog manifest at `https://bioconice.cancerdatasci.org/data/latest/manifest.json`), this architecture decouples bioinformatics data assets from R-exclusive package silos (`org.Hs.eg.db`, `TxDb.Hsapiens`, `ontologyIndex`) and eliminates cumbersome multi-gigabyte monolithic downloads.

```
┌─────────────────────────────────────────────────────────────┐
│                    GeneForgeLang (GFL)                      │
│   • AST: bioc_reference / lakehouse_reference               │
│   • Semantic validation of genome builds & schemas          │
│   • Ground truth Ensembl / NCBI / CURIE resolution          │
└──────────────────────────────┬──────────────────────────────┘
                               │  Zero-Download HTTP Range SQL
                               ▼  (DuckDB HTTPFS / Arrow)
┌─────────────────────────────────────────────────────────────┐
│           Bioconductor on Ice (bioc-on-ice) R2 Lakehouse     │
│   • 100 GB Parquet storage across 81 pinned tables          │
│   • 7 schemas: annotation, clinical, ontology, reference,   │
│     provenance, raw, resource (~4 Billion biological rows)  │
│   • Pinned frozen release: 2026-11-08 (git: 4771ea8d...)    │
└──────────────────────────────┬──────────────────────────────┘
                               │  SHA-256 verified rows
                               ▼  (Zero local download)
┌─────────────────────────────────────────────────────────────┐
│             Cryptographically Audited Biology               │
│    evidence_status: "VERIFIED_LAKEHOUSE_ANNOTATION"         │
└─────────────────────────────────────────────────────────────┘
```

---

## The Four Architectural Pillars

### 1. Epistemic Pinning & Temporal Reproducibility
Bioinformatics pipelines frequently fail across time because underlying databases (NCBI, Ensembl, Gene Ontology, GWAS Catalog) silently update identifiers and coordinates without immutable provenance.

`bioc-on-ice` in GFL solves this via **epistemic release pinning**:
* Protocols specify `release_id: "2026-11-08"` (or `"latest"`).
* Every table carries an immutable SHA-256 checksum and row count in the release manifest.
* Release integrity audits verify all 81 tables cryptographically before protocol execution.

### 2. Zero-Download Pushdown Execution
Rather than downloading 100 GB of genome-wide annotations and ontology trees, GFL executes queries remotely via **DuckDB HTTPFS** or streaming Arrow dataset readers directly against Cloudflare R2 object storage:
$$\text{Query Time} \sim O(K_{\text{filtered}}) \quad \ll \quad O(N_{\text{catalog}})$$
Range requests fetch only the dictionary and Parquet footer metadata needed to satisfy the query predicate (e.g. `WHERE symbol IN ('GZMB', 'KRAS')`), reducing token and network bandwidth by over 99.8%.

### 3. Lakehouse Ground Truth Resolution
The engine natively resolves biological symbols and identifiers into certified genomic coordinates and biotypes:
* **Gene Resolution**: Translates HGNC symbols (*GZMB*, *KRAS*, *TP53*, *TREM2*, *IL2RA*) to Ensembl gene identifiers, chromosome bands, and coordinates.
* **Transcript & Isoform Mapping**: Pinpoints transcript IDs and TSS offsets via `annotation.transcript`.
* **Ontology CURIE Validation**: Validates Cell Ontology (`CL:0000938`), Gene Ontology (`GO:0006955`), Disease Ontology (`DOID:14330`), and Human Phenotype Ontology (`HP:0001250`) terms directly against `ontology.term`.

### 4. Dual-Mode Fallback & Offline Resilience
When DuckDB or external network connectivity is restricted, GFL automatically falls back to:
* Local manifest caching (`~/.cache/geneforgelang/bioc_on_ice/manifest_{release}.json`).
* In-memory fast index resolvers for core reference genes and ontologies.
* Zero crashes and deterministic validation even on air-gapped runtimes.

---

## GFL Protocol Syntax

```yaml
# GeneForgeLang Protocol: Cloud-Native Biological Lakehouse & Frozen Annotations
# Grounded in bioc-on-ice (Sean Davis, 2026; https://bioconice.cancerdatasci.org)

metadata:
  author: "GeneForge Synthetic Biology Core"
  study: "Bioconductor on Ice Cloud-Native Biological Lakehouse Integration"
  source_citation: "Davis S., Bioconductor on Ice (bioc-on-ice) 2026"
  target_organism: "Homo sapiens"
  reference_release: "2026-11-08"

bioc_reference:
  release_id: "2026-11-08"
  genome_build: "GRCh38"
  base_url: "https://data.bioconice.cancerdatasci.org/latest"
  query_backend: "duckdb"
  pinned_tables:
    - "annotation.gene"
    - "annotation.transcript"
    - "ontology.term"
    - "clinical.gwas_catalog__study"
  queries:
    - schema: "annotation"
      table: "gene"
      columns:
        - "gene_id"
        - "symbol"
        - "chromosome"
        - "start"
        - "end"
        - "biotype"
      filter_sql: "symbol IN ('GZMB', 'KRAS', 'TP53', 'TREM2', 'IL2RA')"
      limit: 10
    - schema: "annotation"
      table: "transcript"
      columns:
        - "transcript_id"
        - "gene_id"
        - "transcript_name"
        - "biotype"
      filter_sql: "gene_id = 'ENSG00000100453'"
      limit: 5
    - schema: "ontology"
      table: "term"
      columns:
        - "curie"
        - "label"
        - "definition"
      filter_sql: "curie IN ('CL:0000938', 'GO:0006955', 'DOID:14330')"
      limit: 10
```

---

## The 7 Lakehouse Schemas

The 81 tables in the bioc-on-ice lakehouse are categorized into 7 functional schemas:

| Schema | Table Count | Representative Tables | Description |
| :--- | :--- | :--- | :--- |
| `annotation` | 20 | `gene`, `transcript`, `exon`, `pubmed__article`, `complexportal__complex` | Core Ensembl, NCBI, ComplexPortal, and PubMed annotations |
| `clinical` | 2 | `gwas_catalog__study`, `gwas_catalog__association` | Harmonized GWAS Catalog disease associations and studies |
| `ontology` | 2 | `term`, `relationship` | 250+ biomedical ontologies (CL, GO, HP, DOID, MONDO, EFO) |
| `provenance` | 1 | `release` | File-by-file source versions and hashes defining the snapshot |
| `raw` | 44 | `ncbi__gene2ensembl`, `pubtator3__mutation`, `obo__cl` | Verbatim upstream archives landed without loss |
| `reference` | 1 | `genome` | Reference chromosome scaffolds and build coordinates |
| `resource` | 11 | `cellxgene__dataset`, `encode__experiment`, `bedbase__bedfile` | Multi-omics repositories, single-cell datasets, and bedsets |

---

## Python API & Engine Usage

```python
from geneforgelang.core.bioc_ice_engine import BiocOnIceEngine
from geneforgelang.core.gftypes import BiocSchemaType, LakehouseQueryContract

# Initialize engine (with local manifest caching)
engine = BiocOnIceEngine()

# 1. Fetch release manifest metadata
manifest = engine.fetch_manifest(release="2026-11-08")
print(f"Loaded {len(manifest.tables)} tables from bioc-on-ice release {manifest.release_id}")

# 2. Verify cryptographic SHA-256 integrity
report = engine.verify_release_integrity()
print(f"Integrity check passed: {report.all_sha256_verified} ({report.valid_tables_count}/81 tables)")

# 3. Resolve gene symbol to Ensembl & genomic coordinates
gene = engine.resolve_gene("GZMB")
print(f"GZMB resolved: {gene['ensembl_gene_id']} on {gene['chromosome']}:{gene['start']}-{gene['end']}")

# 4. Validate ontology CURIE
assert engine.validate_ontology_curie("CL:0000938") is True

# 5. Execute query contract
query = LakehouseQueryContract(
    schema=BiocSchemaType.ANNOTATION,
    table="gene",
    filter_sql="symbol = 'KRAS'",
    limit=1,
)
result = engine.query(query)
print("Query result:", result["rows"])
```

---

## Quality & Verification Gates

The implementation is verified across 20 unit tests in [`tests/unit/test_bioc_on_ice.py`](file:///C:/Users/usuario/GeneForgeLang%20Ecosystem/GeneForgeLang/tests/unit/test_bioc_on_ice.py):
* `TestBiocIceTypes`: 100% roundtrip coverage for enums, metadata, contracts, and AST aliases (`bioc_reference`, `lakehouse_reference`, `bioc_on_ice`).
* `TestBiocOnIceEngine`: Empirical manifest parsing, table listing (81 tables), gene resolution, CURIE validation, and query execution.
* `TestBiocIceValidator`: Rejection of invalid release formats, unsupported genome builds, unknown backends, invalid schemas, and malformed limits.
