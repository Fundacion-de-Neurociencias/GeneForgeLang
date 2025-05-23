# 🧬 GeneForgeLang Syntax Specification

This document defines the **syntactic rules** of GeneForgeLang—the symbolic language for cross-modality biomolecular design.

---

## 📘 Notation

- `<...>` denotes a **non-terminal**.
- `"..."` denotes a **literal symbol**.
- `|` indicates alternatives.
- `[...]` denotes optional elements.
- `{...}` indicates structured metadata or repetition.
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
- `!d:` → unknown DNA  
- `^r:` → tertiary RNA

---

## 🧬 Body

```ebnf
<body> ::= <module> { "-" <module> }
```

Each `<module>` is a symbolic unit (domain, motif, mutation, etc.).

---

## 🧩 Module Syntax

```ebnf
<module> ::= <region> | <motif> | <domain> | <event> | <logic> | <mutation> | <edit> | <delivery> | <dose>
```

---

### 📦 Sequence Regions

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
<position> ::= <int>
```

---

### 🔁 Logical Rules

```ebnf
<logic> ::= <lhs> "=" <rhs>
<lhs> ::= <domain> | <motif> | <tf> | <event>
<rhs> ::= <function> | <location>
```

Examples:
- `Mot(PEST) = Deg`
- `Dom(Kin)-Mot(NLS)*AcK@147 = Localize(Nucleus)`

---

## 🧬 Mutation and Edit Syntax

### 🔬 Mutation Notation

```ebnf
<mutation> ::= "[MUT:" <origin> ":" <ref> ">" <alt> "@" <pos> "]"
<origin> ::= "PAT" | "MAT" | "SOM" | "GER"
```

### 🧨 Structural Variants

```ebnf
<deletion> ::= "[DEL:" <start> "-" <end> "]"
<insertion> ::= "[INS:" <seq> "@" <pos> "]"
```

---

### 🛠️ Edit Operations

```ebnf
<edit> ::= "EDIT:Base(" <ref> "→" <alt> "@" <pos> ")" [<metadata>]
         | "EDIT:Prime(" <insdel> "@" <pos> ")" [<metadata>]
<metadata> ::= "{" <keyval> { "," <keyval> } "}"
<keyval> ::= <key> "=" <value>
```

---

## 🚚 Delivery Syntax

```ebnf
<delivery> ::= "DELIV(" <vector> "@" <route> ")"
<vector> ::= "mRNA" | "LNP" | "AAV" | "NP_mRNA" | ...
<route> ::= "IV" | "IT" | "local" | "ex vivo"
```

---

## 💉 Dose Schedule

```ebnf
<dose> ::= "DOSE(" <int> "):" <edit>
```

Example:
```text
DOSE(2):EDIT:Base(A→G@Q335X){dose=mid, day=21}
```

---

## ✅ Valid Examples

```text
~d:[TATA]-ATG-[EX]-[IN]-[EX2]
^p:Dom(Kin)-Mot(NLS)*AcK@147 = Localize(Nucleus)
:r:Cap5'-Ex1-Intr1-Ex2-UTR3'
EDIT:Base(A→G@Q335X){tool=ABE, cells=hepatocyte}
DELIV(mRNA+LNP@IV)
DOSE(1):EDIT:Base(A→G@Q335X){dose=low, day=0}
```

---

## ❌ Invalid Examples

```text
~r::TATA]       # double colon, invalid structure
:p:Dom()        # empty domain
*Exon1          # missing prefix
[DEL:12]        # malformed deletion syntax
```

---

## 🔄 Syntax vs. Grammar

- **Syntax** ensures inputs are **well-formed** and **parsable**.
- **Grammar** defines **semantic meaning** and **logic** of components.

---

**Version:** 0.2 (post-CRISPR2 update)  
© 2025 Fundación de Neurociencias — MIT License
