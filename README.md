# 🧬 GeneForgeLang: Symbolic-to-Sequence Protein Design Toolkit

GeneForgeLang is a symbolic language and toolset for generative biology. It connects high-level biological design intentions to low-level amino acid sequences via AI, rules, and natural language.

---

## 🚀 Features

| Module                      | Description |
|----------------------------|-------------|
| 🧠 Phrase → Protein         | Generate realistic protein sequences from symbolic phrases |
| 🧪 Protein → Phrase         | Infer functional motifs from amino acid sequences |
| 📖 Phrase → Description     | Translate symbolic design into scientific English |
| 🧬 Mutate Protein           | Generate variants of proteins from the same symbolic seed |
| 📦 Export to FASTA          | Download generated proteins for downstream use |
| 📊 Analyze Protein          | Visualize amino acid composition as bar plot |
| 📚 Symbolic Language        | GeneForgeLang syntax allows structured protein definitions |

---

## 🧪 Example

### Input Phrase:
^p:Dom(Kin)-Mot(NLS)*AcK@147=Localize(Nucleus)

yaml
Copiar
Editar

### Output:
- Seed: `MKKK`
- Generated protein: realistic sequence (via ProtGPT2)
- Properties: length, charge, MW
- Description: *“This protein contains a kinase domain, a nuclear localization signal, and lysine acetylation at a specific position.”*
- Export: `.fasta` format
- Graph: bar plot of amino acid composition

---

## ▶️ How to Use

1. Clone this repo
2. Install dependencies:
```bash
pip install -r requirements.txt
Launch the interface:

bash
Copiar
Editar
python app.py
Navigate to:

cpp
Copiar
Editar
http://127.0.0.1:7860
📁 Repository Structure

File	Description
app.py	Main UI app with all functionality
semillas.json	Phrase-to-seed dictionary
translate_to_geneforgelang.py	Reverse translator
README.md	This file
requirements.txt	Python dependencies
🧠 Developed by
Fundación de Neurociencias
Licensed under the MIT License

Join us in shaping symbolic bio-AI.

yaml
Copiar
Editar

