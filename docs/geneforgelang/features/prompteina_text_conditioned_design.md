# Prompteina Text-Conditioned All-Atom Protein Design in GeneForgeLang (GFL)

## 1. Overview and Biological Rationale

Traditional protein design models require rigid, coordinate-level inputs (hotspot residue lists, structural scaffolds, or fixed bounding boxes). In contrast, **Prompteina** (Baker Lab / Institute for Protein Design, University of Washington, and Allen Institute for AI - Ai2) allows researchers to design protein structures and sequences directly from structured natural language prompts.

Analogous to text-to-image diffusion models, Prompteina maps text embeddings directly to all-atom 3D coordinates and amino acid sequences across multiple scales:
- **Macro-topology:** Overall fold (e.g., three-helix bundle, TIM barrel).
- **Fine-grained active sites:** Specific residue-level interactions and hydrogen bonding networks.
- **Negative design:** Explicit avoidance of non-specific binding surfaces or catalytic gateways.
- **Experimental Milestone:** Successfully generated the first experimentally validated *de novo* binders for **GM2A** (ganglioside GM2 activator protein, deficiency of which causes Tay-Sachs/Sandhoff-related neurodegeneration), yielding sub-micromolar hits ($< 1\,\mu\text{M}$).

## 2. GFL Contract Specification

In GFL, text-conditioned design is formalized using `NaturalLanguageConditioningContract` and `TextConditionedDesignContract` within the `design` block:

```gfl
design GM2ABinderDesign {
  entity: "ProteinSequence"
  model: "prompteina"
  objective: {
    maximize: "binding_affinity"
  }
  count: 50
  output: "gm2a_de_novo_binders"

  prompt_conditioning: {
    macro_topology: "De novo three-helix bundle with amphipathic packing"
    interaction_site: "Target the apical hydrophobic cavity of GM2A, forming hydrogen bonds with Thr108 and hydrophobic packing against Leu115"
    negative_design: "Avoid binding the lipid transfer gateway residues Lys88-Asp91"
    symmetry: "C1"
    sequence_composition: "High thermal stability, depleted in cysteines and flexible loops"
    guidance_scale: 8.0
    num_inference_steps: 60
  }
}
```

## 3. Semantic Validation Rules

`EnhancedSemanticValidator` enforces:
- `guidance_scale`: Must be a strictly positive number ($> 0.0$, typically $5.0 - 12.0$).
- `num_inference_steps`: Must be a strictly positive integer ($> 0$, typically $30 - 100$).
- Model recognition: `"prompteina"` and `"Prompteina"` recognized as valid generative models.
- Tool compatibility: `"prompteina"` authorized for `["design", "simulation", "analysis", "validation"]`.
