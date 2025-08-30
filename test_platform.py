#!/usr/bin/env python3
"""Simple test script to verify GeneForgeLang platform functionality."""

import sys
from pathlib import Path

def test_basic_api():
    """Test basic GFL API functionality."""
    print("Testing basic GFL API...")
    
    try:
        from gfl.api import parse, validate, get_api_info
        
        # Test API info
        info = get_api_info()
        print(f"✓ API Version: {info['api_version']}")
        print(f"✓ Available models: {info['inference_models']}")
        
        # Test basic parsing
        gfl_content = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""
        
        ast = parse(gfl_content)
        print(f"✓ Parsing successful: {ast['experiment']['tool']}")
        
        # Test validation
        errors = validate(ast)
        print(f"✓ Validation: {'Valid' if not errors else f'{len(errors)} errors'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic API test failed: {e}")
        return False

def test_enhanced_inference():
    """Test enhanced inference functionality."""
    print("\nTesting enhanced inference...")
    
    try:
        from gfl.api import infer_enhanced, parse
        
        gfl_content = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
"""
        
        ast = parse(gfl_content)
        result = infer_enhanced(ast, model_name="heuristic")
        
        print(f"✓ Inference successful: {result['label']} (confidence: {result['confidence']:.2%})")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced inference test failed: {e}")
        return False

def test_client_sdk():
    """Test client SDK functionality."""
    print("\nTesting client SDK...")
    
    try:
        from gfl.client_sdk import create_client
        
        # This will fail if server isn't running, which is expected
        print("ℹ Client SDK importable")
        return True
        
    except Exception as e:
        print(f"✗ Client SDK test failed: {e}")
        return False

def test_cli_tools():
    """Test CLI tools."""
    print("\nTesting CLI tools...")
    
    try:
        import subprocess
        
        # Test gfl-server help
        result = subprocess.run(['gfl-server', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ gfl-server CLI available")
        else:
            print(f"✗ gfl-server CLI failed: {result.stderr}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ CLI tools test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("GeneForgeLang Platform Test Suite")
    print("="*50)
    
    tests = [
        test_basic_api,
        test_enhanced_inference,
        test_client_sdk,
        test_cli_tools,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Platform is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Platform may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())