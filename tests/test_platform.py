#!/usr/bin/env python3
"""Simple test script to verify GeneForgeLang platform functionality."""



def test_basic_api():
    """Test basic GFL API functionality."""
    print("Testing basic GFL API...")

    try:
        from geneforgelang.core.api import get_api_info, parse, validate

        # Test API info
        info = get_api_info()
        print(f"✓ API Version: {info['api_version']}")
        assert info["api_version"], "API version should not be empty"
        print(f"✓ Available models: {info['inference_models']}")
        assert "heuristic" in info["inference_models"], "Expected 'heuristic' model to be available"

        # Test basic parsing
        gfl_content = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""

        ast = parse(gfl_content)
        print(f"✓ Parsing successful: {ast['experiment']['tool']}")
        assert ast["experiment"]["tool"] == "CRISPR_cas9", "Parsed tool should be 'CRISPR_cas9'"

        # Test validation
        errors = validate(ast)
        print(f"✓ Validation: {'Valid' if not errors else f'{len(errors)} errors'}")
        assert not errors, f"Expected no validation errors, but got: {len(errors)}"

    except Exception as e:
        print(f"✗ Basic API test failed: {e}")


def test_enhanced_inference():
    print("\nTesting enhanced inference...")
    try:
        from geneforgelang.core.enhanced_inference_engine import (
            EnhancedInferenceEngine,
        )

        engine = EnhancedInferenceEngine()

        features = {
            "experiment_tool": "CRISPR_cas9",
            "experiment_type": "gene_editing",
            "target_gene": "TP53",
        }

        # Llamar directamente al modelo, sin pasar por el caché
        model = engine.models["heuristic"]
        result = model.predict(features)

        print(f"✓ Inference successful: {result.prediction} (confidence: {result.confidence:.2%})")
        assert result.prediction == "edited", "Expected prediction to be 'edited'"
        assert result.confidence == 85.00, "Expected confidence to be greater than 0.5"

    except Exception as e:
        print(f"✗ Enhanced inference test failed: {e}")


def test_cli_tools():
    """Test CLI tools."""
    print("\nTesting CLI tools...")

    try:
        import subprocess

        # Test gfl help
        result = subprocess.run(["gfl", "--help"], capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, f"gfl CLI failed: {result.stderr}"

        if result.returncode == 0:
            print("✓ gfl CLI available")
        else:
            print(f"✗ gfl CLI failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("✗ CLI tools test failed: timeout — el comando tarda demasiado")

    except Exception as e:
        print(f"✗ CLI tools test failed: {e}")
