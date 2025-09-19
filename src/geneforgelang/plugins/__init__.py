"""GeneForgeLang plugin system."""

try:
    from .base import BaseGeneratorPlugin, BaseGFLPlugin, BaseOptimizerPlugin
    from .plugin_registry import get_available_generators, get_available_optimizers, plugin_registry

    __all__ = [
        "BaseGFLPlugin",
        "BaseGeneratorPlugin",
        "BaseOptimizerPlugin",
        "plugin_registry",
        "get_available_generators",
        "get_available_optimizers",
    ]
except ImportError:
    __all__ = []
