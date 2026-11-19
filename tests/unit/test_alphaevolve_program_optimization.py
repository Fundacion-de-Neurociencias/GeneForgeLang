"""Unit tests for AlphaEvolve program evolution optimization in GeneForgeLang."""

from geneforgelang.core.gftypes import ProgramEvolutionContract
from geneforgelang.core.validator import EnhancedSemanticValidator


def test_program_evolution_contract_instantiation_and_dict() -> None:
    """Test creating and serializing a ProgramEvolutionContract."""
    contract = ProgramEvolutionContract(
        seed_program="protocols/hts_pipetting.py",
        fitness_metric="yield_and_purity_f1",
        mutation_engine="gemini-1.5-pro",
        population_size=25,
        generations=10,
        elitism_rate=0.15,
        mutation_operators=["diff_prompt", "semantic_refactor"],
        timeout_per_eval_seconds=45.0,
        deterministic_eval_harness="tests/eval_hts_protocol.py",
        target_fitness_threshold=0.98,
    )

    data = contract.to_dict()
    assert data["seed_program"] == "protocols/hts_pipetting.py"
    assert data["fitness_metric"] == "yield_and_purity_f1"
    assert data["population_size"] == 25
    assert data["generations"] == 10
    assert data["elitism_rate"] == 0.15
    assert len(data["mutation_operators"]) == 2
    assert data["target_fitness_threshold"] == 0.98


def test_validator_accepts_alpha_evolve_strategy() -> None:
    """Test that validator accepts AlphaEvolve with valid parameters."""
    validator = EnhancedSemanticValidator()
    strategy = {
        "name": "AlphaEvolve",
        "alpha_evolve": {
            "seed_program": "protocols/hts_pipetting.py",
            "population_size": 20,
            "generations": 12,
            "elitism_rate": 0.20,
        },
    }
    validator._validate_optimize_strategy(strategy)
    assert validator.result.is_valid
    assert len(validator.result.errors) == 0


def test_validator_accepts_program_evolution_strategy() -> None:
    """Test that validator accepts ProgramEvolution as an alias."""
    validator = EnhancedSemanticValidator()
    strategy = {
        "name": "ProgramEvolution",
        "population_size": 15,
        "generations": 8,
        "elitism_rate": 0.10,
        "seed_program": "scoring_heuristics/affinity_scorer.py",
    }
    validator._validate_optimize_strategy(strategy)
    assert validator.result.is_valid
    assert len(validator.result.errors) == 0


def test_validator_catches_invalid_alpha_evolve_params() -> None:
    """Test that validator catches invalid population size and elitism rate."""
    validator = EnhancedSemanticValidator()
    strategy = {
        "name": "AlphaEvolve",
        "alpha_evolve": {
            "seed_program": "",  # invalid empty string
            "population_size": -5,  # invalid negative
            "generations": 0,  # invalid zero
            "elitism_rate": 1.5,  # invalid > 1.0
        },
    }
    validator._validate_optimize_strategy(strategy)
    assert not validator.result.is_valid
    assert len(validator.result.errors) > 0
    errors = [e.message for e in validator.result.errors]
    assert any("population_size must be a positive integer" in e for e in errors)
    assert any("generations must be a positive integer" in e for e in errors)
    assert any("elitism_rate must be a float between 0.0 and 1.0" in e for e in errors)
    assert any("seed_program must be a non-empty string" in e for e in errors)
