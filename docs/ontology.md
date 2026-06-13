# GeneForgeLang Ontology

**Version:** 0.1
**Maintainer:** Fundación de Neurociencias
**License:** MIT
**Purpose:** Provide a unified ontological foundation for symbolic reasoning in molecular design, reconciling biological logic and philosophical logic through GeneForgeLang (GFL).

---

## 1. Ontological Premises

| Domain              | Description                                                                  |
|---------------------|------------------------------------------------------------------------------|
| Philosophical Logic | Reasoning based on causality, implication, modality, and consequence         |
| Biological Logic    | Reasoning constrained by molecular pathways, structural feasibility, species |

This ontology enables **deductive**, **inductive**, and **abductive** reasoning over biological syntax encoded in GFL.

---

## 2. Core Concepts

### 2.1 Entities

| Entity     | GFL Representation             | Ontological Role             |
|------------|--------------------------------|------------------------------|
| Gene       | `~d:[TSS]...`                  | Instructional template       |
| Transcript | `:r:Cap5'-Ex1-Intr1-Ex2-UTR3'` | Intermediate expression unit |
| Protein    | `^p:Dom(...)`                  | Functional effector          |
| Enhancer   | `Ctrl{Enh}`                    | Regulatory controller        |
| Pathway    | `→` sequences of events        | Causal chains                |
| Edit       | `[MUT:...]`, `[INS:...]`       | Change agent                 |

### 2.2 Relations

| Relation    | Syntax              | Meaning                                   |
|-------------|---------------------|-------------------------------------------|
| Causes      | `A → B`             | A triggers or enables B                   |
| Requires    | `A ∧ B`             | B is necessary for A                      |
| Equivalent  | `A ≡ B`             | Semantic equivalence (e.g., isoforms)     |
| Conditional | `if A then B`       | Logic gate for downstream events          |
| Annotates   | `A [note: "..."]`   | Optional human annotation                 |

---

## 3. Logical Operators and GFL Syntax Mapping

| Logic Concept | GFL Representation | Example                                      |
|---------------|--------------------|----------------------------------------------|
| AND (∧)       | `Dom(X)-Mot(Y)`    | Kinase domain AND nuclear localization motif |
| OR (∨)        | `Mot(X)/Mot(Y)`    | Either motif X OR motif Y                    |
| NOT (¬)       | `!Mot(X)` (planned)| Absence of motif X                           |
| IMPLIES (→)   | `X = Y`            | X implies Y (e.g., `Mot(PEST) = Deg`)        |
| CONDITIONAL   | `if PTM(X) → Y`    | If PTM, then downstream localization         |

---

## 4. Reasoning Framework

### 4.1 Deductive Reasoning

From a general GFL rule to a specific output:

```text
Rule: Mot(PEST) = Deg
Input: ^p:Dom(Kin)-Mot(PEST)
→ Inferred: Degradation likely
```

### 4.2 Inductive Reasoning

From observed patterns to a generalized rule:

```text
Observed: MUT@42 → Functional loss
→ Inferred: All variants at position 42 likely deleterious
```

### 4.3 Abductive Reasoning

From observed effects to probable cause:

```text
Phenotype: Loss of enzyme activity
→ Candidate phrase: ^p:Dom(Hyd)-[MUT:G>A@123]
```

---

## 5. Layers and Domains

| Layer   | Ontological Implication                             |
|---------|------------------------------------------------------|
| DNA     | Blueprint; supports edit operations                 |
| RNA     | Structural intermediates; supports splicing logic   |
| Protein | Functional targets; supports PTMs and complex logic |

---

## 6. Species-Aware Reasoning

Species, organ specificity, and delivery mechanisms can be integrated as structured metadata:

```yaml
target:
  gene: "CPS1"
  mutation: "[MUT:G>A@1001]"
  species: "Homo sapiens"
  delivery: "mRNA-nanoparticles"
  edit_type: "Adenine base editor (ABE)"
```

---

## 7. Commentary and Meta-Logic

- Comments allowed via `#` (ignored by parser)
- Meta-level statements prefixed with `//` for human-readable explanation
- Reserved terms allowed in ontology-aware extensions: `causes`, `restores`, `requires`, `localizes`

---

## 8. Roadmap

- ✅ Integration with GFL Transformer for symbolic → causal simulation
- ✅ Export support to OWL and RDF for use in semantic web agents
- ✅ Syntax-to-logic validator for consistency enforcement
- 🔜 Ontology-driven therapeutic reasoning engine
- 🔜 Multi-organism cross-mapping for translational models

---

**End of Ontology Specification**
