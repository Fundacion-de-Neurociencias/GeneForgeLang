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
        post = self.reasoner.posterior(dict(ast_dict))  # best-effort copy
        return {
            "label": base.get("label", "unknown"),
            "confidence": post["confidence"],
            "explanation": ", ".join(post["fired_rules"] or ["base_only"]),
        }

    # stubs for completeness
    def retroinfer_cause(self, phenotype: str) -> Dict[str, Any]:
        return {"variant": "rs0", "confidence": 0.4}

    def evaluate_off_target(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        return {"off_target_hits": []}

    # ------------------------------------------------------------------ #
    def _extract_features(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """Robustly extract lightweight features from dict-AST.

        Supports two shapes:
        - Node list under "children" (legacy)
        - YAML-like dicts with keys like experiment/analyze/params/thresholds
        """
        feats: Dict[str, Any] = {}

        # Legacy node-list AST
        children = ast.get("children") if isinstance(ast, dict) else None
        if isinstance(children, list):
            for n in children:
                t = n.get("type") if isinstance(n, dict) else None
                attrs = n.get("attrs", {}) if isinstance(n, dict) else {}
                val = attrs.get("val")
                if t == "target":
                    feats["target"] = val
                elif t == "effect":
                    feats["effect"] = val
                elif t == "vector":
                    feats["vector"] = val
            return feats

        # YAML-like dict AST (top-level blocks)
        def dig(d: Any, path: str, default: Any = None) -> Any:
            cur = d
            for p in path.split("."):
                if not isinstance(cur, dict) or p not in cur:
                    return default
                cur = cur[p]
            return cur

        feats["experiment_tool"] = dig(ast, "experiment.tool")
        feats["experiment_type"] = dig(ast, "experiment.type")
        feats["strategy"] = dig(ast, "analyze.strategy") or dig(
            ast, "experiment.strategy"
        )
        feats["target_gene"] = dig(ast, "experiment.params.target_gene")
        feats["p_value"] = dig(ast, "analyze.thresholds.p_value")
        feats["log2fc"] = dig(ast, "analyze.thresholds.log2FoldChange")
        feats["simulate"] = (
            bool(ast.get("simulate")) if isinstance(ast, dict) else False
        )
        return {k: v for k, v in feats.items() if v is not None}
