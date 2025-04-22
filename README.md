# GeneForgeLang: A Unified Generative Language for Biomolecular Design

GeneForgeLang is a novel symbolic and generative language designed to represent, interpret, and generate biomolecular constructs—including DNA, RNA, and proteins—while integrating structural, regulatory, and biochemical modifications. It combines insights from previous efforts in synthetic biology grammar (e.g., GenoCAD, Eugene), protein design (ProForma, ProGen, ESM), and regulatory motif syntax (splicing code, enhancer grammar), but introduces a **unified, multi-layer, generative framework** that is both human-readable and machine-optimizable.

---

## Conceptual Foundations

GeneForgeLang integrates concepts and techniques from several pioneering frameworks:

- **GenoCAD**: Inspired our modular, grammar-based composition rules. Like GenoCAD’s part-based grammar, we define permitted syntactic arrangements of functional units.
- **Eugene DSL**: Influenced our rule-based approach to specifying construct architecture and constraints.
- **ProForma**: Informed our inline annotation system for post-translational modifications and variant representations.
- **Enhancer and Splicing Grammars**: Guided our logic for motif combinations and regulatory outcomes.
- **ProGen and ESM**: Reinforced the feasibility of language models that learn and generate biologically valid sequences.
- **Protein Design Languages** (e.g., Hie et al., 2022): Inspired our vision of combining symbolic syntax with generative AI.

GeneForgeLang builds on these, aiming to unify structure, function, and regulatory logic across molecular scales.

---

## What's New in GeneForgeLang

GeneForgeLang builds on established tools and conventions while extending them with key innovations:

### **Incorporated from Existing Frameworks**
- **Domain Grammar Concepts**: Inspired by GenoCAD and Eugene, GeneForgeLang supports context-aware arrangement of genetic and protein parts.
- **PTM Notation**: Compatible with ProForma's inline PTM representation for precise biochemical modifications.
- **Motif & Splicing Code Modeling**: Acknowledges motif-based logic from enhancer grammar and splicing codes to represent regulatory syntax.
- **Transformer Compatibility**: Aligns with techniques from ProGen, ESM, and related protein LLMs by using token structures that are trainable and interpretable.

### **Novel Contributions**
- **Unified Multi-Scale Grammar**: For the first time, a language spans DNA, RNA, and proteins—combining sequence, structure (secondary, tertiary, quaternary), domains, regulatory logic, and PTMs.
- **Structural Level Prefixes**: GeneForgeLang introduces structural markers (e.g., `~`, `:`, `^`, `*`) that define the semantic layer (linear, secondary, tertiary, quaternary), extending conventional linear views.
- **Compact, Accent-Based Syntax**: Incorporates linguistic economy with accents, capitalization, and symbolic modifiers to encode conservation, importance, ambiguity, and epigenetic state.
- **Cross-Modality Compilation**: Allows linking a regulatory sequence (`~d:`), spliced mRNA structure (`:r:`), and folded protein function (`^p:`) in a single design spec.
- **Human-Readable, Programmatic Specification**: Offers a domain-specific language format that scientists can write, interpret, and compile with generative AI.

---

## Syntax Quick Guide

The structural prefix system in GeneForgeLang—`~`, `:`, `^`, `*`—is partially inspired by layered representations of biomolecules in tools such as **ProForma** (used to annotate protein modifications) and structural prediction platforms like **AlphaFold**, which highlight the significance of secondary, tertiary, and quaternary configurations. GeneForgeLang formalizes this multi-layered logic into its core syntax, ensuring both symbolic clarity and computational utility across DNA, RNA, and protein modalities.

### Prefix: `<structure><molecule>:`
- `~d:` Linear DNA
- `:r:` RNA Secondary Structure
- `^p:` Protein Tertiary Structure
- `*p:` Protein Complex (Quaternary)
- `!r:` Ambiguous/undefined structure RNA

### Modifiers and Symbols

Some of the following symbols are adapted from established frameworks like ProForma (e.g., `*` for post-translational modifications and `@` for positional indexing), ensuring compatibility with proteomics standards. Others, such as `'` for conservation or emphasis, and `/` for symbolic junctions or hybrid modularity, are original contributions of GeneForgeLang designed to improve linguistic expressiveness and semantic clarity in sequence representation.
- `*` = PTM (e.g. `K*Ac`) [ProForma-compatible]
- `'` = Conservation/accent (e.g. `Y'`) [original from GeneForgeLang]
- `^` = Epigenetic (e.g. `^mC`) [novel integration with sequence]
- `[]` = Annotations (e.g. `[TF(GATA1)]`) [inspired by Eugene constraint blocks]
- `@` = Position (e.g. `K@27`)
- `=` = Consequence (e.g. `Mot(PEST)=Deg`)
- `:` = Structure scope
- `/` = Module junctions (e.g. `Dom(Kin)/Mot(NLS)`)

### Example
```text
^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)
~d:[TATA]atgCTGAC[MUT:A>G@42][TF(GATA1)]^mC@-135
*r:p53:p63↔LZ
```

---

## How It Works
GeneForgeLang can be interpreted by both humans and AI systems:
- Parse and annotate biological sequences.
- Generate candidates using transformer models trained on biomolecular syntax.
- Connect DNA → RNA → protein in a symbolic pipeline.
- Export to standard formats or link with structure predictors.

### Visual Workflow
```
Design Intent (GeneForgeLang spec)
        ↓
 Symbolic Compiler (Parser/Tokenizer)
        ↓
 Sequence Generator (Transformer / LLM)
        ↓
 Biological Validator / Structural Predictor (AlphaFold, RNAfold...)
        ↓
 Annotated Output / Variant Designer / MO Interface
```

---

## License
MIT License © 2025 Fundación de Neurociencias

---

## Authors
GeneForgeLang is developed by Fundación de Neurociencias. It integrates community standards and scientific advances while proposing a new, unified grammar for the next generation of biological design.

This project acknowledges foundational contributions from:
- GenoCAD
- Eugene DSL
- ProForma Notation
- Splicing Code Project
- ProGen / ESM Protein Language Models
- High-Level Protein Design Programming Languages

Join the project. Help refine the syntax. Shape the language of life.
