# GeneForgeLang Use Case: In Vivo Base Editing for CPS1 Deficiency (K.J. Case)

## Case Overview

- **Case ID**: `KJ_CRISPR2`
- **Title**: In vivo CRISPR 2.0 base editing for CPS1 gene mutation
- **Source**: [NEJM Article](https://www.nejm.org/doi/full/10.1056/NEJMoa2504747)
- **Clinical Context**: First human case of in vivo base editing for a monogenic disease—CPS1 deficiency, a rare urea cycle disorder.
- **Patient**: Infant with lethal autosomal recessive mutations in *CPS1*
- **Objective**: Reverse a paternal nonsense mutation (Q335X) using adenosine base editing (ABE) delivered via mRNA + LNP

---

## 1. Molecular Summary

### Genetic Background

```gfl
~d:CPS1[
  MUT:PAT:G>A@Q335X,  # Nonsense (stop gain)
  MUT:MAT:G>A@E714X   # Nonsense
]
Editing Strategy
gfl
Copiar
Editar
EDIT:Base(A→G@Q335X){
  tool=ABE,
  model=K-abe,
  target=CPS1,
  cells=hepatocyte,
  efficacy=partial
}
DELIV(mRNA+LNP@IV)
Dosing Timeline
gfl
Copiar
Editar
DOSE(1):EDIT:Base(A→G@Q335X){dose=low, day=0, response=minimal}
DOSE(2):EDIT:Base(A→G@Q335X){dose=mid, day=21, response=↓ammonia}
DOSE(3):EDIT:Base(A→G@Q335X){dose=high, day=42, response=↑metabolic stability}
Functional Restoration (Protein Level)
gfl
Copiar
Editar
^p:Dom(CPS)-Mot(MitoTarget)*AcK@42=UreaCycle(On)
2. Symbolic Design Summary (GFL v1.0)
gfl
Copiar
Editar
~d:[TATA]CPS1[TF(HNF4A)][MUT:PAT:G>A@Q335X]
EDIT:Base(A→G@Q335X){tool=ABE, target=CPS1, cells=hepatocyte}
DELIV(mRNA+LNP@IV)
DOSE(1-3)
^p:Dom(CPS)-Mot(MitoTarget)=UreaCycle(On)
