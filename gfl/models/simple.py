from typing import Any, Dict


class SimpleHeuristicModel:
    """Slightly more realistic heuristic baseline.

    - If p_value < 0.01 -> label "significant"
    - If experiment tool mentions CRISPR/gene editing -> label "edited"
    - If simulate block is present -> label "simulated"
    - Else -> label "benign"
    """

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        p = features.get("p_value")
        tool = str(features.get("experiment_tool", "")).lower()
        exp_type = str(features.get("experiment_type", "")).lower()
        simulate = bool(features.get("simulate"))

        if isinstance(p, (int, float)) and p < 0.01:
            return {"label": "significant"}
        if "crispr" in tool or "edit" in exp_type or "gene_edit" in exp_type:
            return {"label": "edited"}
        if simulate:
            return {"label": "simulated"}
        return {"label": "benign"}


__all__ = ["SimpleHeuristicModel"]
