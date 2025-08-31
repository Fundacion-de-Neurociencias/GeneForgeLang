"""
Comprehensive test of the GeneForgeLang optimize block implementation.

This example demonstrates the new 'optimize' block for intelligent experimental
loops, as described in the proposal. It shows how to define parameter search
spaces, optimization strategies, and automated experimentation loops.
"""

from gfl.api import parse, validate, infer
from gfl.models.dummy import DummyGeneModel


def test_active_learning_optimization():
    """Test active learning optimization for parameter tuning."""

    optimize_gfl = """
    metadata:
      experiment_id: OPTIM_ACTIVE_001
      researcher: Dr. Jane Smith
      project: crispr_optimization
      description: Active learning optimization of CRISPR parameters

    optimize:
      # Define the parameter search space
      search_space:
        promoter_strength: range(0.1, 1.0)
        terminator_efficiency: choice([0.8, 0.9, 0.95, 0.99])
        guide_concentration: range(10, 100)
        temperature: range(25, 42)

      # Optimization strategy configuration
      strategy:
        name: ActiveLearning
        uncertainty_metric: entropy
        initial_samples: 5

      # Optimization objective
      objective:
        maximize: gene_expression_level

      # Budget constraints
      budget:
        max_experiments: 50
        max_time: 48h
        convergence_threshold: 0.01

      # Experiment to run in each iteration
      run:
        experiment:
          tool: SyntheticCircuitSimulator
          type: gene_editing
          strategy: activation
          params:
            promoter: ${promoter_strength}
            terminator: ${terminator_efficiency}
            guide_rna_conc: ${guide_concentration}
            incubation_temp: ${temperature}
            target_gene: GFP
            replicates: 3
            duration: 24h
    """

    print("=== Testing Active Learning Optimization ===")
    print("Parsing GFL...")

    # Parse the GFL
    ast = parse(optimize_gfl)
    assert ast is not None, "Failed to parse GFL"
    print("✓ Successfully parsed GFL")

    # Check structure
    assert "optimize" in ast, "Optimize block not found in AST"
    assert "metadata" in ast, "Metadata block not found in AST"
    print("✓ All expected blocks present")

    # Validate the optimize block structure
    optimize = ast["optimize"]

    # Check search space
    search_space = optimize["search_space"]
    assert len(search_space) == 4
    assert search_space["promoter_strength"] == "range(0.1, 1.0)"
    assert search_space["terminator_efficiency"] == "choice([0.8, 0.9, 0.95, 0.99])"
    print("✓ Search space structure is correct")

    # Check strategy
    strategy = optimize["strategy"]
    assert strategy["name"] == "ActiveLearning"
    assert strategy["uncertainty_metric"] == "entropy"
    print("✓ Strategy configuration is correct")

    # Check objective
    objective = optimize["objective"]
    assert objective["maximize"] == "gene_expression_level"
    print("✓ Objective configuration is correct")

    # Check budget
    budget = optimize["budget"]
    assert budget["max_experiments"] == 50
    assert budget["max_time"] == "48h"
    print("✓ Budget configuration is correct")

    # Check nested experiment
    run_block = optimize["run"]
    assert "experiment" in run_block
    experiment = run_block["experiment"]
    assert experiment["tool"] == "SyntheticCircuitSimulator"
    assert experiment["params"]["promoter"] == "${promoter_strength}"
    assert experiment["params"]["terminator"] == "${terminator_efficiency}"
    print("✓ Nested experiment structure is correct")

    # Validate the workflow
    print("Validating workflow...")
    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    else:
        print("✓ Workflow validation passed")

    return True


def test_bayesian_optimization():
    """Test Bayesian optimization for drug discovery."""

    bayesian_gfl = """
    optimize:
      search_space:
        compound_dose: range(0.1, 50.0)
        treatment_duration: range(6, 72)
        buffer_ph: range(6.5, 8.5)
        cell_density: choice([10000, 50000, 100000, 200000])

      strategy:
        name: BayesianOptimization
        acquisition_function: expected_improvement
        kernel: rbf

      objective:
        maximize: cell_viability
        minimize: toxicity

      budget:
        max_experiments: 80
        max_cost: 15000

      run:
        experiment:
          tool: flow_cytometry
          type: screening
          params:
            dose: ${compound_dose}
            duration: ${treatment_duration}
            ph: ${buffer_ph}
            cells_per_well: ${cell_density}
            compound: test_drug_X
            replicates: 4
    """

    print("\\n=== Testing Bayesian Optimization ===")

    ast = parse(bayesian_gfl)
    assert ast is not None
    print("✓ Successfully parsed Bayesian optimization GFL")

    # This should fail validation because of conflicting objectives
    errors = validate(ast)
    assert len(errors) > 0, "Expected validation errors for conflicting objectives"
    print("✓ Correctly detected conflicting objectives")

    return True


def test_genetic_algorithm_optimization():
    """Test genetic algorithm for circuit design."""

    genetic_gfl = """
    metadata:
      experiment_id: GA_CIRCUIT_001
      project: synthetic_biology

    optimize:
      search_space:
        promoter_type: choice([T7, lac, ara, trp])
        ribosome_binding_site: choice([strong, medium, weak])
        protein_tag: choice([His6, FLAG, GFP, none])
        plasmid_copy: range(1, 20)

      strategy:
        name: GeneticAlgorithm
        population_size: 50
        mutation_rate: 0.1
        crossover_rate: 0.8
        selection_method: tournament

      objective:
        maximize: protein_yield

      budget:
        max_experiments: 200
        max_time: 7d

      run:
        experiment:
          tool: SyntheticCircuitSimulator
          type: gene_editing
          strategy: expression
          params:
            promoter: ${promoter_type}
            rbs: ${ribosome_binding_site}
            tag: ${protein_tag}
            copy_number: ${plasmid_copy}
            target_protein: mCherry
            host_strain: E.coli_BL21
            induction: IPTG
            replicates: 3
    """

    print("\\n=== Testing Genetic Algorithm Optimization ===")

    ast = parse(genetic_gfl)
    assert ast is not None
    print("✓ Successfully parsed genetic algorithm GFL")

    # Check the complex workflow
    optimize = ast["optimize"]
    assert len(optimize["search_space"]) == 4
    assert optimize["strategy"]["name"] == "GeneticAlgorithm"
    assert optimize["strategy"]["population_size"] == 50
    print("✓ Complex genetic algorithm configuration is correct")

    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    print("✓ Genetic algorithm validation passed")

    return True


def test_optimize_with_analyze_block():
    """Test optimization with analysis in the run block."""

    analyze_gfl = """
    optimize:
      search_space:
        threshold_p_value: range(0.001, 0.1)
        fold_change_cutoff: range(1.2, 5.0)

      strategy:
        name: GridSearch
        grid_resolution: 10

      objective:
        minimize: false_positive_rate

      budget:
        max_experiments: 25

      run:
        analyze:
          strategy: differential
          data: rnaseq_dataset
          thresholds:
            p_value: ${threshold_p_value}
            fold_change: ${fold_change_cutoff}
          filters:
            - remove_low_counts
            - normalize
          operations:
            - type: differential_expression
              params:
                method: DESeq2
    """

    print("\\n=== Testing Optimization with Analysis ===")

    ast = parse(analyze_gfl)
    assert ast is not None
    print("✓ Successfully parsed optimization with analysis")

    # Check that analyze block is in run
    optimize = ast["optimize"]
    assert "analyze" in optimize["run"]
    assert optimize["run"]["analyze"]["strategy"] == "differential"
    print("✓ Analysis block correctly nested in run")

    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    print("✓ Optimize with analyze validation passed")

    return True


def test_parameter_injection_validation():
    """Test parameter injection validation."""

    # Test with correct parameter references
    correct_gfl = """
    optimize:
      search_space:
        temp: range(20, 40)
        conc: range(1, 10)

      strategy:
        name: RandomSearch

      objective:
        maximize: yield

      budget:
        max_experiments: 10

      run:
        experiment:
          tool: PCR
          type: validation
          params:
            temperature: ${temp}
            concentration: ${conc}
            duration: 30m
    """

    print("\\n=== Testing Parameter Injection ===")

    ast = parse(correct_gfl)
    assert ast is not None
    print("✓ Successfully parsed parameter injection syntax")

    # Check parameter injection
    params = ast["optimize"]["run"]["experiment"]["params"]
    assert params["temperature"] == "${temp}"
    assert params["concentration"] == "${conc}"
    assert params["duration"] == "30m"  # Non-injected parameter
    print("✓ Parameter injection syntax is correct")

    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    print("✓ Parameter injection validation passed")

    return True


def test_invalid_optimize_blocks():
    """Test various invalid optimize block configurations."""

    print("\\n=== Testing Invalid Optimize Block Detection ===")

    # Test missing required fields
    invalid_configs = [
        # Missing search_space
        {
            "optimize": {
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 10},
                "run": {"experiment": {"tool": "PCR", "type": "validation"}}
            }
        },
        # Empty search_space
        {
            "optimize": {
                "search_space": {},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 10},
                "run": {"experiment": {"tool": "PCR", "type": "validation"}}
            }
        },
        # Missing strategy name
        {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"uncertainty_metric": "entropy"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 10},
                "run": {"experiment": {"tool": "PCR", "type": "validation"}}
            }
        },
        # Conflicting objectives
        {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency", "minimize": "cost"},
                "budget": {"max_experiments": 10},
                "run": {"experiment": {"tool": "PCR", "type": "validation"}}
            }
        },
        # Empty budget
        {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {},
                "run": {"experiment": {"tool": "PCR", "type": "validation"}}
            }
        },
        # Missing run block
        {
            "optimize": {
                "search_space": {"param": "range(0, 10)"},
                "strategy": {"name": "ActiveLearning"},
                "objective": {"maximize": "efficiency"},
                "budget": {"max_experiments": 10}
            }
        }
    ]

    for i, invalid_ast in enumerate(invalid_configs, 1):
        errors = validate(invalid_ast)
        assert len(errors) > 0, f"Configuration {i} should have validation errors"
        print(f"✓ Configuration {i}: Correctly detected validation errors")

    return True


def run_all_tests():
    """Run all optimize block tests."""
    print("GeneForgeLang Optimize Block Implementation Test")
    print("=" * 50)

    tests = [
        test_active_learning_optimization,
        test_bayesian_optimization,
        test_genetic_algorithm_optimization,
        test_optimize_with_analyze_block,
        test_parameter_injection_validation,
        test_invalid_optimize_blocks,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} raised exception: {e}")

    print(f"\\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Optimize block implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
