"""Tests for GeneForgeLang plugin interfaces.

This module tests the specialized plugin interfaces for design and optimize
blocks, ensuring they provide proper contracts for external tool integration.
"""

from typing import Any, Dict, List

import pytest

from gfl.plugins.example_implementations import (
    BayesianOptimizer,
    MoleculeTransformerGenerator,
    ProteinVAEGenerator,
)
from gfl.plugins.interfaces import (
    BayesianOptimizerPlugin,
    DesignCandidate,
    EntityType,
    ExperimentResult,
    GeneratorPlugin,
    MoleculeGeneratorPlugin,
    OptimizationStep,
    OptimizationStrategy,
    OptimizerPlugin,
    PriorsPlugin,
    SequenceGeneratorPlugin,
    get_available_generators,
    get_available_optimizers,
    register_generator_plugin,
    register_optimizer_plugin,
)
from gfl.plugins.plugin_registry import PluginDependency, PluginPriority


class TestDesignCandidate:
    """Test DesignCandidate data structure."""

    def test_design_candidate_creation(self):
        """Test basic DesignCandidate creation."""
        candidate = DesignCandidate(
            sequence="MKLLVLSLSLVLVAPMAAQAAEITLVPSVKLQIGDRDNRGYYWDGGHWRDHGWHGWRDY",
            properties={"stability": 0.85, "binding_affinity": 0.72},
            confidence=0.91,
        )

        assert candidate.sequence.startswith("MKLL")
        assert candidate.properties["stability"] == 0.85
        assert candidate.confidence == 0.91
        assert candidate.metadata == {}

    def test_design_candidate_with_metadata(self):
        """Test DesignCandidate with metadata."""
        metadata = {"model_version": "v1.2", "temperature": 0.8}
        candidate = DesignCandidate(sequence="ATCGATCGATCG", properties={"gc_content": 0.5}, metadata=metadata)

        assert candidate.metadata["model_version"] == "v1.2"
        assert candidate.metadata["temperature"] == 0.8


class TestExperimentResult:
    """Test ExperimentResult data structure."""

    def test_experiment_result_success(self):
        """Test successful experiment result."""
        result = ExperimentResult(
            parameters={"temperature": 25.5, "concentration": 100},
            objective_value=0.87,
            metrics={"efficiency": 0.87, "specificity": 0.92},
            success=True,
        )

        assert result.parameters["temperature"] == 25.5
        assert result.objective_value == 0.87
        assert result.success is True
        assert result.error_message is None

    def test_experiment_result_failure(self):
        """Test failed experiment result."""
        result = ExperimentResult(
            parameters={"temperature": 95.0}, objective_value=0.0, success=False, error_message="Temperature too high"
        )

        assert result.success is False
        assert result.error_message == "Temperature too high"
        assert result.objective_value == 0.0


class TestOptimizationStep:
    """Test OptimizationStep data structure."""

    def test_optimization_step_basic(self):
        """Test basic OptimizationStep creation."""
        step = OptimizationStep(parameters={"learning_rate": 0.01, "batch_size": 32}, iteration=5)

        assert step.parameters["learning_rate"] == 0.01
        assert step.iteration == 5
        assert step.expected_improvement is None

    def test_optimization_step_with_metrics(self):
        """Test OptimizationStep with acquisition function metrics."""
        step = OptimizationStep(parameters={"param1": 1.5}, iteration=10, expected_improvement=0.25, uncertainty=0.15)

        assert step.expected_improvement == 0.25
        assert step.uncertainty == 0.15


class MockGeneratorPlugin(GeneratorPlugin):
    """Mock generator plugin for testing."""

    @property
    def name(self) -> str:
        return "mock_generator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_entities(self) -> List[EntityType]:
        return [EntityType.PROTEIN_SEQUENCE, EntityType.DNA_SEQUENCE]

    def generate(
        self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
    ) -> List[DesignCandidate]:
        """Generate mock candidates."""
        candidates = []
        for i in range(count):
            if entity == EntityType.PROTEIN_SEQUENCE.value:
                sequence = "MKLLVL" + "A" * (20 + i)
            else:
                sequence = "ATCG" * (10 + i)

            candidates.append(
                DesignCandidate(sequence=sequence, properties={"mock_property": 0.5 + i * 0.1}, confidence=0.8)
            )

        return candidates

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseGFLPlugin."""
        return {"processed": True}


class MockOptimizerPlugin(OptimizerPlugin):
    """Mock optimizer plugin for testing."""

    def __init__(self):
        super().__init__()
        self.setup_called = False
        self.iteration = 0

    @property
    def name(self) -> str:
        return "mock_optimizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_strategies(self) -> List[OptimizationStrategy]:
        return [OptimizationStrategy.BAYESIAN_OPTIMIZATION, OptimizationStrategy.RANDOM_SEARCH]

    def setup(
        self, search_space: Dict[str, str], strategy: Dict[str, Any], objective: Dict[str, Any], budget: Dict[str, Any]
    ) -> None:
        """Mock setup."""
        self.setup_called = True

    def suggest_next(self, experiment_history: List[ExperimentResult]) -> OptimizationStep:
        """Mock suggestion."""
        self.iteration += 1
        return OptimizationStep(parameters={"param1": self.iteration * 0.1}, iteration=self.iteration)

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process method required by BaseGFLPlugin."""
        return {"processed": True}


class TestGeneratorPlugin:
    """Test GeneratorPlugin abstract interface."""

    def test_generator_plugin_instantiation(self):
        """Test that GeneratorPlugin can be instantiated through subclass."""
        generator = MockGeneratorPlugin()

        assert generator.name == "mock_generator"
        assert generator.version == "1.0.0"
        assert EntityType.PROTEIN_SEQUENCE in generator.supported_entities
        assert EntityType.DNA_SEQUENCE in generator.supported_entities

    def test_generator_plugin_generate(self):
        """Test generator plugin generation."""
        generator = MockGeneratorPlugin()

        candidates = generator.generate(
            entity="ProteinSequence", objective={"maximize": "stability"}, constraints=["length(20, 50)"], count=3
        )

        assert len(candidates) == 3
        assert all(isinstance(c, DesignCandidate) for c in candidates)
        assert candidates[0].sequence.startswith("MKLLVL")
        assert candidates[0].properties["mock_property"] == 0.5

    def test_generator_plugin_validation_methods(self):
        """Test generator plugin validation methods."""
        generator = MockGeneratorPlugin()

        # Test default validation (should return empty lists)
        obj_errors = generator.validate_objective({"maximize": "stability"})
        constraint_errors = generator.validate_constraints(["length(20, 50)"])

        assert obj_errors == []
        assert constraint_errors == []

    def test_generator_plugin_time_estimation(self):
        """Test generation time estimation."""
        generator = MockGeneratorPlugin()

        time_estimate = generator.estimate_generation_time(10, "ProteinSequence")

        assert isinstance(time_estimate, float)
        assert time_estimate == 10.0  # Default implementation

    def test_generator_plugin_constraints_support(self):
        """Test supported constraints method."""
        generator = MockGeneratorPlugin()

        constraints = generator.get_supported_constraints()

        assert isinstance(constraints, list)
        assert constraints == []  # Default implementation


class TestOptimizerPlugin:
    """Test OptimizerPlugin abstract interface."""

    def test_optimizer_plugin_instantiation(self):
        """Test that OptimizerPlugin can be instantiated through subclass."""
        optimizer = MockOptimizerPlugin()

        assert optimizer.name == "mock_optimizer"
        assert optimizer.version == "1.0.0"
        assert OptimizationStrategy.BAYESIAN_OPTIMIZATION in optimizer.supported_strategies

    def test_optimizer_plugin_setup(self):
        """Test optimizer plugin setup."""
        optimizer = MockOptimizerPlugin()

        optimizer.setup(
            search_space={"param1": "range(0, 1)"},
            strategy={"name": "BayesianOptimization"},
            objective={"maximize": "efficiency"},
            budget={"max_experiments": 50},
        )

        assert optimizer.setup_called is True

    def test_optimizer_plugin_suggestion(self):
        """Test optimizer plugin suggestion."""
        optimizer = MockOptimizerPlugin()
        optimizer.setup({}, {}, {}, {})

        # Test first suggestion
        step1 = optimizer.suggest_next([])
        assert isinstance(step1, OptimizationStep)
        assert step1.iteration == 1
        assert step1.parameters["param1"] == 0.1

        # Test second suggestion
        step2 = optimizer.suggest_next([])
        assert step2.iteration == 2
        assert step2.parameters["param1"] == 0.2

    def test_optimizer_plugin_should_stop(self):
        """Test optimizer stopping condition."""
        optimizer = MockOptimizerPlugin()

        # Test with max_experiments budget
        history = [ExperimentResult({"p": 1}, 0.5) for _ in range(5)]
        budget = {"max_experiments": 10}

        assert optimizer.should_stop(history, budget) is False

        # Test when budget is reached
        history = [ExperimentResult({"p": 1}, 0.5) for _ in range(10)]
        assert optimizer.should_stop(history, budget) is True

        # Test convergence
        converged_history = [
            ExperimentResult({"p": 1}, 0.85),
            ExperimentResult({"p": 2}, 0.851),
            ExperimentResult({"p": 3}, 0.849),
        ]
        convergence_budget = {"convergence_threshold": 0.01}

        assert optimizer.should_stop(converged_history, convergence_budget) is True

    def test_optimizer_plugin_state_management(self):
        """Test optimizer state save/load."""
        optimizer = MockOptimizerPlugin()

        # Test default state
        state = optimizer.get_optimization_state()
        assert isinstance(state, dict)

        # Test state loading (should not raise)
        optimizer.load_optimization_state({"iteration": 5})

    def test_optimizer_plugin_time_estimation(self):
        """Test remaining time estimation."""
        optimizer = MockOptimizerPlugin()

        history = [ExperimentResult({"p": 1}, 0.5)]
        budget = {"max_experiments": 10}

        remaining_time = optimizer.estimate_remaining_time(history, budget)

        # Default implementation returns None
        assert remaining_time is None


class TestSequenceGeneratorPlugin:
    """Test SequenceGeneratorPlugin specialized interface."""

    def test_sequence_generator_constraints(self):
        """Test sequence-specific constraint validation."""

        class MockSequenceGenerator(SequenceGeneratorPlugin):
            @property
            def name(self) -> str:
                return "mock_seq_gen"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def supported_entities(self) -> List[EntityType]:
                return [EntityType.PROTEIN_SEQUENCE]

            def generate(
                self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
            ) -> List[DesignCandidate]:
                return []

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        generator = MockSequenceGenerator()

        # Test valid constraints
        valid_constraints = ["length(20, 50)", "gc_content(0.4, 0.6)", "has_motif('ATG')"]
        errors = generator.validate_constraints(valid_constraints)
        assert errors == []

        # Test invalid constraints
        invalid_constraints = ["length(20, 50", "gc_content(0.4, 0.6", "has_motif('ATG'"]
        errors = generator.validate_constraints(invalid_constraints)
        assert len(errors) == 3  # All have syntax errors

    def test_sequence_generator_supported_constraints(self):
        """Test sequence generator supported constraints."""

        class MockSequenceGenerator(SequenceGeneratorPlugin):
            @property
            def name(self) -> str:
                return "mock_seq_gen"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def supported_entities(self) -> List[EntityType]:
                return [EntityType.PROTEIN_SEQUENCE]

            def generate(
                self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
            ) -> List[DesignCandidate]:
                return []

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        generator = MockSequenceGenerator()
        constraints = generator.get_supported_constraints()

        expected_constraints = [
            "length",
            "gc_content",
            "has_motif",
            "no_stop_codons",
            "synthesizability",
            "secondary_structure",
        ]
        assert all(c in constraints for c in expected_constraints)


class TestMoleculeGeneratorPlugin:
    """Test MoleculeGeneratorPlugin specialized interface."""

    def test_molecule_generator_constraints(self):
        """Test molecule-specific constraint validation."""

        class MockMoleculeGenerator(MoleculeGeneratorPlugin):
            @property
            def name(self) -> str:
                return "mock_mol_gen"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def supported_entities(self) -> List[EntityType]:
                return [EntityType.SMALL_MOLECULE]

            def generate(
                self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
            ) -> List[DesignCandidate]:
                return []

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        generator = MockMoleculeGenerator()

        # Test valid constraints
        valid_constraints = ["molecular_weight < 500", "logP < 5"]
        errors = generator.validate_constraints(valid_constraints)
        assert errors == []

        # Test invalid constraints
        invalid_constraints = ["molecular_weight 500", "logP invalid"]
        errors = generator.validate_constraints(invalid_constraints)
        assert len(errors) == 2

    def test_molecule_generator_supported_constraints(self):
        """Test molecule generator supported constraints."""

        class MockMoleculeGenerator(MoleculeGeneratorPlugin):
            @property
            def name(self) -> str:
                return "mock_mol_gen"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def supported_entities(self) -> List[EntityType]:
                return [EntityType.SMALL_MOLECULE]

            def generate(
                self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
            ) -> List[DesignCandidate]:
                return []

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        generator = MockMoleculeGenerator()
        constraints = generator.get_supported_constraints()

        expected_constraints = [
            "molecular_weight",
            "logP",
            "rotatable_bonds",
            "hbd_count",
            "hba_count",
            "drug_likeness",
            "synthetic_accessibility",
            "toxicity",
        ]
        assert all(c in constraints for c in expected_constraints)


class TestBayesianOptimizerPlugin:
    """Test BayesianOptimizerPlugin specialized interface."""

    def test_bayesian_optimizer_strategies(self):
        """Test Bayesian optimizer supported strategies."""

        class MockBayesianOptimizer(BayesianOptimizerPlugin):
            @property
            def name(self) -> str:
                return "mock_bayes_opt"

            @property
            def version(self) -> str:
                return "1.0.0"

            def setup(
                self,
                search_space: Dict[str, str],
                strategy: Dict[str, Any],
                objective: Dict[str, Any],
                budget: Dict[str, Any],
            ) -> None:
                pass

            def suggest_next(self, experiment_history: List[ExperimentResult]) -> OptimizationStep:
                return OptimizationStep(parameters={}, iteration=1)

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        optimizer = MockBayesianOptimizer()
        strategies = optimizer.supported_strategies

        assert OptimizationStrategy.BAYESIAN_OPTIMIZATION in strategies
        assert OptimizationStrategy.ACTIVE_LEARNING in strategies

    def test_bayesian_optimizer_search_space_validation(self):
        """Test Bayesian optimizer search space validation."""

        class MockBayesianOptimizer(BayesianOptimizerPlugin):
            @property
            def name(self) -> str:
                return "mock_bayes_opt"

            @property
            def version(self) -> str:
                return "1.0.0"

            def setup(
                self,
                search_space: Dict[str, str],
                strategy: Dict[str, Any],
                objective: Dict[str, Any],
                budget: Dict[str, Any],
            ) -> None:
                pass

            def suggest_next(self, experiment_history: List[ExperimentResult]) -> OptimizationStep:
                return OptimizationStep(parameters={}, iteration=1)

            def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        optimizer = MockBayesianOptimizer()

        # Test valid search space
        valid_space = {"param1": "range(0, 1)", "param2": "choice([1, 2, 3])"}
        errors = optimizer.validate_search_space(valid_space)
        assert errors == []

        # Test invalid search space
        invalid_space = {
            "param1": "range(0)",  # Missing second value
            "param2": "choice([])",  # Empty choice
        }
        errors = optimizer.validate_search_space(invalid_space)
        assert len(errors) == 2


class TestExampleImplementations:
    """Test example plugin implementations."""

    def test_protein_vae_generator(self):
        """Test ProteinVAEGenerator example implementation."""
        generator = ProteinVAEGenerator()

        assert generator.name == "ProteinVAEGenerator"
        assert generator.version == "1.2.0"
        assert EntityType.PROTEIN_SEQUENCE in generator.supported_entities

        # Test generation
        candidates = generator.generate(
            entity="ProteinSequence", objective={"maximize": "stability"}, constraints=["length(50, 100)"], count=2
        )

        assert len(candidates) == 2
        assert all(isinstance(c, DesignCandidate) for c in candidates)
        assert all(50 <= len(c.sequence) <= 100 for c in candidates)

    def test_molecule_transformer_generator(self):
        """Test MoleculeTransformerGenerator example implementation."""
        generator = MoleculeTransformerGenerator()

        assert generator.name == "MoleculeTransformerGenerator"
        assert EntityType.SMALL_MOLECULE in generator.supported_entities

        # Test generation
        candidates = generator.generate(
            entity="SmallMolecule",
            objective={"maximize": "binding_affinity"},
            constraints=["molecular_weight < 500"],
            count=2,
        )

        assert len(candidates) == 2
        assert all(isinstance(c, DesignCandidate) for c in candidates)

    def test_bayesian_optimizer_implementation(self):
        """Test BayesianOptimizer example implementation."""
        optimizer = BayesianOptimizer()

        assert optimizer.name == "BayesianOptimizer"
        assert OptimizationStrategy.BAYESIAN_OPTIMIZATION in optimizer.supported_strategies

        # Test setup
        optimizer.setup(
            search_space={"param1": "range(0, 1)"},
            strategy={"name": "BayesianOptimization"},
            objective={"maximize": "efficiency"},
            budget={"max_experiments": 10},
        )

        # Test suggestion
        step = optimizer.suggest_next([])
        assert isinstance(step, OptimizationStep)
        assert "param1" in step.parameters


class TestPluginRegistration:
    """Test plugin registration utilities."""

    def test_register_generator_plugin_valid(self):
        """Test registering a valid generator plugin."""

        # Test that registration works with valid plugin
        try:
            register_generator_plugin(MockGeneratorPlugin, "test_generator", version="1.0.0")
        except Exception as e:
            pytest.fail(f"Registration should succeed: {e}")

    def test_register_generator_plugin_invalid(self):
        """Test registering an invalid generator plugin."""

        class InvalidPlugin:
            pass

        with pytest.raises(TypeError):
            register_generator_plugin(InvalidPlugin, "invalid_generator")

    def test_register_optimizer_plugin_valid(self):
        """Test registering a valid optimizer plugin."""

        try:
            register_optimizer_plugin(MockOptimizerPlugin, "test_optimizer", version="1.0.0")
        except Exception as e:
            pytest.fail(f"Registration should succeed: {e}")

    def test_get_available_plugins(self):
        """Test getting available plugins."""

        # Register test plugins
        register_generator_plugin(MockGeneratorPlugin, "test_gen", version="1.0.0")
        register_optimizer_plugin(MockOptimizerPlugin, "test_opt", version="1.0.0")

        # Get available plugins
        generators = get_available_generators()
        optimizers = get_available_optimizers()

        assert isinstance(generators, dict)
        assert isinstance(optimizers, dict)
