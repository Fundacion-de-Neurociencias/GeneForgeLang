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
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type

try:
    from importlib.metadata import entry_points as _entry_points, version

    HAS_ENTRY_POINTS = True
except ImportError:
    try:
        from importlib_metadata import (
            entry_points as _entry_points,
            version,
        )  # Python < 3.8

        HAS_ENTRY_POINTS = True
    except ImportError:
        HAS_ENTRY_POINTS = False
        _entry_points = None

        def version(x):
            return "unknown"


logger = logging.getLogger(__name__)


# Plugin lifecycle and dependency enums
class PluginState(Enum):
    """Plugin lifecycle states."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginPriority(Enum):
    """Plugin execution priority."""

    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    BACKGROUND = 10


@dataclass
class PluginDependency:
    """Represents a plugin dependency."""

    name: str
    version_spec: Optional[str] = None  # e.g., ">=1.0.0", "~=2.1"
    optional: bool = False
    import_name: Optional[str] = None  # Package import name if different

    def is_satisfied(self) -> bool:
        """Check if this dependency is satisfied."""
        try:
            if self.import_name:
                __import__(self.import_name)
            else:
                __import__(self.name)

            if self.version_spec:
                try:
                    pkg_version = version(self.name)
                    return self._check_version_spec(pkg_version, self.version_spec)
                except Exception:
                    return not self.optional

            return True
        except ImportError:
            return self.optional

    def _check_version_spec(self, current: str, spec: str) -> bool:
        """Simple version checking (basic implementation)."""
        # This is a simplified version checker
        # In production, consider using packaging.specifiers
        if spec.startswith(">="):
            required = spec[2:].strip()
            return current >= required
        elif spec.startswith("~="):
            required = spec[2:].strip()
            # Compatible release (~= means same major.minor, any patch)
            current_parts = current.split(".")
            required_parts = required.split(".")
            if len(current_parts) >= 2 and len(required_parts) >= 2:
                return (
                    current_parts[0] == required_parts[0]
                    and current_parts[1] == required_parts[1]
                )
        elif spec.startswith("=="):
            required = spec[2:].strip()
            return current == required
        return True


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
    """Base class for GFL plugins with enhanced features."""

    def __init__(self):
        self._state = PluginState.UNLOADED
        self._error: Optional[str] = None

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

    @property
    def priority(self) -> PluginPriority:
        """Plugin execution priority (default: NORMAL)."""
        return PluginPriority.NORMAL

    @property
    def dependencies(self) -> List[PluginDependency]:
        """Plugin dependencies (default: none)."""
        return []

    @property
    def state(self) -> PluginState:
        """Current plugin state."""
        return self._state

    @property
    def error(self) -> Optional[str]:
        """Last error message if in ERROR state."""
        return self._error

    def _set_state(self, state: PluginState, error: Optional[str] = None) -> None:
        """Internal method to update plugin state."""
        self._state = state
        self._error = error

    def on_load(self) -> None:
        """Called when plugin is loaded. Override to add custom logic."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded. Override to add custom logic."""
        pass

    def on_activate(self) -> None:
        """Called when plugin becomes active. Override to add custom logic."""
        pass

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated. Override to add custom logic."""
        pass

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GFL data and return results."""
        pass

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration. Return list of errors."""
        return []

    def get_metadata(self) -> Dict[str, Any]:
        """Get comprehensive plugin metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "priority": self.priority.value,
            "state": self.state.value,
            "type": self.__class__.__name__,
            "module": self.__class__.__module__,
            "dependencies": [
                {
                    "name": dep.name,
                    "version_spec": dep.version_spec,
                    "optional": dep.optional,
                    "satisfied": dep.is_satisfied(),
                }
                for dep in self.dependencies
            ],
            "error": self.error,
        }


@dataclass
class PluginInfo:
    """Enhanced information about a registered plugin."""

    name: str
    version: str
    plugin_class: Type[Any]
    instance: Optional[Any] = None
    entry_point: Optional[str] = None
    state: PluginState = PluginState.UNLOADED
    load_error: Optional[str] = None
    dependencies: List[PluginDependency] = field(default_factory=list)
    priority: PluginPriority = PluginPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_loaded(self) -> bool:
        """Check if plugin is loaded."""
        return self.state in (PluginState.LOADED, PluginState.ACTIVE)

    def check_dependencies(self) -> List[str]:
        """Check plugin dependencies and return list of missing ones."""
        missing = []
        for dep in self.dependencies:
            if not dep.is_satisfied():
                if dep.optional:
                    logger.warning(
                        f"Optional dependency {dep.name} not satisfied for plugin {self.name}"
                    )
                else:
                    missing.append(f"{dep.name}{dep.version_spec or ''}")
        return missing

    def load(self, registry_hooks: Optional[List[PluginLifecycleHook]] = None) -> Any:
        """Load the plugin instance with dependency checking and lifecycle hooks."""
        if self.state == PluginState.LOADED and self.instance is not None:
            return self.instance

        # Check dependencies first
        missing_deps = self.check_dependencies()
        if missing_deps:
            error_msg = f"Missing dependencies: {', '.join(missing_deps)}"
            self._set_error_state(error_msg)
            raise RuntimeError(error_msg)

        try:
            self._set_state(PluginState.LOADING)

            # Notify hooks
            self._notify_hooks(registry_hooks, PluginState.LOADING)

            if self.instance is None:
                self.instance = self.plugin_class()

            # Update plugin internal state if it's an enhanced plugin
            if hasattr(self.instance, "_set_state"):
                self.instance._set_state(PluginState.LOADED)

            # Get enhanced metadata
            if hasattr(self.instance, "priority"):
                self.priority = self.instance.priority
            if hasattr(self.instance, "dependencies"):
                self.dependencies = self.instance.dependencies

            # Call lifecycle hook
            if hasattr(self.instance, "on_load"):
                self.instance.on_load()

            self._set_state(PluginState.LOADED)

            # Notify hooks
            self._notify_hooks(registry_hooks, PluginState.LOADED)

            logger.debug(f"Successfully loaded plugin: {self.name}")
            return self.instance

        except Exception as e:
            error_msg = str(e)
            self._set_error_state(error_msg)
            logger.error(f"Failed to load plugin {self.name}: {e}")
            raise

    def unload(
        self, registry_hooks: Optional[List[PluginLifecycleHook]] = None
    ) -> None:
        """Unload the plugin instance."""
        if self.state == PluginState.UNLOADED:
            return

        try:
            # Call lifecycle hook
            if self.instance and hasattr(self.instance, "on_unload"):
                self.instance.on_unload()

            # Update plugin internal state
            if self.instance and hasattr(self.instance, "_set_state"):
                self.instance._set_state(PluginState.UNLOADED)

            self.instance = None
            self._set_state(PluginState.UNLOADED)

            # Notify hooks
            self._notify_hooks(registry_hooks, PluginState.UNLOADED)

            logger.debug(f"Unloaded plugin: {self.name}")

        except Exception as e:
            error_msg = f"Error during unload: {e}"
            self._set_error_state(error_msg)
            logger.error(f"Failed to unload plugin {self.name}: {e}")

    def activate(
        self, registry_hooks: Optional[List[PluginLifecycleHook]] = None
    ) -> None:
        """Activate the plugin."""
        if self.state != PluginState.LOADED:
            raise RuntimeError(f"Plugin {self.name} must be loaded before activation")

        try:
            if self.instance and hasattr(self.instance, "on_activate"):
                self.instance.on_activate()

            if self.instance and hasattr(self.instance, "_set_state"):
                self.instance._set_state(PluginState.ACTIVE)

            self._set_state(PluginState.ACTIVE)

            # Notify hooks
            self._notify_hooks(registry_hooks, PluginState.ACTIVE)

            logger.debug(f"Activated plugin: {self.name}")

        except Exception as e:
            error_msg = f"Error during activation: {e}"
            self._set_error_state(error_msg)
            logger.error(f"Failed to activate plugin {self.name}: {e}")

    def deactivate(
        self, registry_hooks: Optional[List[PluginLifecycleHook]] = None
    ) -> None:
        """Deactivate the plugin."""
        if self.state != PluginState.ACTIVE:
            return

        try:
            if self.instance and hasattr(self.instance, "on_deactivate"):
                self.instance.on_deactivate()

            if self.instance and hasattr(self.instance, "_set_state"):
                self.instance._set_state(PluginState.LOADED)

            self._set_state(PluginState.LOADED)

            # Notify hooks
            self._notify_hooks(registry_hooks, PluginState.LOADED)

            logger.debug(f"Deactivated plugin: {self.name}")

        except Exception as e:
            error_msg = f"Error during deactivation: {e}"
            self._set_error_state(error_msg)
            logger.error(f"Failed to deactivate plugin {self.name}: {e}")

    def _set_state(self, state: PluginState) -> None:
        """Internal method to update plugin state."""
        self.state = state
        if state != PluginState.ERROR:
            self.load_error = None

    def _set_error_state(self, error_msg: str) -> None:
        """Set plugin to error state."""
        self.state = PluginState.ERROR
        self.load_error = error_msg
        if self.instance and hasattr(self.instance, "_set_state"):
            self.instance._set_state(PluginState.ERROR, error_msg)

    def _notify_hooks(
        self, hooks: Optional[List[PluginLifecycleHook]], state: PluginState
    ) -> None:
        """Notify registry hooks of state change."""
        if not hooks:
            return

        for hook in hooks:
            try:
                hook(self.name, state, plugin_info=self)
            except Exception as e:
                logger.warning(f"Plugin lifecycle hook failed for {self.name}: {e}")


class _Registry:
    """Enhanced plugin registry with entry point discovery, dependency management and lifecycle hooks."""

    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._discovered = False
        self._hooks: List[PluginLifecycleHook] = []
        self._plugin_order: List[str] = []  # For dependency-based ordering

    def add_lifecycle_hook(self, hook: PluginLifecycleHook) -> None:
        """Add a lifecycle hook for plugin state changes."""
        self._hooks.append(hook)

    def remove_lifecycle_hook(self, hook: PluginLifecycleHook) -> None:
        """Remove a lifecycle hook."""
        if hook in self._hooks:
            self._hooks.remove(hook)

    def register(
        self,
        name: str,
        plugin: Any,
        version: str = "unknown",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a plugin instance with enhanced metadata."""
        if hasattr(plugin, "name"):
            name = plugin.name
        if hasattr(plugin, "version"):
            version = plugin.version

        # Get dependencies and priority if available
        dependencies = []
        priority = PluginPriority.NORMAL
        if hasattr(plugin, "dependencies"):
            dependencies = plugin.dependencies
        if hasattr(plugin, "priority"):
            priority = plugin.priority

        plugin_info = PluginInfo(
            name=name,
            version=version,
            plugin_class=plugin.__class__,
            instance=plugin,
            state=PluginState.LOADED,
            dependencies=dependencies,
            priority=priority,
            config=config or {},
        )

        # Update plugin state if it supports enhanced interface
        if hasattr(plugin, "_set_state"):
            plugin._set_state(PluginState.LOADED)

        self._plugins[name] = plugin_info
        self._update_plugin_order()
        logger.debug(f"Registered plugin: {name} v{version}")

    def register_class(
        self,
        name: str,
        plugin_class: Type[Any],
        version: str = "unknown",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a plugin class (lazy loading) with enhanced metadata."""
        # Try to get static information from class
        dependencies = []
        priority = PluginPriority.NORMAL

        # Check if class has static dependency/priority information
        if hasattr(plugin_class, "_dependencies"):
            dependencies = plugin_class._dependencies
        if hasattr(plugin_class, "_priority"):
            priority = plugin_class._priority

        plugin_info = PluginInfo(
            name=name,
            version=version,
            plugin_class=plugin_class,
            state=PluginState.UNLOADED,
            dependencies=dependencies,
            priority=priority,
            config=config or {},
        )
        self._plugins[name] = plugin_info
        self._update_plugin_order()
        logger.debug(f"Registered plugin class: {name} v{version}")

    def _update_plugin_order(self) -> None:
        """Update plugin loading order based on dependencies and priorities."""
        # Simple topological sort based on dependencies
        # This is a basic implementation - for production consider using a proper graph library
        ordered = []
        visited = set()
        temp_visited = set()

        def visit(plugin_name: str) -> None:
            if plugin_name in temp_visited:
                logger.warning(f"Circular dependency detected involving {plugin_name}")
                return
            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            if plugin_name in self._plugins:
                for dep in self._plugins[plugin_name].dependencies:
                    if dep.name in self._plugins and not dep.optional:
                        visit(dep.name)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            ordered.append(plugin_name)

        # Sort by priority first, then apply topological ordering
        plugin_names = sorted(
            self._plugins.keys(),
            key=lambda x: self._plugins[x].priority.value,
            reverse=True,
        )

        for name in plugin_names:
            visit(name)

        self._plugin_order = ordered

    def get(self, name: str) -> Any:
        """Get a plugin instance, loading if necessary."""
        if not self._discovered:
            self._discover_plugins()

        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' is not registered")

        plugin_info = self._plugins[name]
        return plugin_info.load(self._hooks)

    def get_info(self, name: str) -> PluginInfo:
        """Get plugin information without loading."""
        if not self._discovered:
            self._discover_plugins()

        if name not in self._plugins:
            raise ValueError(f"Plugin '{name}' is not registered")

        return self._plugins[name]

    def activate_plugin(self, name: str) -> None:
        """Load and activate a plugin."""
        plugin_info = self.get_info(name)
        if plugin_info.state != PluginState.LOADED:
            plugin_info.load(self._hooks)
        plugin_info.activate(self._hooks)

    def deactivate_plugin(self, name: str) -> None:
        """Deactivate a plugin."""
        plugin_info = self.get_info(name)
        plugin_info.deactivate(self._hooks)

    def unload_plugin(self, name: str) -> None:
        """Unload a plugin."""
        plugin_info = self.get_info(name)
        plugin_info.unload(self._hooks)

    def get_active_plugins(self) -> List[PluginInfo]:
        """Get list of active plugins in execution order."""
        if not self._discovered:
            self._discover_plugins()

        active = [
            self._plugins[name]
            for name in self._plugin_order
            if name in self._plugins and self._plugins[name].state == PluginState.ACTIVE
        ]
        return active

    def get_plugins_by_state(self, state: PluginState) -> List[PluginInfo]:
        """Get plugins filtered by state."""
        if not self._discovered:
            self._discover_plugins()

        return [
            plugin_info
            for plugin_info in self._plugins.values()
            if plugin_info.state == state
        ]

    def validate_all_dependencies(self) -> Dict[str, List[str]]:
        """Validate dependencies for all plugins. Returns dict of plugin_name -> missing_deps."""
        if not self._discovered:
            self._discover_plugins()

        results = {}
        for name, plugin_info in self._plugins.items():
            missing = plugin_info.check_dependencies()
            if missing:
                results[name] = missing

        return results

    def names(self) -> List[str]:
        """Get list of available plugin names in execution order."""
        if not self._discovered:
            self._discover_plugins()

        return self._plugin_order.copy()

    def list_plugins(self) -> List[PluginInfo]:
        """Get list of all plugin info in execution order."""
        if not self._discovered:
            self._discover_plugins()

        return [
            self._plugins[name] for name in self._plugin_order if name in self._plugins
        ]

    def process_with_plugins(
        self, data: Dict[str, Any], plugin_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process data through active plugins in dependency order."""
        if plugin_names is None:
            # Use all active plugins
            active_plugins = self.get_active_plugins()
        else:
            # Use specified plugins, but respect dependency order
            active_plugins = []
            for name in self._plugin_order:
                if name in plugin_names and name in self._plugins:
                    plugin_info = self._plugins[name]
                    if plugin_info.state == PluginState.ACTIVE:
                        active_plugins.append(plugin_info)

        result = data.copy()
        for plugin_info in active_plugins:
            try:
                if plugin_info.instance:
                    result = plugin_info.instance.process(result)
                    logger.debug(f"Processed data with plugin: {plugin_info.name}")
            except Exception as e:
                logger.error(f"Plugin {plugin_info.name} processing failed: {e}")
                # Continue with other plugins rather than failing entirely

        return result

    def _discover_plugins(self) -> None:
        """Discover plugins via entry points with enhanced dependency tracking."""
        if self._discovered:
            return

        logger.debug("Discovering plugins via entry points...")

        if not HAS_ENTRY_POINTS:
            logger.warning("Entry points not available, skipping plugin discovery")
            self._discovered = True
            return

        try:
            # Discover plugins from entry points
            if hasattr(_entry_points, "select"):  # Python 3.10+
                gfl_plugins = _entry_points.select(group="gfl.plugins")
            else:  # Python 3.8-3.9
                all_entry_points = _entry_points()
                # Handle both dict-like and list-like entry points APIs
                if hasattr(all_entry_points, 'get'):
                    gfl_plugins = all_entry_points.get("gfl.plugins", [])
                else:
                    # For newer versions where entry_points() returns a different type
                    gfl_plugins = []
                    try:
                        for group in all_entry_points:
                            if group.group == "gfl.plugins":
                                gfl_plugins.append(group)
                    except AttributeError:
                        # Fallback: no entry points found
                        gfl_plugins = []

            for ep in gfl_plugins:
                try:
                    plugin_class = ep.load()

                    # Try to get version from plugin or package
                    plugin_version = "unknown"
                    if hasattr(plugin_class, "version"):
                        plugin_version = plugin_class.version
                    elif hasattr(plugin_class, "__version__"):
                        plugin_version = plugin_class.__version__
                    else:
                        # Try to get version from package
                        try:
                            # Extract package name from entry point
                            pkg_name = ep.value.split(":")[0].split(".")[0]
                            plugin_version = version(pkg_name)
                        except Exception:
                            pass

                    self.register_class(ep.name, plugin_class, plugin_version)
                    logger.debug(f"Discovered plugin via entry point: {ep.name}")

                except Exception as e:
                    logger.warning(f"Failed to load plugin {ep.name}: {e}")

        except Exception as e:
            logger.error(f"Plugin discovery failed: {e}")

        # Auto-register built-in plugins
        self._try_autoregister_builtin()

        # Update plugin order after all discoveries
        self._update_plugin_order()

        # Log discovery summary
        self._log_discovery_summary()

        self._discovered = True

    def _log_discovery_summary(self) -> None:
        """Log summary of plugin discovery results."""
        total_plugins = len(self._plugins)

        logger.info(f"Plugin discovery complete: {total_plugins} plugins found")

        # Skip dependency validation here to avoid recursion
        # Dependencies will be validated when plugins are actually used

    def _try_autoregister_builtin(self) -> None:
        """Auto-register built-in demo plugins with dependency checking."""
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

                # Get version from module if available
                plugin_version = "built-in"
                if hasattr(module, "__version__"):
                    plugin_version = module.__version__
                elif hasattr(plugin_class, "version"):
                    plugin_version = plugin_class.version

                # Register as class for lazy loading
                self.register_class(name, plugin_class, plugin_version)
                logger.debug(f"Auto-registered built-in plugin: {name}")

            except Exception as e:
                logger.debug(f"Could not auto-register {name}: {e}")

    def reload_plugins(self) -> None:
        """Force reload of all plugins with proper cleanup."""
        logger.info("Reloading all plugins...")

        # Unload all plugins first
        for plugin_info in self._plugins.values():
            try:
                plugin_info.unload(self._hooks)
            except Exception as e:
                logger.warning(f"Error unloading plugin {plugin_info.name}: {e}")

        # Clear registry state
        self._discovered = False
        self._plugins.clear()
        self._plugin_order.clear()

        # Rediscover
        self._discover_plugins()

        logger.info("Plugin reload complete")


# Enhanced plugin registry instance
plugin_registry = _Registry()


# Convenience functions
def get_plugin(name: str) -> Any:
    """Get a plugin by name."""
    return plugin_registry.get(name)


def list_plugins() -> List[PluginInfo]:
    """List all available plugins."""
    return plugin_registry.list_plugins()


def get_active_plugins() -> List[PluginInfo]:
    """Get list of active plugins."""
    return plugin_registry.get_active_plugins()


def activate_plugin(name: str) -> None:
    """Activate a plugin by name."""
    plugin_registry.activate_plugin(name)


def deactivate_plugin(name: str) -> None:
    """Deactivate a plugin by name."""
    plugin_registry.deactivate_plugin(name)


def process_with_plugins(
    data: Dict[str, Any], plugin_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Process data through plugins."""
    return plugin_registry.process_with_plugins(data, plugin_names)


def validate_plugin_dependencies() -> Dict[str, List[str]]:
    """Validate all plugin dependencies."""
    return plugin_registry.validate_all_dependencies()


def add_lifecycle_hook(hook: PluginLifecycleHook) -> None:
    """Add a plugin lifecycle hook."""
    plugin_registry.add_lifecycle_hook(hook)


def discover_plugins() -> None:
    """Force plugin discovery."""
    plugin_registry._discover_plugins()


def register_plugin(
    name: str,
    plugin: Any,
    version: str = "unknown",
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Register a plugin."""
    plugin_registry.register(name, plugin, version, config)


def register_plugin_class(
    name: str,
    plugin_class: Type[Any],
    version: str = "unknown",
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Register a plugin class for lazy loading."""
    plugin_registry.register_class(name, plugin_class, version, config)


__all__ = [
    # Core classes
    "plugin_registry",
    "GFLPlugin",
    "EnhancedGFLPlugin",
    "BaseGFLPlugin",
    "PluginInfo",
    "PluginLifecycleHook",
    # Enums and data classes
    "PluginState",
    "PluginPriority",
    "PluginDependency",
    # Convenience functions
    "get_plugin",
    "list_plugins",
    "get_active_plugins",
    "activate_plugin",
    "deactivate_plugin",
    "process_with_plugins",
    "validate_plugin_dependencies",
    "add_lifecycle_hook",
    "discover_plugins",
    "register_plugin",
    "register_plugin_class",
]
