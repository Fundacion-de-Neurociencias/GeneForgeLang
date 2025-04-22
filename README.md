# 🧬 GeneForgeLang: A Semantic Language for Protein Design

**GeneForgeLang** is a symbolic, human-readable, and machine-optimizable language to express biological design intentions across DNA, RNA, and protein space. This repository demonstrates how to:

- 🧠 Translate symbolic phrases into protein sequences using ProtGPT2
- 🔁 Translate generated proteins back into GeneForgeLang phrases
- ⚙️ Use AI-assisted generation and rule-based interpretation together

---

## 📁 Project Structure

| File                              | Description |
|-----------------------------------|-------------|
| `generar_desde_frase.py`          | Generates a protein from a fixed GeneForgeLang phrase. |
| `generar_desde_frase_input.py`    | Generates a protein from a user-specified phrase (command-line). |
| `generar_desde_frase_json.py`     | Same as above, but reads phrase logic from `semillas.json`. |
| `semillas.json`                   | Dictionary of symbolic phrase patterns and protein seeds. |
| `translate_to_geneforgelang.py`   | Reverse translator: interprets a protein sequence and generates a GeneForgeLang phrase. |

---

## ▶️ Usage

### 🔹 Forward Translation (GeneForgeLang → Protein)

Run:

```bash
python generar_desde_frase_json.py "^p:Dom(Kin)'-Mot(NLS)*P@147=Localize(Membrane)"
```

Output:

```
🧪 Semilla generada desde la frase: MKKK
🧬 Proteína generada:
MKKKAAKRRKKKPPRELPAAAGG...
```

### 🔹 Reverse Translation (Protein → GeneForgeLang)

Run:

```bash
python translate_to_geneforgelang.py MKKKGETSTKEEEKQHEIKEEEKKEVVKKEVVKKEEGEKEKEKEKEKEKEKE
```

Output:

```
🔍 GeneForgeLang:
^p:Dom(Kin)-Mot(NLS)-Mot(PEST)
```

---

## 🔬 How It Works

### 🧠 GeneForgeLang phrases

Are symbolic representations like:

```
^p:Dom(Kin)-Mot(NLS)*AcK@147=Localize(Nucleus)
```

Which express:
- The molecule and its structural layer (`^p:` = tertiary protein)
- Functional domains and motifs (`Dom(Kin)`, `Mot(NLS)`)
- Modifications (`*AcK@147`)
- Expected effect or destination (`=Localize(Nucleus)`)

### 🧪 Protein Generation

These phrases are converted to seed fragments (`MKKK`, `MPRRR`, etc.) and completed using **ProtGPT2**, a protein language model hosted on Hugging Face.

### 🔁 Reverse Interpretation

The tool analyzes patterns like:
- Poly-K or MKKK → `Dom(Kin)`
- PRKR, PKKKRKV → `Mot(NLS)`
- High E/D content → `Mot(PEST)`
- Specific motifs like `QAK` → `*AcK@X`

And reconstructs a symbolic design phrase.

---

## 🔐 License

MIT License © 2025 Fundación de Neurociencias  
Contributions welcome under open standards.

---

## 🤝 Contribute

1. Fork this repository
2. Add new phrase-to-seed mappings in `semillas.json`
3. Propose new detection rules in `translate_to_geneforgelang.py`
4. Submit a pull request

---

## 📣 Stay tuned

This is part of the **GeneForge Project**, a generative open-source AI toolkit for protein, RNA, and DNA design.

Explore:
- [GeneForgeLang grammar](https://github.com/Fundacion-de-Neurociencias/geneforge-lang)
- [Spaces (coming soon)](https://huggingface.co/spaces)