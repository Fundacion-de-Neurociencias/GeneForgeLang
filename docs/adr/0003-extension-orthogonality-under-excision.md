# ADR-0003: Extension Orthogonality under Excision

## Status
Accepted

## Context
In GeneForgeLang (GFL), extensions provide specialized domain-specific syntax and external metadata integrations (such as protein sequence evidence, structural scores, and model bridges). However, to prevent structural degradation, accidental coupling, and cognitive debt inside an open-source language ecosystem, we must establish a rigorous, mathematically auditable boundary between the base GFL core and its optional extensions. 

Rather than stating a weak guideline like *"Extensions must be removable,"* we define a formal property: **Extension Orthogonality under Excision**.

## Decision

### 1. Mathematical Formalization of Orthogonality

Let:
* $\mathcal{C}$ be the Core Semantics of GeneForgeLang (including type lattice, base grammar, and core compiler invariants).
* $\mathcal{E}$ be the set of active language extensions.
* $E \in \mathcal{E}$ be a specific language extension.
* $\vdash_{\mathcal{C} \cup \{E\}}$ represent semantic derivation or compilation under the extended core.
* $\vdash_{\mathcal{C}}$ represent semantic derivation under the bare core.

An extension $E$ is formally **orthogonal** to the core under excision if and only if the following four properties hold:

1. **Semantic Invariance under Excision**:
   $$\forall \alpha \in \text{Core Programs}, \quad \text{Eval}_{\mathcal{C} \cup \{E\}}(\alpha) \equiv \text{Eval}_{\mathcal{C}}(\alpha)$$
   The evaluation of any core program must be identical regardless of whether extension $E$ is loaded or completely removed from the environment.
   
2. **Independence of Semantic Transitions**:
   No semantic state transition or causal reduction rule in $\mathcal{C}$ may depend on syntax, AST nodes, or types introduced by $E$.
   
3. **Preservation of Closure Proofs**:
   The removal of $E$ must preserve all structural type-safety and closure proofs of the base compiler $\mathcal{C}$.
   
4. **Preservation of Parser Completeness**:
   The base parser completeness for the core grammar must be fully preserved when $E$ is excised:
   $$\mathcal{L}(\text{Grammar}_{\mathcal{C}}) \cap \mathcal{L}(\text{Grammar}_{E}) = \emptyset$$
   The languages recognized by the base core and the extension must be disjoint, ensuring that the base parser is robust under the excision of any extension.

---

### 2. Dual-Level Verification Architecture

We implement a two-tiered validation framework to enforce this orthogonality automatically during CI:

#### Nivel 1 — Hard Mechanical Gate (Blocking)
This level is 100% automated and blocks commits/merges in the CI system (`make constitutional`) if any violation occurs.

* **Core Contamination Prevention**: Prohibits any direct or transitive imports from `geneforgelang.extensions` into core semantic modules, specifically:
  - `geneforgelang.core.gftypes` (and future `semantic.lattice`)
  - `geneforgelang.core.inference` (and future `semantic.conflict`)
  - `geneforgelang.core.validator` (and future `semantic.constraints`)
  - `geneforgelang.core.execution` (and future `semantic.runtime`)
  
* **Reverse Contamination Prevention**: Prohibits any direct or transitive imports from `geneforgelang.core` (or future `semantic`) modules into `geneforgelang.extensions`.
  - Extensions must consume compiler-neutral IR and act as strictly syntax-only or metadata-only plugins.
  
* **Sunsetability Excision Simulation**: 
  The architectural audit tool will dynamically simulate the excision of each extension by removing it from `sys.path` and mocking it as missing, verifying that:
  - All core imports resolve successfully.
  - The base parser compiles.
  - Core unit tests continue to pass with 100% success.

#### Nivel 2 — Structured Governance Scoring (Review Assist)
For aspects that are epistemological and interpretative in nature, the audit produces a diagnostic signal for human reviewers rather than blocking automatically. Each extension is scored across 5 dimensions on a scale of 0–5:

1. **Irreducibility Depth (0–5)**: Does the extension's design/justification demonstrate that it represents a structural mathematical necessity that cannot be expressed using base GFL primitives?
2. **Ontological Neutrality (0–5)**: Does the extension refrain from introducing disguised or implicit biological/domain semantics into the core type systems?
3. **Provider Abstraction Purity (0–5)**: Does the extension compile to a provider-neutral Intermediate Representation (IR), keeping third-party APIs (like ESM or AlphaFold) abstracted?
4. **Primitive Necessity (0–5)**: Does the extension introduce real formal expressivity without polluting the base language grammar?
5. **Sunsetability Confidence (0–5)**: How easily can the extension be excised from a live deployment or AST graph without leaving lingering artifacts or residues?

##### Scoring Threshold Actions:
* **Score $< 15$**: **Automatic Reject** (the extension is too coupled or poorly designed to be reviewed).
* **Score $15 - 20$**: **Mandatory Reviewer Escalation** (requires formal sign-off by two language maintainers).
* **Score $> 20$**: **Normal Review** (eligible for merge following standard review cycles).

## Consequences
* **Decoupled Language Growth**: Prevents GeneForgeLang from mutating from a clean scientific programming language into a bloated, coupled framework.
* **Guaranteed Portability**: Ensures that scientific GFL files written using custom plugins remain perfectly parsing and readable by base compilers.
* **Strict Quality Control**: Establishes a "constitutional" quality gate separate from standard CI linting, cementing GFL's commitment to syntactic and semantic preservation.
