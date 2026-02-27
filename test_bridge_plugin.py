"""Test script to check if the bridge editor plugin is registered."""

import sys
import os

# Add the parent directory to the path so we can import gfl modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the plugin registry
    from gfl.plugins.plugin_registry import plugin_registry
    
    # List all registered plugins
    plugins = plugin_registry.list_plugins()
    print("Available plugins:")
    for plugin in plugins:
        print(f"- {plugin.name} (version: {plugin.version})")
        
    # Check if our bridge editor plugin is registered
    bridge_plugin = None
    for plugin in plugins:
        if plugin.name == "bridge_editor":
            bridge_plugin = plugin
            break
            
    if bridge_plugin:
        print(f"\nBridge Editor plugin found!")
        print(f"Name: {bridge_plugin.name}")
        print(f"Version: {bridge_plugin.version}")
        print(f"Instance: {bridge_plugin.instance}")
        
        # Try to create an instance of the plugin
        if bridge_plugin.instance is None:
            print("Plugin instance is None, trying to load it...")
            try:
                plugin_instance = plugin_registry.get_plugin("bridge_editor")
                print(f"Plugin instance loaded: {plugin_instance}")
                print(f"Plugin name: {plugin_instance.name}")
            except Exception as e:
                print(f"Error loading plugin instance: {e}")
        else:
            print(f"Plugin instance already loaded: {bridge_plugin.instance}")
            print(f"Plugin name: {bridge_plugin.instance.name}")
    else:
        print("\nBridge Editor plugin NOT found in registry!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()