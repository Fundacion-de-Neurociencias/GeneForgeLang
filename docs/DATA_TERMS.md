# External Data Sources & Terms of Use

GeneForgeLang (GFL) is an open-source declarative domain-specific language (DSL) and validation library. **GFL does not bundle, host, or redistribute external proprietary, clinical, or third-party biological datasets.** When users configure optional plugins or engines to query external services, they supply their own credentials and are responsible for complying with the upstream provider's terms of use:

| External Source | Scope in GFL | Governing Terms & Licensing |
| :--- | :--- | :--- |
| **Google DeepMind AlphaGenome / AlphaGenome 2** | Variant impact scoring (`AVI`), 1 Mb cell-specific regulatory context, and Atlas URL construction (`gfl-plugin-alphagenome`, `alphagenome2_engine.py`). | Subject to Google DeepMind AlphaGenome API / non-commercial research terms of service (not for clinical or diagnostic use). Users must supply their own `ALPHAGENOME_API_KEY`. |
| **Ensembl** | Gene/transcript identifier resolution, genomic sequences, and VEP annotations (`bioc-on-ice` / external connectors). | Data and APIs provided by EMBL-EBI Ensembl under the Ensembl open-access data disclaimer and Apache 2.0 software license. |
| **UniProt** | Protein sequence metadata, functional annotations, and ontology cross-references. | Provided by the UniProt Consortium under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. Proper attribution to UniProt is required in downstream publications. |
| **Bioconductor on Ice (`bioc-on-ice`)** | Language-agnostic frozen Parquet lakehouse references (`bioc_reference:`). | Subject to the upstream `bioc-on-ice` release licenses and respective underlying public database licenses. |

> **Clinical & Personal Data Notice**: GFL is research software. Never commit API keys, `.env` files, or patient/clinical datasets into the repository. Local `.env` files are ignored via `.gitignore` and enforced by `gitleaks` CI scanning.
