"""Enhanced Inference Engine with Advanced ML Model Integration.

This module provides a comprehensive inference system with:
- Secure model loading with safety practices
- Advanced inference capabilities with confidence scoring
- Model explanation and interpretation
- Integration with performance optimization system
- Support for multiple model architectures
- Caching and optimization for better performance
"""

from __future__ import annotations

import hashlib
import json
import logging
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from gfl.performance import cached, get_monitor

# Optional ML dependencies with graceful fallback
try:
    import torch
    import torch.nn.functional as F
    from transformers import (
        AutoConfig,
        AutoModel,
        AutoModelForCausalLM,
        AutoModelForSequenceClassification,
        AutoTokenizer,
        PreTrainedModel,
        PreTrainedTokenizer,
    )

    HAS_ML_DEPS = True
except ImportError:
    # Graceful fallback for environments without ML dependencies
    HAS_ML_DEPS = False
    torch = None
    F = None

    # Mock classes for type hints when ML deps are not available
    class PreTrainedModel:
        pass

    class PreTrainedTokenizer:
        pass


# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """Enhanced inference result with confidence and explanations."""

    prediction: Any
    confidence: float
    explanation: str
    raw_output: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, float]] = None
    attention_weights: Optional[List[float]] = None
    model_metadata: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prediction": self.prediction,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "raw_output": self.raw_output,
            "feature_importance": self.feature_importance,
            "attention_weights": self.attention_weights,
            "model_metadata": self.model_metadata,
            "processing_time": self.processing_time,
        }


@dataclass
class ModelConfig:
    """Configuration for ML models."""

    model_name: str
    model_type: str = "heuristic"  # heuristic, transformers, custom
    model_path: Optional[str] = None
    tokenizer_name: Optional[str] = None
    device: str = "cpu"
    max_length: int = 512
    batch_size: int = 1
    cache_results: bool = True
    security_checks: bool = True
    revision: str = "main"  # Pin model revision for security
    trust_remote_code: bool = False  # Security: Never allow remote code

    # Model-specific parameters
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.9
    num_beams: int = 1

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.trust_remote_code:
            warnings.warn(
                "trust_remote_code=True is a security risk. "
                "Setting to False for safety.",
                UserWarning,
            )
            self.trust_remote_code = False


class BaseMLModel(ABC):
    """Abstract base class for ML models."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._model = None
        self._tokenizer = None
        self._device = torch.device(config.device) if HAS_ML_DEPS else None

    @abstractmethod
    def load_model(self) -> None:
        """Load the model and tokenizer."""
        pass

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Make predictions on input features."""
        pass

    @abstractmethod
    def explain_prediction(
        self, features: Dict[str, Any], result: InferenceResult
    ) -> str:
        """Provide explanation for the prediction."""
        pass

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None


class HeuristicModel(BaseMLModel):
    """Enhanced heuristic model with better explanations."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load heuristic rules for inference."""
        return {
            "gene_editing": {
                "keywords": ["crispr", "cas9", "cas12", "edit", "knockout"],
                "prediction": "edited",
                "confidence": 0.85,
                "explanation": "Gene editing detected based on CRISPR/Cas keywords",
            },
            "expression_analysis": {
                "keywords": ["differential", "expression", "rna-seq", "microarray"],
                "prediction": "expression_change",
                "confidence": 0.75,
                "explanation": "Expression analysis detected",
            },
            "significant_result": {
                "threshold_key": "p_value",
                "threshold_value": 0.01,
                "prediction": "significant",
                "confidence": 0.90,
                "explanation": "Statistically significant result detected",
            },
            "simulation": {
                "keywords": ["simulate", "simulation", "model"],
                "prediction": "simulated",
                "confidence": 0.70,
                "explanation": "Simulation analysis detected",
            },
        }

    def load_model(self) -> None:
        """Heuristic model doesn't need loading."""
        self._model = "loaded"  # Mark as loaded

    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Make heuristic predictions with explanations."""
        if not self.is_loaded():
            self.load_model()

        with get_monitor().time_operation("heuristic_inference"):
            # Extract text features for keyword matching
            text_features = self._extract_text_features(features)

            # Apply rules in order of priority
            for rule_name, rule in self.rules.items():
                result = self._apply_rule(rule_name, rule, features, text_features)
                if result:
                    return result

            # Default prediction
            return InferenceResult(
                prediction="unknown",
                confidence=0.5,
                explanation="No specific patterns detected, default prediction",
                raw_output=features,
                model_metadata={"model_type": "heuristic", "rules_applied": 0},
            )

    def _extract_text_features(self, features: Dict[str, Any]) -> str:
        """Extract text content from features for analysis."""
        text_parts = []
        for key, value in features.items():
            if isinstance(value, str):
                text_parts.append(value.lower())
            elif isinstance(value, dict):
                text_parts.extend(self._extract_text_features(value).split())
        return " ".join(text_parts)

    def _apply_rule(
        self, rule_name: str, rule: Dict[str, Any], features: Dict[str, Any], text: str
    ) -> Optional[InferenceResult]:
        """Apply a single heuristic rule."""
        # Keyword-based rules
        if "keywords" in rule:
            for keyword in rule["keywords"]:
                if keyword in text:
                    return InferenceResult(
                        prediction=rule["prediction"],
                        confidence=rule["confidence"],
                        explanation=f"{rule['explanation']} (keyword: {keyword})",
                        raw_output=features,
                        feature_importance={keyword: 1.0},
                        model_metadata={
                            "model_type": "heuristic",
                            "rule_applied": rule_name,
                            "matched_keyword": keyword,
                        },
                    )

        # Threshold-based rules
        if "threshold_key" in rule:
            threshold_key = rule["threshold_key"]
            threshold_value = rule["threshold_value"]

            if threshold_key in features:
                value = features[threshold_key]
                if isinstance(value, (int, float)) and value < threshold_value:
                    return InferenceResult(
                        prediction=rule["prediction"],
                        confidence=rule["confidence"],
                        explanation=f"{rule['explanation']} ({threshold_key}: {value})",
                        raw_output=features,
                        feature_importance={
                            threshold_key: abs(value - threshold_value)
                        },
                        model_metadata={
                            "model_type": "heuristic",
                            "rule_applied": rule_name,
                            "threshold_met": True,
                        },
                    )

        return None

    def explain_prediction(
        self, features: Dict[str, Any], result: InferenceResult
    ) -> str:
        """Provide detailed explanation for heuristic predictions."""
        explanation_parts = [result.explanation]

        if result.feature_importance:
            important_features = sorted(
                result.feature_importance.items(), key=lambda x: x[1], reverse=True
            )[:3]  # Top 3 features

            explanation_parts.append(
                f"Key factors: {', '.join([f'{k} ({v:.2f})' for k, v in important_features])}"
            )

        return ". ".join(explanation_parts)


class TransformersModel(BaseMLModel):
    """Model wrapper for HuggingFace Transformers with security practices."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not HAS_ML_DEPS:
            raise ImportError(
                "ML dependencies (torch, transformers) required for TransformersModel. "
                "Install with: pip install torch transformers"
            )

    def load_model(self) -> None:
        """Securely load transformers model and tokenizer."""
        with get_monitor().time_operation("model_loading"):
            try:
                # Security: Pin revision and disable remote code execution
                logger.info(f"Loading model: {self.config.model_name}")

                # Load tokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.config.tokenizer_name or self.config.model_name,
                    revision=self.config.revision,
                    trust_remote_code=False,  # Security: Never execute remote code
                    use_fast=True,
                )

                # Handle missing pad token
                if self._tokenizer.pad_token is None:
                    self._tokenizer.pad_token = self._tokenizer.eos_token

                # Load model based on type
                if self.config.model_type == "causal_lm":
                    self._model = AutoModelForCausalLM.from_pretrained(
                        self.config.model_name,
                        revision=self.config.revision,
                        trust_remote_code=False,
                        torch_dtype=torch.float16
                        if self._device.type == "cuda"
                        else torch.float32,
                    )
                elif self.config.model_type == "sequence_classification":
                    self._model = AutoModelForSequenceClassification.from_pretrained(
                        self.config.model_name,
                        revision=self.config.revision,
                        trust_remote_code=False,
                    )
                else:
                    self._model = AutoModel.from_pretrained(
                        self.config.model_name,
                        revision=self.config.revision,
                        trust_remote_code=False,
                    )

                # Move to device
                self._model.to(self._device)
                self._model.eval()  # Set to evaluation mode

                logger.info(f"Model loaded successfully on {self._device}")

            except Exception as e:
                logger.error(f"Failed to load model {self.config.model_name}: {e}")
                raise

    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Make predictions using the transformers model."""
        if not self.is_loaded():
            self.load_model()

        with get_monitor().time_operation("transformers_inference"):
            try:
                # Extract text for tokenization
                input_text = self._prepare_input_text(features)

                # Tokenize input
                inputs = self._tokenizer(
                    input_text,
                    return_tensors="pt",
                    max_length=self.config.max_length,
                    truncation=True,
                    padding=True,
                )

                # Move inputs to device
                inputs = {k: v.to(self._device) for k, v in inputs.items()}

                # Make prediction
                with torch.no_grad():
                    outputs = self._model(**inputs)

                # Process outputs based on model type
                result = self._process_outputs(outputs, inputs, features)

                return result

            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                return InferenceResult(
                    prediction="error",
                    confidence=0.0,
                    explanation=f"Prediction failed: {str(e)}",
                    raw_output={"error": str(e)},
                )

    def _prepare_input_text(self, features: Dict[str, Any]) -> str:
        """Prepare input text from features dictionary."""
        text_parts = []

        # Extract key fields in a structured way
        for key in ["experiment_tool", "experiment_type", "strategy", "target_gene"]:
            if key in features and features[key]:
                text_parts.append(f"{key}: {features[key]}")

        # Add other textual features
        for key, value in features.items():
            if isinstance(value, str) and key not in [
                "experiment_tool",
                "experiment_type",
                "strategy",
                "target_gene",
            ]:
                text_parts.append(f"{key}: {value}")

        return ". ".join(text_parts) if text_parts else "No text features available"

    def _process_outputs(
        self, outputs, inputs: Dict[str, Any], features: Dict[str, Any]
    ) -> InferenceResult:
        """Process model outputs into InferenceResult."""
        if hasattr(outputs, "logits"):
            # Classification or causal LM case
            logits = outputs.logits

            if logits.dim() == 3:  # Causal LM: [batch, seq, vocab]
                # Use last token logits for next token prediction
                logits = logits[:, -1, :]

            # Get probabilities
            probs = F.softmax(logits, dim=-1)
            confidence = float(torch.max(probs))
            predicted_class = int(torch.argmax(logits, dim=-1))

            # Generate prediction label
            if hasattr(self._model.config, "id2label"):
                prediction = self._model.config.id2label.get(
                    predicted_class, f"class_{predicted_class}"
                )
            else:
                prediction = f"class_{predicted_class}"

            # Extract attention weights if available
            attention_weights = None
            if hasattr(outputs, "attentions") and outputs.attentions:
                # Average attention across heads and layers
                attention_weights = (
                    outputs.attentions[-1].mean(dim=1).squeeze().tolist()
                )

            return InferenceResult(
                prediction=prediction,
                confidence=confidence,
                explanation=f"Transformers model prediction with {confidence:.2%} confidence",
                raw_output={
                    "logits": logits.cpu().numpy().tolist(),
                    "probabilities": probs.cpu().numpy().tolist(),
                },
                attention_weights=attention_weights,
                model_metadata={
                    "model_type": "transformers",
                    "model_name": self.config.model_name,
                    "predicted_class": predicted_class,
                },
            )

        else:
            # Generic case - use hidden states
            hidden_states = outputs.last_hidden_state
            pooled_output = torch.mean(hidden_states, dim=1)  # Mean pooling

            return InferenceResult(
                prediction="feature_extracted",
                confidence=0.8,
                explanation="Feature extraction completed",
                raw_output={
                    "hidden_states_shape": list(hidden_states.shape),
                    "pooled_features": pooled_output.cpu().numpy().tolist(),
                },
                model_metadata={
                    "model_type": "transformers",
                    "model_name": self.config.model_name,
                    "feature_dim": hidden_states.shape[-1],
                },
            )

    def explain_prediction(
        self, features: Dict[str, Any], result: InferenceResult
    ) -> str:
        """Provide explanation for transformers predictions."""
        explanation_parts = [result.explanation]

        if result.attention_weights:
            # Find tokens with highest attention
            input_text = self._prepare_input_text(features)
            tokens = self._tokenizer.tokenize(input_text)

            if len(tokens) == len(result.attention_weights):
                # Find top 3 attended tokens
                token_attention = list(zip(tokens, result.attention_weights))
                top_tokens = sorted(token_attention, key=lambda x: x[1], reverse=True)[
                    :3
                ]

                explanation_parts.append(
                    f"Key tokens: {', '.join([f'{token} ({att:.2f})' for token, att in top_tokens])}"
                )

        return ". ".join(explanation_parts)


class EnhancedInferenceEngine:
    """Enhanced inference engine with advanced ML model integration."""

    def __init__(self):
        self.models: Dict[str, BaseMLModel] = {}
        self.default_model = "heuristic"
        self._register_default_models()

    def _register_default_models(self) -> None:
        """Register default models."""
        # Register enhanced heuristic model
        heuristic_config = ModelConfig(
            model_name="enhanced_heuristic", model_type="heuristic"
        )
        self.register_model("heuristic", HeuristicModel(heuristic_config))
        self.register_model("enhanced_heuristic", HeuristicModel(heuristic_config))

    def register_model(self, name: str, model: BaseMLModel) -> None:
        """Register a new model."""
        self.models[name] = model
        logger.info(f"Registered model: {name}")

    def load_transformers_model(
        self, name: str, model_name: str, model_type: str = "auto", **kwargs
    ) -> None:
        """Load a HuggingFace transformers model."""
        if not HAS_ML_DEPS:
            raise ImportError("ML dependencies required for transformers models")

        config = ModelConfig(model_name=model_name, model_type=model_type, **kwargs)

        model = TransformersModel(config)
        self.register_model(name, model)

    @cached(cache_name="inference_results", ttl=300.0, max_size=1000)
    def predict(
        self, model_name: Optional[str], features: Dict[str, Any], explain: bool = True
    ) -> InferenceResult:
        """Make predictions using specified model."""
        model_name = model_name or self.default_model

        if model_name not in self.models:
            raise ValueError(
                f"Model '{model_name}' not found. Available: {list(self.models.keys())}"
            )

        model = self.models[model_name]

        with get_monitor().time_operation(f"inference_{model_name}"):
            # Make prediction
            result = model.predict(features)

            # Add explanation if requested
            if explain and result.explanation:
                detailed_explanation = model.explain_prediction(features, result)
                result.explanation = detailed_explanation

            # Add processing metadata
            result.model_metadata = result.model_metadata or {}
            result.model_metadata.update(
                {
                    "engine_version": "enhanced_v1.0",
                    "features_hash": self._hash_features(features),
                }
            )

            return result

    def batch_predict(
        self, model_name: Optional[str], feature_list: List[Dict[str, Any]]
    ) -> List[InferenceResult]:
        """Make batch predictions."""
        return [
            self.predict(model_name, features, explain=False)
            for features in feature_list
        ]

    def compare_models(
        self, features: Dict[str, Any], model_names: Optional[List[str]] = None
    ) -> Dict[str, InferenceResult]:
        """Compare predictions across multiple models."""
        model_names = model_names or list(self.models.keys())
        results = {}

        for model_name in model_names:
            if model_name in self.models:
                try:
                    results[model_name] = self.predict(model_name, features)
                except Exception as e:
                    logger.error(f"Model {model_name} failed: {e}")
                    results[model_name] = InferenceResult(
                        prediction="error",
                        confidence=0.0,
                        explanation=f"Model failed: {e}",
                    )

        return results

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a registered model."""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")

        model = self.models[model_name]
        return {
            "name": model_name,
            "type": model.config.model_type,
            "loaded": model.is_loaded(),
            "config": model.config.__dict__ if hasattr(model, "config") else {},
        }

    def list_models(self) -> List[str]:
        """List all registered models."""
        return list(self.models.keys())

    def _hash_features(self, features: Dict[str, Any]) -> str:
        """Create hash of features for caching."""
        feature_str = json.dumps(features, sort_keys=True, default=str)
        return hashlib.sha256(feature_str.encode()).hexdigest()[:16]


# Global inference engine instance
_inference_engine: Optional[EnhancedInferenceEngine] = None


def get_inference_engine() -> EnhancedInferenceEngine:
    """Get global inference engine instance."""
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = EnhancedInferenceEngine()
    return _inference_engine


# Convenience functions for backward compatibility
def predict_with_model(model_name: str, features: Dict[str, Any]) -> InferenceResult:
    """Convenience function for model prediction."""
    return get_inference_engine().predict(model_name, features)


def load_transformers_model(name: str, model_name: str, **kwargs) -> None:
    """Convenience function to load transformers model."""
    get_inference_engine().load_transformers_model(name, model_name, **kwargs)
