# HVL Implementation Plan — GeneForgeLang (GFL) Repository

**Status:** DRAFT — Pending coordinator review
**Version:** 3.0-revised
**Scope:** This document applies ONLY to the GeneForgeLang repository. It does NOT prescribe runtime implementation, data access, or inference logic. Those belong to the GeneForge repository.

---

## 0. Guiding Principle

> **GFL defines formal validity, not biological truth.**

This is the non-negotiable epistemic boundary. GFL specifies:
- what constitutes a valid symbolic structure,
- what transformations are formally permitted,
- what invariants must hold,
- what contracts a compliant runtime must honor.

GFL does NOT:
- validate empirical claims against external databases,
- calibrate probabilities against observed outcomes,
- arbitrate between competing biological hypotheses,
- learn, adapt, or self-modify based on evidence.

---

## 1. Objective

Formalize the Hard Validation Layer (HVL) as a **contract layer**:
- define what the HVL must do (observation, classification, restriction, invalidation),
- define what the HVL must NEVER do (causal participation, probability rewriting, adaptive scoring, hidden reweighting),
- export the invariant contract so that GeneForge can consume it operationally,
- deprecate PFUL explicitly to prevent epistemic contamination,
- freeze GFL conceptual expansion beyond HVL contract, invariant export, and error taxonomy.

---

## 2. Non-Intervention Principle (HVL Contract)

The following must be inscribed in `docs/spec/HVL.md` as a hard architectural rule:

```text
The HVL may observe, classify, restrict, or invalidate outputs,
but it may never participate in causal generation,
probability generation,
causal propagation,
or intervention optimization.
```

This prohibits the following HVL inflation patterns:
- re-ranking outputs based on HVL scores,
- auto-correcting inferences,
- injecting HVL feedback into the causal pipeline,
- using HVL as a meta-agent, LLM judge, policy optimizer, or orchestration brain.

HVL must remain:
- narrow,
- rigid,
- auditable,
- limited,
- boring.

---

## 3. What GFL Will Deliver

### 3.1 HVL Contract Specification (`docs/spec/HVL.md`)

Define the HVL formally with **five pillars** (revised from four):

1. **Semantic Validity** — Does the output violate any GFL invariant?
2. **Evidence Alignment** — Does the output diverge from available external evidence under an explicit quality model? (Renamed from "Empirical Consistency" to avoid the dangerous implication that external evidence "validates" the system.)
3. **Predictive Calibration** — Are the probabilities emitted by the runtime calibrated against observable outcomes and operational proxies?
4. **Drift Detection** — Is the runtime progressively diverging from known formal baselines?
5. **Evidence Quality Assessment** — Is the external evidence itself trustworthy before it is used for alignment?

Safety grading (graduated, not binary):
- `SAFE`
- `RESTRICTED`
- `RESEARCH_ONLY`
- `UNSAFE`

Hard rule on invariant conflict:
> If external evidence contradicts a GFL invariant, the system MUST emit `ANOMALY_RECORD` + `EPISTEMIC_REVIEW_REQUIRED`. It MUST NOT auto-modify GFL, GF, weights, or heuristics.

### 3.2 Invariant Export Contract (`spec/invariant_manifest.json` or `spec/invariant_manifest.yaml`)

GFL will compile its semantic invariants into a machine-readable manifest.
- This manifest is the **operational contract** consumed by GeneForge/HVL.
- The conformance suite (`tests/conformance_suite/`) remains what it is: a **compliance testing tool** for verifying that implementations respect the standard.
- The conformance suite is NEVER used as a runtime input.
- The invariant manifest is NEVER confused with the conformance suite.

### 3.3 Error Taxonomy Expansion (`src/geneforgelang/core/errors.py`)

Add formal error codes for HVL findings:
- `HVL_SEMANTIC_VIOLATION`
- `HVL_EVIDENCE_ALIGNMENT_MISMATCH`
- `HVL_EVIDENCE_QUALITY_LOW`
- `HVL_UNCALIBRATED`
- `HVL_DRIFT_DETECTED`
- `HVL_UNSAFE_OUTPUT`
- `HVL_ANOMALY_RECORD`
- `HVL_EPISTEMIC_REVIEW_REQUIRED`

### 3.4 PFUL Deprecation (`docs/deprecated/`)

Move the following documents to `docs/deprecated/` with a `NON-CANONICAL` banner:
- `docs/spec/PFUL.md`
- `docs/spec/ERC.md`

Rationale for deprecation (to be documented in a `README.md` inside `docs/deprecated/`):
- PFUL describes a self-modifying learning loop that adjusts epistemic weights and heuristics based on observed outcomes.
- This destroys strong falsifiability by making the system its own epistemic arbiter.
- PFUL conflicts with the HVL Non-Intervention Principle.
- PFUL conflicts with `INVARIANT_BOUNDARIES.md` by allowing internal learning to blur into the Immutable Core.
- Deprecation is permanent. There is no "reactivation path" for PFUL without a full GFL-RFC and version bump.

### 3.5 Constitution & Boundary Updates

Update:
- `CONSTITUTION.md` — introduce HVL as external falsification layer; correct "GFL defines formal validity, not biological truth."
- `INVARIANT_BOUNDARIES.md` — clarify that the Immutable Core is protected from ANY self-modification loop, including legacy PFUL concepts.

---

## 4. What GFL Will NOT Do

- No implementation of external database queries (OpenTargets, ClinVar, DepMap, Reactome).
- No calibration logic, drift detection logic, or evidence quality scoring logic.
- No runtime integration.
- No maintenance of PFUL in any form (frozen, congelated, or legacy mode).
- No expansion of conceptual architecture beyond the items listed in Section 3.

---

## 5. Success Criteria

- [ ] `docs/spec/HVL.md` exists and contains the Non-Intervention Principle.
- [ ] `spec/invariant_manifest.*` exists and is decoupled from the conformance suite.
- [ ] Error taxonomy includes all HVL codes.
- [ ] PFUL and ERC are moved to `docs/deprecated/` with `NON-CANONICAL` banners.
- [ ] `CONSTITUTION.md` and `INVARIANT_BOUNDARIES.md` are updated.
- [ ] No new conceptual modules are added to GFL beyond this plan.

---

## 6. Risk: GFL Epistemological Inflation

The primary risk is silent drift toward:
> "GFL as biological ontology"

Guardrails:
- Every proposed GFL change must answer: "Does this define formal validity, or does it claim biological truth?"
- If the latter, reject.

---

*This plan is ready for coordinator review. No implementation should proceed until explicitly authorized.*
