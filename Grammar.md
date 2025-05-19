# **GeneForgeLang Grammar Specification**

GeneForgeLang defines a **compact, symbolic and structured language** to describe and design biomolecular entities—DNA, RNA, and proteins—at multiple levels: sequence, structure, function, and regulation.

This grammar is inspired by existing biological coding systems (GenoCAD, Eugene, ProForma, ProGen), but introduces new mechanisms for **structural abstraction, semantic compactness**, and **cross-modality integration**.

---

## **1. Structural Prefix Convention**

Every GeneForgeLang sentence starts with a prefix that encodes both:

- The **molecular modality** (`d`, `r`, `p`)  
- The **structural level**:

| Symbol | Level         | Description                                |
|--------|---------------|--------------------------------------------|
| `~`    | Linear        | Raw sequence, primary structure            |
| `:`    | Secondary     | Structural motifs (e.g., helices, loops)   |
| `^`    | Tertiary      | Folded domains, 3D configuration           |
| `*`    | Quaternary    | Complex/multimeric interaction             |
| `!`    | Unknown       | Ambiguous/unspecified structure            |

### Examples

- `~d:` = Linear DNA  
- `^p:` = Folded protein  
- `:r:` = RNA stem-loop  
- `*p:` = Multimeric protein complex  

---

## **2. Core Grammar Units**

### 2.1 Modifiers and Symbols

| Symbol | Function                                   | Source            |
|--------|--------------------------------------------|-------------------|
| `*`    | Post-translational modification            | from ProForma     |
| `'`    | High conservation / emphasis               | GeneForgeLang     |
| `^`    | Epigenetic state (e.g., methylation)       | GeneForgeLang     |
| `@`    | Position/indexing                          | from ProForma     |
| `[]`   | Functional annotation / logical wrapper     | from Eugene       |
| `=`    | Explicit consequence (e.g. function)        | GeneForgeLang     |
| `/`    | Module junction or co-occurrence            | GeneForgeLang     |
| `:`    | Structure level indicator                   | GeneForgeLang     |
| `-`    | Sequence or domain linkage                  | GeneForgeLang     |

---

## **3. Module Syntax**

### 3.1 Sequence Regions

| Token        | Description               |
|--------------|---------------------------|
| `[EX]`       | Exon                      |
| `[IN]`       | Intron                    |
| `[UTR5]`     | 5' Untranslated Region    |
| `[UTR3]`     | 3' Untranslated Region    |
| `[TATA]`     | Promoter box              |
| `[TSS]`      | Transcription start site  |

### 3.2 Functional Domains and Motifs

| Expression           | Meaning                                  |
|----------------------|------------------------------------------|
| `Dom(Kin)`           | Kinase domain                            |
| `Mot(NLS)`           | Nuclear localization signal              |
| `Mot(PEST)`          | Degradation motif                        |
| `TF(GATA1)`          | Transcription factor binding motif       |
| `Ctrl{Enh+Sil}`      | Regulatory logic block                   |

### 3.3 Biochemical Events

| Expression           | Meaning                                  |
|----------------------|------------------------------------------|
| `K*Ac@27`            | Acetylation at Lysine 27                 |
| `Y*P@123`            | Phosphorylation of Tyrosine 123          |
| `^mC@-135`           | Methylated CpG at upstream position      |
| `[MUT:A>G@42]`        | A→G substitution at position 42         |
| `[DEL:9-12]`          | Deletion of codons 9 to 12              |
| `[INS:TG@55]`         | Insertion of TG at 55                   |

---

## **4. Logical Expressions and Rules**

| Form                          | Interpretation                                         |
|-------------------------------|--------------------------------------------------------|
| `Mot(PEST)=Deg`               | Motif induces degradation                             |
| `TF(GATA1)+Dom(HDAC)=Silence` | Binding with HDAC leads to transcriptional silencing |
| `if PTM(K*Ac) → Localize(Nucleus)` | Conditional logic via modification            |

---

## **5. Structural Examples**

### 5.1 Linear Coding Region

```text
~d:[TATA]ATGCTGAC[MUT:A>G@42][TF(GATA1)]^mC@-135
```

### 5.2 Folded Protein with Regulatory Motif

```text
^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)
```

### 5.3 Multimeric Complex

```text
*p:p53:p63↔LZ
```
### 5.4 BNF Grammar
<phrase> ::= <prefix><module_list>
<prefix> ::= "~d:" | ":r:" | "^p:" | "*p:" | "!p:"
<module_list> ::= <module> | <module> "-" <module_list>
<module> ::= "Dom(" <text> ")" | "Mot(" <text> ")" | ...
---

## **6. Integration with AI Models**

GeneForgeLang is designed to:

- Serve as **input/output format** for transformer-based generative models.
- Provide **symbolic structure** for LLMs trained on biological sequences.
- Enable **conditional generation** by parsing high-level semantic specs.
- Support **translation** into FASTA, SBOL, GenBank and ProForma-compatible outputs.

---

## **7. Applications**

- **Gene design** with functional and regulatory logic
- **Protein engineering** with explicit folding constraints
- **Variant simulation and codon optimization**
- **Human–AI co-design interfaces for synthetic biology**
- **Semantic annotation for omics pipelines**



---

## **Version**

Grammar Spec v0.9 (beta)  
© 2025 Fundación de Neurociencias (MIT License)
