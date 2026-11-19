# Regulatory Genomics Dual-Head Contracts (BPNet & AtacWorks)

## Theoretical Foundation

Based on **MIT 6.874 (Deep Learning in the Life Sciences — Lecture 7: Regulatory Genomics)** and foundational architectures such as **BPNet** (Avsec Ž., Kundaje A. et al., *Nature Genetics* 2021) and **AtacWorks** (Lal A. et al., 2020/2021).

### The Spatial Representation Problem

A central flaw in earlier regulatory deep learning models was collapsing continuous genomic signal tracks into a single scalar value (such as mean signal or binary peak classification).

> *"Two predictions can have the same total read count while putting the signal in different places."*

Consider an observed footprint with read counts `(0, 100, 0)`:
- Prediction 1 with probabilities `(0.1, 0.8, 0.1)` yields a Multinomial profile negative log-likelihood (NLL) of **22.3**.
- Prediction 2 with probabilities `(0.4, 0.2, 0.4)` yields an NLL of **160.9**.

Both predictions have identical predicted totals ($100$ reads), yet Prediction 1 preserves the base-resolution binding position whereas Prediction 2 places signal away from the core binding site.

### Dual-Head Architecture in GeneForgeLang

GFL addresses this by decoupling regulatory predictions into two complementary heads:
1. **Count Head (`count_head`)**: Models total read count magnitude using Negative Binomial or Poisson dispersion loss.
2. **Profile Head (`profile_head`)**: Models spatial base-pair distribution across loci using Multinomial profile loss and Jensen-Shannon Divergence (JSD).

---

## Signal Modalities

GFL distinguishes the epistemic origin of genomic tracks via `SignalModality`:
- `DE_NOVO_SEQUENCE_DIRECT`: Direct sequence-to-profile models predicting binding or accessibility from DNA sequence alone (e.g. BPNet, Enformer, AlphaGenome).
- `SIGNAL_DENOISED_ENRICHED`: Signal enhancement and denoising from low-coverage experimental tracks (e.g. AtacWorks on sparse single-cell ATAC-seq).
- `EXPERIMENTAL_EMPIRICAL`: Raw crosslink or cleavage data from wet-lab assays (ChIP-nexus, ATAC-seq, CUT&RUN).

---

## The Epistemic Barrier Invariant

> *"The useful connection is between the measurement, the loss function, and the biological question. Accurate prediction can guide experiments; it does not establish a mechanism by itself."*

To protect scientific integrity and prevent hallucinated mechanistic claims:
- All regulatory predictions default to `PREDICTIVE_GUIDANCE` or `HYPOTHESIS_GENERATING`.
- GFL's `EnhancedSemanticValidator` strictly forbids setting `epistemic_level: VALIDATED_MECHANISM` unless `orthogonal_validation_confirmed: true` is explicitly certified by empirical assay cross-checking.

---

## GFL Syntax

```yaml
metadata:
  name: "OCT4_Regulatory_Profile"
  version: "1.0.0"

regulatory_profile:
  profile_id: "OCT4_Enhancer_DualHead"
  target_factor: "OCT4"
  locus: "chr1:15432000-15433000"
  cell_type: "H1_hESC"
  modality: "de_novo_sequence_direct"
  source_model: "BPNet"

  count_head:
    expected_total_counts: 100.0
    tolerance_fold: 1.5
    dispersion: 0.1
    loss_model: "negative_binomial"

  profile_head:
    resolution: "base_pair"
    loss_metric: "multinomial_nll"
    max_jsd_threshold: 0.18
    strand_mode: "stranded_plus_minus"

  epistemic_level: "predictive_guidance"
  orthogonal_validation_required: true
  orthogonal_validation_confirmed: false
```
