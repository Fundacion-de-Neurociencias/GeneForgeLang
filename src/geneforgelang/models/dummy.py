from typing import Any


class DummyGeneModel:
    """Basic gene prediction model for testing and development.

    This is a simple rule-based model that provides basic predictions
    for gene-related experiments. Used primarily in tests and demos.
    """

    def __init__(self):
        # Simple lookup table for common gene patterns
        self.gene_patterns = {
            "TP53": "tumor_suppressor",
            "BRCA1": "dna_repair",
            "BRCA2": "dna_repair",
            "MYC": "oncogene",
            "EGFR": "receptor_tyrosine_kinase",
        }

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        gene = features.get("target_gene") or features.get("target")
        strategy = (features.get("strategy") or "").lower()
        exp_type = (features.get("experiment_type") or "").lower()

        if not gene:
            return {"label": "unknown", "confidence": 0.0}

        # Basic pattern matching
        gene_type = self.gene_patterns.get(gene.upper(), "unknown")

        if "differential" in strategy or "expression" in strategy:
            return {"label": "expression_change", "gene_type": gene_type, "confidence": 0.7}
        if "edit" in exp_type or "gene_edit" in exp_type or "crispr" in (features.get("experiment_tool") or "").lower():
            return {"label": "edited", "gene_type": gene_type, "confidence": 0.8}
        return {"label": "targeted", "gene_type": gene_type, "confidence": 0.6}


__all__ = ["DummyGeneModel"]
