🧬 GeneForgeLang: Symbolic-to-Sequence & Cross-Modality Biomolecular Design Toolkit
GeneForgeLang is a symbolic, generative language that allows scientists to design and interpret DNA, RNA, and protein sequences with unified syntax and AI support.

This toolkit enables:

Generation of realistic proteins from symbolic design

Translation of symbolic phrases across DNA ↔ RNA ↔ Protein

Structured, human-readable and AI-trainable syntax

Semantic equivalence across molecular layers

Synthetic enhancer design with cell-specific transcription factor logic

🚀 Features
Module	Description
🧠 Phrase → Protein	Generate realistic protein sequences from symbolic phrases
🔁 Transcode Molecule Types	Translate GeneForgeLang phrases between DNA, RNA, and Protein
📖 Phrase → English	Interpret symbolic code into scientific natural language
🧬 Enhancer Generator	Create synthetic regulatory sequences (e.g., ARE elements)
📚 Universal Grammar	Compact notation with motifs, domains, PTMs, and splicing
🔄 Sequence → Phrase (WIP)	Infer functional representation from sequences
⚙️ AI-Ready Interface	Compatible with transformer-based models like ProtGPT2

🧪 Example Input Phrases
DNA → RNA
~d:Prom-Exon1-Intr1-Exon2
↓
:r:Cap5'-Ex1-Ex2-UTR3'

RNA → Protein
:r:Ex1-Ex2
↓
^p:Dom(Kin)-Mot(NLS)*AcK@147

🧬 Enhancer Design Example: ARE Activation
We include a working notebook demonstrating the design of a synthetic enhancer targeting the antioxidant response element (ARE) pathway.

📂 examples/enhancer_ARE_example.ipynb

This shows how to:

Define an enhancer targeting NQO1 via the NRF2 pathway

Use the GeneForge enhancer generator to create regulatory DNA fragments

Specify transcription factors like NFE2L2, MAFG, ATF4

Simulate transcriptional logic for activation in hepatocytes

GeneForgeLang YAML example:

enhancer:
name: "ARE_Synthetic_Enhancer"
target_gene: "NQO1"
cell_type: "hepatocyte"
species: "Homo sapiens"
factors:
- NFE2L2
- MAFG
- ATF4
goal: "activate"
model: "GeneForgeEnhancerGen-v1"

This is a live demonstration of how GeneForgeLang enables symbolic and modular genetic programming.

▶️ How to Use
Clone this repo:

git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang

Install dependencies:

pip install -r requirements.txt

Launch the app:

python app.py

Open in browser:
http://127.0.0.1:7860

📁 File Overview
File	Description
app.py	Full Gradio app (all tabs)
semillas.json	Phrase-to-seed dictionary
transcoder.py	DNA/RNA/protein converter
generate_from_phrase.py	AI-based generator from GFL
describe_phrase.py	English interpretation module
translate_to_geneforgelang.py	Inference engine: Sequence → Phrase
examples/enhancer_ARE_example.ipynb	Notebook for enhancer design
requirements.txt	Python dependencies
README.md	This file

🧠 Developed by
Fundación de Neurociencias
Project lead: Manuel Menéndez González
Licensed under the MIT License

Join us in shaping symbolic bio-AI. Contributions are welcome!
