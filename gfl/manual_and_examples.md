# 📘 GeneForgeLang Manual and Example Files

This document serves as both a usage guide and a repository of illustrative `.gfl` examples for using **GeneForgeLang (GFL)**. It is intended to support users, developers, and model designers who want to encode, simulate, or analyze gene editing and regulatory effects in a symbolic and structured way.

---

## 🧠 What is GFL?

**GeneForgeLang (GFL)** is a symbolic domain-specific language designed to represent genetic edits, molecular targets, functional consequences, biological pathways, and predicted phenotypic effects.

GFL serves as the input layer to the **GeneForge** inference and simulation engine.

---

## 🔧 Core Concepts

- **Edit**: a genetic modification, such as a SNP, deletion, insertion, or replacement.
- **Target**: a molecular entity impacted by the edit (gene, protein, RNA, enhancer).
- **Effect**: a consequence at the functional, expression, or structural level.
- **Pathway**: a known biological process that may be disrupted.
- **Link**: a directional causal relation between components.
- **Simulate**: a prediction task that links upstream events to phenotypic outcomes.

---

## 🧬 Syntax Example: Basic Oncogene Disruption

```gfl
edit(SNP:rs1042522)
target(gene:TP53)
effect(function:loss_of_function)
pathway(p53:cell_cycle_arrest)
link(edit->target)
link(target->effect)
link(effect->pathway)
simulate(tumorigenesis)
```

---

## 🧬 Syntax Example: Enhancer Perturbation

```gfl
edit(DEL:chr8_128726000_128728000)
target(enhancer:MYC_superenhancer)
effect(expression:downregulated)
target(gene:MYC)
pathway(MYC:proliferation)
link(edit->target)
link(target->effect)
link(effect->pathway)
simulate(hypoproliferation)
```

---

## 🧬 Syntax Example: RNA Mislocalization in Neurodegeneration

```gfl
edit(SNP:rs123456)
target(RNA:tau_mRNA)
effect(localization:cytoplasmic_retention)
pathway(tau:axonal_transport)
simulate(neurodegeneration)
```

---

## 📂 File Format

- File extension: `.gfl`
- Encoding: UTF-8
- Each statement must be in a single line.
- Blocks of statements may be parsed and represented as abstract syntax trees (ASTs).

---

## 📤 Interoperability

GFL scripts can be:

- Parsed by `gfl/parser.py` into structured dictionaries (AST)
- Interpreted by `inference_engine.py` for prediction
- Validated via `validation_pipeline.py` with real omics datasets
- Visualized via HEVisum integration (WIP)

---

## ✅ Next Steps

To test your `.gfl` scripts:
1. Place them in `gfl/examples/`
2. Use `parser.py` to load and convert to AST
3. Run `inference_engine.predict_effect()` or `simulate()`

---

## 📁 Example File: `examples/oncogene_editing.gfl`

```gfl
edit(SNP:rs1042522)
target(gene:TP53)
effect(function:loss_of_function)
pathway(p53:apoptosis)
link(edit->target)
link(target->effect)
link(effect->pathway)
simulate(tumorigenesis)
```

---

## 📁 Example File: `examples/phenotype_simulation.gfl`

```gfl
edit(REPL:chr7_55181320:C>T)
target(gene:BRAF)
effect(function:constitutive_activation)
pathway(MAPK:cell_proliferation)
simulate(cutaneous_melanoma)
```

---

For additional features, version control, or cross-ontology mapping, please refer to the upcoming `gfl/extensions/` and `docs/ontology_mapping.md`.
