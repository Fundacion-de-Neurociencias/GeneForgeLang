# 🧬 GeneForgeLang Syntax Specification

This document defines the **syntactic rules** of GeneForgeLang—the symbolic language for cross-modality biomolecular design.

---

## 📘 Notation

- `<...>` denotes a **non-terminal**.
- `"..."` denotes a **literal symbol**.
- `|` indicates alternatives.
- `[...]` denotes optional elements.
- `{...}` indicates metadata or key-value structures.
- `(...)` groups sub-elements.

---

## 🎯 Top-Level Expression

```ebnf
<expression> ::= <prefix> ":" <body>
```

---

## 🔤 Prefixes

```ebnf
<prefix> ::= "~d" | ":r" | "^p" | "*p" | "!d" | "^r"
```

**Examples:**

- `~d:` → linear DNA  
- `:r:` → structured RNA  
- `^p:` → folded protein  
- `*p:` → multimeric protein  

---

## 🧬 Body

```ebnf
<body> ::= <module> { "-" <module> }
```

Each module is a unit of information: domain, mutation, logic, edit, etc.

---

## 🧩 Module Syntax

```ebnf
<module> ::= <region> | <motif> | <domain> | <event> | <logic> | <mutation>
           | <edit> | <delivery> | <dose> | <effect> | <hypothesis>
           | <simulate> | <time> | <pathway> | <macro> | <use>
```

---

### 🧬 Sequence Regions

```ebnf
<region> ::= "[" <label> "]"
<label> ::= "EX" | "IN" | "UTR5" | "UTR3" | "TATA" | "TSS"
```

---

### 🧷 Domains and Motifs

```ebnf
<domain> ::= "Dom(" <name> ")"
<motif>  ::= "Mot(" <name> ")"
<tf>     ::= "TF(" <name> ")"
```

---

### 🧪 Post-Translational Modifications

```ebnf
<event> ::= <residue> "*" <mod> "@" <position>
<residue> ::= "K" | "Y" | "S" | "T" | ...
<mod> ::= "Ac" | "P" | "Ub" | "m" | ...
```

---

### 🔁 Logical Rules

```ebnf
<logic> ::= <lhs> "=" <rhs>
<lhs> ::= <domain> | <motif> | <tf> | <event>
<rhs> ::= <function> | <location>
```

---

### 🧬 Mutations

```ebnf
<mutation> ::= "[MUT:" [<origin> ":"] <ref> ">" <alt> "@" <pos> "]"
<origin> ::= "PAT" | "MAT" | "SOM" | "GER"
```

---

### 🔨 Edits

```ebnf
<edit> ::= "EDIT:" <tool> "(" <operation> ")" [<metadata>]
<tool> ::= "Base" | "Prime" | "ARCUS"
<operation> ::= e.g. "A→G@42", "INS:CTT@27"
<metadata> ::= "{" <kvpair> { "," <kvpair> } "}"
<kvpair> ::= <key> "=" <value>
```

---

### 💉 Delivery and Dosing

```ebnf
<delivery> ::= "DELIV(" <vector> "@" <route> ")"
<vector> ::= "mRNA" | "LNP" | "AAV" | ...
<route> ::= "IV" | "IT" | "local" | "ex vivo"

<dose> ::= "DOSE(" <int> "):" <edit>
```

---

### ⏳ Timed Events

```ebnf
<time> ::= "TIME(" <day_expr> "):" <module>
<day_expr> ::= e.g. "0d", "7d", "3w"
```

---

### 🧠 Effects and Reasoning

```ebnf
<effect> ::= "EFFECT(" <description> ")"
<hypothesis> ::= "HYPOTHESIS:" <logic_statement>
<simulate> ::= "SIMULATE:" "{" <option_list> "}"
```

---

### 🔬 Pathways and Omics

```ebnf
<pathway> ::= "PATHWAY:" <molecule_chain>
```

---

### 🧩 Macros and Calls

```ebnf
<macro> ::= "MACRO:" <name> "=" "{" <body> "}"
<use> ::= "USE:" <name>
```

---

## ✅ Valid Examples

```gfl
~d:[TATA]-ATG-[EX]-[IN]-[EX2]
^p:Dom(Kin)-Mot(NLS)*AcK@147=Localize(Nucleus)
EDIT:Base(G→A@Q335X){target=CPS1}
DELIV(mRNA+LNP@IV)
DOSE(2):EDIT:Base(A→G@123){rate=low}
TIME(7d):EDIT:Base(G→A@Q335X)
EFFECT(restore function=urea cycle)
HYPOTHESIS: if MUT(Q335X) → loss(CPS1)
SIMULATE: {EDIT:Base(...), OUTCOME:↓ammonia}
PATHWAY: ARG → CPS1 → Carbamoyl-P
MACRO:FIX1={DELIV(...) - EDIT:Base(...)}
USE:FIX1
```

---

## ❌ Invalid Examples

```gfl
~r::TATA]        # double colon
:p:Dom()         # missing domain
*EX              # missing prefix
[DEL:12]         # malformed deletion
```

---

## 🔄 Syntax vs. Grammar

- **Syntax** = ensures well-formed, machine-parseable phrases
- **Grammar** = defines semantic logic and transformation behavior

---

## Version

Syntax Spec v1.1  
© 2025 Fundación de Neurociencias — MIT License
