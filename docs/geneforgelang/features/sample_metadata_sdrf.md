# SDRF Sample Metadata Contract (`sample_metadata`)

The `sample_metadata` block (alias: `sdrf_contract`) provides a declarative contract for proteomics sample metadata inspired by the **SDRF-Proteomics** curation workflow (`PRIDE`, `iProX`, `MassIVE`, `ProteomeXchange`).

It enforces four invariants at validation time:

1. **Valid Repository & Accession**: `accession` must follow ProteomeXchange-style identifiers (`PXD`, `IPX`, `MSV`, or `RPXD` followed by at least 6 digits) and `repository` must be one of `pride`, `iprox`, `massive`, `proteomexchange`.
2. **Mandatory Source Citations**: `source_citations` must be non-empty (e.g., `PMID`, `DOI`, or PX record) when `require_source_citations: true`.
3. **Non-Fabricated Sample & File Names**: Every sample in `samples` must declare non-empty, non-placeholder `source_name`, `organism`, `assay_name`, and `data_file` fields.
4. **By-Reference Artifact Grounding**: Optional `artifact_ref` handles on sample entries are validated using `NumericProvenanceAuditor.is_valid_reference`.

## Implementation

- **AST Types**: `ProteomicsRepository`, `SDRFSampleEntry`, `SDRFMetadataContract` in `src/geneforgelang/core/gftypes.py`.
- **Auditor**: `SampleMetadataAuditor` and `SDRFAuditReport` in `src/geneforgelang/core/sample_metadata.py`.
- **Validator**: `_validate_sample_metadata_block` in `src/geneforgelang/core/validator.py`.
- **Exemplar**: `examples/features/sdrf_sample_metadata_contract.gfl`.
