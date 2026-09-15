"""GeneForgeLang plugin system."""

try:
    from geneforgelang.plugins import auto_register  # noqa: F401

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