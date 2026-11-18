# Permutation Baseline Gate (`shuffled_control`) for Bio-Foundation Model Auditing

## Overview & Scientific Grounding

The **Permutation Baseline Gate** (`permutation_baseline:`, `sequence_signal_audit:`) provides a falsifiable, deterministic mechanism in GeneForgeLang (GFL) to verify whether a generative model encodes **genuine evolutionary sequence knowledge** rather than literature memorization or compositional priors.

Grounded in the **Phylo** sequence-vs-shuffled benchmark (Xinming Tu & Leo Chen, November 2026), models are evaluated on next-residue or sequence continuation tasks over native biological sequences (including unstudied bacterial protein families with zero published papers) versus composition-preserving shuffled copies of those same prefixes:

$$\text{Permutation Gap} = \text{Acc}_{\text{native}} - \text{Acc}_{\text{shuffled}}$$

* Models trained purely on text/literature score near zero on both native and shuffled controls ($\text{Gap} \approx 0$).
* Models trained at scale on raw biological sequences exhibit a statistically significant positive gap above the shuffled baseline ($\text{Gap} \ge \text{min\_permutation\_gap}$).

---

## Supported Permutation Control Modes

1. **`uniform_shuffle`**: Seeded Fisher-Yates permutation preserving exact 1st-order monomer composition (amino acid or nucleotide counts).
2. **`dipeptide_shuffle` / `dinucleotide_shuffle`**: Seeded **Altschul-Erickson (1985)** exact Eulerian-trail permutation preserving exact 2-mer transition frequencies as well as start/end boundary residues, preventing false positives from simple local repeat or GC/hydrophobicity bias.

---

## Declarative GFL Syntax

```yaml
permutation_baseline:
  contract_id: "phylo_unstudied_bacterial_protein_audit_01"
  sequence_type: "protein"
  model_id: "claude-fable-5.2"
  reference_prefix: "MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ"
  target_suffix: "GKSFEVLKDR"
  control_mode: "dipeptide_shuffle"
  seed: 42
  min_permutation_gap: 0.20
```

It can also be nested directly inside `verifiable_dna:` (`VerifiableRewardContract`) under `domain: "permutation_baseline_gap"`.

---

## Programmatic Usage

```python
from geneforgelang.core.gftypes import PermutationControlMode, SequencePermutationBaselineContract
from geneforgelang.core.permutation_baseline import PermutationBaselineAuditor

contract = SequencePermutationBaselineContract(
    contract_id="audit_01",
    sequence_type="protein",
    reference_prefix="MKKLLVLSLVLAAGAVQADAKPGKTVVAYGTDQ",
    target_suffix="GKSFEVLKDR",
    control_mode=PermutationControlMode.DIPEPTIDE_SHUFFLE,
    seed=42,
    min_permutation_gap=0.20,
    model_id="claude-fable-5.2",
)

result = PermutationBaselineAuditor.audit_predictions(
    contract,
    native_prediction="GKSFEVLKAA",
    shuffled_prediction="GAAAAAAAAA",
)
# result.passes_gate -> True
# result.evidence_status -> "PERMUTATION_CONTROL_VERIFIED"
```
