# 🧬 GeneForgeLang: Symbolic-to-Sequence & Cross-Modality Biomolecular Design Toolkit

**GeneForgeLang (GFL)** is a symbolic, generative language that allows scientists to **design, analyze and simulate** DNA, RNA, and protein structures with unified syntax and AI-compatible logic.

---

## 🌐 What It Enables

- ✅ Symbolic design of gene therapies, edits, enhancers, and protein domains
- 🔁 Cross-modality conversion: DNA ↔ RNA ↔ Protein
- 🧠 Causal and conditional logic: `if A then B`, `EDIT(...)`, `EFFECT(...)`
- 🧬 Multi-level modeling with time, dosage, pathway, and simulation
- 📡 Integration with AI models for code generation and interpretation

---

## 🚀 Core Features

| Module                  | Description                                                             |
|-------------------------|-------------------------------------------------------------------------|
| 🧠 Phrase → Protein      | Generate realistic protein sequences from symbolic phrases              |
| 🔁 Transcode Molecules   | Translate GeneForgeLang phrases between DNA, RNA, and Protein           |
| 📖 Phrase → English      | Interpret symbolic code into natural scientific language                |
| 🧬 Enhancer Generator    | Create regulatory sequences with TF logic and conditionals              |
| 🔮 Simulate Edits        | Predict outcomes via `SIMULATE:` and `HYPOTHESIS:` logic                |
| ⏳ Timeline & Dosing     | Represent `DOSE(n)` and `TIME(n):` blocks for therapeutic modeling      |
| ⚙️ AI-Ready Interface     | Compatible with transformers like ProtGPT2, GeneForgeTransformer         |

---

## 🧪 Example Input Phrases

### DNA → RNA

```gfl
~d:[TATA]-ATG-[EX]-[IN]-[EX2]
↓
:r:Cap5'-Ex1-Ex2-UTR3'
```

### RNA → Protein

```gfl
:r:Ex1-Ex2
↓
^p:Dom(Kin)-Mot(NLS)*AcK@147
```

---

## 🔬 In Vivo Gene Editing Example (CRISPR 2.0)

```gfl
~d:[TATA]CPS1[MUT:PAT:A>G@1001]
EDIT:Base(A→G@1001){efficacy=partial, cells=liver}
DELIV(mRNA+LNP@IV)
DOSE(1):EDIT:Base(A→G@1001)
TIME(0d):DELIV(...)
EFFECT(restore function=urea cycle)
HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)
SIMULATE: {EDIT:Base(...), OUTCOME:↓ammonia}
MACRO:FIX1 = {DELIV(...) - EDIT:Base(...)}
USE:FIX1
```

---

## 🧬 Enhancer Design Example: ARE Activation

```yaml
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
```

📂 See: `examples/enhancer_ARE_example.ipynb`

---

## ▶️ How to Use this Example

### 1. Clone the repo:

```bash
git clone https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git
cd GeneForgeLang
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Launch the app:

```bash
python app.py
```

Then open:

[http://127.0.0.1:7860](http://127.0.0.1:7860)

---

## 📁 File Overview

| File                             | Description                                                |
|----------------------------------|------------------------------------------------------------|
| `app.py`                         | Gradio interface with parser and editor                    |
| `parser.py`                      | Main GFL parser with logic, edits, macros, and more        |
| `parser_notebook.ipynb`          | Jupyter notebook for interactive parsing                   |
| `semillas.json`                  | Test cases and GFL templates                               |
| `geneforge_grammar.json`         | Structured grammar definitions and mappings                |
| `syntax.md`                      | Formal syntax specification (EBNF-like)                    |
| `grammar.md`                     | Full grammar and symbolic logic for GFL                    |
| `test_parser.py`                 | Unit tests with `pytest` for new blocks and logic          |
| `examples/enhancer_ARE_example.ipynb` | Enhancer design notebook                              |
| `requirements.txt`              | Python dependencies                                        |
| `README.md`                      | This file                                                  |

---

## 🧠 Developed By

**Fundación de Neurociencias**  
Project lead: *Manuel Menéndez González*  
Licensed under the **MIT License**

Join us in shaping symbolic bio-AI.  
📬 Contributions welcome via [issues](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues) or pull requests!

---

## 🚀 GeneForgeLang — Project Status (June 2025)

**GeneForgeLang (GFL)** is a declarative DSL and autonomous engine for planning, simulating, and adaptively executing genetic and omics experiments.

- **Robust pipeline:** Runs experiments defined in the DSL with automatic adaptive logic.
- **Real integration:** Executes Scanpy pipelines on real `.h5ad` data.
- **Automatic feedback:** Dynamically adjusts the AST based on experimental results.
- **Resilient:** Never crashes, always reports clear status and error reasons.
- **Ready for:** multi-omics, plugins, advanced reporting, web/CLI dashboards.

### Quick example execution

```bash
python -m scripts.fix_and_demo
Requires a .h5ad file in data/example.h5ad (an example is provided).

You can edit experimental parameters in examples/example1.gfl.

Documentation & Support
Main repo: https://github.com/Fundacion-de-Neurociencias/GeneForgeLang

Fundación de Neurociencias

For questions, contributions, or troubleshooting: contact the project maintainer.


---

## Example: Running a basic scRNA-seq pipeline

You can run a real demo pipeline using the included GFL example:

```bash
python applications/launch_pipeline.py
This will parse, adapt, and (optionally) execute the experiment steps defined in applications/pipeline_basic_scRNA.gfl.


---

## Example: Running a basic scRNA-seq pipeline

You can run a real demo pipeline using the included GFL example:

```bash
python applications/launch_pipeline.py
This will parse, adapt, and (optionally) execute the experiment steps defined in applications/pipeline_basic_scRNA.gfl.

