#!/usr/bin/env python3
"""
Test script to verify plugin discovery
"""

import json

import requests


def test_plugin_discovery():
    """Test if the biopython_tools plugin is discovered by the service"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/v2/plugins")
        if response.status_code == 200:
            plugins_data = response.json()
            plugins = plugins_data.get("plugins", [])

            print("Available plugins:")
            for plugin in plugins:
                print(f"  - {plugin['name']} (v{plugin['version']})")

            # Check if our plugin is in the list
            biopython_plugin = next((p for p in plugins if p["name"] == "biopython_tools"), None)
            if biopython_plugin:
                print(f"\n✓ biopython_tools plugin found: {biopython_plugin}")
                return True
            else:
                print("\n✗ biopython_tools plugin not found in the list")
                return False
        else:
            print(f"Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to service: {e}")
        return False


if __name__ == "__main__":
    test_plugin_discovery()
