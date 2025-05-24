# GeneForgeLang Grammar Specification (v1.2)

GeneForgeLang (GFL) is a symbolic, structured, cross-modality, and reasoning-enhanced language designed to represent, analyze, simulate, and deduce properties of biomolecular systems—DNA, RNA, proteins, gene therapies, and synthetic biological constructs.

Built from GenoCAD, ProForma, SBOL, and AI logic grammars, GFL introduces semantic compactness, logical abstraction, therapeutic modeling, and causal reasoning for synthetic biology, molecular medicine, and AI automation.

---

## 1. Structural Prefix Convention

Each GFL phrase starts with a molecular prefix combining:

- Molecular modality: `d` (DNA), `r` (RNA), `p` (protein)
- Structural abstraction:

| Symbol | Level      | Description                                   |
|--------|------------|-----------------------------------------------|
| `~`    | Linear     | Raw sequence, coding or non-coding            |
| `:`    | Secondary  | Structural motifs (stem-loops, helices)       |
| `^`    | Tertiary   | Folded domains, 3D configuration              |
| `*`    | Quaternary | Complex/multimeric interaction                |
| `!`    | Unknown    | Ambiguous/unspecified structure               |

Examples:
- `~d:` = Linear DNA  
- `^p:` = Folded protein  
- `:r:` = Structured RNA  
- `*p:` = Multimeric protein complex  

---

## 2. Core Grammar Units

### 2.1 Symbols and Modifiers

| Symbol     | Function                                 |
|------------|------------------------------------------|
| `*`        | Post-translational modification          |
| `'`        | High conservation or emphasis            |
| `^`        | Epigenetic mark                          |
| `@`        | Index or position                        |
| `[]`       | Annotation block                         |
| `{}`       | Metadata block                           |
| `=`        | Function mapping                         |
| `/`        | Co-occurrence or junction                |
| `:`        | Structural prefix                        |
| `-`        | Sequential linkage                       |
| `#`        | Human-readable comment                   |
| `TIME()`   | Timestamped expression                   |
| `EFFECT()` | Biological/clinical outcome              |
| `HYPOTHESIS:` | Logical premise                      |
| `SIMULATE:`  | Predictive model                       |
| `PATHWAY:`   | Regulatory/metabolic flow              |
| `MACRO:`     | Macro definition                       |
| `USE:`       | Macro invocation                       |

---

## 3. Modules and Functional Components

### 3.1 Sequence-Level Tokens

| Token    | Meaning                    |
|----------|----------------------------|
| `[EX]`   | Exon                       |
| `[IN]`   | Intron                     |
| `[UTR5]` | 5' UTR                     |
| `[UTR3]` | 3' UTR                     |
| `[TATA]` | Promoter motif             |
| `[TSS]`  | Transcription start site   |

### 3.2 Regulatory Elements

| Token          | Meaning                          |
|----------------|----------------------------------|
| `Dom(Kin)`     | Kinase domain                    |
| `Mot(NLS)`     | Nuclear localization signal      |
| `TF(GATA1)`    | Transcription factor site        |
| `Ctrl{Enh+Sil}`| Enhancer/silencer combo logic    |

---

## 4. Mutation and Editing

### 4.1 Mutations

| Syntax                    | Meaning                         |
|---------------------------|---------------------------------|
| `[MUT:PAT:A>G@Q335X]`     | Paternal point mutation         |
| `[MUT:MAT:E>T@714X]`      | Maternal point mutation         |
| `[MUT:SOM:del@exon4]`     | Somatic deletion                |

### 4.2 Gene/RNA Editing

| Syntax                              | Meaning                                  |
|-------------------------------------|------------------------------------------|
| `EDIT:Base(A→G@123)`                | Base editing                             |
| `EDIT:Prime(INS:TTA@245)`           | Prime editing insertion                  |
| `EDIT:ARCUS(DEL:exon5)`             | ARCUS deletion                           |
| `EDIT:RNA_Transport(nuc→axon)`      | Spatial RNA redirection                  |

### 4.3 Edit Metadata

```
EDIT:Base(G→A@Q335X){efficacy=partial, cells=liver}
EDIT:Prime(INS:AGC@122){target=BRCA1}
```

---

## 5. Therapeutic & Clinical Logic

### 5.1 Delivery

```
DELIV(mRNA+LNP@IV)
DELIV(AAV9@IT)
```

### 5.2 Dosing / Time

```
DOSE(1):EDIT:Base(G→A@Q335X)
TIME(0d):DELIV(mRNA@IV)
TIME(7d):EDIT:Base(G→A@Q335X)
```

### 5.3 Conditional Logic

```
if MUT(PAT:A>G@Q335X) then EDIT:Base(G→A@Q335X)
EFFECT(restore function=urea cycle)
```

### 5.4 Predictive Logic

```
HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)
SIMULATE: {EDIT:Base(...), OUTCOME:↓ammonia}
```

### 5.5 EFFECT Operator

| Syntax                          | Meaning                                |
|----------------------------------|----------------------------------------|
| `EFFECT(↑neurite_growth@24h)`    | Neurite growth increase after 24h      |

---

## 6. Multi-omic & Pathway Modeling

```
PATHWAY: ARG+NH3 → CPS1 → Carbamoyl-P → OTC
TRANSCRIPTOME: ↑CPS1(mRNA)
PROTEOME: CPS1*P@K347
```

---

## 7. Macros and Reuse

```
MACRO:EDIT_CPS1 = {
  DELIV(mRNA+LNP@IV)
  EDIT:Base(A→G@Q335X){target=CPS1}
}
USE:EDIT_CPS1
```

---

## 8. Reasoning and Simulation Enhancements

### 8.1 Mechanisms

```
TRANSCRIBE(Promoter→Gene)
SPLICE(Exon2, Exon4)
TRANSLATE(mRNA→Protein)
INHIBIT(miR29b → BACE1_mRNA)
```

### 8.2 Localization / Context

```
RNA(STMN2){localization=axonal_tip}
EFFECT(↑Translation@local_synapse){via=local_mTOR}
```

### 8.3 Feedback Loops

```
if Protein(P53) > threshold then INDUCE(p21)
AUTOREGULATE(TF1){repression=strong}
```

### 8.4 Evolution / Probability

```
PROB(Mutation[ARG>GLY@codon121])=0.002
FITNESS(DNA_variant_X)=+2.1
EPISTASIS(variantA+variantB){effect=nonadditive}
```

### 8.5 Formal Logic

```
∀x ∈ Exon: PRESERVE(x) ⇒ ↑Function
¬EXIST(mutation@codon618) ⇒ FUNCTIONAL
(MUT1 ∧ MUT2) ⇒ ↓Expression
```

---

## 9. Diagnostics and Simulation Blocks

```
SIMULATE:{CellLine=HEK293, Mutation=CFTR(ΔF508), Drug=VX-770}
DIAGNOSE:{if ↓ATP7B_mRNA & ↑serum_copper then Wilson_Disease}
```

---

## Version

**Grammar Spec v1.2**  
Post-logical reasoning, RNA transport, feedback & epistasis extensions  
© 2025 Fundación de Neurociencias — MIT License