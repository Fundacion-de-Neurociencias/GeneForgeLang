# Latent Discovery & Biomarker Replication Gate (`latent_discovery`)

The `latent_discovery` block (alias: `biomarker_discovery_gate`) provides a declarative scientific gate inspired by **Glyph** (Holland et al.) for auditing foundation-model latent feature discovery workflows.

Rather than treating foundation-model embeddings as opaque predictors, `latent_discovery` enforces four verifiable invariants before any latent feature is promoted as a `novel_candidate` or `rediscovered_positive_control`:

1. **Sparse Autoencoder (SAE) Probe Specification (`sae_probe`)**: Declares the `foundation_model`, `target_layer`, `dictionary_size`, `sparsity_l0`, `multiple_testing_correction` (`fdr_bh`, `bonferroni`, `holm`), and `fdr_threshold`.
2. **Confounder Adjustment (`confounder_adjustment`)**: Requires explicit `confounders` and residual significance (`residual_p_value <= max_adjusted_p_value`) after multivariable adjustment.
3. **External Multi-Cohort Replication (`external_replication`)**: Enforces replication across at least `min_external_cohorts` distinct `cohort_ids`, directional concordance (`direction_concordant: true`), and incremental predictive gain (`observed_delta_auc >= min_delta_auc`).
4. **Literature Novelty Triage (`literature_triage`)**: Separates `rediscovered_positive_control` markers (with `citation_evidence`) from `novel_candidate` markers (without existing literature citations), requiring at least one positive control when `require_positive_controls: true`. Optional `artifact_ref` fields are validated using `NumericProvenanceAuditor.is_valid_reference`.

## Implementation

- **AST Types**: `DiscoveryNoveltyStatus`, `SAEProbeSpec`, `ConfounderAdjustmentContract`, `ExternalReplicationContract`, `LiteratureNoveltyTriageContract`, `LatentDiscoveryContract` in `src/geneforgelang/core/gftypes.py`.
- **Auditor**: `LatentDiscoveryAuditor` and `LatentDiscoveryAuditReport` in `src/geneforgelang/core/latent_discovery.py`.
- **Validator**: `_validate_latent_discovery_block` in `src/geneforgelang/core/validator.py`.
- **Exemplar**: `examples/features/glyph_latent_discovery_gate.gfl`.
