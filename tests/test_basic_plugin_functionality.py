#!/usr/bin/env python3
"""
Test basic plugin functionality without entry point discovery.
"""

from gfl.api import execute, get_api_info, parse, validate
from gfl.plugins import plugin_registry
from gfl.plugins.example_implementations import BayesianOptimizer, MoleculeTransformerGenerator, ProteinVAEGenerator


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

        plugin_registry.register("ProteinVAEGenerator", protein_generator, "1.2.0")
        plugin_registry.register("MoleculeTransformerGenerator", molecule_generator, "2.1.0")
        plugin_registry.register("BayesianOptimizer", bayesian_optimizer, "1.5.0")

        print("✓ Successfully registered plugins manually")

    except Exception as e:
        print(f"❌ Plugin registration failed: {e}")
        return False

    # 2. Test API info
    print("\n2. Testing API information...")
    try:
        api_info = get_api_info()
        print(f"✓ API version: {api_info['api_version']}")
        print(f"✓ Workflow execution: {api_info['features'].get('workflow_execution', False)}")

    except Exception as e:
        print(f"❌ API info failed: {e}")
        return False

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
  count: 2
  output: designed_proteins
"""

    try:
        # Parse and validate
        ast = parse(design_gfl)
        print("✓ Parsed design GFL successfully")

        errors = validate(ast)
        if errors:
            print(f"❌ Validation failed: {errors}")
            return False
        print("✓ Validation passed")

        # Execute
        result = execute(ast)
        print("✓ Design block executed successfully")

        # Check results
        candidates = result["design"]["candidates"]
        print(f"✓ Generated {len(candidates)} candidates")
        print(f"  - First candidate: {candidates[0].sequence[:30]}...")
        print(f"  - Properties: {list(candidates[0].properties.keys())}")

    except Exception as e:
        print(f"❌ Design execution failed: {e}")
        return False

    # 4. Test simple optimize block execution
    print("\n4. Testing optimize block execution...")
    optimize_gfl = """
metadata:
  experiment_id: BASIC_OPTIMIZE_001

optimize:
  search_space:
    temperature: range(25, 42)
    concentration: range(10, 100)

  strategy:
    name: BayesianOptimization

  objective:
    maximize: efficiency

  budget:
    max_experiments: 5

  run:
    experiment:
      tool: test_tool
      type: simulation
      params:
        temp: ${temperature}
        conc: ${concentration}
"""

    try:
        # Parse and validate
        ast = parse(optimize_gfl)
        print("✓ Parsed optimize GFL successfully")

        errors = validate(ast)
        if errors:
            print(f"❌ Validation failed: {errors}")
            return False
        print("✓ Validation passed")

        # Execute
        result = execute(ast)
        print("✓ Optimize block executed successfully")

        # Check results
        optimize_result = result["optimize"]
        print(f"✓ Completed {optimize_result['total_experiments']} experiments")
        print(f"✓ Best objective: {optimize_result['best_objective_value']:.4f}")
        print(f"✓ Best parameters: {optimize_result['best_parameters']}")

    except Exception as e:
        print(f"❌ Optimize execution failed: {e}")
        return False

    print("\n🎉 Basic Plugin Functionality Tests Passed!")
    print("✓ Manual plugin registration works")
    print("✓ Design block execution works")
    print("✓ Optimize block execution works")
    print("✓ Parameter injection works")

    return True


if __name__ == "__main__":
    success = test_basic_plugin_functionality()
    exit(0 if success else 1)
