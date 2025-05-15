# 🧬 GeneForgeLang: Symbolic-to-Sequence & Cross-Modality Biomolecular Design Toolkit

**GeneForgeLang** is a symbolic, generative language that allows scientists to design and interpret DNA, RNA, and protein sequences with unified syntax and AI support.

This toolkit enables:
- Generation of realistic proteins from symbolic design
- Translation of symbolic phrases across DNA ↔ RNA ↔ Protein
- Structured, human-readable and AI-trainable syntax
- Semantic equivalence across molecular layers

---

## 🚀 Features

| Module                      | Description |
|----------------------------|-------------|
| 🧠 Phrase → Protein         | Generate realistic protein sequences from symbolic phrases |
| 🔁 Transcode Across Molecules | Translate GeneForgeLang phrases between DNA, RNA, and Protein |
| 📚 Universal Grammar        | One structure to rule them all: motifs, domains, PTMs, splicing |
| 🧬 Compact Notation         | Prefixes, accents, and structural markers for efficiency |
| 🧠 AI-Ready Output          | Compatible with transformer-based models like ProtGPT2 |

---

## 🧪 Example Input Phrases

### DNA → RNA

~d:Prom-Exon1-Intr1-Exon2 ↓ :r:Cap5'-Ex1-Ex2-UTR3'

shell
Copiar
Editar

### RNA → Protein

:r:Ex1-Ex2 ↓ ^p:Dom(Kin)-Mot(NLS)

🧪 Enhancer Design Example: ARE Activation
We include a new example notebook that demonstrates the design of a synthetic enhancer targeting the antioxidant response element (ARE) pathway.

📂 examples/enhancer_ARE_example.ipynb

This example shows how to:

Define an enhancer targeting the NFE2L2 (NRF2) pathway

Use the GeneForge enhancer generator to create regulatory DNA fragments

Specify desired transcription factors like MAFG, NFE2L2, ATF4

Simulate output and logic constraints

Example YAML input (GeneForgeLang):

<pre><code>enhancer: name: "ARE_Synthetic_Enhancer" target_gene: "NQO1" cell_type: "hepatocyte" species: "Homo sapiens" factors: - NFE2L2 - MAFG - ATF4 goal: "activate" model: "GeneForgeEnhancerGen-v1" </code></pre>
This is a showcase of how GeneForgeLang can describe and execute genetic programming logic with natural and regulatory semantics.

---

## ▶️ How to Use

1. Clone this repo
2. Install dependencies:
```bash
pip install -r requirements.txt
Launch the interface:

python app.py
Navigate to:
http://127.0.0.1:7860
📁 Files

File	Description
app.py	Full Gradio app (all tabs)
semillas.json	Seed dictionary
transcoder.py	Script for DNA/RNA/protein conversion
requirements.txt	Python dependencies
README.md	This file
🧠 Developed by
Fundación de Neurociencias
MIT License

Join us in shaping symbolic bio-AI.
