# **GeneForgeLang Grammar Specification (v1.1)**

GeneForgeLang (GFL) is a **symbolic, structured, and cross-modality language** designed to represent, analyze, and simulate biomolecular entities—DNA, RNA, and proteins—at sequence, structural, functional, regulatory, and therapeutic levels.

Built on inspirations from GenoCAD, Eugene, ProForma, and SBOL, GFL introduces **semantic compactness**, **logical abstraction**, and **therapeutic modeling** for synthetic biology, molecular medicine, and AI reasoning.

---

## **1. Structural Prefix Convention**

Each GFL phrase starts with a **molecular prefix** combining:

- Molecular modality: `d` (DNA), `r` (RNA), `p` (protein)
- Structural abstraction:

| Symbol | Level      | Description                                   |
|--------|------------|-----------------------------------------------|
| `~`    | Linear     | Raw sequence, coding or non-coding            |
| `:`    | Secondary  | Structural motifs (stem-loops, alpha helices) |
| `^`    | Tertiary   | Folded domains, 3D configuration              |
| `*`    | Quaternary | Complex/multimeric interaction                |
| `!`    | Unknown    | Ambiguous/unspecified structure               |

**Examples:**

- `~d:` = Linear DNA  
- `^p:` = Folded protein  
- `:r:` = RNA stem-loop  
- `*p:` = Multimeric protein complex  

---

## **2. Core Grammar Units**

### 2.1 Symbols and Modifiers

| Symbol     | Function                                       | Origin        |
|------------|------------------------------------------------|---------------|
| `*`        | Post-translational modification                | ProForma      |
| `'`        | High conservation or emphasis                  | GeneForgeLang |
| `^`        | Epigenetic state (e.g. methylation)            | GeneForgeLang |
| `@`        | Index or positional reference                  | ProForma      |
| `[]`       | Logical annotation block                       | Eugene        |
| `{}`       | Metadata block for structured properties       | GFL           |
| `=`        | Causality or function mapping                  | GFL           |
| `/`        | Co-occurrence or module junction               | GFL           |
| `:`        | Structural prefix or operator indicator        | GFL           |
| `-`        | Sequential linkage                             | GFL           |
| `#`        | Human-readable comment (not parsed)            | GFL           |
| `TIME()`   | Timestamped expression                         | GFL           |
| `EFFECT()` | Describes biological or clinical outcome       | GFL           |
| `HYPOTHESIS:` | Formal logic premise                       | GFL           |
| `SIMULATE:`  | Predictive design block                      | GFL           |
| `PATHWAY:`   | Metabolic or regulatory sequence             | GFL           |
| `MACRO:`     | Reusable definition                          | GFL           |
| `USE:`       | Macro invocation                             | GFL           |

---

## **3. Modules and Functional Components**

### 3.1 Sequence-Level Units

| Token    | Description              |
|----------|--------------------------|
| `[EX]`   | Exon                     |
| `[IN]`   | Intron                   |
| `[UTR5]` | 5' Untranslated Region   |
| `[UTR3]` | 3' Untranslated Region   |
| `[TATA]` | Promoter box             |
| `[TSS]`  | Transcription start site |

### 3.2 Functional and Regulatory Elements

| Expression      | Meaning                           |
|-----------------|-----------------------------------|
| `Dom(Kin)`      | Kinase domain                     |
| `Mot(NLS)`      | Nuclear localization signal       |
| `Mot(PEST)`     | Degradation motif                 |
| `TF(GATA1)`     | Transcription factor binding site |
| `Ctrl{Enh+Sil}` | Combined enhancer/silencer logic  |

---

## **4. Mutation and Editing Logic**

### 4.1 Mutation Encoding with Provenance

| Syntax                | Meaning                    |
|------------------------|---------------------------|
| `[MUT:PAT:A>G@Q335X]`  | Paternal point mutation    |
| `[MUT:MAT:E>T@714X]`   | Maternal point mutation    |
| `[MUT:SOM:del@exon4]`  | Somatic deletion in exon 4 |

### 4.2 Genome Editing and RNA Engineering Operations

| Expression                      | Description                                        |
|--------------------------------|----------------------------------------------------|
| `EDIT:Base(A→G@123)`            | Base editing at position                          |
| `EDIT:Prime(INS:...)`           | Prime editing                                      |
| `EDIT:ARCUS(DEL:...)`           | ARCUS deletion                                     |
| `EDIT:RNA_Transport(R→T)`       | CRISPR-TO style spatial RNA localization           |

### 4.3 Structured Metadata for Edits

```gfl
EDIT:Base(G→A@Q335X){efficacy=partial, cells=liver}
EDIT:Base(A→T@123){rate=low, target=CPS1}
```

---

## **5. Therapeutic and Clinical Modeling**

### 5.1 Delivery and Administration

```gfl
DELIV(mRNA+LNP@IV)
DELIV(AAV9@IT)
```

### 5.2 Dosing and Chronology

```gfl
DOSE(1):EDIT:Base(G→A@Q335X)
TIME(0d):DELIV(mRNA@IV)
TIME(7d):EDIT:Base(G→A@Q335X)
```

### 5.3 Conditional and Functional Modeling

```gfl
if MUT(PAT:A>G@Q335X) then EDIT:Base(G→A@Q335X)
EFFECT(restore function=urea cycle)
```

### 5.4 Predictive and Declarative Reasoning

```gfl
HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)
SIMULATE: {EDIT:Base(...), OUTCOME:↓ammonia}
```
### 5.5 EFFECT Operator

| Syntax                          | Meaning                                        |
|----------------------------------|------------------------------------------------|
| `EFFECT(↑neurite_growth@24h)`    | Increase neurite growth after 24h             |

---

## **6. Pathway and Multi-omic Integration**

```gfl
PATHWAY: ARG+NH3 → CPS1 → Carbamoyl-P → OTC
TRANSCRIPTOME: ↑CPS1(mRNA)
PROTEOME: CPS1*P@K347
```

---

## **7. Macros and Abstractions**

```gfl
MACRO:EDIT_CPS1 = {
  DELIV(mRNA+LNP@IV)
  EDIT:Base(A→G@Q335X){target=CPS1}
}
USE:EDIT_CPS1
```

---

## **8. Integration with AI Models**

GeneForgeLang serves as:

- **Symbolic input/output layer** for LLMs (e.g., GeneForge Transformer, ProtGPT)
- **Generative prompt template** for editing or simulating variants
- **Interoperable exporter** to FASTA, GenBank, SBOL, ProForma
- **Anchor for reverse-engineering molecular edits from phenotype descriptions**

---

## **9. Applications**

- Gene therapy design with variant targeting logic  
- Protein modeling with motifs and functional tags  
- Human-AI codevelopment of synthetic pathways  
- Phenotype ↔ Genotype simulations  
- Clinical annotation pipelines for precision medicine  

---

## **Version**

**Grammar Spec v1.1** (post-CRISPR2 + logic/simulation extensions)  
© 2025 Fundación de Neurociencias — MIT License
