"""GeneForgeLang plugin system."""

try:
    from geneforgelang.plugins.base import BaseGeneratorPlugin, BaseGFLPlugin, BaseOptimizerPlugin
    from geneforgelang.plugins.plugin_registry import get_available_generators, get_available_optimizers, plugin_registry

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
