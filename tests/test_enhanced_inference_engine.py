"""Tests for enhanced inference engine and advanced ML model integration."""

import unittest
from unittest.mock import patch

# Import modules under test
try:
    from gfl.enhanced_inference_engine import (
        EnhancedInferenceEngine,
        HeuristicModel,
        InferenceResult,
        ModelConfig,
        get_inference_engine,
    )
    from gfl.models.advanced_models import (
        GenomicClassificationModel,
        MultiModalGenomicModel,
        ProteinGenerationModel,
    )

    HAS_ENHANCED_ENGINE = True
except ImportError:
    HAS_ENHANCED_ENGINE = False

# Mock torch and transformers if not available
try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class TestInferenceResult(unittest.TestCase):
    """Test InferenceResult data class."""

    def test_inference_result_creation(self):
        """Test basic InferenceResult creation."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        result = InferenceResult(
            prediction="test_prediction",
            confidence=0.85,
            explanation="Test explanation",
        )

        self.assertEqual(result.prediction, "test_prediction")
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.explanation, "Test explanation")

    def test_inference_result_to_dict(self):
        """Test InferenceResult serialization."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        result = InferenceResult(
            prediction="test",
            confidence=0.9,
            explanation="Test",
            raw_output={"key": "value"},
            feature_importance={"feature1": 0.8},
        )

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["prediction"], "test")
        self.assertEqual(result_dict["confidence"], 0.9)
        self.assertEqual(result_dict["raw_output"]["key"], "value")


class TestModelConfig(unittest.TestCase):
    """Test ModelConfig class."""

    def test_model_config_creation(self):
        """Test ModelConfig creation with defaults."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="test_model")

        self.assertEqual(config.model_name, "test_model")
        self.assertEqual(config.model_type, "heuristic")
        self.assertEqual(config.device, "cpu")
        self.assertFalse(config.trust_remote_code)  # Should default to False for security

    def test_model_config_security_override(self):
        """Test that trust_remote_code is forced to False for security."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        # Try to set trust_remote_code=True, should be overridden to False
        with patch("warnings.warn") as mock_warn:
            config = ModelConfig(model_name="test_model", trust_remote_code=True)

            self.assertFalse(config.trust_remote_code)
            mock_warn.assert_called_once()


class TestHeuristicModel(unittest.TestCase):
    """Test HeuristicModel implementation."""

    def test_heuristic_model_creation(self):
        """Test heuristic model creation."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="test_heuristic", model_type="heuristic")
        model = HeuristicModel(config)

        self.assertIsInstance(model.rules, dict)
        self.assertIn("gene_editing", model.rules)
        self.assertIn("expression_analysis", model.rules)

    def test_heuristic_model_prediction(self):
        """Test heuristic model predictions."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="test_heuristic")
        model = HeuristicModel(config)

        # Test gene editing detection
        features = {"experiment_tool": "CRISPR_cas9", "experiment_type": "gene_editing"}

        result = model.predict(features)

        self.assertIsInstance(result, InferenceResult)
        self.assertEqual(result.prediction, "edited")
        self.assertGreater(result.confidence, 0.8)
        self.assertIn("editing", result.explanation.lower())

    def test_heuristic_model_threshold_rules(self):
        """Test threshold-based heuristic rules."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="test_heuristic")
        model = HeuristicModel(config)

        # Test p-value threshold rule
        features = {"p_value": 0.005}  # Below 0.01 threshold

        result = model.predict(features)

        self.assertEqual(result.prediction, "significant")
        self.assertGreater(result.confidence, 0.85)

    def test_heuristic_model_default_prediction(self):
        """Test default prediction for unknown features."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="test_heuristic")
        model = HeuristicModel(config)

        # Empty features should give unknown prediction
        features = {}

        result = model.predict(features)

        self.assertEqual(result.prediction, "unknown")
        self.assertEqual(result.confidence, 0.5)


@unittest.skipUnless(HAS_TORCH, "PyTorch not available")
class TestTransformersModel(unittest.TestCase):
    """Test TransformersModel implementation."""

    def test_transformers_model_creation(self):
        """Test transformers model creation."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        config = ModelConfig(model_name="distilbert-base-uncased", model_type="auto", device="cpu")

        # Don't actually load the model in tests
        with patch("gfl.enhanced_inference_engine.AutoTokenizer"):
            with patch("gfl.enhanced_inference_engine.AutoModel"):
                from gfl.enhanced_inference_engine import TransformersModel

                model = TransformersModel(config)

                self.assertEqual(model.config.model_name, "distilbert-base-uncased")
                self.assertFalse(model.is_loaded())


class TestAdvancedModels(unittest.TestCase):
    """Test advanced model implementations."""

    def test_genomic_classification_model_heuristic(self):
        """Test genomic classification model heuristic fallback."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        # Create model that will fall back to heuristics
        model = GenomicClassificationModel()

        # Test gene editing classification
        features = {"experiment_tool": "CRISPR_cas9", "experiment_type": "gene_editing"}

        result = model.predict(features)

        self.assertIsInstance(result, InferenceResult)
        self.assertEqual(result.prediction, "gene_editing")
        self.assertGreater(result.confidence, 0.8)

    def test_protein_generation_model_seed_extraction(self):
        """Test protein generation model seed extraction."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        model = ProteinGenerationModel()

        # Test kinase domain detection
        features = {"experiment_type": "kinase domain analysis"}
        seed = model._extract_protein_seed(features)

        self.assertEqual(seed, "MKKK")

        # Test nuclear localization detection
        features = {"target": "nuclear localization signal"}
        seed = model._extract_protein_seed(features)

        self.assertEqual(seed, "MPRRR")

    def test_multimodal_model_component_integration(self):
        """Test multimodal model component integration."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        model = MultiModalGenomicModel()

        # Test that component models are created
        self.assertIsNotNone(model.protein_model)
        self.assertIsNotNone(model.classification_model)

        # Test should_generate_protein logic
        features = {"experiment_type": "protein analysis"}
        mock_result = InferenceResult("test", 0.8, "test")

        should_generate = model._should_generate_protein(features, mock_result)
        self.assertTrue(should_generate)


class TestEnhancedInferenceEngine(unittest.TestCase):
    """Test EnhancedInferenceEngine functionality."""

    def test_engine_creation(self):
        """Test inference engine creation."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        self.assertIn("heuristic", engine.list_models())
        self.assertEqual(engine.default_model, "heuristic")

    def test_model_registration(self):
        """Test model registration."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        # Register a new heuristic model
        config = ModelConfig(model_name="custom_heuristic")
        custom_model = HeuristicModel(config)

        engine.register_model("custom", custom_model)

        self.assertIn("custom", engine.list_models())

        # Test model info
        info = engine.get_model_info("custom")
        self.assertEqual(info["type"], "heuristic")
        self.assertFalse(info["loaded"])  # Not loaded initially

    def test_prediction_with_caching(self):
        """Test prediction with caching."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        features = {"experiment_tool": "CRISPR_cas9"}

        # First prediction
        result1 = engine.predict("heuristic", features)

        # Second prediction should use cache (same features)
        result2 = engine.predict("heuristic", features)

        self.assertEqual(result1.prediction, result2.prediction)
        self.assertEqual(result1.confidence, result2.confidence)

    def test_model_comparison(self):
        """Test model comparison functionality."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        features = {"experiment_tool": "CRISPR_cas9", "target_gene": "TP53"}

        # Compare available models
        results = engine.compare_models(features)

        self.assertIsInstance(results, dict)
        self.assertIn("heuristic", results)

        # Each result should be an InferenceResult
        for model_name, result in results.items():
            self.assertIsInstance(result, InferenceResult)

    def test_batch_prediction(self):
        """Test batch prediction functionality."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        feature_list = [
            {"experiment_tool": "CRISPR_cas9"},
            {"experiment_type": "RNA-seq"},
            {"p_value": 0.001},
        ]

        results = engine.batch_predict("heuristic", feature_list)

        self.assertEqual(len(results), 3)
        self.assertTrue(all(isinstance(r, InferenceResult) for r in results))

    def test_global_inference_engine(self):
        """Test global inference engine singleton."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine1 = get_inference_engine()
        engine2 = get_inference_engine()

        # Should be the same instance
        self.assertIs(engine1, engine2)

    def test_error_handling(self):
        """Test error handling for invalid models."""
        if not HAS_ENHANCED_ENGINE:
            self.skipTest("Enhanced inference engine not available")

        engine = EnhancedInferenceEngine()

        # Test prediction with non-existent model
        with self.assertRaises(ValueError):
            engine.predict("nonexistent_model", {})

        # Test model info for non-existent model
        with self.assertRaises(ValueError):
            engine.get_model_info("nonexistent_model")


class TestIntegrationWithLegacyEngine(unittest.TestCase):
    """Test integration with legacy inference engine."""

    def test_legacy_engine_enhancement(self):
        """Test that legacy engine can use enhanced features."""
        # This test requires both old and new engines
        try:
            from gfl.inference_engine import InferenceEngine
            from gfl.models.dummy import DummyGeneModel

            # Create legacy engine with dummy model
            legacy_model = DummyGeneModel()
            engine = InferenceEngine(legacy_model)

            # Test enhanced prediction
            ast_dict = {
                "experiment": {
                    "tool": "CRISPR_cas9",
                    "type": "gene_editing",
                    "params": {"target_gene": "TP53"},
                }
            }

            # Test with enhanced=False (legacy path)
            result_legacy = engine.predict_effect(ast_dict, enhanced=False)
            self.assertIn("label", result_legacy)
            self.assertIn("confidence", result_legacy)

            # Test with enhanced=True if available
            if HAS_ENHANCED_ENGINE:
                result_enhanced = engine.predict_effect(ast_dict, enhanced=True)
                self.assertIn("label", result_enhanced)
                self.assertIn("confidence", result_enhanced)
                # Enhanced result should have additional fields
                self.assertTrue(
                    "enhanced_result" in result_enhanced
                    or result_enhanced["explanation"] != result_legacy["explanation"]
                )

        except ImportError:
            self.skipTest("Legacy inference engine not available")


if __name__ == "__main__":
    unittest.main()
