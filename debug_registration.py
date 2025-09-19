#!/usr/bin/env python3
"""Debug script for plugin registration."""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test plugin registration
examples_path = Path(__file__).parent / "examples" / "gfl-genesis" / "plugins"
print(f"Examples path exists: {examples_path.exists()}")
if examples_path.exists():
    print(f"Contents of examples path: {list(examples_path.iterdir())}")

# Try to import the on-target scorer plugin directly
plugin_path = examples_path / "gfl-plugin-ontarget-scorer" / "gfl_plugin_ontarget_scorer" / "plugin.py"
print(f"On-target plugin path exists: {plugin_path.exists()}")

if plugin_path.exists():
    import importlib.util

    spec = importlib.util.spec_from_file_location("ontarget_plugin", plugin_path)
    if spec is not None and spec.loader is not None:
        print("Successfully created spec")
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("Successfully loaded module")
            OnTargetScorerPlugin = module.OnTargetScorerPlugin
            print(f"Successfully got plugin class: {OnTargetScorerPlugin}")

            # Try to instantiate
            plugin_instance = OnTargetScorerPlugin()
            print(f"Successfully instantiated plugin: {plugin_instance}")
            print(f"Plugin name: {plugin_instance.name}")
        except Exception as e:
            print(f"Error loading plugin: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("Failed to create spec")
else:
    print("Plugin file not found")

# Check the auto_register module
auto_register_path = Path(__file__).parent / "gfl" / "plugins" / "auto_register.py"
print(f"Auto-register path exists: {auto_register_path.exists()}")

if auto_register_path.exists():
    try:
        from gfl.plugins.auto_register import auto_register_example_plugins

        print("Successfully imported auto_register")
        auto_register_example_plugins()
        print("Called auto_register_example_plugins")
    except Exception as e:
        print(f"Error importing/running auto_register: {e}")
        import traceback

        traceback.print_exc()
