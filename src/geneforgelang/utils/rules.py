"""Probabilistic rules for GFL inference."""

# Default probabilistic rules for inference
default_rules = {
    "gene_editing": {"efficiency": 0.75, "off_target_risk": 0.15, "confidence": 0.85},
    "protein_design": {"stability": 0.80, "expression": 0.70, "confidence": 0.75},
    "optimization": {"convergence": 0.90, "improvement": 0.65, "confidence": 0.80},
}
