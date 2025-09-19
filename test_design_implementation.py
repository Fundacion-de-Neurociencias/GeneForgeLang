"""
Comprehensive test of the GeneForgeLang design block implementation.

This example demonstrates the new 'design' block for generative hypothesis tasks,
as described in the paper concept. It shows how to specify the generation of
new biological sequences or structures, optimizing an objective in a search space.
"""

from gfl.api import infer, parse, validate
from gfl.models.dummy import DummyGeneModel


def test_protein_design_example():
    """Test a complete protein design workflow."""

    # Example 1: Protein design for binding affinity
    protein_design_gfl = """
    metadata:
      experiment_id: PROT_DESIGN_001
      researcher: Dr. Jane Smith
      project: covid_therapeutics
      description: Design proteins with high binding affinity to ACE2 receptor

    design:
      # Define what we're designing
      entity: ProteinSequence

      # Specify the generative model plugin
      model: ProteinGeneratorVAE

      # Define the optimization objective
      objective:
        maximize: binding_affinity
        target: ACE2_receptor

      # Add constraints to the design
      constraints:
        - length(120, 150)
        - has_motif("E_box")
        - synthesizability > 0.7
        - stability > 0.6

      # Number of candidates to generate
      count: 10

      # Output variable for use in subsequent steps
      output: designed_candidates

    # Analyze the generated candidates
    analyze:
      strategy: functional
      data: designed_candidates
      thresholds:
        binding_score: 0.8
        stability_score: 0.7
      operations:
        - type: sort
          params:
            by: binding_affinity
            order: descending
        - type: filter
          params:
            top_n: 5
    """

    print("=== Testing Protein Design Example ===")
    print("Parsing GFL...")

    # Parse the GFL
    ast = parse(protein_design_gfl)
    assert ast is not None, "Failed to parse GFL"
    print("✓ Successfully parsed GFL")

    # Check structure
    assert "design" in ast, "Design block not found in AST"
    assert "analyze" in ast, "Analyze block not found in AST"
    assert "metadata" in ast, "Metadata block not found in AST"
    print("✓ All expected blocks present")

    # Validate the design block structure
    design = ast["design"]
    assert design["entity"] == "ProteinSequence"
    assert design["model"] == "ProteinGeneratorVAE"
    assert design["objective"]["maximize"] == "binding_affinity"
    assert design["objective"]["target"] == "ACE2_receptor"
    assert design["count"] == 10
    assert design["output"] == "designed_candidates"
    assert len(design["constraints"]) == 4
    print("✓ Design block structure is correct")

    # Validate the workflow
    print("Validating workflow...")
    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    else:
        print("✓ Workflow validation passed")

    # Test inference (simulation)
    print("Running inference simulation...")
    try:
        model = DummyGeneModel()
        result = infer(model, ast)
        assert isinstance(result, dict), f"Expected dict result, got {type(result)}"
        print("✓ Inference completed successfully")
    except Exception as e:
        print(f"❌ Inference failed: {e}")
        return False

    return True


def test_dna_design_example():
    """Test DNA sequence design workflow."""

    dna_design_gfl = """
    design:
      entity: DNASequence
      model: DNADesignerGAN
      objective:
        minimize: off_target_effects
      constraints:
        - length(50, 100)
        - gc_content(0.4, 0.6)
        - no_restriction_sites
      count: 20
      output: guide_rnas

    analyze:
      strategy: comparative
      data: guide_rnas
      thresholds:
        specificity_score: 0.9
    """

    print("\n=== Testing DNA Design Example ===")

    ast = parse(dna_design_gfl)
    assert ast is not None
    print("✓ Successfully parsed DNA design GFL")

    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    print("✓ DNA design validation passed")

    return True


def test_small_molecule_design_example():
    """Test small molecule design workflow."""

    molecule_design_gfl = """
    metadata:
      experiment_id: DRUG_DESIGN_001
      project: alzheimer_therapeutics

    design:
      entity: SmallMolecule
      model: MoleculeTransformer
      objective:
        maximize: activity
        target: amyloid_beta
      constraints:
        - molecular_weight < 500
        - logP < 5
        - rotatable_bonds < 10
        - drug_likeness > 0.8
      count: 100
      output: candidate_drugs

    analyze:
      strategy: pathway
      data: candidate_drugs
      thresholds:
        activity_score: 0.7
        toxicity_score: 0.2
      operations:
        - type: clustering
          params:
            method: scaffold
            n_clusters: 10
        - type: filter
          params:
            representative_only: true
    """

    print("\n=== Testing Small Molecule Design Example ===")

    ast = parse(molecule_design_gfl)
    assert ast is not None
    print("✓ Successfully parsed small molecule design GFL")

    # Check the complex workflow
    assert ast["design"]["entity"] == "SmallMolecule"
    assert ast["design"]["count"] == 100
    assert len(ast["design"]["constraints"]) == 4
    assert len(ast["analyze"]["operations"]) == 2
    print("✓ Complex workflow structure is correct")

    errors = validate(ast)
    if errors:
        print(f"❌ Validation errors: {errors}")
        return False
    print("✓ Small molecule design validation passed")

    return True


def test_multi_objective_design_error():
    """Test that conflicting objectives are properly detected."""

    invalid_gfl = """
    design:
      entity: ProteinSequence
      model: ProteinGeneratorVAE
      objective:
        maximize: binding_affinity
        minimize: toxicity  # This should cause an error
      count: 10
      output: proteins
    """

    print("\n=== Testing Multi-Objective Error Detection ===")

    ast = parse(invalid_gfl)
    errors = validate(ast)

    # Should have validation errors for conflicting objectives
    assert len(errors) > 0, "Expected validation errors for conflicting objectives"

    # Check that the error mentions the conflicting objectives
    error_text = " ".join(errors).lower()
    assert "maximize" in error_text and "minimize" in error_text
    print("✓ Correctly detected conflicting objectives")

    return True


def run_all_tests():
    """Run all design block tests."""
    print("GeneForgeLang Design Block Implementation Test")
    print("=" * 50)

    tests = [
        test_protein_design_example,
        test_dna_design_example,
        test_small_molecule_design_example,
        test_multi_objective_design_error,
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

    print("\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Design block implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
