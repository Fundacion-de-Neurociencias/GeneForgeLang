from typing import Any, Dict


class DummyGeneModel:
    """Very small heuristic model for demo/integration tests.

    - If a target gene is present, predicts label based on strategy/type.
    - Otherwise returns 'unknown'.
    """

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        gene = features.get("target_gene") or features.get("target")
        strategy = (features.get("strategy") or "").lower()
        exp_type = (features.get("experiment_type") or "").lower()

        if not gene:
            return {"label": "unknown"}

        if "differential" in strategy or "expression" in strategy:
            return {"label": "expression_change"}
        if "edit" in exp_type or "gene_edit" in exp_type or "crispr" in (features.get("experiment_tool") or "").lower():
            return {"label": "edited"}
        return {"label": "targeted"}


__all__ = ["DummyGeneModel"]
