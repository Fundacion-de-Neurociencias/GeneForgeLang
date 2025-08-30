from typing import Any, Dict, Optional

from gfl.prob_rules import ProbReasoner, default_rules

# Import enhanced inference capabilities
try:
    from gfl.enhanced_inference_engine import (
        EnhancedInferenceEngine,
        get_inference_engine,
        InferenceResult,
    )

    HAS_ENHANCED_ENGINE = True
except ImportError:
    HAS_ENHANCED_ENGINE = False
    EnhancedInferenceEngine = None
    InferenceResult = None


class InferenceEngine:
    """Inference engine with probabilistic rule layer."""

    def __init__(self, model):
        self.model = model
        self.reasoner = ProbReasoner(default_rules())

        # Enhanced inference engine integration
        if HAS_ENHANCED_ENGINE:
            self.enhanced_engine = get_inference_engine()
            # Register the legacy model if it has a predict method
            if hasattr(model, "predict"):
                try:
                    from gfl.enhanced_inference_engine import ModelConfig, BaseMLModel

                    class LegacyModelWrapper(BaseMLModel):
                        def __init__(self, legacy_model):
                            config = ModelConfig(
                                model_name="legacy_model", model_type="heuristic"
                            )
                            super().__init__(config)
                            self.legacy_model = legacy_model

                        def load_model(self):
                            self._model = self.legacy_model

                        def predict(self, features):
                            result = self.legacy_model.predict(features)
                            return InferenceResult(
                                prediction=result.get("label", "unknown"),
                                confidence=0.7,  # Default confidence for legacy models
                                explanation="Legacy model prediction",
                                raw_output=result,
                            )

                        def explain_prediction(self, features, result):
                            return "Legacy model - limited explanation available"

                    wrapper = LegacyModelWrapper(model)
                    self.enhanced_engine.register_model("legacy", wrapper)
                except Exception:
                    # If registration fails, continue without enhanced features
                    pass
        else:
            self.enhanced_engine = None

    # ------------------------------------------------------------------ #
    def predict_effect(
        self,
        ast_dict: Dict[str, Any],
        enhanced: bool = True,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Predict genomic effects with optional enhanced inference.

        Args:
            ast_dict: AST dictionary containing experiment details
            enhanced: Whether to use enhanced inference engine if available
            model_name: Specific model to use ("heuristic", "legacy", etc.)

        Returns:
            Dictionary with prediction results
        """
        features = self._extract_features(ast_dict)

        # Try enhanced inference first if available and requested
        if enhanced and self.enhanced_engine:
            try:
                model_name = model_name or "heuristic"  # Default to heuristic model

                result = self.enhanced_engine.predict(model_name, features)

                # Apply probabilistic reasoning to enhance the result
                post = self.reasoner.posterior(dict(ast_dict))

                # Combine enhanced result with probabilistic reasoning
                enhanced_confidence = (result.confidence + post["confidence"]) / 2

                explanation_parts = [result.explanation]
                if post["fired_rules"]:
                    explanation_parts.append(
                        f"Rules applied: {', '.join(post['fired_rules'])}"
                    )

                return {
                    "label": result.prediction
                    if isinstance(result.prediction, str)
                    else str(result.prediction),
                    "confidence": enhanced_confidence,
                    "explanation": ". ".join(explanation_parts),
                    "enhanced_result": result.to_dict(),
                    "probabilistic_reasoning": post,
                }

            except Exception:
                # Fall back to legacy inference if enhanced fails
                pass

        # Legacy inference path
        base = self.model.predict(features)
        post = self.reasoner.posterior(dict(ast_dict))  # best-effort copy
        return {
            "label": base.get("label", "unknown"),
            "confidence": post["confidence"],
            "explanation": ", ".join(post["fired_rules"] or ["base_only"]),
        }

    def generate_protein(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate protein sequence based on GFL specification.

        Uses enhanced inference engine if available, falls back to simple heuristic.
        """
        if self.enhanced_engine:
            try:
                # Try to use protein generation model
                features = self._extract_features(ast_dict)
                result = self.enhanced_engine.predict("protein_generation", features)

                return {
                    "sequence": result.prediction,
                    "confidence": result.confidence,
                    "explanation": result.explanation,
                    "analysis": result.raw_output,
                }
            except Exception:
                # Fall back to heuristic
                pass

        # Simple heuristic protein generation
        features = self._extract_features(ast_dict)
        seed = "M"  # Default methionine start

        if "kinase" in str(features).lower():
            seed += "KKK"
        if "nuclear" in str(features).lower():
            seed += "RRR"

        return {
            "sequence": seed + "ACDEFGHIKLMNPQRSTVWY"[:20],  # Simple sequence
            "confidence": 0.3,
            "explanation": "Simple heuristic protein generation",
        }

    def compare_models(
        self, ast_dict: Dict[str, Any], model_names: Optional[list] = None
    ) -> Dict[str, Any]:
        """Compare predictions across multiple models."""
        if not self.enhanced_engine:
            return {"error": "Enhanced inference engine not available"}

        try:
            features = self._extract_features(ast_dict)
            results = self.enhanced_engine.compare_models(features, model_names)

            return {
                "comparisons": {k: v.to_dict() for k, v in results.items()},
                "available_models": self.enhanced_engine.list_models(),
            }
        except Exception as e:
            return {"error": str(e)}

    # Enhanced stubs for completeness
    def retroinfer_cause(self, phenotype: str) -> Dict[str, Any]:
        """Infer potential genetic causes for observed phenotype."""
        # This could be enhanced with actual causality inference
        return {"variant": "rs0", "confidence": 0.4, "method": "heuristic"}

    def evaluate_off_target(self, ast_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate potential off-target effects for gene editing experiments."""
        features = self._extract_features(ast_dict)

        # Enhanced off-target evaluation if CRISPR is detected
        if "crispr" in str(features).lower():
            return {
                "off_target_hits": [],
                "risk_score": 0.2,
                "evaluation_method": "enhanced_heuristic",
                "recommendations": ["Validate with additional assays"],
            }

        return {"off_target_hits": [], "risk_score": 0.1}

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
