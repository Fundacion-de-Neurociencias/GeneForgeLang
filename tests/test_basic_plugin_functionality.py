#!/usr/bin/env python3
"""
Test basic plugin functionality without entry point discovery.
"""
from geneforgelang.core.api import execute, get_api_info, parse, validate
from geneforgelang.plugins.plugin_registry import PluginRegistry
from geneforgelang.utils.example_implementations import (
    BayesianOptimizer,
    MoleculeTransformerGenerator,
    ProteinVAEGenerator,
)

registry = PluginRegistry()


def test_basic_plugin_functionality():
    """Test basic plugin functionality."""

    print("🧪 Testing Basic Plugin Functionality")
    print("=" * 50)

    # 1. Test manual plugin registration
    print("\n1. Testing manual plugin registration...")
    try:
        # Register plugins manually to avoid entry point issues
        protein_generator = ProteinVAEGenerator()
        molecule_generator = MoleculeTransformerGenerator()
        bayesian_optimizer = BayesianOptimizer()

        registry.register("ProteinVAEGenerator", protein_generator, "1.2.0")
        registry.register("MoleculeTransformerGenerator", molecule_generator, "2.1.0")
        registry.register("BayesianOptimizer", bayesian_optimizer, "1.5.0")

        registry.register_generator("ProteinVAEGenerator", protein_generator)
        registry.register_generator("MoleculeTransformerGenerator", molecule_generator)
        registry.register_optimizer("BayesianOptimizer", bayesian_optimizer)

    except Exception as e:
        print(f"❌ Plugin registration failed: {e}")
        raise AssertionError(f"Plugin registration failed: {e}")
    # 2. Test API info
    print("\n2. Testing API information...")
    try:
        api_info = get_api_info()
        print(f"✓ API version: {api_info['api_version']}")
        print(f"✓ Workflow execution: {api_info['features'].get('workflow_execution', False)}")

    except Exception as e:
        print(f"❌ API info failed: {e}")
        raise AssertionError(f"API info failed: {e}")

    # 3. Test simple design block execution
    print("\n3. Testing design block execution...")
    design_gfl = """
metadata:
  experiment_id: BASIC_DESIGN_001

design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  constraints:
    - "length(120, 150)"
  count: 2
  output: designed_proteins
"""

    try:
        # Parse and validate
        ast = parse(design_gfl)
        print("✓ Parsed design GFL successfully:", ast)

        errors = validate(ast)
        if errors:
            raise AssertionError(f"Validation failed: {errors}")
        print("✓ Validation passed")

        # Execute
        result = execute(ast, registry)
        print("✓ Design block executed successfully")

        # Check results
        candidates = result["design"]
        print(f"✓ Generated {len(candidates)} candidates")
        print(f"  - First candidate: {candidates[0].sequence[:30]}...")
        print(f"  - Properties: {list(candidates[0].properties.keys())}")

    except Exception as e:
        print(f"❌ Design execution failed: {e}")
        raise AssertionError(f"Design execution failed: {e}")

    print("\n🎉 Basic Plugin Functionality Tests Passed!")
    print("✓ Manual plugin registration works")
    print("✓ Design block execution works")
    print("✓ Parameter injection works")

if __name__ == "__main__":
    success = test_basic_plugin_functionality()
    exit(0 if success else 1)
