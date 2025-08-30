"""Tests for enhanced plugin system with dependencies and lifecycle hooks."""

import pytest
from typing import Dict, Any, List

from gfl.plugins.plugin_registry import (
    plugin_registry,
    BaseGFLPlugin,
    PluginInfo,
    PluginState,
    PluginPriority,
    PluginDependency,
    get_plugin,
    activate_plugin,
    process_with_plugins,
    validate_plugin_dependencies,
    add_lifecycle_hook,
)


class MockPlugin(BaseGFLPlugin):
    """Mock plugin for testing."""

    def __init__(
        self,
        name: str = "mock",
        version: str = "1.0.0",
        priority: PluginPriority = PluginPriority.NORMAL,
        dependencies: List[PluginDependency] = None,
    ):
        super().__init__()
        self._name = name
        self._version = version
        self._priority = priority
        self._dependencies = dependencies or []
        self.load_called = False
        self.unload_called = False
        self.activate_called = False
        self.deactivate_called = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def priority(self) -> PluginPriority:
        return self._priority

    @property
    def dependencies(self) -> List[PluginDependency]:
        return self._dependencies

    def on_load(self) -> None:
        self.load_called = True

    def on_unload(self) -> None:
        self.unload_called = True

    def on_activate(self) -> None:
        self.activate_called = True

    def on_deactivate(self) -> None:
        self.deactivate_called = True

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = data.copy()
        result[f"processed_by_{self.name}"] = True
        return result


class TestPluginDependency:
    """Test plugin dependency checking."""

    def test_dependency_satisfied_import_available(self):
        """Test dependency satisfaction when import is available."""
        dep = PluginDependency("sys")  # sys is always available
        assert dep.is_satisfied()

    def test_dependency_not_satisfied_import_unavailable(self):
        """Test dependency not satisfied when import unavailable."""
        dep = PluginDependency("nonexistent_package_12345")
        assert not dep.is_satisfied()

    def test_optional_dependency_not_satisfied(self):
        """Test optional dependency handling."""
        dep = PluginDependency("nonexistent_package_12345", optional=True)
        assert dep.is_satisfied()  # Optional deps are always "satisfied"

    def test_version_spec_satisfied(self):
        """Test version specification checking."""
        # This is a basic test - in practice you'd need packaging library
        PluginDependency("sys", ">=1.0.0")
        # We can't easily test version checking without mocking
        # In a real test, you'd mock the version() function


class TestPluginInfo:
    """Test enhanced PluginInfo functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_plugin = MockPlugin()
        self.plugin_info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            plugin_class=MockPlugin,
        )

    def test_plugin_info_initialization(self):
        """Test PluginInfo initialization."""
        assert self.plugin_info.name == "test_plugin"
        assert self.plugin_info.version == "1.0.0"
        assert self.plugin_info.state == PluginState.UNLOADED
        assert not self.plugin_info.is_loaded

    def test_plugin_load_success(self):
        """Test successful plugin loading."""
        instance = self.plugin_info.load()

        assert self.plugin_info.is_loaded
        assert self.plugin_info.state == PluginState.LOADED
        assert instance is not None
        assert instance.load_called

    def test_plugin_load_with_dependencies_missing(self):
        """Test plugin loading with missing dependencies."""
        dep = PluginDependency("nonexistent_package_12345", optional=False)
        self.plugin_info.dependencies = [dep]

        with pytest.raises(RuntimeError, match="Missing dependencies"):
            self.plugin_info.load()

        assert self.plugin_info.state == PluginState.ERROR

    def test_plugin_activate_deactivate(self):
        """Test plugin activation and deactivation."""
        # Load first
        instance = self.plugin_info.load()

        # Activate
        self.plugin_info.activate()
        assert self.plugin_info.state == PluginState.ACTIVE
        assert instance.activate_called

        # Deactivate
        self.plugin_info.deactivate()
        assert self.plugin_info.state == PluginState.LOADED
        assert instance.deactivate_called

    def test_plugin_unload(self):
        """Test plugin unloading."""
        instance = self.plugin_info.load()

        self.plugin_info.unload()
        assert self.plugin_info.state == PluginState.UNLOADED
        assert instance.unload_called
        assert self.plugin_info.instance is None


class TestEnhancedRegistry:
    """Test enhanced plugin registry functionality."""

    def setup_method(self):
        """Set up clean registry for each test."""
        # Clear the global registry
        plugin_registry._plugins.clear()
        plugin_registry._plugin_order.clear()
        plugin_registry._hooks.clear()
        plugin_registry._discovered = False

    def test_register_plugin_with_priority(self):
        """Test plugin registration with priority."""
        high_priority = MockPlugin("high", priority=PluginPriority.HIGH)
        low_priority = MockPlugin("low", priority=PluginPriority.LOW)

        plugin_registry.register("high", high_priority)
        plugin_registry.register("low", low_priority)

        names = plugin_registry.names()
        # High priority plugins should come first in execution order
        assert names.index("high") < names.index("low")

    def test_plugin_dependency_ordering(self):
        """Test plugin ordering based on dependencies."""
        # Create plugins with dependencies
        base_plugin = MockPlugin("base")
        dependent_plugin = MockPlugin(
            "dependent", dependencies=[PluginDependency("base", optional=False)]
        )

        plugin_registry.register("base", base_plugin)
        plugin_registry.register("dependent", dependent_plugin)

        names = plugin_registry.names()
        # Base plugin should come before dependent plugin
        assert names.index("base") < names.index("dependent")

    def test_lifecycle_hooks(self):
        """Test plugin lifecycle hooks."""
        hook_calls = []

        def test_hook(plugin_name: str, state: PluginState, **kwargs):
            hook_calls.append((plugin_name, state))

        add_lifecycle_hook(test_hook)

        # Register and activate a plugin
        mock_plugin = MockPlugin("test")
        plugin_registry.register("test", mock_plugin)
        activate_plugin("test")

        # Check hook was called
        assert len(hook_calls) >= 2  # At least for LOADING and ACTIVE states
        assert ("test", PluginState.LOADED) in hook_calls
        assert ("test", PluginState.ACTIVE) in hook_calls

    def test_process_with_plugins(self):
        """Test data processing through multiple plugins."""
        plugin1 = MockPlugin("plugin1", priority=PluginPriority.HIGH)
        plugin2 = MockPlugin("plugin2", priority=PluginPriority.LOW)

        plugin_registry.register("plugin1", plugin1)
        plugin_registry.register("plugin2", plugin2)

        activate_plugin("plugin1")
        activate_plugin("plugin2")

        data = {"original": True}
        result = process_with_plugins(data)

        # Both plugins should have processed the data
        assert result["processed_by_plugin1"]
        assert result["processed_by_plugin2"]
        assert result["original"]

    def test_validate_plugin_dependencies(self):
        """Test plugin dependency validation."""
        # Plugin with missing dependency
        bad_plugin = MockPlugin(
            "bad",
            dependencies=[
                PluginDependency("nonexistent_package_12345", optional=False)
            ],
        )

        # Plugin with satisfied dependency
        good_plugin = MockPlugin(
            "good",
            dependencies=[
                PluginDependency("sys", optional=False)  # sys is always available
            ],
        )

        plugin_registry.register("bad", bad_plugin)
        plugin_registry.register("good", good_plugin)

        issues = validate_plugin_dependencies()

        assert "bad" in issues
        assert "good" not in issues

    def test_get_plugins_by_state(self):
        """Test filtering plugins by state."""
        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")

        plugin_registry.register("plugin1", plugin1)
        plugin_registry.register("plugin2", plugin2)

        # Initially both should be loaded (registered plugins are loaded)
        loaded_plugins = plugin_registry.get_plugins_by_state(PluginState.LOADED)
        assert len(loaded_plugins) == 2

        # Activate one plugin
        activate_plugin("plugin1")

        active_plugins = plugin_registry.get_plugins_by_state(PluginState.ACTIVE)
        loaded_plugins = plugin_registry.get_plugins_by_state(PluginState.LOADED)

        assert len(active_plugins) == 1
        assert len(loaded_plugins) == 1
        assert active_plugins[0].name == "plugin1"
        assert loaded_plugins[0].name == "plugin2"


class TestPluginErrorHandling:
    """Test error handling in plugin system."""

    def setup_method(self):
        """Set up clean registry for each test."""
        plugin_registry._plugins.clear()
        plugin_registry._plugin_order.clear()
        plugin_registry._hooks.clear()
        plugin_registry._discovered = False

    def test_plugin_load_error(self):
        """Test error handling during plugin loading."""

        class FailingPlugin(BaseGFLPlugin):
            @property
            def name(self):
                return "failing"

            @property
            def version(self):
                return "1.0.0"

            def __init__(self):
                super().__init__()
                raise RuntimeError("Intentional failure")

            def process(self, data):
                return data

        plugin_registry.register_class("failing", FailingPlugin)

        with pytest.raises(RuntimeError):
            get_plugin("failing")

        plugin_info = plugin_registry.get_info("failing")
        assert plugin_info.state == PluginState.ERROR
        assert plugin_info.load_error is not None

    def test_plugin_processing_error_continues(self):
        """Test that plugin processing errors don't stop other plugins."""

        class FailingProcessPlugin(MockPlugin):
            def process(self, data):
                raise RuntimeError("Processing failed")

        failing_plugin = FailingProcessPlugin("failing")
        good_plugin = MockPlugin("good")

        plugin_registry.register("failing", failing_plugin)
        plugin_registry.register("good", good_plugin)

        activate_plugin("failing")
        activate_plugin("good")

        data = {"test": True}
        # Should not raise exception, but should continue processing with good plugin
        result = process_with_plugins(data)

        # Good plugin should have processed despite failing plugin
        assert result["processed_by_good"]
        assert "processed_by_failing" not in result
