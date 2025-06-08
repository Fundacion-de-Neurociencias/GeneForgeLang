# 🧬 GeneForgeLang Syntax Specification (v1.2)

This document defines the **syntactic rules** of GeneForgeLang (GFL)—a symbolic language for cross-modality biomolecular representation and reasoning.

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
<prefix> ::= "~d" | ":r" | "^p" | "*p" | "!d" | "^r" | "*^p"
```

Examples:

- `~d:` → linear DNA  
- `^p:` → folded protein  
- `:r:` → structured RNA  
- `*p:` → multimeric protein  
- `*^p:` → folded domain within complex

---

## 🧬 Body

```ebnf
<body> ::= <module> { "-" <module> }
```

Each module is a unit of information: domain, motif, mutation, logic, edit, etc.

---

## 🧩 Module Syntax

```ebnf
<module> ::= <region> | <motif> | <domain> | <tf> | <event> | <logic> | <mutation>
           | <edit> | <delivery> | <dose> | <effect> | <hypothesis>
           | <simulate> | <diagnose> | <time> | <pathway> | <macro> | <use>
           | <mechanism> | <probability> | <feedback> | <formal_logic>
```

---

### 🧬 Sequence Regions

```ebnf
<region> ::= "[" <label> "]"
<label> ::= "EX" | "IN" | "UTR5" | "UTR3" | "TATA" | "TSS"
```

---

### 🧷 Domains, Motifs, TFs

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
<mod> ::= "Ac" | "P" | "Ub" | ...
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

### 🛠 Edits

```ebnf
<edit> ::= "EDIT:" <tool> "(" <operation> ")" [<metadata>]
<tool> ::= "Base" | "Prime" | "ARCUS" | "RNA_Transport"
<operation> ::= <source> "→" <target> | "INS:" <seq> "@" <pos> | ...
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
<day_expr> ::= "0d" | "7d" | "3w"
```

---

### 🧠 Effects and Reasoning

```ebnf
<effect> ::= "EFFECT(" <direction> <outcome> [ "@" <time> ] [ <metadata> ] ")"
<direction> ::= "↑" | "↓" | "→"
<outcome> ::= <function> | <phenotype>

<hypothesis> ::= "HYPOTHESIS:" "if" <condition> "then" <consequence>
<simulate> ::= "SIMULATE:" "{" <kvpair> { "," <kvpair> } "}"
<diagnose> ::= "DIAGNOSE:" "{" <if_cond> "then" <diagnosis> "}"
```

---

### 🔬 Pathways and Omics

```ebnf
<pathway> ::= "PATHWAY:" <molecule_chain>
```

---

### 📦 Macros

```ebnf
<macro> ::= "MACRO:" <name> "=" "{" <body> "}"
<use> ::= "USE:" <name>
```

---

### ⚙️ Feedback and Regulation

```ebnf
<feedback> ::= "AUTOREGULATE(" <target> ")" "{" <kvpair> "}"
```

---

### 🎲 Probability and Fitness

```ebnf
<probability> ::= "PROB(" <mutation> ")" "=" <float>
<fitness> ::= "FITNESS(" <variant> ")" "=" <float>
<epistasis> ::= "EPISTASIS(" <variant1> "+" <variant2> ")" "{" <kvpair> "}"
```

---

### ∀ Formal Logic

```ebnf
<formal_logic> ::= "∀" <var> "∈" <set> ":" <statement>
                 | "¬" <statement>
                 | "(" <statement> ")" "⇒" <statement>
                 | "(" <statement> ")" "∧" "(" <statement> ")"
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
EFFECT(↑neurite_growth@24h){via=mTOR}
HYPOTHESIS: if MUT(Q335X) → Loss(CPS1)
SIMULATE: {Mutation=CFTR(ΔF508), Drug=VX-770}
PATHWAY: ARG → CPS1 → Carbamoyl-P
MACRO:FIX1={DELIV(...) - EDIT:Base(...)}
USE:FIX1
```

---

## 🔄 Syntax vs. Grammar

- **Syntax** = defines well-formed machine-parseable phrases
- **Grammar** = defines transformation and logic

---

## Version

Syntax Spec v1.2  
© 2025 Fundación de Neurociencias — MIT License