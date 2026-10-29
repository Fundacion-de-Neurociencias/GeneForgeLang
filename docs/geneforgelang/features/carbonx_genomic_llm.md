# Carbon-X Genomic Foundation LLM Integration

## 1. Overview
**Carbon-X** (`HuggingFaceBio/Carbon-X`) is a frontier 14.8-billion parameter genomic foundation language model designed for deep DNA sequence understanding and molecular reasoning. Built upon the Qwen3-14B backbone, Carbon-X combines standard natural language text reasoning with a specialized vocabulary of **5,515 6-mer DNA tokens**.

With a context window of **40,960 tokens**, Carbon-X can process up to **~245,760 bp** ($245.76\text{ kb}$) of contiguous genomic DNA in a single forward pass, spanning entire genes, complex mammalian promoter-enhancer topologies, and non-coding regulatory hubs.

In GeneForgeLang (GFL), Carbon-X is exposed through first-class declarative contracts (`genomic_llm:` / `carbonx:`), biophysical validation, and local execution on sovereign hardware nodes.

---

## 2. GFL Declarative Syntax

```yaml
genomic_llm:
  name: "dctn1_promoter_variant_reasoning"
  model: "carbonx-14b"
  task_type: "variant_effect_reasoning"
  max_context_tokens: 40960
  temperature: 0.2
  target_locus:
    chrom: "chr2"
    start: 74588200
    end: 74591200
    strand: "+"
    assembly: "GRCh38"
    gene_symbol: "DCTN1"
  query:
    prompt: "Analyze the regulatory disruption of non-coding variant rs12345 in the DCTN1 promoter. Assess its impact on SP1 transcription factor binding and retrograde motor neuron transport."
    task_type: "variant_effect_reasoning"
    variant_delta:
      ref: "C"
      alt: "T"
      pos: 74589320
    sequence: "GGGCGGGGCGGGCCGCTAGCTAGCTAGCGATCGATCGATCGATCGATCGCGCTAGCTA"
    max_new_tokens: 1024
  metadata:
    organism: "Homo sapiens"
    disease_context: "Amyotrophic Lateral Sclerosis / Frontotemporal Dementia"
```

---

## 3. Supported Task Types
Carbon-X in GFL formalizes five primary reasoning paradigms:

| Task Type | Description |
| :--- | :--- |
| `variant_effect_reasoning` | Evaluates single nucleotide alterations and indels on transcription factor binding, splicing, and CpG methylation. |
| `locus_annotation` | Structural annotation of core promoters (TATA, CAAT, SP1, Inr), enhancers, CAGE peaks, and chromatin boundaries. |
| `promoter_generation` | De novo generation of synthetic regulatory elements optimized for targeted expression and tissue specificity. |
| `pathway_impact` | Traces downstream signaling and phenotypic pathways impacted by expression changes at the target locus. |
| `chat_with_dna` | Interactive conversational reasoning directly grounded in contiguous sequence context. |

---

## 4. Tokenization & Context Window Mechanics
- **6-mer DNA Tokenizer**:
  $$\text{DNA Tokens} = \left\lceil \frac{\text{len(DNA)}}{6} \right\rceil$$
- **Max DNA Capacity**: $40,960 \times 6 = 245,760\text{ bp}$.
- **Hybrid ChatML Framing**:
  ```text
  <|im_start|>system
  You are Carbon-X, a frontier genomic foundation language model...<|im_end|>
  <|im_start|>user
  Task: Variant Effect Reasoning. Evaluate the regulatory...
  Target Locus: GRCh38 chr2:74588200-74591200 (+) | Associated Gene: DCTN1
  Variant Alteration: C > T at position 74589320
  <|dna_start|>GGGCGG GGCGGG CCGCTA...<|dna_end|>
  Analyze the regulatory disruption...<|im_end|>
  <|im_start|>assistant
  ```

---

## 5. Sovereign Deployment on Apple Silicon (M4 Max)
To adhere to institutional compliance, zero cloud data exfiltration, and the owner's privacy rule (no personal data on the Mac Studio), Carbon-X is hosted locally on the Mac Studio node (`PCMARIOOLDEPI.ISPA.local`, 64 GB unified memory):
- **Script**: `scripts/deploy_carbonx_macstudio.sh`
- **Inference Server**: `llama-cpp-python` with Apple Metal GPU acceleration (`-DGGML_METAL=on`).
- **Endpoint**: `http://10.48.3.222:8000/v1/chat/completions`.
- **Offline Fallback**: When the remote server is unreachable, `CarbonXEngine` performs deterministic biophysical evaluation with GC/CpG profiling and motif preservation analysis marked with `evidence_status = "carbonx_offline_evaluation"`.
