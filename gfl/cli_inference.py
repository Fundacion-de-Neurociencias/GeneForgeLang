"""CLI commands for enhanced inference engine testing and demonstration.

This module provides command-line tools to test and demonstrate the advanced
ML model integration capabilities of the GeneForgeLang inference system.
"""

import argparse
import json
from typing import Any, Dict, Optional

# Import GFL API
try:
    from gfl.api import parse, validate
    from gfl.enhanced_inference_engine import get_inference_engine
    from gfl.models.advanced_models import (
        create_genomic_classification_model,
        create_multimodal_genomic_model,
        create_protein_generation_model,
    )

    HAS_GFL_API = True
except ImportError as e:
    print(f"Warning: Could not import GFL API: {e}")
    HAS_GFL_API = False

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from rich import print as rich_print
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None


def print_output(content: str, style: str = "info") -> None:
    """Print output with optional rich formatting."""
    if HAS_RICH and console:
        if style == "error":
            console.print(content, style="red bold")
        elif style == "success":
            console.print(content, style="green bold")
        elif style == "warning":
            console.print(content, style="yellow")
        else:
            console.print(content)
    else:
        print(content)


def load_gfl_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a GFL file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        ast = parse(content)
        errors = validate(ast)

        if errors:
            print_output(f"GFL validation errors: {errors}", "warning")

        return ast
    except Exception as e:
        print_output(f"Error loading GFL file: {e}", "error")
        return None


def demo_inference_models():
    """Demonstrate different inference models."""
    if not HAS_GFL_API:
        print_output("GFL API not available", "error")
        return

    # Get inference engine
    engine = get_inference_engine()

    # Register advanced models
    print_output("Registering advanced models...", "info")

    try:
        # Register classification model
        classification_model = create_genomic_classification_model()
        engine.register_model("genomic_classification", classification_model)

        # Register multimodal model
        multimodal_model = create_multimodal_genomic_model()
        engine.register_model("multimodal", multimodal_model)

        # Register protein generation model if torch is available
        if HAS_TORCH:
            try:
                protein_model = create_protein_generation_model()
                engine.register_model("protein_generation", protein_model)
                print_output("✓ Protein generation model registered", "success")
            except Exception as e:
                print_output(f"⚠ Protein generation model failed: {e}", "warning")

        print_output(f"✓ Registered {len(engine.list_models())} models", "success")

    except Exception as e:
        print_output(f"Error registering models: {e}", "error")
        return

    # Test sample GFL features
    test_features = [
        {
            "name": "CRISPR Gene Editing",
            "features": {
                "experiment_tool": "CRISPR_cas9",
                "experiment_type": "gene_editing",
                "target_gene": "TP53",
                "strategy": "knockout",
            },
        },
        {
            "name": "RNA-seq Analysis",
            "features": {
                "experiment_type": "expression_analysis",
                "strategy": "differential_expression",
                "p_value": 0.001,
                "log2FoldChange": 2.5,
            },
        },
        {
            "name": "Protein Domain Analysis",
            "features": {
                "experiment_type": "functional_analysis",
                "target_gene": "BRCA1",
                "strategy": "domain_analysis",
                "keywords": "kinase domain nuclear localization",
            },
        },
    ]

    # Test each sample with different models
    for sample in test_features:
        print_output(f"\n=== Testing: {sample['name']} ===", "info")

        # Test with each available model
        for model_name in engine.list_models():
            try:
                result = engine.predict(model_name, sample["features"])

                if HAS_RICH and console:
                    # Rich table output
                    table = Table(title=f"Model: {model_name}")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value", style="green")

                    table.add_row("Prediction", str(result.prediction))
                    table.add_row("Confidence", f"{result.confidence:.2%}")
                    table.add_row("Explanation", result.explanation)

                    console.print(table)
                else:
                    # Plain text output
                    print_output(f"Model: {model_name}")
                    print_output(f"  Prediction: {result.prediction}")
                    print_output(f"  Confidence: {result.confidence:.2%}")
                    print_output(f"  Explanation: {result.explanation}")

            except Exception as e:
                print_output(f"  Error with {model_name}: {e}", "error")


def test_inference_file(file_path: str, model_name: Optional[str] = None, output_file: Optional[str] = None):
    """Test inference on a specific GFL file."""
    if not HAS_GFL_API:
        print_output("GFL API not available", "error")
        return

    # Load GFL file
    ast = load_gfl_file(file_path)
    if not ast:
        return

    # Extract features from AST
    from gfl.inference_engine import InferenceEngine
    from gfl.models.dummy import DummyGeneModel

    # Create temporary inference engine to extract features
    temp_engine = InferenceEngine(DummyGeneModel())
    features = temp_engine._extract_features(ast)

    print_output(f"Extracted features: {json.dumps(features, indent=2)}", "info")

    # Get inference engine and run prediction
    engine = get_inference_engine()

    try:
        # Register advanced models if not already registered
        if "genomic_classification" not in engine.list_models():
            classification_model = create_genomic_classification_model()
            engine.register_model("genomic_classification", classification_model)

        # Use specified model or default heuristic
        model_name = model_name or "heuristic"

        print_output(f"Running inference with model: {model_name}", "info")
        result = engine.predict(model_name, features)

        # Format results
        output_data = {
            "file_path": file_path,
            "model_used": model_name,
            "features": features,
            "prediction_result": result.to_dict(),
            "gfl_ast": ast,
        }

        # Output results
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, default=str)
            print_output(f"Results saved to: {output_file}", "success")
        else:
            if HAS_RICH and console:
                panel = Panel(
                    f"Prediction: {result.prediction}\\nConfidence: {result.confidence:.2%}\\nExplanation: {result.explanation}",
                    title="Inference Result",
                    expand=False,
                )
                console.print(panel)
            else:
                print_output("=== Inference Result ===")
                print_output(f"Prediction: {result.prediction}")
                print_output(f"Confidence: {result.confidence:.2%}")
                print_output(f"Explanation: {result.explanation}")

    except Exception as e:
        print_output(f"Inference failed: {e}", "error")
        import traceback

        print_output(traceback.format_exc(), "error")


def benchmark_models(iterations: int = 10):
    """Benchmark different models for performance comparison."""
    if not HAS_GFL_API:
        print_output("GFL API not available", "error")
        return

    import time

    engine = get_inference_engine()

    # Register models for benchmarking
    try:
        classification_model = create_genomic_classification_model()
        engine.register_model("genomic_classification", classification_model)
    except Exception as e:
        print_output(f"Could not register classification model: {e}", "warning")

    # Test features
    test_features = {
        "experiment_tool": "CRISPR_cas9",
        "experiment_type": "gene_editing",
        "target_gene": "TP53",
        "p_value": 0.01,
    }

    results = {}

    for model_name in engine.list_models():
        print_output(f"Benchmarking {model_name}...", "info")

        times = []
        for i in range(iterations):
            start_time = time.time()
            try:
                engine.predict(model_name, test_features)
                end_time = time.time()
                times.append(end_time - start_time)
            except Exception as e:
                print_output(f"  Error in iteration {i+1}: {e}", "error")

        if times:
            avg_time = sum(times) / len(times)
            results[model_name] = {
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "iterations": len(times),
            }

    # Display results
    if HAS_RICH and console:
        table = Table(title="Model Performance Benchmark")
        table.add_column("Model", style="cyan")
        table.add_column("Avg Time (ms)", justify="right")
        table.add_column("Min Time (ms)", justify="right")
        table.add_column("Max Time (ms)", justify="right")
        table.add_column("Iterations", justify="right")

        for model_name, metrics in results.items():
            table.add_row(
                model_name,
                f"{metrics['avg_time']*1000:.2f}",
                f"{metrics['min_time']*1000:.2f}",
                f"{metrics['max_time']*1000:.2f}",
                str(metrics["iterations"]),
            )

        console.print(table)
    else:
        print_output("=== Benchmark Results ===")
        for model_name, metrics in results.items():
            print_output(f"{model_name}:")
            print_output(f"  Average: {metrics['avg_time']*1000:.2f}ms")
            print_output(f"  Range: {metrics['min_time']*1000:.2f}-{metrics['max_time']*1000:.2f}ms")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Enhanced GFL Inference CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    subparsers.add_parser("demo", help="Demonstrate inference models")

    # Test file command
    test_parser = subparsers.add_parser("test", help="Test inference on GFL file")
    test_parser.add_argument("file", help="Path to GFL file")
    test_parser.add_argument("--model", "-m", help="Model to use for inference")
    test_parser.add_argument("--output", "-o", help="Output file for results")

    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark model performance")
    benchmark_parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=10,
        help="Number of iterations for benchmark",
    )

    # List models command
    subparsers.add_parser("list", help="List available models")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "demo":
        demo_inference_models()
    elif args.command == "test":
        test_inference_file(args.file, args.model, args.output)
    elif args.command == "benchmark":
        benchmark_models(args.iterations)
    elif args.command == "list":
        if HAS_GFL_API:
            engine = get_inference_engine()
            models = engine.list_models()
            print_output(f"Available models: {', '.join(models)}")

            for model_name in models:
                try:
                    info = engine.get_model_info(model_name)
                    print_output(f"  {model_name}: {info['type']} ({'loaded' if info['loaded'] else 'not loaded'})")
                except Exception as e:
                    print_output(f"  {model_name}: Error getting info - {e}")
        else:
            print_output("GFL API not available", "error")


if __name__ == "__main__":
    main()
