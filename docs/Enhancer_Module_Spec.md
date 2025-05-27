# 🧬 GeneForge Enhancer Module

## Overview

This module enables the generation of **synthetic enhancer sequences** that regulate gene expression in a **cell-type-specific** and **transcription-factor-aware** manner. Enhancers are short DNA sequences that act as switches to turn genes on/off or modulate their expression. This capability expands GeneForge beyond protein and RNA generation into **regulatory genomic design**.

---

## 💡 Functionalities

* Generate synthetic enhancers from scratch (*de novo*).
* Predict enhancer strength and tissue specificity.
* Model transcription factor (TF) binding site composition.
* Simulate the impact of enhancer variants on gene expression.
* Export in FASTA, YAML (GeneForgeLang), and JSON formats.

---

## 🧩 Input Schema (YAML)

```yaml
- enhancer:
    name: "EPO_Hematopoietic_Enhancer"
    target_gene: "EPO"
    cell_type: "hematopoietic_progenitor"
    species: "Mus musculus"
    factors: ["GATA1", "KLF1", "TAL1"]
    goal: "upregulate"
    model: "GeneForgeEnhancerGen-v1"
    validate_in_silico: true
    simulate_context: "blood_lineage"
```

---

## 📤 Output Example

```json
{
  "sequence": "AGGTCAGGCTGATAACCTTGTAGGTCA...",
  "binding_sites": [
    {"TF": "GATA1", "pos": 17, "score": 0.93},
    {"TF": "KLF1", "pos": 45, "score": 0.88}
  ],
  "predicted_activity": 0.87,
  "tissue_specificity": "hematopoietic cells"
}
```

---

## 🛠️ Training Datasets

* ENCODE
* FANTOM5
* VISTA Enhancer Browser
* Cell-type-specific ATAC-seq/ChIP-seq datasets

---

## 🔬 Use Cases

* Control expression of therapeutic genes
* Modulate cell fate (e.g., hematopoietic vs neuronal)
* Build gene circuits for synthetic biology
* Test enhancer variants for disease-linked genes

---

## 📦 Integration in Repo

Place this module in the folder: `enhancer_design/`

* Add a README inside `enhancer_design/` explaining usage and schema.
* Add inference and example notebooks under `examples/`.
* Add the YAML parser in `gene_tokenizer/yaml_parser.py`
* Register the enhancer model in `model/gene_transformer.py`

---

## ✅ Next Steps

* Validate output using enhancer-promoter reporter assays.
* Support enhancer-blocker-insulator relationships.
* Cross-species enhancer translation using alignment modules.

---

## 👥 Contributors

GeneForge Team @ Fundación de Neurociencias
