"""Automatic plugin registration for GeneForgeLang.

This module provides automatic registration of built-in example plugins
to ensure they are available when using the GFL API.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def auto_register_example_plugins() -> None:
    """Automatically register example plugins if they are available."""
    try:
        # Try to import and register example plugins
        from .example_implementations import register_example_plugins

        register_example_plugins()
        logger.info("Successfully auto-registered example plugins")
    except ImportError as e:
        logger.debug(f"Example plugins not available for auto-registration: {e}")

    # Always try to register the genesis project plugins directly
    try:
        _register_genesis_plugins()
    except Exception as ex:
        logger.warning(f"Failed to auto-register genesis plugins: {ex}")


def _register_genesis_plugins() -> None:
    """Register genesis project plugins directly."""
    # Add the examples directory to the path
    examples_path = Path(__file__).parent.parent.parent / "examples" / "gfl-genesis" / "plugins"
    logger.info(f"Looking for genesis plugins at: {examples_path}")
    if examples_path.exists():
        sys.path.insert(0, str(examples_path))
        logger.info("Added examples path to sys.path")

    # Try to register the on-target scorer plugin
    try:
        # Dynamically import the plugin class
        import importlib.util

        from gfl.plugins.plugin_registry import register_plugin_class

        plugin_path = examples_path / "gfl-plugin-ontarget-scorer" / "gfl_plugin_ontarget_scorer" / "plugin.py"
        logger.info(f"Looking for on-target plugin at: {plugin_path}")
        if plugin_path.exists():
            spec = importlib.util.spec_from_file_location("ontarget_plugin", plugin_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                OnTargetScorerPlugin = module.OnTargetScorerPlugin
                register_plugin_class("ontarget_scorer", OnTargetScorerPlugin, "0.1.0", {})
                logger.info("Registered on-target scorer plugin")
    except Exception as e:
        logger.error(f"Could not register on-target scorer plugin: {e}")
        import traceback

        logger.error(traceback.format_exc())

    # Try to register the off-target scorer plugin
    try:
        # Dynamically import the plugin class
        import importlib.util

        from gfl.plugins.plugin_registry import register_plugin_class

        plugin_path = examples_path / "gfl-plugin-offtarget-scorer" / "gfl_plugin_offtarget_scorer" / "plugin.py"
        logger.info(f"Looking for off-target plugin at: {plugin_path}")
        if plugin_path.exists():
            spec = importlib.util.spec_from_file_location("offtarget_plugin", plugin_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                OffTargetScorerPlugin = module.OffTargetScorerPlugin
                register_plugin_class("offtarget_scorer", OffTargetScorerPlugin, "0.1.0", {})
                logger.info("Registered off-target scorer plugin")
    except Exception as e:
        logger.error(f"Could not register off-target scorer plugin: {e}")
        import traceback

        logger.error(traceback.format_exc())

    # Try to register the CRISPR evaluator plugin
    try:
        # Dynamically import the plugin class
        import importlib.util

        from gfl.plugins.plugin_registry import register_plugin_class

        plugin_path = examples_path / "gfl-crispr-evaluator" / "gfl_crispr_evaluator" / "plugin.py"
        logger.info(f"Looking for CRISPR evaluator plugin at: {plugin_path}")
        if plugin_path.exists():
            spec = importlib.util.spec_from_file_location("crispr_evaluator_plugin", plugin_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                CRISPREvaluatorPlugin = module.CRISPREvaluatorPlugin
                register_plugin_class("crispr_evaluator", CRISPREvaluatorPlugin, "0.1.0", {})
                logger.info("Registered CRISPR evaluator plugin")
    except Exception as e:
        logger.error(f"Could not register CRISPR evaluator plugin: {e}")
        import traceback

        logger.error(traceback.format_exc())


def get_available_plugins_info() -> Dict[str, Any]:
    """Get information about available plugins."""
    try:
        from .interfaces import get_available_generators, get_available_optimizers

        generators = get_available_generators()
        optimizers = get_available_optimizers()

        return {
            "generators": list(generators.keys()),
            "optimizers": list(optimizers.keys()),
            "total_generators": len(generators),
            "total_optimizers": len(optimizers),
        }
    except Exception as e:
        logger.warning(f"Failed to get plugin information: {e}")
        return {"generators": [], "optimizers": [], "total_generators": 0, "total_optimizers": 0}


# Auto-register plugins when this module is imported
auto_register_example_plugins()
