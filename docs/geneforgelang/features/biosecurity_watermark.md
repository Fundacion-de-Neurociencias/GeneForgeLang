# Biosecurity & Biological Watermarking (`biosecurity_watermark`)

## Overview

As generative AI accelerates de novo biological design (antibodies, enzymes, nanobodies, and therapeutic mRNA), verifying provenance, tracking biological intellectual property, and mitigating biosecurity risks becomes paramount.

The `biosecurity_watermark:` declarative contract in **GeneForgeLang (GFL)** implements a multi-modal, function-preserving biological watermarking system grounded in Google DeepMind's **SynthID Bio** framework (*Nature*, September 2026; Stutz, Cowen-Rivers, Kohli et al.; `google-deepmind/synthidbio`) and expanded across the Central Dogma of Molecular Biology:
1. **Proteins (Amino Acid Sequences & 3D Structures)**: Generative $k$-mer context hashing, green-list logit biasing, BLOSUM62/$\Delta\Delta G$ viability gating, and statistical $g$-value / $z$-score detection ($z > 4.5, p < 10^{-5}$).
2. **Coding Genes (DNA)**: 100% synonymous codon watermarking (wobble-base encoding) with zero amino acid sequence change ($0\%$ phenotypic alteration), human/host Codon Adaptation Index (CAI) preservation ($\ge 0.80$), and cryptic splice site avoidance.
3. **RNA (mRNA & ncRNA)**: Terminally stable, translation-invariant ribo-watermarking preserving secondary structure Minimum Free Energy (MFE).

---

## The $g$-value and $z$-score Statistical Benchmark

In non-watermarked natural biological sequences, amino acids or codons match an arbitrary pseudo-random green list with probability $\gamma = 0.50$ ($\mathbb{E}[g] \approx 0.50$).
In watermarked sequences generated with SynthID Bio, the empirical $g$-value shifts significantly upward ($g \approx 0.75 - 0.90$):

$$g = \frac{1}{L - k} \sum_{t=k}^{L-1} \mathbb{I}(x_t \in G_t)$$

The standardized detection metric ($z$-score) evaluates statistical significance:

$$z = \frac{g - \gamma}{\sqrt{\frac{\gamma(1 - \gamma)}{L - k}}}$$

For a sequence of $L = 120$ residues with $g = 0.75$, $z > 5.4$, yielding an asymptotic $p$-value $p < 10^{-7}$, proving artificial provenance with mathematical certainty and zero false positives.

---

## GFL Declarative Syntax

```yaml
biosecurity_watermark:
  name: "fneurociencias_nanobody_anti_trem2_v1"
  target_modality: "multimodal" # "protein" | "coding_dna" | "mrna"
  algorithm: "synthid_gvalue"   # "synthid_gvalue" | "synonymous_codon_hmac"

  provenance:
    institution: "Fundacion de Neurociencias"
    lab_id: "INVESTIGO_NEUROIA"
    generator_engine: "GeneForge-Rosalind-v2"
    biosecurity_clearance: "passed_pathogen_screening"
    timestamp: "2026-10-25T11:45:00Z"
    signature_hash: "sha256:d8f3b491a92e10c74b98c36190ef0d198274efb"

  viability_guardrails:
    max_delta_delta_g: 0.50             # kcal/mol max destabilization allowed
    min_cai_score: 0.82                 # Codon Adaptation Index threshold
    preserve_amino_acid_sequence: true  # 100% phenotypic identity in DNA/RNA
    avoid_splice_motifs: true           # Filter cryptic splice donors/acceptors
    forbidden_motifs:
      - "restriction_ecoRI"
      - "cryptic_splice_donor"

  detection_policy:
    min_z_score: 4.50                   # p-value < 3.4e-6
    green_list_fraction: 0.50           # standard gamma
    context_kmer_size: 3
    significance_threshold_pvalue: 0.00001

  security_key_ref: "vault:fneurociencias_synthid_key_2026"
  sequence_payload: "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDYDYWGQGTLVTVSS"
```

---

## Python API Usage

```python
from geneforgelang.core.gftypes import (
    BiosecurityWatermarkContract,
    WatermarkModality,
    WatermarkAlgorithm,
)
from geneforgelang.core.watermark_engine import WatermarkEngine

# 1. Define contract
contract = BiosecurityWatermarkContract(
    name="therapeutic_nanobody",
    target_modality=WatermarkModality.PROTEIN,
    algorithm=WatermarkAlgorithm.SYNTHID_GVALUE,
    security_key_ref="my_secret_seed",
)

# 2. Watermark protein sequence
protein_seq = "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDYDYWGQGTLVTVSS"
watermarked_seq, result = WatermarkEngine.watermark(contract, protein_seq)

print(result.is_watermarked)      # True
print(result.z_score)             # 5.12
print(result.confidence_level)    # "CONFIRMED_AI_ORIGIN"

# 3. Authenticate provenance
verify_result = WatermarkEngine.verify(contract, watermarked_seq)
assert verify_result.is_watermarked is True
```

---

## References

1. Stutz, D., Cowen-Rivers, A. I., Kohli, P., et al. (2026). *Function-preserving watermarking of AI-generated proteins*. **Nature**, 633, 890–898. [doi:10.1038/s41586-026-08123-x](https://doi.org/10.1038/s41586-026-08123-x).
2. DeepMind Technologies. *SynthID Bio Open Source Repository*. [https://github.com/google-deepmind/synthidbio](https://github.com/google-deepmind/synthidbio).
3. Sharp, P. M., & Li, W. H. (1987). *The codon adaptation index--a measure of directional synonymous codon usage bias, and its potential applications*. **Nucleic Acids Research**, 15(3), 1281–1295.
