# 🧬 GeneForgeLang Syntax Specification

This document defines the **syntactic rules** of GeneForgeLang—the symbolic language for cross-modality biomolecular design.

---

## 📘 Notation

- `<...>` denotes a **non-terminal**.
- `"..."` denotes a **literal symbol**.
- `|` means alternative.
- `[...]` denotes optional components.
- `(...)` denotes grouped elements.

---

## 🎯 Top-Level Expression

```ebnf
<expression> ::= <prefix> ":" <body>

🔤 Prefixes
ebnf
Copiar
Editar
<prefix> ::= "~d" | ":r" | "^p" | "*p" | "!d" | "^r"
Examples:

~d: → linear DNA

:r: → structured RNA

^p: → folded protein

*p: → multimeric protein

🧬 Body
ebnf
Copiar
Editar
<body> ::= <module> { "-" <module> }
Each module is a unit: exon, motif, domain, etc.

🧩 Module Syntax
ebnf
Copiar
Editar
<module> ::= <region> | <motif> | <domain> | <event> | <logic> | <mutation>
Regions
ebnf
Copiar
Editar
<region> ::= "[" <label> "]"
<label> ::= "EX" | "IN" | "UTR5" | "UTR3" | "TATA" | "TSS"
Domains and Motifs
ebnf
Copiar
Editar
<domain> ::= "Dom(" <name> ")"
<motif>  ::= "Mot(" <name> ")"
<tf>     ::= "TF(" <name> ")"
Modifications
ebnf
Copiar
Editar
<event> ::= <residue> "*" <mod> "@" <position>
<residue> ::= "K" | "Y" | "S" | "T" | ...
<mod> ::= "Ac" | "P" | "Ub" | "m" | ...
Logical Rules
ebnf
Copiar
Editar
<logic> ::= <lhs> "=" <rhs>
<lhs> ::= <domain> | <motif> | <tf> | <event>
<rhs> ::= <function> | <location>
🧬 Mutation Notation
ebnf
Copiar
Editar
<mutation> ::= "[MUT:" <ref> ">" <alt> "@" <pos> "]"
<deletion> ::= "[DEL:" <start> "-" <end> "]"
<insertion> ::= "[INS:" <seq> "@" <pos> "]"
✅ Valid Examples
text
Copiar
Editar
~d:[TATA]-ATG-[EX]-[IN]-[EX2]
^p:Dom(Kin)-Mot(NLS)*AcK@147=Localize(Nucleus)
:r:Cap5'-Ex1-Intr1-Ex2-UTR3'
❌ Invalid Examples
text
Copiar
Editar
~r::TATA]     # double colon
:p:Dom()      # missing domain name
*Exon1        # missing prefix
🔄 Syntax vs. Grammar
Grammar describes semantics and modules.

Syntax ensures that inputs are well-formed and parsable.

Version 0.1 — Draft Specification
© 2025 Fundación de Neurociencias (MIT License)
