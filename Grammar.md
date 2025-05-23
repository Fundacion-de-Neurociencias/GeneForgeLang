# **GeneForgeLang Grammar Specification (v1.0)**

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

| Symbol | Function                                 | Origin        |
|--------|------------------------------------------|---------------|
| `*`    | Post-translational modification          | ProForma      |
| `'`    | High conservation or emphasis            | GeneForgeLang |
| `^`    | Epigenetic state (e.g. methylation)      | GeneForgeLang |
| `@`    | Index or positional reference            | ProForma      |
| `[]`   | Logical annotation block                 | Eugene        |
| `{}`   | Metadata block for structured properties | GFL v1.0      |
| `=`    | Causality or function mapping            | GFL           |
| `/`    | Co-occurrence or module junction         | GFL           |
| `:`    | Structural prefix or operator indicator  | GFL           |
| `-`    | Sequential linkage                       | GFL           |
| `#`    | Human-readable comment (not parsed)      | GFL           |

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

**Provenance types**: `PAT`, `MAT`, `SOM`, `GER`

### 4.2 Genome Editing Operations

| Expression                | Description                         |
|---------------------------|-------------------------------------|
| `EDIT:Base(A→G@Q335X)`    | Base editing at codon Q335X         |
| `EDIT:Prime(INS:CTT@27)`  | Prime editing: insert CTT at pos 27 |
| `EDIT:ARCUS(DEL:codon12)` | ARCUS editing to delete codon 12    |

**Supported editors**:
```json
{
  "ABE": "Adenine Base Editor",
  "CBE": "Cytosine Base Editor",
  "Prime": "Prime Editor",
  "Cas9": "Cas9 Endonuclease"
}
```

**Supported delivery types**:
```json
{
  "NP_mRNA": "Nanoparticle-delivered mRNA",
  "AAV": "Adeno-Associated Virus",
  "LNP": "Lipid Nanoparticle"
}
```

### 4.3 Structured Metadata for Edits

| Example                                               | Meaning                             |
|--------------------------------------------------------|-------------------------------------|
| `EDIT:Base(G→A@Q335X){efficacy=partial, cells=liver}` | Partial editing in liver cells      |
| `EDIT:Base(A→T@123){rate=low, target=CPS1}`           | Slow editing targeted to CPS1 gene  |

---

## **5. Therapeutic and Clinical Modeling**

### 5.1 Delivery and Administration

| Syntax               | Meaning                                  |
|----------------------|------------------------------------------|
| `DELIV(mRNA+LNP@IV)` | mRNA + lipid nanoparticle via IV         |
| `DELIV(AAV9@IT)`     | AAV serotype 9 via intrathecal injection |

### 5.2 Dosing and Chronology

```gfl
DOSE(1):EDIT:Base(G→A@Q335X)
DOSE(2):EDIT:Base(G→A@Q335X)
```

### 5.3 Conditional Logic

```gfl
if MUT(PAT:A>G@Q335X) then EDIT:Base(G→A@Q335X)
```

---

## **6. Structural Examples**

### 6.1 CRISPR Case — CPS1 Base Editing (with semantics)

```gfl
~d:[TATA]ATGCTGAC[MUT:PAT:Q>STOP@335][MUT:MAT:E>T@714]
EDIT:Base(STOP→Q@335){tool=K-ABE, efficacy=partial, cells=hepatocyte}
DELIV(mRNA+LNP@IV)
DOSE(1):EDIT:Base(STOP→Q@335)
```

### 6.2 Regulatory Protein Domain

```gfl
^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)
```

---

## **7. Formal Grammar (BNF Snippet)**

```bnf
<phrase> ::= <prefix> <module_list>
<prefix> ::= "~d:" | ":r:" | "^p:" | "*p:" | "!p:"
<module_list> ::= <module> | <module> "-" <module_list>
<module> ::= "Dom(" <text> ")" 
           | "Mot(" <text> ")" 
           | "EDIT:" <edit_expr> 
           | "MUT:" <mut_expr> 
           | ...
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

- **Gene therapy design** with variant targeting logic  
- **Protein modeling** with motifs and functional tags  
- **Human-AI codevelopment** of synthetic pathways  
- **Phenotype ↔ Genotype simulations**  
- **Clinical annotation pipelines for precision medicine**

---

## **Version**

**Grammar Spec v1.0 (Release)**  
© 2025 Fundación de Neurociencias — MIT License  
