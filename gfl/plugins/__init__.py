"""GeneForgeLang plugin system with specialized interfaces.

This package provides:
1. Base plugin architecture with lifecycle management
2. Specialized interfaces for design and optimize blocks
3. Example implementations for reference
4. Plugin registry with dependency management
"""

from .interfaces import (
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
from .plugin_registry import (
    BaseGFLPlugin,
    GFLPlugin,
    PluginDependency,
    PluginInfo,
    PluginPriority,
    PluginState,
    activate_plugin,
    deactivate_plugin,
    get_active_plugins,
    get_plugin,
    plugin_registry,
    register_plugin,
)

__all__ = [
    # Plugin registry core
    "BaseGFLPlugin",
    "GFLPlugin",
    "PluginDependency",
    "PluginInfo",
    "PluginPriority",
    "PluginState",
    "plugin_registry",
    "activate_plugin",
    "deactivate_plugin",
    "get_active_plugins",
    "get_plugin",
    "register_plugin",
    # Specialized interfaces
    "GeneratorPlugin",
    "OptimizerPlugin",
    "PriorsPlugin",
    "SequenceGeneratorPlugin",
    "MoleculeGeneratorPlugin",
    "BayesianOptimizerPlugin",
    # Data structures
    "DesignCandidate",
    "ExperimentResult",
    "OptimizationStep",
    "EntityType",
    "OptimizationStrategy",
    # Interface utilities
    "register_generator_plugin",
    "register_optimizer_plugin",
    "get_available_generators",
    "get_available_optimizers",
]
