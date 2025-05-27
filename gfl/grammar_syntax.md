# 📘 Gramática de GeneForgeLang (GFL)

GeneForgeLang es un lenguaje simbólico diseñado para representar procesos de edición genética, regulación génica y efectos moleculares y fenotípicos en distintos niveles de abstracción.

## 🎯 Objetivos

- Describir ediciones genéticas (SNP, deleciones, inserciones, reemplazos).
- Representar efectos funcionales y fenotípicos.
- Modelar relaciones causales y temporales entre elementos.
- Integrar multiómica, redes de interacción y predicciones computacionales.

---

## 🧬 Gramática General (BNF simplificada)

```bnf
<program>        ::= { <statement> }

<statement>      ::= <edit_stmt> 
                   | <target_stmt> 
                   | <effect_stmt> 
                   | <pathway_stmt> 
                   | <link_stmt> 
                   | <simulate_stmt>

<edit_stmt>      ::= "edit(" <edit_type> ":" <identifier> ")"
<target_stmt>    ::= "target(" <target_type> ":" <identifier> ")"
<effect_stmt>    ::= "effect(" <effect_type> ":" <description> ")"
<pathway_stmt>   ::= "pathway(" <pathway_name> ":" <process> ")"
<link_stmt>      ::= "link(" <source> "->" <destination> ")"
<simulate_stmt>  ::= "simulate(" <phenotype> ")"

<edit_type>      ::= "SNP" | "DEL" | "INS" | "REPL"
<target_type>    ::= "gene" | "protein" | "RNA" | "enhancer"
<effect_type>    ::= "function" | "expression" | "structure" | "localization"

<identifier>     ::= [a-zA-Z0-9_-]+
<description>    ::= [a-zA-Z0-9_-]+
<process>        ::= [a-zA-Z0-9_-]+
<phenotype>      ::= [a-zA-Z0-9_-]+
```

---

## ✅ Ejemplo

```gfl
edit(SNP:rs123456)
target(gene:BRCA1)
effect(function:loss_of_function)
pathway(DNA_repair:homologous_recombination)
link(edit->target)
link(target->effect)
simulate(breast_cancer_risk)
```

---

# 🧠 Sintaxis Formal de GeneForgeLang (GFL)

Este documento detalla la sintaxis modular del lenguaje GFL según sus cinco niveles semánticos principales: Secuencia, Estructura, Función, Efecto y Simulación.

---

## 🔬 Nivel 1: Edición (SECUENCIA)

```gfl
edit(SNP:rsID)
edit(DEL:chr17_41276045_41276130)
edit(INS:chr3_1830021:T)
edit(REPL:chr2_130451200:A>G)
```

---

## 🧩 Nivel 2: Target (OBJETIVO MOLECULAR)

```gfl
target(gene:TP53)
target(protein:p53)
target(RNA:miR-21)
target(enhancer:MYC_superenhancer)
```

---

## ⚙️ Nivel 3: Efecto Funcional o Molecular

```gfl
effect(function:loss_of_function)
effect(expression:upregulated)
effect(structure:misfolded)
effect(localization:mislocalized)
```

---

## 🔁 Nivel 4: Vía Molecular o Red

```gfl
pathway(TGF_beta:cell_cycle_arrest)
pathway(PI3K:AKT_signaling)
```

---

## 🔗 Nivel 5: Relaciones Causales y Simulaciones

```gfl
link(edit->target)
link(target->effect)
link(effect->pathway)
simulate(cancer_proliferation)
simulate(neurodegeneration)
```

---

## 🧪 Composición

Un archivo GFL puede incluir tantas sentencias como sea necesario para describir un escenario complejo. Las relaciones se establecen con `link()` y pueden formar grafos.

---

## 📚 Notas

- Todos los identificadores deben ser compatibles con estándares como HGNC, Ensembl, UniProt o dbSNP.
- Se recomienda versionar las sentencias por fecha o contexto de análisis (experimental, in silico, predictivo).
- Las estructuras pueden ser exportadas a JSON para integración computacional.
