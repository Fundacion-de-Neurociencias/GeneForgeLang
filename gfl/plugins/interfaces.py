"""Plugin interfaces for GeneForgeLang's design and optimize blocks.

This module defines the abstract base classes that serve as contracts for all external
tools that want to be compatible with GFL's advanced workflow blocks. These interfaces
standardize how the GFL execution engine interacts with specialized AI/ML tools.

Plugin developers must implement these interfaces to create tools that integrate
seamlessly with GFL's declarative workflow specifications.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .plugin_registry import BaseGFLPlugin, PluginDependency, PluginPriority

logger = logging.getLogger(__name__)


# Enums for plugin capabilities
class EntityType(Enum):
    """Supported biological entity types for design plugins."""

    PROTEIN_SEQUENCE = "ProteinSequence"
    DNA_SEQUENCE = "DNASequence"
    RNA_SEQUENCE = "RNASequence"
    SMALL_MOLECULE = "SmallMolecule"
    PEPTIDE = "Peptide"
    ANTIBODY = "Antibody"


class OptimizationStrategy(Enum):
    """Supported optimization strategies for optimize plugins."""

    RANDOM_SEARCH = "RandomSearch"
    GRID_SEARCH = "GridSearch"
    BAYESIAN_OPTIMIZATION = "BayesianOptimization"
    ACTIVE_LEARNING = "ActiveLearning"
    REINFORCEMENT_LEARNING = "ReinforcementLearning"
    EVOLUTIONARY = "Evolutionary"
    GRADIENT_DESCENT = "GradientDescent"


@dataclass
class DesignCandidate:
    """Represents a generated biological entity candidate."""

    sequence: str
    """The primary sequence (amino acids, nucleotides, or SMILES string)"""

    properties: Dict[str, Any] = field(default_factory=dict)
    """Predicted or computed properties of the candidate"""

    confidence: Optional[float] = None
    """Model confidence score (0-1) if available"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata about generation process"""


@dataclass
class OptimizationStep:
    """Represents one step in an optimization loop."""

    parameters: Dict[str, Any]
    """Parameter values to test in this step"""

    iteration: int
    """Iteration number in the optimization sequence"""

    expected_improvement: Optional[float] = None
    """Expected improvement score if using acquisition functions"""

    uncertainty: Optional[float] = None
    """Parameter uncertainty estimate if available"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional step metadata"""


@dataclass
class ExperimentResult:
    """Results from executing an experiment with specific parameters."""

    parameters: Dict[str, Any]
    """Parameters used in this experiment"""

    objective_value: float
    """Measured objective function value"""

    metrics: Dict[str, float] = field(default_factory=dict)
    """Additional measured metrics"""

    success: bool = True
    """Whether experiment completed successfully"""

    error_message: Optional[str] = None
    """Error details if experiment failed"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional experimental metadata"""


# Core plugin interfaces
class GeneratorPlugin(BaseGFLPlugin):
    """Abstract base class for biological entity generation plugins.

    GeneratorPlugin instances are responsible for creating new biological entities
    (proteins, DNA, RNA, small molecules, etc.) based on specified objectives and
    constraints. This is the core interface for GFL's design block.

    Plugins implementing this interface typically integrate with AI/ML models like:
    - Variational Autoencoders (VAEs) for protein design
    - Generative Adversarial Networks (GANs) for molecular generation
    - Transformer models for sequence design
    - Diffusion models for structure-based design
    """

    @property
    @abstractmethod
    def supported_entities(self) -> List[EntityType]:
        """Return list of entity types this plugin can generate.

        Returns:
            List of EntityType enums that this plugin supports.
        """
        pass

    @abstractmethod
    def generate(
        self, entity: str, objective: Dict[str, Any], constraints: List[str], count: int, **kwargs
    ) -> List[DesignCandidate]:
        """Generate biological entity candidates based on design specification.

        This method implements the core generative capability, taking the design
        requirements from a GFL design block and producing candidates that meet
        the specified criteria.

        Args:
            entity: Type of biological entity to design (e.g., "ProteinSequence")
            objective: Optimization objective with 'maximize'/'minimize' and optional 'target'
            constraints: List of constraint expressions to satisfy
            count: Number of candidates to generate
            **kwargs: Additional plugin-specific parameters

        Returns:
            List of DesignCandidate objects containing generated entities

        Raises:
            ValueError: If entity type is not supported or parameters are invalid
            RuntimeError: If generation process fails
        """
        pass

    def validate_objective(self, objective: Dict[str, Any]) -> List[str]:
        """Validate that the objective is compatible with this plugin.

        Args:
            objective: Design objective dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        return []

    def validate_constraints(self, constraints: List[str]) -> List[str]:
        """Validate that constraints are compatible with this plugin.

        Args:
            constraints: List of constraint expressions

        Returns:
            List of validation error messages (empty if valid)
        """
        return []

    def estimate_generation_time(self, count: int, entity: str) -> float:
        """Estimate time required for generation in seconds.

        Args:
            count: Number of candidates to generate
            entity: Entity type

        Returns:
            Estimated time in seconds
        """
        return float(count)  # Default: 1 second per candidate

    def get_supported_constraints(self) -> List[str]:
        """Get list of constraint types supported by this plugin.

        Returns:
            List of constraint type names (e.g., ['length', 'gc_content', 'motif'])
        """
        return []


class OptimizerPlugin(BaseGFLPlugin):
    """Abstract base class for experiment optimization plugins.

    OptimizerPlugin instances implement intelligent experimental design algorithms
    that can efficiently explore parameter spaces to find optimal experimental
    conditions. This is the core interface for GFL's optimize block.

    Plugins implementing this interface typically integrate with optimization libraries:
    - Scikit-optimize for Bayesian optimization
    - Optuna for advanced hyperparameter optimization
    - GPyOpt for Gaussian process optimization
    - Ray Tune for distributed optimization
    - Custom reinforcement learning agents
    """

    @property
    @abstractmethod
    def supported_strategies(self) -> List[OptimizationStrategy]:
        """Return list of optimization strategies this plugin supports.

        Returns:
            List of OptimizationStrategy enums supported by this plugin.
        """
        pass

    @abstractmethod
    def setup(
        self, search_space: Dict[str, str], strategy: Dict[str, Any], objective: Dict[str, Any], budget: Dict[str, Any]
    ) -> None:
        """Initialize the optimization algorithm with problem specification.

        This method is called once before optimization begins to configure
        the algorithm with the complete problem definition.

        Args:
            search_space: Parameter definitions using range() and choice() syntax
            strategy: Algorithm configuration (name, hyperparameters)
            objective: Optimization objective (maximize/minimize target)
            budget: Resource constraints (max_experiments, max_time, etc.)

        Raises:
            ValueError: If configuration is invalid or unsupported
            RuntimeError: If setup fails
        """
        pass

    @abstractmethod
    def suggest_next(self, experiment_history: List[ExperimentResult]) -> OptimizationStep:
        """Suggest the next parameter configuration to evaluate.

        This is the core intelligence of the optimization algorithm - using
        the history of previous experiments to intelligently select the most
        promising next configuration.

        Args:
            experiment_history: Complete history of experiments and their results

        Returns:
            OptimizationStep containing next parameters to test

        Raises:
            StopIteration: If optimization should terminate (budget exhausted, converged)
            RuntimeError: If suggestion generation fails
        """
        pass

    def should_stop(self, experiment_history: List[ExperimentResult], budget: Dict[str, Any]) -> bool:
        """Determine if optimization should terminate.

        Args:
            experiment_history: Complete history of experiments
            budget: Budget constraints from optimize block

        Returns:
            True if optimization should stop, False to continue
        """
        # Check budget constraints
        if "max_experiments" in budget:
            if len(experiment_history) >= budget["max_experiments"]:
                return True

        # Check convergence if specified
        if "convergence_threshold" in budget and len(experiment_history) >= 3:
            recent_values = [r.objective_value for r in experiment_history[-3:]]
            if max(recent_values) - min(recent_values) < budget["convergence_threshold"]:
                return True

        return False

    def get_optimization_state(self) -> Dict[str, Any]:
        """Get current optimization algorithm state for checkpointing.

        Returns:
            Dictionary containing algorithm state that can be serialized
        """
        return {}

    def load_optimization_state(self, state: Dict[str, Any]) -> None:
        """Load optimization algorithm state from checkpoint.

        Args:
            state: Previously saved algorithm state
        """
        pass

    def estimate_remaining_time(
        self, experiment_history: List[ExperimentResult], budget: Dict[str, Any]
    ) -> Optional[float]:
        """Estimate remaining optimization time in seconds.

        Args:
            experiment_history: Experiment history for time estimation
            budget: Budget constraints

        Returns:
            Estimated remaining time in seconds, or None if unknown
        """
        return None


class PriorsPlugin(BaseGFLPlugin):
    """Abstract base class for Bayesian prior integration plugins.

    PriorsPlugin instances handle the integration of prior knowledge into
    experimental design and analysis workflows. This supports GFL's with_priors
    clause by enabling sophisticated statistical modeling.
    """

    @abstractmethod
    def specify_priors(self, parameters: Dict[str, Any], prior_type: str, **kwargs) -> Dict[str, Any]:
        """Specify prior distributions for experimental parameters.

        Args:
            parameters: Parameter definitions from experiment/analyze blocks
            prior_type: Type of prior specification ('informative', 'non_informative', 'conjugate')
            **kwargs: Additional prior specification parameters

        Returns:
            Dictionary containing prior distribution specifications
        """
        pass

    @abstractmethod
    def update_posteriors(self, priors: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Update posterior distributions based on observed data.

        Args:
            priors: Prior distribution specifications
            data: Observed experimental data

        Returns:
            Dictionary containing updated posterior distributions
        """
        pass

    def validate_priors(self, priors: Dict[str, Any]) -> List[str]:
        """Validate prior distribution specifications.

        Args:
            priors: Prior distribution specifications

        Returns:
            List of validation error messages (empty if valid)
        """
        return []


# Specialized plugin classes for common use cases
class SequenceGeneratorPlugin(GeneratorPlugin):
    """Specialized base class for sequence-based entity generators.

    Provides common functionality for proteins, DNA, and RNA sequence generation.
    """

    def validate_constraints(self, constraints: List[str]) -> List[str]:
        """Validate sequence-specific constraints."""
        errors = []

        for constraint in constraints:
            # Basic constraint syntax validation
            if constraint.startswith("length(") and not constraint.endswith(")"):
                errors.append(f"Invalid length constraint syntax: {constraint}")
            elif constraint.startswith("gc_content(") and not constraint.endswith(")"):
                errors.append(f"Invalid gc_content constraint syntax: {constraint}")
            elif constraint.startswith("has_motif(") and not constraint.endswith(")"):
                errors.append(f"Invalid motif constraint syntax: {constraint}")

        return errors

    def get_supported_constraints(self) -> List[str]:
        """Common sequence constraints."""
        return ["length", "gc_content", "has_motif", "no_stop_codons", "synthesizability", "secondary_structure"]


class MoleculeGeneratorPlugin(GeneratorPlugin):
    """Specialized base class for small molecule generators.

    Provides common functionality for drug-like molecule generation.
    """

    def validate_constraints(self, constraints: List[str]) -> List[str]:
        """Validate molecule-specific constraints."""
        errors = []

        for constraint in constraints:
            # Drug-likeness constraint validation
            if "molecular_weight" in constraint and not any(op in constraint for op in ["<", ">", "="]):
                errors.append(f"Invalid molecular_weight constraint: {constraint}")
            elif "logP" in constraint and not any(op in constraint for op in ["<", ">", "="]):
                errors.append(f"Invalid logP constraint: {constraint}")

        return errors

    def get_supported_constraints(self) -> List[str]:
        """Common molecular constraints."""
        return [
            "molecular_weight",
            "logP",
            "rotatable_bonds",
            "hbd_count",
            "hba_count",
            "drug_likeness",
            "synthetic_accessibility",
            "toxicity",
        ]


class BayesianOptimizerPlugin(OptimizerPlugin):
    """Specialized base class for Bayesian optimization plugins.

    Provides common functionality and validation for Bayesian optimization approaches.
    """

    @property
    def supported_strategies(self) -> List[OptimizationStrategy]:
        """Bayesian optimization strategies."""
        return [OptimizationStrategy.BAYESIAN_OPTIMIZATION, OptimizationStrategy.ACTIVE_LEARNING]

    def validate_search_space(self, search_space: Dict[str, str]) -> List[str]:
        """Validate search space for Bayesian optimization."""
        errors = []

        for param, definition in search_space.items():
            if definition.startswith("range("):
                # Validate continuous parameter ranges
                try:
                    content = definition[6:-1]  # Remove 'range(' and ')'
                    parts = [p.strip() for p in content.split(",")]
                    if len(parts) != 2:
                        errors.append(f"Range for {param} must have exactly 2 values")
                    else:
                        float(parts[0])  # Check if numeric
                        float(parts[1])
                except (ValueError, IndexError):
                    errors.append(f"Invalid range syntax for parameter {param}: {definition}")
            elif definition.startswith("choice("):
                # Validate discrete parameter choices
                if definition == "choice([])":
                    errors.append(f"Empty choice list for parameter {param}")

        return errors


# Utility functions for plugin developers
def register_generator_plugin(
    plugin_class: type,
    name: str,
    version: str = "1.0.0",
    priority: PluginPriority = PluginPriority.NORMAL,
    dependencies: Optional[List[PluginDependency]] = None,
) -> None:
    """Convenience function to register a generator plugin.

    Args:
        plugin_class: The plugin class implementing GeneratorPlugin
        name: Plugin name
        version: Plugin version
        priority: Plugin execution priority
        dependencies: List of plugin dependencies
    """
    from .plugin_registry import plugin_registry

    # Validate that class implements GeneratorPlugin
    if not issubclass(plugin_class, GeneratorPlugin):
        raise TypeError("Plugin class must inherit from GeneratorPlugin")

    instance = plugin_class()
    plugin_registry.register(name, instance, version)


def register_optimizer_plugin(
    plugin_class: type,
    name: str,
    version: str = "1.0.0",
    priority: PluginPriority = PluginPriority.NORMAL,
    dependencies: Optional[List[PluginDependency]] = None,
) -> None:
    """Convenience function to register an optimizer plugin.

    Args:
        plugin_class: The plugin class implementing OptimizerPlugin
        name: Plugin name
        version: Plugin version
        priority: Plugin execution priority
        dependencies: List of plugin dependencies
    """
    from .plugin_registry import plugin_registry

    # Validate that class implements OptimizerPlugin
    if not issubclass(plugin_class, OptimizerPlugin):
        raise TypeError("Plugin class must inherit from OptimizerPlugin")

    instance = plugin_class()
    plugin_registry.register(name, instance, version)


def get_available_generators() -> Dict[str, GeneratorPlugin]:
    """Get all registered generator plugins.

    Returns:
        Dictionary mapping plugin names to GeneratorPlugin instances
    """
    from .plugin_registry import plugin_registry

    generators = {}
    for info in plugin_registry.list_plugins():
        if info.instance and isinstance(info.instance, GeneratorPlugin):
            generators[info.name] = info.instance

    return generators


def get_available_optimizers() -> Dict[str, OptimizerPlugin]:
    """Get all registered optimizer plugins.

    Returns:
        Dictionary mapping plugin names to OptimizerPlugin instances
    """
    from .plugin_registry import plugin_registry

    optimizers = {}
    for info in plugin_registry.list_plugins():
        if info.instance and isinstance(info.instance, OptimizerPlugin):
            optimizers[info.name] = info.instance

    return optimizers
