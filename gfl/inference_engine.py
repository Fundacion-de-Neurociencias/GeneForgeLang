from typing import Any, Dict
from gfl.prob_rules import ProbReasoner, default_rules

class InferenceEngine:
    """Inference engine with probabilistic rule layer."""
    def __init__(self, model):
        self.model = model
        self.reasoner = ProbReasoner(default_rules())

    # ------------------------------------------------------------------ #
    def predict_effect(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        base = self.model.predict(self._extract_features(ast_dict))
        post = self.reasoner.posterior(ast_dict | {})  # ensure dict copy
        return {
            "label": base.get("label", "unknown"),
            "confidence": post["confidence"],
            "explanation": ", ".join(post["fired_rules"] or ["base_only"])
        }

    # stubs for completeness
    def retroinfer_cause(self, phenotype: str) -> Dict[str, Any]:
        return {"variant": "rs0", "confidence": 0.4}

    def evaluate_off_target(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        return {"off_target_hits": []}

    # ------------------------------------------------------------------ #
    def _extract_features(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        feats: Dict[str, Any] = {}
        for n in ast["children"]:
            if n["type"] == "target":
                feats["target"] = n["attrs"].get("val")
            if n["type"] == "effect":
                feats["effect"] = n["attrs"].get("val")
            if n["type"] == "vector":
                feats["vector"] = n["attrs"].get("val")
        return feats
