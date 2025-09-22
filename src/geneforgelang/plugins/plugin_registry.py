"""Plugin registry for managing GFL plugins."""

import importlib.metadata
from typing import Any, Dict, List, Type

from gfl.plugins.base import BaseGeneratorPlugin, BaseGFLPlugin, BaseOptimizerPlugin


class PluginRegistry:
    """Registry for managing GFL plugins."""

    def __init__(self):
        self._generators: dict[str, type[BaseGeneratorPlugin]] = {}
        self._optimizers: dict[str, type[BaseOptimizerPlugin]] = {}
        self._plugins: dict[str, type[BaseGFLPlugin]] = {}
        self._container_images: dict[str, str] = {}  # Maps plugin names to container images

        # Auto-register builtin plugins
        self._register_builtin_plugins()
        # Auto-discover external plugins
        self._discover_plugins()

    def _register_builtin_plugins(self):
        """Register builtin plugins."""
        try:
            from gfl.plugins.builtin.protein_generator import SimpleProteinGenerator
            from gfl.plugins.builtin.simple_optimizer import SimpleOptimizer

            self.register_generator("ProteinVAEGenerator", SimpleProteinGenerator)
            self.register_optimizer("BayesianOptimization", SimpleOptimizer)

        except ImportError:
            pass  # Builtin plugins not available

    def _discover_plugins(self):
        """Discover and register external plugins via entry points."""
        # Discover regular plugins
        for entry_point in importlib.metadata.entry_points().get("gfl.plugins", []):
            try:
                plugin_class = entry_point.load()
                self._register_plugin(entry_point.name, plugin_class)
            except Exception:
                pass  # Skip plugins that fail to load

        # Discover container images for plugins
        for entry_point in importlib.metadata.entry_points().get("gfl.plugin_containers", []):
            try:
                container_image = entry_point.load() if callable(entry_point.load) else entry_point.value
                self._container_images[entry_point.name] = container_image
            except Exception:
                pass  # Skip container images that fail to load

    def _register_plugin(self, name: str, plugin_class: type[BaseGFLPlugin]):
        """Register a plugin by name."""
        if issubclass(plugin_class, BaseGeneratorPlugin):
            self.register_generator(name, plugin_class)
        elif issubclass(plugin_class, BaseOptimizerPlugin):
            self.register_optimizer(name, plugin_class)
        else:
            self._plugins[name] = plugin_class

    def register_generator(self, name: str, plugin_class: type[BaseGeneratorPlugin]):
        """Register a generator plugin."""
        self._generators[name] = plugin_class
        self._plugins[name] = plugin_class

    def register_optimizer(self, name: str, plugin_class: type[BaseOptimizerPlugin]):
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

    def get_container_image(self, plugin_name: str) -> str | None:
        """Get the container image for a plugin, if available."""
        return self._container_images.get(plugin_name)

    def list_generators(self) -> list[str]:
        """List available generator plugins."""
        return list(self._generators.keys())

    def list_optimizers(self) -> list[str]:
        """List available optimizer plugins."""
        return list(self._optimizers.keys())

    def list_plugins(self) -> list[str]:
        """List all available plugins."""
        return list(self._plugins.keys())


# Global registry instance
plugin_registry = PluginRegistry()


def get_available_generators() -> dict[str, type[BaseGeneratorPlugin]]:
    """Get available generator plugins."""
    return plugin_registry._generators


def get_available_optimizers() -> dict[str, type[BaseOptimizerPlugin]]:
    """Get available optimizer plugins."""
    return plugin_registry._optimizers


def register_plugin_class(name: str, plugin_class: type[BaseGFLPlugin], version: str = "1.0.0", metadata: dict = None):
    """Register a plugin class by name."""
    if issubclass(plugin_class, BaseGeneratorPlugin):
        plugin_registry.register_generator(name, plugin_class)
    elif issubclass(plugin_class, BaseOptimizerPlugin):
        plugin_registry.register_optimizer(name, plugin_class)
    else:
        plugin_registry._plugins[name] = plugin_class
