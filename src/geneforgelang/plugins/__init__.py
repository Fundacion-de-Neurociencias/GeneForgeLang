"""GeneForgeLang plugin system."""

try:
    pass

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
