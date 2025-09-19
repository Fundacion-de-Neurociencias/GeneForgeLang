"""Plugin registry for managing GFL plugins."""

from typing import Dict, Any, Type, List
from gfl.plugins.base import BaseGFLPlugin, BaseGeneratorPlugin, BaseOptimizerPlugin


class PluginRegistry:
    """Registry for managing GFL plugins."""
    
    def __init__(self):
        self._generators: Dict[str, Type[BaseGeneratorPlugin]] = {}
        self._optimizers: Dict[str, Type[BaseOptimizerPlugin]] = {}
        self._plugins: Dict[str, Type[BaseGFLPlugin]] = {}
        
        # Auto-register builtin plugins
        self._register_builtin_plugins()
    
    def _register_builtin_plugins(self):
        """Register builtin plugins."""
        try:
            from gfl.plugins.builtin.protein_generator import SimpleProteinGenerator
            from gfl.plugins.builtin.simple_optimizer import SimpleOptimizer
            
            self.register_generator("ProteinVAEGenerator", SimpleProteinGenerator)
            self.register_optimizer("BayesianOptimization", SimpleOptimizer)
            
        except ImportError:
            pass  # Builtin plugins not available
    
    def register_generator(self, name: str, plugin_class: Type[BaseGeneratorPlugin]):
        """Register a generator plugin."""
        self._generators[name] = plugin_class
        self._plugins[name] = plugin_class
    
    def register_optimizer(self, name: str, plugin_class: Type[BaseOptimizerPlugin]):
        """Register an optimizer plugin."""
        self._optimizers[name] = plugin_class
        self._plugins[name] = plugin_class
    
    def get_generator(self, name: str) -> BaseGeneratorPlugin:
        """Get a generator plugin instance."""
        if name not in self._generators:
            raise ValueError(f"Generator '{name}' not found")
        return self._generators[name]()
    
    def get_optimizer(self, name: str) -> BaseOptimizerPlugin:
        """Get an optimizer plugin instance."""
        if name not in self._optimizers:
            raise ValueError(f"Optimizer '{name}' not found")
        return self._optimizers[name]()
    
    def list_generators(self) -> List[str]:
        """List available generator plugins."""
        return list(self._generators.keys())
    
    def list_optimizers(self) -> List[str]:
        """List available optimizer plugins."""
        return list(self._optimizers.keys())
    
    def list_plugins(self) -> List[str]:
        """List all available plugins."""
        return list(self._plugins.keys())


# Global registry instance
plugin_registry = PluginRegistry()


def get_available_generators() -> Dict[str, Type[BaseGeneratorPlugin]]:
    """Get available generator plugins."""
    return plugin_registry._generators


def get_available_optimizers() -> Dict[str, Type[BaseOptimizerPlugin]]:
    """Get available optimizer plugins."""
    return plugin_registry._optimizers


def register_plugin_class(name: str, plugin_class: Type[BaseGFLPlugin], version: str = "1.0.0", metadata: dict = None):
    """Register a plugin class by name."""
    if issubclass(plugin_class, BaseGeneratorPlugin):
        plugin_registry.register_generator(name, plugin_class)
    elif issubclass(plugin_class, BaseOptimizerPlugin):
        plugin_registry.register_optimizer(name, plugin_class)
    else:
        plugin_registry._plugins[name] = plugin_class
