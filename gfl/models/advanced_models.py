"""Advanced ML Models for GeneForgeLang Inference.

This module provides enhanced model implementations with:
- Protein sequence generation models (ProtGPT2 integration)
- Genomic classification models
- Multi-modal models for different genomic tasks
- Secure model loading and caching
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from gfl.enhanced_inference_engine import (
    BaseMLModel,
    InferenceResult,
    ModelConfig,
    TransformersModel,
)

# Optional ML dependencies with graceful fallback
try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModelForCausalLM, AutoTokenizer

    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False
    torch = None
    F = None

logger = logging.getLogger(__name__)


class ProteinGenerationModel(TransformersModel):
    """Specialized model for protein sequence generation using ProtGPT2."""

    def __init__(self, config: Optional[ModelConfig] = None):
        if config is None:
            config = ModelConfig(
                model_name="nferruz/ProtGPT2",
                model_type="causal_lm",
                tokenizer_name="nferruz/ProtGPT2",
                max_length=200,
                temperature=0.8,
                top_k=50,
                top_p=0.9,
            )
        super().__init__(config)

        # Protein-specific seed mappings
        self.protein_seeds = {
            "kinase_domain": "MKKK",
            "nuclear_localization": "MPRRR",
            "pest_degradation": "MDGQL",
            "transcription_factor": "MKTFG",
            "acetylation_site": "MKQAK",
            "phosphorylation_site": "MKRP",
            "nuclear_transport": "MPKRK",
            "membrane_localization": "MAIFL",
            "default": "M",
        }

    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Generate protein sequence based on GFL features."""
        if not self.is_loaded():
            self.load_model()

        try:
            # Extract protein generation seed from features
            seed = self._extract_protein_seed(features)

            # Generate protein sequence
            protein_sequence = self._generate_protein_sequence(seed)

            # Analyze generated sequence
            analysis = self._analyze_protein_sequence(protein_sequence)

            return InferenceResult(
                prediction=protein_sequence,
                confidence=analysis["confidence"],
                explanation=f"Generated protein sequence from seed '{seed}': {analysis['description']}",
                raw_output={
                    "seed_used": seed,
                    "sequence_length": len(protein_sequence),
                    "amino_acid_composition": analysis["composition"],
                },
                feature_importance=analysis.get("feature_importance", {}),
                model_metadata={
                    "model_type": "protein_generation",
                    "model_name": self.config.model_name,
                    "generation_params": {
                        "temperature": self.config.temperature,
                        "top_k": self.config.top_k,
                        "max_length": self.config.max_length,
                    },
                },
            )

        except Exception as e:
            logger.error(f"Protein generation failed: {e}")
            return InferenceResult(
                prediction="",
                confidence=0.0,
                explanation=f"Protein generation failed: {str(e)}",
                raw_output={"error": str(e)},
            )

    def _extract_protein_seed(self, features: Dict[str, Any]) -> str:
        """Extract appropriate protein seed from GFL features."""
        # Check for specific protein features mentioned in the GFL code
        feature_text = str(features).lower()

        # Priority-based mapping
        if any(keyword in feature_text for keyword in ["kinase", "kin", "domain"]):
            return self.protein_seeds["kinase_domain"]
        elif any(keyword in feature_text for keyword in ["nuclear", "nls", "nucleus"]):
            return self.protein_seeds["nuclear_localization"]
        elif any(keyword in feature_text for keyword in ["pest", "degradation"]):
            return self.protein_seeds["pest_degradation"]
        elif any(keyword in feature_text for keyword in ["transcription", "tf", "gata"]):
            return self.protein_seeds["transcription_factor"]
        elif any(keyword in feature_text for keyword in ["acetyl", "ack", "acetylation"]):
            return self.protein_seeds["acetylation_site"]
        elif any(keyword in feature_text for keyword in ["phosphor", "phospho", "kinase"]):
            return self.protein_seeds["phosphorylation_site"]
        elif any(keyword in feature_text for keyword in ["membrane", "localize"]):
            return self.protein_seeds["membrane_localization"]
        else:
            return self.protein_seeds["default"]

    def _generate_protein_sequence(self, seed: str) -> str:
        """Generate protein sequence using the model."""
        # Tokenize seed
        inputs = self._tokenizer(seed, return_tensors="pt", padding=True)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        # Generate sequence
        with torch.no_grad():
            output = self._model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_length=self.config.max_length,
                min_length=20,
                do_sample=True,
                top_k=self.config.top_k,
                top_p=self.config.top_p,
                temperature=self.config.temperature,
                pad_token_id=self._tokenizer.eos_token_id,
                num_return_sequences=1,
                early_stopping=True,
            )

        # Decode generated sequence
        generated_sequence = self._tokenizer.decode(output[0], skip_special_tokens=True)

        # Clean up the sequence (remove seed if present)
        if generated_sequence.startswith(seed):
            generated_sequence = generated_sequence[len(seed) :].strip()

        return generated_sequence

    def _analyze_protein_sequence(self, sequence: str) -> Dict[str, Any]:
        """Analyze generated protein sequence."""
        if not sequence:
            return {
                "confidence": 0.0,
                "description": "Empty sequence generated",
                "composition": {},
            }

        # Count amino acids
        amino_acids = "ACDEFGHIKLMNPQRSTVWY"
        composition = {}
        for aa in amino_acids:
            count = sequence.count(aa)
            if count > 0:
                composition[aa] = count / len(sequence)

        # Basic quality metrics
        length_score = min(len(sequence) / 50, 1.0)  # Prefer sequences around 50 AA
        diversity_score = len(composition) / 20  # Amino acid diversity

        # Check for common protein motifs (simplified)
        motif_score = 0.0
        common_motifs = ["KK", "RR", "NLS", "PEST", "ATP"]
        for motif in common_motifs:
            if motif in sequence.upper():
                motif_score += 0.2

        confidence = (length_score + diversity_score + min(motif_score, 1.0)) / 3

        # Generate description
        description_parts = [
            f"Length: {len(sequence)} AA",
            f"Diversity: {len(composition)} different amino acids",
        ]

        if motif_score > 0:
            description_parts.append("Contains recognizable motifs")

        return {
            "confidence": confidence,
            "description": ", ".join(description_parts),
            "composition": composition,
            "feature_importance": {
                "sequence_length": length_score,
                "amino_acid_diversity": diversity_score,
                "motif_presence": min(motif_score, 1.0),
            },
        }

    def explain_prediction(self, features: Dict[str, Any], result: InferenceResult) -> str:
        """Explain protein generation prediction."""
        explanation_parts = [result.explanation]

        if result.raw_output:
            seed = result.raw_output.get("seed_used", "unknown")
            length = result.raw_output.get("sequence_length", 0)

            explanation_parts.append(f"Used seed '{seed}' to generate {length} amino acid sequence")

            if result.feature_importance:
                top_factors = sorted(result.feature_importance.items(), key=lambda x: x[1], reverse=True)
                explanation_parts.append(f"Quality factors: {', '.join([f'{k} ({v:.2f})' for k, v in top_factors])}")

        return ". ".join(explanation_parts)


class GenomicClassificationModel(TransformersModel):
    """Model for classifying genomic experiments and their outcomes."""

    def __init__(self, config: Optional[ModelConfig] = None):
        if config is None:
            config = ModelConfig(
                model_name="microsoft/DialoGPT-medium",  # Can be replaced with specialized model
                model_type="sequence_classification",
                max_length=512,
            )
        super().__init__(config)

        # Genomic classification categories
        self.classification_rules = {
            "gene_editing": {
                "keywords": ["crispr", "cas9", "cas12", "edit", "knockout", "knock-in"],
                "confidence_boost": 0.9,
            },
            "expression_analysis": {
                "keywords": ["rna-seq", "microarray", "expression", "differential"],
                "confidence_boost": 0.85,
            },
            "variant_analysis": {
                "keywords": ["snp", "variant", "mutation", "gwas"],
                "confidence_boost": 0.8,
            },
            "epigenetic_analysis": {
                "keywords": ["methylation", "histone", "chromatin", "chip-seq"],
                "confidence_boost": 0.75,
            },
            "functional_analysis": {
                "keywords": ["pathway", "enrichment", "go", "kegg"],
                "confidence_boost": 0.7,
            },
        }

    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Classify genomic experiment type and significance."""
        if not self.is_loaded():
            # Use heuristic classification if model not loaded
            return self._heuristic_classification(features)

        try:
            # Prepare input for classification
            self._prepare_classification_input(features)

            # Use parent class for transformers prediction
            base_result = super().predict(features)

            # Enhance with genomic-specific analysis
            enhanced_result = self._enhance_genomic_classification(features, base_result)

            return enhanced_result

        except Exception as e:
            logger.warning(f"Transformers classification failed, using heuristic: {e}")
            return self._heuristic_classification(features)

    def _prepare_classification_input(self, features: Dict[str, Any]) -> str:
        """Prepare structured input for genomic classification."""
        input_parts = []

        # Add experiment details
        if "experiment" in features:
            exp = features["experiment"]
            if isinstance(exp, dict):
                tool = exp.get("tool", "")
                exp_type = exp.get("type", "")
                if tool:
                    input_parts.append(f"Tool: {tool}")
                if exp_type:
                    input_parts.append(f"Type: {exp_type}")

        # Add analysis strategy
        if "analyze" in features:
            analyze = features["analyze"]
            if isinstance(analyze, dict):
                strategy = analyze.get("strategy", "")
                if strategy:
                    input_parts.append(f"Analysis: {strategy}")

        # Add parameters
        for key in ["target_gene", "p_value", "log2FoldChange"]:
            if key in features:
                input_parts.append(f"{key}: {features[key]}")

        return ". ".join(input_parts) if input_parts else "Genomic analysis task"

    def _heuristic_classification(self, features: Dict[str, Any]) -> InferenceResult:
        """Fallback heuristic classification."""
        feature_text = str(features).lower()

        # Find best matching category
        best_category = "unknown"
        best_confidence = 0.5
        matched_keywords = []

        for category, rules in self.classification_rules.items():
            matches = []
            for keyword in rules["keywords"]:
                if keyword in feature_text:
                    matches.append(keyword)

            if matches:
                confidence = rules["confidence_boost"] * (len(matches) / len(rules["keywords"]))
                if confidence > best_confidence:
                    best_category = category
                    best_confidence = confidence
                    matched_keywords = matches

        return InferenceResult(
            prediction=best_category,
            confidence=best_confidence,
            explanation=f"Classified as {best_category} based on keywords: {', '.join(matched_keywords)}",
            raw_output=features,
            feature_importance={kw: 1.0 for kw in matched_keywords},
            model_metadata={
                "model_type": "genomic_classification_heuristic",
                "matched_keywords": matched_keywords,
                "classification_rules_applied": len(matched_keywords),
            },
        )

    def _enhance_genomic_classification(
        self, features: Dict[str, Any], base_result: InferenceResult
    ) -> InferenceResult:
        """Enhance base classification with genomic domain knowledge."""
        # Apply genomic-specific rules to boost confidence
        feature_text = str(features).lower()

        prediction = base_result.prediction
        confidence = base_result.confidence
        explanation_parts = [base_result.explanation]

        # Check for genomic keywords and boost confidence
        for category, rules in self.classification_rules.items():
            matched_keywords = [kw for kw in rules["keywords"] if kw in feature_text]
            if matched_keywords and category.lower() in prediction.lower():
                boost = len(matched_keywords) * 0.1
                confidence = min(confidence + boost, 1.0)
                explanation_parts.append(f"Confidence boosted by genomic keywords: {', '.join(matched_keywords)}")

        return InferenceResult(
            prediction=prediction,
            confidence=confidence,
            explanation=". ".join(explanation_parts),
            raw_output=base_result.raw_output,
            feature_importance=base_result.feature_importance,
            attention_weights=base_result.attention_weights,
            model_metadata={**base_result.model_metadata, "genomic_enhancement": True},
        )


class MultiModalGenomicModel(BaseMLModel):
    """Multi-modal model that combines different specialized models."""

    def __init__(self, config: Optional[ModelConfig] = None):
        if config is None:
            config = ModelConfig(model_name="multimodal_genomic", model_type="multimodal")
        super().__init__(config)

        # Initialize component models
        self.protein_model = ProteinGenerationModel()
        self.classification_model = GenomicClassificationModel()

    def load_model(self) -> None:
        """Load all component models."""
        try:
            # Load protein model if ML dependencies available
            if HAS_ML_DEPS:
                self.protein_model.load_model()
                logger.info("Protein generation model loaded")
        except Exception as e:
            logger.warning(f"Could not load protein model: {e}")

        # Classification model uses heuristics as fallback
        self._model = "loaded"  # Mark as loaded

    def predict(self, features: Dict[str, Any]) -> InferenceResult:
        """Multi-modal prediction combining classification and generation."""
        if not self.is_loaded():
            self.load_model()

        # Get classification prediction
        classification_result = self.classification_model.predict(features)

        results = {"classification": classification_result}

        # Add protein generation if appropriate
        if self._should_generate_protein(features, classification_result):
            try:
                protein_result = self.protein_model.predict(features)
                results["protein_generation"] = protein_result
            except Exception as e:
                logger.warning(f"Protein generation failed: {e}")

        # Combine results
        combined_result = self._combine_results(results, features)

        return combined_result

    def _should_generate_protein(self, features: Dict[str, Any], classification: InferenceResult) -> bool:
        """Determine if protein generation is appropriate."""
        # Generate protein if it's a protein-related experiment
        protein_related = any(
            keyword in str(features).lower() for keyword in ["protein", "peptide", "amino", "sequence"]
        )

        classification_suggests_protein = any(
            keyword in classification.prediction.lower() for keyword in ["edit", "expression", "functional"]
        )

        return protein_related or classification_suggests_protein

    def _combine_results(self, results: Dict[str, InferenceResult], features: Dict[str, Any]) -> InferenceResult:
        """Combine multiple model results into unified prediction."""
        classification = results["classification"]

        # Base result from classification
        combined_prediction = {
            "experiment_type": classification.prediction,
            "classification_confidence": classification.confidence,
        }

        explanation_parts = [f"Experiment classified as: {classification.prediction}"]

        # Add protein generation if available
        if "protein_generation" in results:
            protein_result = results["protein_generation"]
            combined_prediction["generated_protein"] = protein_result.prediction
            combined_prediction["protein_confidence"] = protein_result.confidence

            explanation_parts.append(f"Generated protein sequence of {len(protein_result.prediction)} amino acids")

        # Calculate overall confidence
        confidences = [r.confidence for r in results.values()]
        overall_confidence = sum(confidences) / len(confidences)

        return InferenceResult(
            prediction=combined_prediction,
            confidence=overall_confidence,
            explanation=". ".join(explanation_parts),
            raw_output={
                "individual_results": {k: v.to_dict() for k, v in results.items()},
                "features": features,
            },
            model_metadata={
                "model_type": "multimodal",
                "component_models": list(results.keys()),
                "combination_strategy": "weighted_average",
            },
        )

    def explain_prediction(self, features: Dict[str, Any], result: InferenceResult) -> str:
        """Explain multi-modal prediction."""
        explanation_parts = [result.explanation]

        if result.raw_output and "individual_results" in result.raw_output:
            individual_results = result.raw_output["individual_results"]

            explanation_parts.append("Component model results:")
            for model_name, model_result in individual_results.items():
                explanation_parts.append(f"- {model_name}: {model_result['explanation']}")

        return "\n".join(explanation_parts)


# Model factory functions
def create_protein_generation_model() -> ProteinGenerationModel:
    """Create protein generation model with default configuration."""
    return ProteinGenerationModel()


def create_genomic_classification_model() -> GenomicClassificationModel:
    """Create genomic classification model with default configuration."""
    return GenomicClassificationModel()


def create_multimodal_genomic_model() -> MultiModalGenomicModel:
    """Create multi-modal genomic model."""
    return MultiModalGenomicModel()
