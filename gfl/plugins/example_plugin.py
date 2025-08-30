"""Example plugin demonstrating enhanced GFL plugin features.

This plugin shows how to use:
- Dependencies
- Priority levels
- Lifecycle hooks
- Configuration validation
"""

from typing import Any, Dict, List

from .plugin_registry import BaseGFLPlugin, PluginDependency, PluginPriority


class ExampleAnalysisPlugin(BaseGFLPlugin):
    """Example plugin for data analysis with enhanced features."""

    @property
    def name(self) -> str:
        """Plugin name."""
        return "example_analysis"

    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"

    @property
    def priority(self) -> PluginPriority:
        """High priority plugin."""
        return PluginPriority.HIGH

    @property
    def dependencies(self) -> List[PluginDependency]:
        """Plugin dependencies."""
        return [
            PluginDependency("numpy", ">=1.20.0", optional=False, import_name="numpy"),
            PluginDependency("pandas", ">=1.3.0", optional=True, import_name="pandas"),
            PluginDependency("scipy", optional=True, import_name="scipy"),
        ]

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"Loading {self.name} plugin...")
        # Initialize resources, connections, etc.

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"Unloading {self.name} plugin...")
        # Cleanup resources, close connections, etc.

    def on_activate(self) -> None:
        """Called when plugin becomes active."""
        print(f"Activating {self.name} plugin...")

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        print(f"Deactivating {self.name} plugin...")

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration."""
        errors = []

        if "analysis_type" not in config:
            errors.append("Missing required 'analysis_type' configuration")

        if "threshold" in config:
            try:
                threshold = float(config["threshold"])
                if threshold < 0 or threshold > 1:
                    errors.append("threshold must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("threshold must be a number")

        return errors

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GFL data and return enhanced results."""
        print(f"Processing data with {self.name} plugin...")

        result = data.copy()

        # Add analysis results
        result["analysis"] = {
            "plugin": self.name,
            "version": self.version,
            "processed_at": "2023-01-01T00:00:00Z",  # In real plugin, use current timestamp
            "status": "success",
        }

        # Example analysis logic
        if "experiment" in data:
            experiment = data["experiment"]
            if experiment.get("type") == "gene_editing":
                result["analysis"]["recommendations"] = [
                    "Consider increasing replication count",
                    "Validate guide RNA specificity",
                    "Monitor off-target effects",
                ]
                result["analysis"]["risk_score"] = 0.3

        return result


class LowPriorityPlugin(BaseGFLPlugin):
    """Example low-priority plugin for demonstrating plugin ordering."""

    @property
    def name(self) -> str:
        return "low_priority_example"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def priority(self) -> PluginPriority:
        """Low priority plugin - runs after others."""
        return PluginPriority.LOW

    @property
    def dependencies(self) -> List[PluginDependency]:
        """Depends on the example analysis plugin."""
        return [
            PluginDependency("example_analysis", optional=False),
        ]

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add supplementary processing."""
        result = data.copy()

        if "analysis" not in result:
            result["analysis"] = {}

        result["analysis"]["supplementary"] = {
            "plugin": self.name,
            "note": "Additional processing completed",
        }

        return result
