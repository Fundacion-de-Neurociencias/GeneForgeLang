# ProTok (Protein Tokenizer) Unified Multimodal Residue Vocabulary

## 1. Overview
**ProTok** is a discrete multimodal tokenization framework for proteins grounded in Harvard Medical School / Pranav Rajpurkar Lab's research (*Romain Hardy, Xiaoman Zhang et al.*, October 2026; [arXiv:2610.18481](https://arxiv.org/abs/2610.18481)).

Historically, protein representations were split across disjoint silos:
- **1D Sequence**: Handled by protein language models (*ESM-2, ProtTrans*) capturing evolutionary conservation but blind to 3D Euclidean distances.
- **3D Structure**: Quantized as coordinates or discrete backbone states (*Foldseek 3Di, GeoBPE, ESM3*) but lacking functional semantics and evolutionary depth.
- **Function**: Treated as external metadata annotations (*Enzyme Commission EC, Gene Ontology GO, CATH*) outside the token stream.

**ProTok unifies Sequence, Structure, and Function into a single discrete token stream**, where each residue is represented by one unified composite token produced via **Multi-Codebook Vector Quantization (VQ)** with **Codebook Group Dropout**.

---

## 2. GFL Declarative Grammar (`protok:` / `unified_protein_stream:`)

```yaml
protok:
  name: "ubiquitin_ligase_trimodal_stream"
  target_protein: "UBQLN2_CHAPERONE_MIMETIC"
  conditioning_mode: "structure_to_function"
  target_modality: "trimodal"
  target_ec_classification: "EC:2.3.2.27"
  expected_lddt_min: 0.92
  sequence_payload: "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"
  dropout_policy:
    allow_missing_sequence: false
    allow_missing_structure: false
    allow_missing_function: true
    dropout_rate: 0.15
  residue_stream:
    - pos: 1
      amino_acid: "M"
      structure_code: 506
      function_code: 45
      dihedral_phi: -60.0
      dihedral_psi: -45.0
      ec_classification: "EC:2.3.2.27"
    - pos: 2
      amino_acid: "Q"
      structure_code: 506
      function_code: 45
      dihedral_phi: -62.5
      dihedral_psi: -42.0
      ec_classification: "EC:2.3.2.27"
  metadata:
    organism: "Homo sapiens"
    disease_context: "Amyotrophic Lateral Sclerosis / Frontotemporal Dementia"
    benchmark: "ProTok StructTokenBench (CATH 4.2 / EC Level 1)"
```

---

## 3. Mathematical Architecture & Token Composition

ProTok utilizes three independent discrete codebook groups:
1. **Sequence Codebook ($V_{\text{seq}} = 24$)**: 20 canonical amino acids plus special tokens (`MASK`, `PAD`, `UNK`).
2. **Structure Codebook ($V_{\text{str}} = 512$)**: Discretizes continuous backbone Ramachandran dihedrals $(\phi, \psi) \in [-180^\circ, 180^\circ]^2$ and secondary structure basins (canonical $\alpha$-helix `506`, canonical $\beta$-sheet `507`, left-handed $\alpha$ `508`).
3. **Function Codebook ($V_{\text{fun}} = 256$)**: Encodes hierarchical Enzyme Commission classifications (EC Levels 1–4) and GO molecular functions.

### Composite Token Space
$$\text{CompositeToken}_i = (\text{CB}_{\text{seq}} \times 512 \times 256) + (\text{CB}_{\text{str}} \times 256) + \text{CB}_{\text{fun}}$$
Total discrete vocabulary capacity: $24 \times 512 \times 256 = 3,145,728$ unique states, allowing bijective forward encoding and exact reverse decomposition.

---

## 4. Codebook Group Dropout

During training and inference, whole codebook groups can be omitted (dropped):
- **Sequence-only**: Structural and functional groups are mapped to standardized `MASK` tokens (`STR_MASK = 511`, `FUN_MASK = 255`).
- **Structure-only**: Sequence and function are masked; predicts designable sequences and zero-shot functional classes.
- **Function-to-All**: Conditioned on target EC/GO, generates compatible sequences and structural backbones.

A single unified model checkpoint operates across any subset of inputs without retraining.

---

## 5. Benchmark Performance Metrics

| Benchmark Task | ProTok Metric | Baseline / Competitor |
| :--- | :--- | :--- |
| **CATH 4.2 Structural Reconstruction** | **$0.939$ lDDT** | Foldseek 3Di ($0.912$), ESM3 ($0.986$, but lowest downstream rank) |
| **Zero-Shot EC Level 1 Retrieval** | **$0.695$ Top-1 Precision** | Best competitor ($0.510$) |
| **StructTokenBench (7 benchmarks, 28 splits)** | **Rank 1 on 21 splits** | Top-2 on 27 of 28 splits |
| **De Novo Backbone Designability** | **$52\%$ viable backbones** | GeoBPE ($21\%$ on identical model size) |

---

## 6. Synergy with SynthID Bio (Biosecurity Watermarking)
ProTok enables structural steganography via `embed_structural_watermark()` in [`ProTokEngine`](file:///C:/Users/usuario/GeneForgeLang%20Ecosystem/GeneForgeLang/src/geneforgelang/core/protok_engine.py):
- Watermark bits are embedded by introducing controlled, imperceptible parity perturbations in structural codebook indices.
- **100% Sequence Preservation**: The amino acid sequence is completely unchanged (zero phenotypic alteration).
- **High Structural Fidelity**: Retains $\ge 0.93$ lDDT without steric clashes.
