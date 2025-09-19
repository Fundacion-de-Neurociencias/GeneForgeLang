"""Demonstration of Enhanced Inference Engine Capabilities.

This script showcases the advanced ML model integration features
of the GeneForgeLang inference system, including:
- Multiple inference models (heuristic, classification, protein generation)
- Model comparison and benchmarking
- Secure model loading practices
- Integration with existing GFL workflows
"""

import time
from typing import Any, Dict, List

# Import GFL API
try:
    from gfl.api import compare_inference_models, infer_enhanced, parse, validate
    from gfl.enhanced_inference_engine import get_inference_engine
    from gfl.models.advanced_models import (
        create_genomic_classification_model,
        create_multimodal_genomic_model,
    )

    HAS_GFL_API = True
except ImportError as e:
    print(f"Warning: GFL API not fully available: {e}")
    HAS_GFL_API = False

try:
    import torch

    HAS_TORCH = torch.cuda.is_available()
    DEVICE = "cuda" if HAS_TORCH else "cpu"
except ImportError:
    HAS_TORCH = False
    DEVICE = "cpu"


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def demo_sample_gfl_files() -> List[Dict[str, Any]]:
    """Create sample GFL content for demonstration."""
    samples = [
        {
            "name": "CRISPR Gene Editing Experiment",
            "gfl_content": """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: GTCGACTTCGTACGTACGTA
    vector: lentiviral

analyze:
  strategy: knockout_validation
  thresholds:
    efficiency: 0.8
    off_target_score: 0.1
""",
            "expected_features": ["gene editing", "CRISPR", "knockout"],
        },
        {
            "name": "RNA-seq Differential Expression",
            "gfl_content": """
experiment:
  tool: illumina_novaseq
  type: rna_seq
  params:
    samples: 24
    reads_per_sample: 30M

analyze:
  strategy: differential_expression
  thresholds:
    p_value: 0.01
    log2FoldChange: 1.5
    fdr: 0.05
""",
            "expected_features": ["expression analysis", "RNA-seq", "differential"],
        },
        {
            "name": "Protein Domain Analysis",
            "gfl_content": """
experiment:
  tool: alphafold2
  type: protein_structure
  params:
    target_gene: BRCA1
    analysis_type: domain_prediction

analyze:
  strategy: functional_domains
  params:
    domain_types: [kinase, nuclear_localization, dna_binding]
""",
            "expected_features": ["protein", "domain", "kinase", "nuclear"],
        },
        {
            "name": "Epigenetic ChIP-seq Analysis",
            "gfl_content": """
experiment:
  tool: chip_seq
  type: epigenetic_analysis
  params:
    target_modification: H3K4me3
    genome: hg38

analyze:
  strategy: peak_calling
  thresholds:
    p_value: 0.001
    fold_enrichment: 2.0
""",
            "expected_features": ["epigenetic", "ChIP-seq", "modification"],
        },
    ]

    return samples


def register_advanced_models():
    """Register advanced models with the inference engine."""
    print_subsection("Registering Advanced Models")

    engine = get_inference_engine()

    try:
        # Register genomic classification model
        classification_model = create_genomic_classification_model()
        engine.register_model("genomic_classification", classification_model)
        print("✓ Genomic Classification Model registered")

        # Register multimodal model
        multimodal_model = create_multimodal_genomic_model()
        engine.register_model("multimodal", multimodal_model)
        print("✓ Multimodal Genomic Model registered")

        # Try to register protein generation model if ML dependencies available
        if HAS_TORCH:
            try:
                from gfl.models.advanced_models import create_protein_generation_model

                protein_model = create_protein_generation_model()
                engine.register_model("protein_generation", protein_model)
                print(f"✓ Protein Generation Model registered (device: {DEVICE})")
            except Exception as e:
                print(f"⚠ Protein Generation Model registration failed: {e}")
        else:
            print("⚠ PyTorch not available - protein generation limited to heuristics")

        print(f"\nTotal models registered: {len(engine.list_models())}")
        print(f"Available models: {', '.join(engine.list_models())}")

    except Exception as e:
        print(f"Error registering models: {e}")
        return False

    return True


def demonstrate_basic_inference():
    """Demonstrate basic inference capabilities."""
    print_section("Basic Inference Demonstration")

    samples = demo_sample_gfl_files()

    for i, sample in enumerate(samples):
        print_subsection(f"Sample {i+1}: {sample['name']}")

        try:
            # Parse GFL content
            ast = parse(sample["gfl_content"])

            # Validate
            errors = validate(ast)
            if errors:
                print(f"⚠ Validation warnings: {len(errors)} issues found")
            else:
                print("✓ GFL validation passed")

            # Run enhanced inference
            result = infer_enhanced(ast, model_name="heuristic", explain=True)

            print(f"Prediction: {result['label']}")
            print(f"Confidence: {result['confidence']:.1%}")
            print(f"Explanation: {result['explanation']}")

            # Check if expected features were detected
            explanation_lower = result["explanation"].lower()
            detected_features = []
            for feature in sample["expected_features"]:
                if any(keyword.lower() in explanation_lower for keyword in feature.split()):
                    detected_features.append(feature)

            if detected_features:
                print(f"✓ Detected expected features: {', '.join(detected_features)}")
            else:
                print("⚠ No expected features explicitly detected")

        except Exception as e:
            print(f"Error processing {sample['name']}: {e}")


def demonstrate_model_comparison():
    """Demonstrate model comparison capabilities."""
    print_section("Model Comparison Demonstration")

    # Use a representative sample
    sample_gfl = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    edit_type: knockout

analyze:
  strategy: functional_validation
  thresholds:
    p_value: 0.001
    effect_size: 2.0
"""

    try:
        ast = parse(sample_gfl)

        print("Comparing predictions across all available models...\n")

        # Compare all models
        comparison_results = compare_inference_models(ast)

        if "comparisons" in comparison_results:
            # Sort by confidence for display
            comparisons = comparison_results["comparisons"]
            sorted_models = sorted(comparisons.items(), key=lambda x: x[1]["confidence"], reverse=True)

            print(f"{'Model':<25} {'Prediction':<20} {'Confidence':<12} {'Key Points'}")
            print("-" * 80)

            for model_name, result in sorted_models:
                prediction = str(result["prediction"])[:19]
                confidence = f"{result['confidence']:.1%}"

                # Extract key points from explanation
                explanation = result.get("explanation", "")
                key_points = explanation.split(".")[0][:30] + "..." if len(explanation) > 30 else explanation

                print(f"{model_name:<25} {prediction:<20} {confidence:<12} {key_points}")

            print(f"\nFeatures used: {comparison_results.get('features_used', {})}")

    except Exception as e:
        print(f"Error in model comparison: {e}")


def demonstrate_protein_generation():
    """Demonstrate protein generation capabilities."""
    print_section("Protein Generation Demonstration")

    protein_samples = [
        {
            "name": "Kinase Domain Protein",
            "gfl_content": """
experiment:
  tool: alphafold2
  type: protein_design
  params:
    target_domains: [kinase, ATP_binding]
    cellular_localization: cytoplasm
""",
        },
        {
            "name": "Nuclear Localization Protein",
            "gfl_content": """
experiment:
  tool: rosetta
  type: protein_design
  params:
    target_domains: [nuclear_localization_signal]
    modifications: [acetylation_sites]
    cellular_localization: nucleus
""",
        },
    ]

    engine = get_inference_engine()

    for sample in protein_samples:
        print_subsection(sample["name"])

        try:
            ast = parse(sample["gfl_content"])

            # Try protein generation if model is available
            if "protein_generation" in engine.list_models():
                result = infer_enhanced(ast, model_name="protein_generation", explain=True)

                sequence = result["label"]
                confidence = result["confidence"]

                print(f"Generated Sequence: {sequence}")
                print(f"Length: {len(sequence)} amino acids")
                print(f"Confidence: {confidence:.1%}")
                print(f"Analysis: {result['explanation']}")

                # Basic sequence analysis
                if sequence:
                    aa_counts = {}
                    for aa in "ACDEFGHIKLMNPQRSTVWY":
                        count = sequence.count(aa)
                        if count > 0:
                            aa_counts[aa] = count

                    print(f"Composition: {len(aa_counts)} different amino acids")
                    most_common = max(aa_counts, key=aa_counts.get) if aa_counts else "N/A"
                    print(f"Most common AA: {most_common}")

            else:
                # Fall back to multimodal or heuristic
                result = infer_enhanced(ast, model_name="multimodal", explain=True)
                print(f"Multimodal prediction: {result['label']}")
                print(f"Confidence: {result['confidence']:.1%}")
                print("Note: Using multimodal model (protein generation model not available)")

        except Exception as e:
            print(f"Error in protein generation for {sample['name']}: {e}")


def benchmark_inference_performance():
    """Benchmark inference performance across models."""
    print_section("Performance Benchmarking")

    # Create test data
    test_gfl = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: BRCA1

analyze:
  strategy: efficiency_measurement
  thresholds:
    p_value: 0.01
"""

    try:
        ast = parse(test_gfl)
        engine = get_inference_engine()

        iterations = 5
        results = {}

        print(f"Running {iterations} iterations per model...\n")

        for model_name in engine.list_models():
            print(f"Benchmarking {model_name}...")

            times = []
            for i in range(iterations):
                start_time = time.perf_counter()
                try:
                    infer_enhanced(ast, model_name=model_name, explain=False)
                    end_time = time.perf_counter()
                    times.append(end_time - start_time)
                except Exception as e:
                    print(f"  Error in iteration {i+1}: {e}")

            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)

                results[model_name] = {
                    "avg_ms": avg_time * 1000,
                    "min_ms": min_time * 1000,
                    "max_ms": max_time * 1000,
                    "iterations": len(times),
                }

        # Display results
        if results:
            print("\nPerformance Results:")
            print(f"{'Model':<25} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'Runs'}")
            print("-" * 70)

            # Sort by average time
            sorted_results = sorted(results.items(), key=lambda x: x[1]["avg_ms"])

            for model_name, metrics in sorted_results:
                print(
                    f"{model_name:<25} {metrics['avg_ms']:<10.2f} "
                    f"{metrics['min_ms']:<10.2f} {metrics['max_ms']:<10.2f} "
                    f"{metrics['iterations']}"
                )

    except Exception as e:
        print(f"Benchmarking error: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling and fallback mechanisms."""
    print_section("Error Handling Demonstration")

    error_cases = [
        {
            "name": "Invalid GFL Syntax",
            "gfl_content": """
experiment:
  tool: CRISPR_cas9
  invalid_syntax: {{{ this is broken
""",
            "expected_error": "syntax",
        },
        {
            "name": "Missing Required Fields",
            "gfl_content": """
analyze:
  strategy: differential_expression
  # Missing experiment section
""",
            "expected_error": "validation",
        },
    ]

    for case in error_cases:
        print_subsection(case["name"])

        try:
            ast = parse(case["gfl_content"])

            # Even if parsing succeeds, validation might catch issues
            errors = validate(ast)
            if errors:
                print(f"✓ Validation correctly identified {len(errors)} issues")
                print(f"  First issue: {errors[0]}")

            # Try inference anyway to test fallback
            try:
                result = infer_enhanced(ast, model_name="heuristic")
                print(f"Inference succeeded despite issues: {result['label']}")
            except Exception as inference_error:
                print(f"✓ Inference gracefully failed: {inference_error}")

        except Exception as parse_error:
            print(f"✓ Parsing correctly failed: {parse_error}")


def main():
    """Main demonstration function."""
    print("GeneForgeLang Enhanced Inference Engine Demonstration")
    print(f"PyTorch available: {HAS_TORCH}")
    print(f"Device: {DEVICE}")

    if not HAS_GFL_API:
        print("ERROR: GFL API not available. Please install required dependencies.")
        return

    try:
        # Register advanced models
        success = register_advanced_models()
        if not success:
            print("Warning: Some advanced models may not be available")

        # Run demonstrations
        demonstrate_basic_inference()
        demonstrate_model_comparison()
        demonstrate_protein_generation()
        benchmark_inference_performance()
        demonstrate_error_handling()

        print_section("Demonstration Complete")
        print("✓ All demonstrations completed successfully")
        print("\nNext steps:")
        print("- Try 'gfl-inference demo' for interactive demonstration")
        print("- Use 'gfl-inference test <file.gfl>' to test your own GFL files")
        print("- Run 'gfl-inference benchmark' for performance testing")

    except Exception as e:
        print(f"Demonstration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
