# Verifiable DNA Computation & Sequence Localization in GeneForgeLang (GFL)

## 1. Overview and Epistemic Rationale

Genomic Large Language Models (LLMs) frequently hallucinate biochemical facts, coordinates, and reading frames when reasoning across multi-megabase genomic assemblies. While natural language reasoning allows conceptual hypothesis generation, biological computing requires exact, deterministic proofs.

Inspired by **FineDNA** (which establishes mid-training with 300B+ tokens, SFT with deterministic verifiers, and RLVR for hard-to-learn tasks like sequence localization), **GeneForgeLang (GFL)** introduces formal declarative syntax and verifiable contracts for deterministic biochemical computation and sequence localization within the GFL AST.

By formalizing verifiable rewards within the GFL specification, researchers can:
1. Define **ground-truth verifiable reward contracts** for Reinforcement Learning with Verifiable Rewards (RLVR).
2. Execute **deterministic nucleotide calculations** (6-frame translation, reverse complementation, GC skew, ORF detection, and restriction enzyme cleavage).
3. Specify unambiguous **sequence localization constraints** across multiple coordinate conventions (0-based half-open vs. 1-based closed) with support for degenerate IUPAC patterns and dual-strand searches.
4. Generate tamper-evident **cryptographic verification proofs** (SHA-256) confirming that LLM reasoning traces comply with biochemical reality.

---

## 2. Declarative Syntax Specification

### 2.1 The `verifiable_dna` AST Block

A standard GFL file may declare a top-level `verifiable_dna` block (or `rlvr_verifier` alias):

```gfl
verifiable_dna:
  task_id: "FineDNA-RLVR-Localization-Task-01"
  domain: "sequence_localization"
  ground_truth_reference: "45-98:+"
  reward_success: 1.0
  reward_failure: 0.0
  deterministic_evaluator: "gfl_deterministic_reward_oracle"
  localization_contract:
    contract_id: "loc_target_locus_chr17"
    query_pattern: "ATGCGATCGATCG"
    target_sequence: "NNNNNATGCGATCGATCGNNNNN"
    mode: "exact_match"
    coordinate_system: "1_based_closed"
    strand_orientation: "dual_strand"
  computation_contract:
    contract_id: "comp_reading_frame_f1"
    computation_type: "translation"
    input_dna: "ATGCGATCGATCGTAA"
    reading_frame: 1
    expected_output: "MRSI*"
```

---

## 3. Supported Task Domains & Contracts

### 3.1 Sequence Localization (`SequenceLocalizationContract`)
- **Modes**:
  - `EXACT_MATCH`: Bitwise substring search.
  - `IUPAC_PATTERN`: Ambiguous nucleotide regex matching (`R`, `Y`, `S`, `W`, `K`, `M`, `B`, `D`, `H`, `V`, `N`).
  - `FUZZY_HAMMING`: Bounded mismatch distance search.
- **Coordinate Systems**:
  - `1_BASED_CLOSED`: Standard clinical, VCF, and UCSC visualization coordinates $[start, end]$.
  - `0_BASED_HALF_OPEN`: Standard BED, Python slicing, and BAM coordinates $[start, end)$.
- **Strand Orientations**:
  - `FORWARD`: Forward strand search (`+`).
  - `REVERSE`: Reverse-complement strand search (`-`).
  - `DUAL_STRAND`: Concurrent search on both strands.

### 3.2 Deterministic DNA Computations (`DNAComputationContract`)
- `TRANSCRIPTION`: $T \to U$ mRNA synthesis.
- `REVERSE_COMPLEMENT`: Watson-Crick canonical inversion ($A \leftrightarrow T$, $C \leftrightarrow G$).
- `TRANSLATION`: 6-frame translation (frames $+1, +2, +3$ and $-1, -2, -3$) translating triplets to standard amino acid single-letter codes with stop codons marked as `*`.
- `GC_SKEW_WINDOW`: Oligonucleotide compositional skew:
  $$\text{GC Skew} = \frac{G - C}{G + C}$$
- `ORF_DETECTION`: Identification of Open Reading Frames ($\ge \text{orf\_min\_len\_nt}$) bounded by start codon `ATG` and stop codons `TAA`, `TAG`, `TGA`.
- `RESTRICTION_DIGEST`: Enzymatic cleavage simulation at specific palindromic recognition motifs (e.g. EcoRI `G^AATTC`).

### 3.3 Verifiable Rewards (`VerifiableRewardContract`)
- Evaluates model predictions against ground truth or dynamically computes answers using deterministic sub-contracts.
- Emits cryptographic SHA-256 verification tokens binding the task ID, domain, candidate solution, and verification timestamp:
  $$\text{Proof} = \text{SHA256}(\text{task\_id} \parallel \text{domain} \parallel \text{candidate\_solution})$$

---

## 4. Architectural Boundaries

Per **ADR-ARCH-001** and GFL Core Invariants:
- **GFL Core**: Defines AST dataclasses, serialization protocols, grammar rules, and deterministic semantic validators.
- **GeneForge (`gf/`) / FineDNA Executors**: Consume GFL AST specifications to steer RLVR training policies, execute agentic verification tools, or reward model fine-tuning. GFL does not perform LLM training or heavy tensor computation.
