"""Test script to check if the bridge editor plugin is registered."""

import os
import sys

# Add the parent directory to the path so we can import gfl modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the plugin registry
    from geneforgelang.plugins.plugin_registry import plugin_registry

    # List all registered plugins
    plugins = plugin_registry.list_plugins()
    print("Available plugins:")
    for plugin_name in plugins:
        print(f"- {plugin_name}")

    # Check if our bridge editor plugin is registered
    bridge_plugin_name = None
    if "bridge_editor" in plugins:
        bridge_plugin_name = "bridge_editor"

    if bridge_plugin_name:
        print(f"\nBridge Editor plugin is registered with name: {bridge_plugin_name}")

        # Try to create an instance of the plugin
        try:
            plugin_instance = plugin_registry.get_plugin("bridge_editor")
            print(f"Plugin instance loaded: {plugin_instance}")
            if hasattr(plugin_instance, "name"):
                print(f"Plugin name: {plugin_instance.name}")
            if hasattr(plugin_instance, "version"):
                print(f"Plugin version: {plugin_instance.version}")
        except Exception as e:
            print(f"Error loading plugin instance: {e}")
    else:
        print("\nBridge Editor plugin NOT found in registry!")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
