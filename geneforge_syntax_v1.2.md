# 🧬 GeneForgeLang Syntax Specification (v1.2)

This document defines the **syntactic rules** of GeneForgeLang v1.2 — the symbolic, structured, and reasoning-enhanced language for cross-modality biomolecular design.

---

## 📘 Notation

- `<...>` = non-terminal
- `"..."` = literal string
- `[...]` = optional
- `{...}` = metadata or key-value pairs
- `|` = alternative
- `(...)` = grouping

---

## 🎯 Top-Level Expression

```
<expression> ::= <prefix> ":" <body>
```

---

## 🔤 Prefixes

```
<prefix> ::= "~d" | ":r" | "^p" | "*p" | "!d" | "^r" | "*r" | ":p"
```

---

## 🧬 Body

```
<body> ::= <module> { "-" <module> }
```

---

## 🧩 Modules

```
<module> ::= <region> | <motif> | <domain> | <tf> | <ptm> | <mutation>
           | <edit> | <delivery> | <dose> | <logic>
           | <effect> | <hypothesis> | <simulate> | <time>
           | <pathway> | <macro> | <use> | <mechanism>
           | <feedback> | <probability> | <fitness> | <epistasis>
           | <diagnose>
```

---

## 📚 Region & Regulatory Elements

```
<region> ::= "[" <label> "]"
<label> ::= "EX" | "IN" | "UTR5" | "UTR3" | "TATA" | "TSS"

<domain> ::= "Dom(" <name> ")"
<motif>  ::= "Mot(" <name> ")"
<tf>     ::= "TF(" <name> ")"
```

---

## 🧪 Post-Translational Modifications

```
<ptm> ::= <residue> "*" <mod> "@" <position>
<residue> ::= "K" | "S" | "T" | "Y" | ...
<mod> ::= "Ac" | "P" | "Ub" | "m" | ...
```

---

## 🔄 Mutations

```
<mutation> ::= "[MUT:" [<origin> ":"] <ref> ">" <alt> "@" <pos> "]"
<origin> ::= "PAT" | "MAT" | "SOM" | "GER"
```

---

## 🛠️ Edits

```
<edit> ::= "EDIT:" <tool> "(" <operation> ")" [<metadata>]
<tool> ::= "Base" | "Prime" | "ARCUS" | "RNA_Transport"
<operation> ::= <edit_event> | <mutation> | <coord_change>
<metadata> ::= "{" <kvpair> { "," <kvpair> } "}"
```

---

## 💉 Delivery & Dose

```
<delivery> ::= "DELIV(" <vector> "@" <route> ")"
<vector> ::= "mRNA" | "LNP" | "AAV" | ...
<route> ::= "IV" | "IT" | "local"

<dose> ::= "DOSE(" <int> "):" <edit>
```

---

## 🧠 Logic & Reasoning

```
<logic> ::= "if" <condition> "then" <action>
<effect> ::= "EFFECT(" <symbol> <outcome> [ "@" <time> ] [ <metadata> ] ")"
<symbol> ::= "↑" | "↓" | "→"
<outcome> ::= <function> | <phenotype>

<hypothesis> ::= "HYPOTHESIS:" "if" <logic_statement> "then" <consequence>
<simulate> ::= "SIMULATE:" "{" <sim_options> "}"
<time> ::= "TIME(" <day_expr> "):" <module>
<pathway> ::= "PATHWAY:" <flow>
```

---

## 🧠 Advanced Reasoning

```
<mechanism> ::= "TRANSCRIBE(" <src> "→" <dst> ")" | "SPLICE(" ... ")" | ...
<feedback> ::= "AUTOREGULATE(" <entity> ")" "{" <metadata> "}"
<probability> ::= "PROB(" <mutation> ")=" <float>
<fitness> ::= "FITNESS(" <variant> ")=" <float>
<epistasis> ::= "EPISTASIS(" <var1> "+" <var2> ")" "{" <metadata> "}"
```

---

## 🧪 Diagnostics

```
<diagnose> ::= "DIAGNOSE:" "{" "if" <conditions> "then" <diagnosis> "}"
```

---

## 🧩 Macros

```
<macro> ::= "MACRO:" <name> "=" "{" <body> "}"
<use> ::= "USE:" <name>
```

---

## ✅ Valid Examples

```
~d:[TATA]-ATG-[EX]-[IN]-[EX]
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

```
~r::TATA]        # double colon
:p:Dom()         # missing domain
*EX              # missing prefix
[DEL:12]         # malformed deletion
```

---

## 🔄 Syntax vs Grammar

- **Syntax** = form and parsing
- **Grammar** = semantic logic and inference layer

---

## 📜 Version

**Syntax Spec v1.2**  
© 2025 Fundación de Neurociencias — MIT License