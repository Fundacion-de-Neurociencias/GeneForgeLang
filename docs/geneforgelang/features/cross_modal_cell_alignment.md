# Cross-Modal Cell Alignment Contract (`cell_alignment`)

The `cell_alignment` block (alias: `cross_modal_cell_bridge`) provides a model-agnostic declarative contract inspired by **Bloom** for aligning cell identities across fragmented studies that measure disjoint cellular modalities (such as `scrna_seq`, `scatac_seq`, `electrophysiology`, `patch_seq`, `morphology`, and `spatial_transcriptomics`).

It enforces four scientific invariants at validation time:

1. **Paired Bridge Requirement**: Aligning disjoint study modalities requires declaring `bridge_model` and non-empty `bridge_modalities`.
2. **Species & Cross-Species Guard**: `bridge_species` and per-study `species` are mandatory; if any study differs from `bridge_species`, silent transfer is rejected unless `allow_cross_species_transfer: true` and `ortholog_anchors` are explicitly declared.
3. **Reference Taxonomy & Anchor Controls**: Mappings must ground to `reference_taxonomy` via `taxonomy_curie`, meet `min_mapping_confidence` and `max_unmapped_fraction`, and verify at least one `is_anchor: true` control against `anchor_cell_types`.
4. **By-Reference Grounding**: Optional `artifact_ref` handles on mappings and gene-peak links are validated using `NumericProvenanceAuditor.is_valid_reference`.
5. **Gene-Depth Coverage Control**: Optional `min_genes_per_cell` and per-study `observed_median_genes` gate out under-covered studies before alignment.
6. **Selective Cell-Access Gene–Peak Links**: Optional `gene_peak_links` (`GenePeakAccessLink`) and `min_gene_peak_attention` capture candidate enhancer–gene pairs (with optional `ag2_link_ref` to `AlphaGenome2`) for selective cell-type targeting hypotheses.

## Implementation

- **AST Types**: `CellModality`, `CellStudySlice`, `CellAlignmentMapping`, `GenePeakAccessLink`, `CellAlignmentContract` in `src/geneforgelang/core/gftypes.py`.
- **Auditor**: `CellAlignmentAuditor` and `CellAlignmentAuditReport` in `src/geneforgelang/core/cell_alignment.py`.
- **Validator**: `_validate_cell_alignment_block` in `src/geneforgelang/core/validator.py`.
- **Exemplar**: `examples/features/bloom_cross_modal_cell_alignment.gfl`.
