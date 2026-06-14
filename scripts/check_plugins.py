#!/usr/bin/env python3
"""Script to check available plugins."""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and initialize
from gfl.plugins.plugin_registry import plugin_registry

# Force discovery
plugin_registry._discover_plugins()

# List plugins
plugins = plugin_registry.list_plugins()
print("Available plugins:")
for plugin in plugins:
    print(f"  - {plugin.name} (v{plugin.version}) - State: {plugin.state.value}")

# Try to get specific plugins
try:
    ontarget = plugin_registry.get("ontarget_scorer")
    print(f"Successfully loaded ontarget_scorer: {ontarget}")
except Exception as e:
    print(f"Failed to load ontarget_scorer: {e}")

try:
    offtarget = plugin_registry.get("offtarget_scorer")
    print(f"Successfully loaded offtarget_scorer: {offtarget}")
except Exception as e:
    print(f"Failed to load offtarget_scorer: {e}")

try:
    crispr_eval = plugin_registry.get("crispr_evaluator")
    print(f"Successfully loaded crispr_evaluator: {crispr_eval}")
except Exception as e:
    print(f"Failed to load crispr_evaluator: {e}")
