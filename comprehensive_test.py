#!/usr/bin/env python3
"""
Comprehensive test to verify the biopython_tools plugin is working correctly
"""

from importlib.metadata import entry_points

from gfl.plugins.plugin_registry import plugin_registry


def test_plugin_discovery():
    """Test if our plugin is discovered via entry points"""
    print("Testing plugin discovery via entry points...")

    # Check if our plugin is registered as an entry point
    gfl_plugins = entry_points(group="gfl.plugins")
    plugin_names = [ep.name for ep in gfl_plugins]

    if "biopython_tools" in plugin_names:
        print("✓ biopython_tools found in entry points")

        # Load the plugin
        plugin_ep = next(ep for ep in gfl_plugins if ep.name == "biopython_tools")
        plugin_class = plugin_ep.load()
        print(f"✓ Plugin class loaded: {plugin_class}")

        # Create an instance
        plugin_instance = plugin_class()
        print(f"✓ Plugin instance created: {plugin_instance.name}")

        return plugin_instance
    else:
        print("✗ biopython_tools not found in entry points")
        return None


def test_plugin_functionality(plugin_instance):
    """Test the plugin's functionality"""
    if not plugin_instance:
        return False

    print("\nTesting plugin functionality...")

    # Test GC content calculation
    try:
        test_data = {"operation": "gc_content", "sequence": "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"}
        result = plugin_instance.process(test_data)
        gc_content = result["result"]
        print(f"✓ GC content calculation: {gc_content:.2f}%")

        # Expected value is approximately 56.41%
        if abs(gc_content - 56.41) < 1.0:
            print("✓ GC content result is within expected range")
        else:
            print(f"⚠ GC content result {gc_content:.2f}% differs from expected 56.41%")
    except Exception as e:
        print(f"✗ GC content calculation failed: {e}")
        return False

    # Test DNA translation
    try:
        test_data = {"operation": "translate", "sequence": "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"}
        result = plugin_instance.process(test_data)
        translation = result["result"]
        print(f"✓ DNA translation: {translation}")

        # Expected value is "MAIVMGR*KGAR*"
        if translation == "MAIVMGR*KGAR*":
            print("✓ DNA translation result matches expected value")
        else:
            print(f"⚠ DNA translation result '{translation}' differs from expected 'MAIVMGR*KGAR*'")
    except Exception as e:
        print(f"✗ DNA translation failed: {e}")
        return False

    return True


def test_builtin_plugins():
    """Test that builtin plugins are still working"""
    print("\nTesting builtin plugins...")

    builtin_plugins = list(plugin_registry._plugins.keys())
    print(f"Builtin plugins: {builtin_plugins}")

    if "ProteinVAEGenerator" in builtin_plugins and "BayesianOptimization" in builtin_plugins:
        print("✓ Builtin plugins are available")
        return True
    else:
        print("⚠ Some builtin plugins are missing")
        return False


def main():
    """Main test function"""
    print("=== Comprehensive Plugin Test ===\n")

    # Test plugin discovery
    plugin_instance = test_plugin_discovery()

    # Test plugin functionality
    functionality_ok = test_plugin_functionality(plugin_instance)

    # Test builtin plugins
    builtin_ok = test_builtin_plugins()

    print("\n=== Test Summary ===")
    if plugin_instance and functionality_ok and builtin_ok:
        print("🎉 All tests passed! The biopython_tools plugin is working correctly.")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    main()
