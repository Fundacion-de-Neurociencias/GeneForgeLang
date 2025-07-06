from .console_plugin import ConsolePlugin
from .alphagenome_plugin import AlphaGenomePlugin
from .variant_simulation_plugin import VariantSimulationPlugin # <-- Nueva línea

class PluginRegistry:
    def __init__(self):
        self._plugins = {
            "Console": ConsolePlugin(),
            "AlphaGenome": AlphaGenomePlugin(),
            "VariantSimulation": VariantSimulationPlugin(), # <-- Nueva línea
            # Añade más plugins aquí
        }

    def get(self, name):
        plugin = self._plugins.get(name)
        if not plugin:
            raise ValueError(f"Plugin '{name}' not found in registry.")
        return plugin

plugin_registry = PluginRegistry()
