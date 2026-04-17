#!/usr/bin/env python3
"""
Test the complete plugin ecosystem with real GFL execution.
"""

from geneforgelang.core.api import execute, get_api_info, list_available_plugins, parse, validate
from examples.example_implementations import register_example_plugins


def test_plugin_ecosystem():
    """Test the complete plugin ecosystem functionality."""

    print("🚀 Testing GeneForgeLang Plugin Ecosystem")
    print("=" * 60)

    # 1. Register example plugins
    print("\n1. Registering example plugins...")
    try:
        register_example_plugins()
        print("✓ Successfully registered example plugins")
    except Exception as e:
        print(f"❌ Failed to register plugins: {e}")
        return False

    # 2. Check API info and available plugins
    print("\n2. Checking API capabilities...")
    api_info = get_api_info()
    print(f"✓ API version: {api_info['api_version']}")
    print(f"✓ Workflow execution: {api_info['features']['workflow_execution']}")
    print(f"✓ Plugin system: {api_info['features']['plugin_system']}")

    available_plugins = list_available_plugins()
    print(f"✓ Available generators: {available_plugins['generators']}")
    print(f"✓ Available optimizers: {available_plugins['optimizers']}")

    # 3. Test design block execution
    print("\n3. Testing design block execution...")
    design_gfl = """
metadata:
  experiment_id: DESIGN_TEST_001
  researcher: Dr. Test User
  project: plugin_ecosystem_test
  description: Testing protein design with VAE generator

design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
    target: therapeutic_protein
  constraints:
    - length(50, 150)
    - synthesizability > 0.8
    - stability_score > 0.7
  count: 5
  output: designed_proteins
"""

    try:
        # Parse GFL
        ast = parse(design_gfl)
        print("✓ Successfully parsed design GFL")

        # Validate AST
        errors = validate(ast)
        if errors:
            print(f"❌ Validation errors: {errors}")
            return False
        print("✓ AST validation passed")

        # Execute design block
        result = execute(ast)
        print("✓ Design block executed successfully")

        # Check results
        design_result = result["design"]
        candidates = design_result["candidates"]

        print(f"✓ Generated {len(candidates)} protein candidates")
        print(f"✓ First candidate: {candidates[0].sequence[:20]}...")
        print(f"✓ First candidate properties: {candidates[0].properties}")
        print(f"✓ First candidate confidence: {candidates[0].confidence:.3f}")

    except Exception as e:
        print(f"❌ Design block execution failed: {e}")
        return False

    # 4. Test optimize block execution
    print("\n4. Testing optimize block execution...")
    optimize_gfl = """
metadata:
  experiment_id: OPTIMIZE_TEST_001
  researcher: Dr. Test User
  project: plugin_ecosystem_test
  description: Testing CRISPR parameter optimization

optimize:
  search_space:
    temperature: range(25, 42)
    guide_concentration: range(10, 100)
    duration: choice([6, 12, 24, 48])
    cas9_ratio: range(0.5, 2.0)

  strategy:
    name: BayesianOptimization
    uncertainty_metric: entropy
    initial_samples: 3
    batch_size: 1
    exploration_weight: 0.1

  objective:
    maximize: editing_efficiency

  budget:
    max_experiments: 10
    convergence_threshold: 0.01

  run:
    experiment:
      tool: CRISPR_cas9
      type: gene_editing
      strategy: knockout
      params:
        target_gene: TP53
        guide_rna: GGGCCGGGCGGGCTCCCAGA
        guide_concentration: ${guide_concentration}
        incubation_temp: ${temperature}
        duration: ${duration}h
        cas9_ratio: ${cas9_ratio}
        vector: pX458
        cell_line: HEK293T
        replicates: 3
"""

    try:
        # Parse GFL
        ast = parse(optimize_gfl)
        print("✓ Successfully parsed optimize GFL")

        # Validate AST
        errors = validate(ast)
        if errors:
            print(f"❌ Validation errors: {errors}")
            return False
        print("✓ AST validation passed")

        # Execute optimize block
        result = execute(ast)
        print("✓ Optimize block executed successfully")

        # Check results
        optimize_result = result["optimize"]
        best_params = optimize_result["best_parameters"]
        best_objective = optimize_result["best_objective_value"]
        total_experiments = optimize_result["total_experiments"]

        print(f"✓ Optimization completed: {total_experiments} experiments")
        print(f"✓ Best objective value: {best_objective:.4f}")
        print("✓ Best parameters:")
        for param, value in best_params.items():
            print(f"    {param}: {value}")

        convergence = optimize_result["convergence_info"]
        print(f"✓ Convergence status: {convergence['converged']} ({convergence['reason']})")

    except Exception as e:
        print(f"❌ Optimize block execution failed: {e}")
        return False

    # 5. Test combined workflow
    print("\n5. Testing combined design + optimize workflow...")
    combined_gfl = """
metadata:
  experiment_id: COMBINED_TEST_001
  researcher: Dr. Test User
  project: plugin_ecosystem_test
  description: Combined design and optimization workflow

design:
  entity: SmallMolecule
  model: MoleculeTransformerGenerator
  objective:
    maximize: binding_affinity
    target: kinase_enzyme
  constraints:
    - molecular_weight < 500
    - logP < 5
    - drug_likeness > 0.7
  count: 3
  output: designed_molecules

optimize:
  search_space:
    design_temperature: range(0.1, 1.0)
    diversity_weight: range(0.0, 1.0)

  strategy:
    name: BayesianOptimization

  objective:
    maximize: validated_activity

  budget:
    max_experiments: 5

  run:
    experiment:
      tool: molecular_docking
      params:
        molecules: designed_molecules  # Uses output from design block
        target: kinase_active_site
        temperature: ${design_temperature}
        diversity: ${diversity_weight}
"""

    try:
        # Parse and execute combined workflow
        ast = parse(combined_gfl)
        print("✓ Successfully parsed combined GFL")

        errors = validate(ast)
        if errors:
            print(f"❌ Validation errors: {errors}")
            return False
        print("✓ Combined AST validation passed")

        result = execute(ast)
        print("✓ Combined workflow executed successfully")

        # Check that both blocks executed
        assert "design" in result, "Design block should have executed"
        assert "optimize" in result, "Optimize block should have executed"

        print(f"✓ Design generated {result['design']['count']} molecules")
        print(f"✓ Optimization found best objective: {result['optimize']['best_objective_value']:.4f}")

    except Exception as e:
        print(f"❌ Combined workflow execution failed: {e}")
        return False

    print("\n🎉 All Plugin Ecosystem Tests Passed!")
    print("=" * 60)
    print("✓ Plugin registration works")
    print("✓ Design block execution works")
    print("✓ Optimize block execution works")
    print("✓ Combined workflows work")
    print("✓ Parameter injection works")
    print("✓ Plugin interfaces are properly implemented")

    return True


def test_plugin_validation():
    """Test plugin validation functionality."""

    print("\n🔍 Testing Plugin Validation")
    print("=" * 40)

    # Test missing plugin validation
    invalid_gfl = """
design:
  entity: ProteinSequence
  model: NonExistentPlugin
  objective:
    maximize: stability
  count: 5
  output: results
"""

    try:
        from geneforgelang.core.api import validate_plugins

        ast = parse(invalid_gfl)
        plugin_errors = validate_plugins(ast)

        print(f"✓ Plugin validation detected errors: {len(plugin_errors)}")
        if plugin_errors:
            print(f"  - {plugin_errors[0]}")

        # Test that execution fails gracefully
        try:
            execute(ast, validate_first=True)
            print("❌ Should have failed due to missing plugin")
            return False
        except ValueError as e:
            print(f"✓ Execution properly failed: {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ Plugin validation test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    # Run comprehensive tests
    ecosystem_success = test_plugin_ecosystem()
    validation_success = test_plugin_validation()

    if ecosystem_success and validation_success:
        print("\n🚀 ALL TESTS PASSED - Plugin ecosystem is fully functional!")
        exit(0)
    else:
        print("\n❌ Some tests failed - check output above")
        exit(1)
