"""Advanced plugin registry with entry point discovery.

This module provides a plugin system that supports:
1. Manual registration at runtime
2. Automatic discovery via entry points
3. Lazy loading for performance
4. Plugin metadata and validation

External packages can register plugins by adding entry points in their pyproject.toml:

[project.entry-points."gfl.plugins"]
my_plugin = "my_package.plugin:MyPlugin"
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Type

try:
    from importlib.metadata import entry_points

    HAS_ENTRY_POINTS = True
except ImportError:
    try:
        from importlib_metadata import entry_points  # Python < 3.8

        HAS_ENTRY_POINTS = True
    except ImportError:
        HAS_ENTRY_POINTS = False
        entry_points = None

logger = logging.getLogger(__name__)


# Plugin interface protocols
class GFLPlugin(Protocol):
    """Protocol that all GFL plugins should implement."""

    @property
    def name(self) -> str:
        """Plugin name."""
        ...

    @property
    def version(self) -> str:
        """Plugin version."""
        ...

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GFL data and return results."""
        ...


class BaseGFLPlugin(ABC):
    """Base class for GFL plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GFL data and return results."""
        pass

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration. Return list of errors."""
        return []

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__,
            "module": self.__class__.__module__,
        }


@dataclass
class PluginInfo:
    """Information about a registered plugin."""

    name: str
    version: str
    plugin_class: Type[Any]
    instance: Optional[Any] = None
    entry_point: Optional[str] = None
    is_loaded: bool = False
    load_error: Optional[str] = None

    def load(self) -> Any:
        """Load the plugin instance."""
        if self.is_loaded and self.instance is not None:
            return self.instance

        try:
            if self.instance is None:
                self.instance = self.plugin_class()
            self.is_loaded = True
            self.load_error = None
            return self.instance
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load plugin {self.name}: {e}")
            raise


class _Registry:
    """Enhanced plugin registry with entry point discovery."""

    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._discovered = False

    def register(self, name: str, plugin: Any, version: str = "unknown") -> None:
        """Register a plugin instance."""
        if hasattr(plugin, "name"):
            name = plugin.name
        if hasattr(plugin, "version"):
            version = plugin.version

        plugin_info = PluginInfo(
            name=name,
            version=version,
            plugin_class=plugin.__class__,
            instance=plugin,
            is_loaded=True,
        )
        self._plugins[name] = plugin_info
        logger.debug(f"Registered plugin: {name} v{version}")

    def register_class(
        self, name: str, plugin_class: Type[Any], version: str = "unknown"
    ) -> None:
        """Register a plugin class (lazy loading)."""
        plugin_info = PluginInfo(
            name=name, version=version, plugin_class=plugin_class, is_loaded=False
        )
        self._plugins[name] = plugin_info
        logger.debug(f"Registered plugin class: {name} v{version}")

    def get(self, name: str) -> Any:
        """Get a plugin instance, loading if necessary."""
        if not self._discovered:
            self._discover_plugins()

        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' is not registered")

        plugin_info = self._plugins[name]
        return plugin_info.load()

    def get_info(self, name: str) -> PluginInfo:
        """Get plugin information without loading."""
        if not self._discovered:
            self._discover_plugins()

        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' is not registered")

        return self._plugins[name]

    def names(self) -> List[str]:
        """Get list of available plugin names."""
        if not self._discovered:
            self._discover_plugins()

        return sorted(self._plugins.keys())

    def list_plugins(self) -> List[PluginInfo]:
        """Get list of all plugin info."""
        if not self._discovered:
            self._discover_plugins()

        return list(self._plugins.values())

    def _discover_plugins(self) -> None:
        """Discover plugins via entry points."""
        if self._discovered:
            return

        logger.debug("Discovering plugins via entry points...")

        if not HAS_ENTRY_POINTS:
            logger.warning("Entry points not available, skipping plugin discovery")
            self._discovered = True
            return

        try:
            # Discover plugins from entry points
            if hasattr(entry_points, "select"):  # Python 3.10+
                gfl_plugins = entry_points.select(group="gfl.plugins")
            else:  # Python 3.8-3.9
                gfl_plugins = entry_points().get("gfl.plugins", [])

            for ep in gfl_plugins:
                try:
                    plugin_class = ep.load()

                    # Try to get version from plugin
                    version = "unknown"
                    if hasattr(plugin_class, "version"):
                        version = plugin_class.version
                    elif hasattr(plugin_class, "__version__"):
                        version = plugin_class.__version__

                    self.register_class(ep.name, plugin_class, version)
                    logger.debug(f"Discovered plugin via entry point: {ep.name}")

                except Exception as e:
                    logger.warning(f"Failed to load plugin {ep.name}: {e}")

        except Exception as e:
            logger.error(f"Plugin discovery failed: {e}")

        # Auto-register built-in plugins
        self._try_autoregister_builtin()

        self._discovered = True

    def _try_autoregister_builtin(self) -> None:
        """Auto-register built-in demo plugins."""
        # Attempt to import demo plugins if they are available.
        builtin_plugins = [
            ("alpha_genome", "gfl.plugins.alpha_genome", "AlphaGenomePlugin"),
            ("variant_sim", "gfl.plugins.variant_sim", "VariantSimulationPlugin"),
        ]

        for name, module_name, class_name in builtin_plugins:
            if name in self._plugins:
                continue  # Already registered via entry point

            try:
                module = __import__(module_name, fromlist=[class_name])
                plugin_class = getattr(module, class_name)

                # Create instance to check if it works
                instance = plugin_class()
                self.register(name, instance)
                logger.debug(f"Auto-registered built-in plugin: {name}")

            except Exception as e:
                logger.debug(f"Could not auto-register {name}: {e}")

    def reload_plugins(self) -> None:
        """Force reload of all plugins."""
        self._discovered = False
        self._plugins.clear()
        self._discover_plugins()


plugin_registry = _Registry()


# Convenience functions
def get_plugin(name: str) -> Any:
    """Get a plugin by name."""
    return plugin_registry.get(name)


def list_plugins() -> List[PluginInfo]:
    """List all available plugins."""
    return plugin_registry.list_plugins()


def discover_plugins() -> None:
    """Force plugin discovery."""
    plugin_registry._discover_plugins()


def register_plugin(name: str, plugin: Any, version: str = "unknown") -> None:
    """Register a plugin."""
    plugin_registry.register(name, plugin, version)


__all__ = [
    "plugin_registry",
    "GFLPlugin",
    "BaseGFLPlugin",
    "PluginInfo",
    "get_plugin",
    "list_plugins",
    "discover_plugins",
    "register_plugin",
]
