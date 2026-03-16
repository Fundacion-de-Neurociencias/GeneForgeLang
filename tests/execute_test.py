#!/usr/bin/env python3
"""
Test script to execute a GFL script through the service
"""

import json

import requests


def test_gfl_execution():
    """Test executing a GFL script through the service"""
    # Read the GFL script
    with open("test_biopython_plugin.gfl") as f:
        gfl_code = f.read()

    # Parse the GFL code
    try:
        parse_response = requests.post("http://127.0.0.1:8000/api/v2/parse", json={"code": gfl_code})

        if parse_response.status_code != 200:
            print(f"Parse error: HTTP {parse_response.status_code}")
            print(parse_response.text)
            return False

        parse_result = parse_response.json()
        if not parse_result.get("success"):
            print(f"Parse failed: {parse_result.get('message')}")
            return False

        ast = parse_result.get("ast")
        print("✓ GFL code parsed successfully")

        # Execute the AST
        execute_response = requests.post("http://127.0.0.1:8000/api/v2/execute", json={"ast": ast})

        if execute_response.status_code != 200:
            print(f"Execute error: HTTP {execute_response.status_code}")
            print(execute_response.text)
            return False

        execute_result = execute_response.json()
        if not execute_result.get("success"):
            print(f"Execute failed: {execute_result.get('message')}")
            return False

        result = execute_result.get("result")
        print("✓ GFL code executed successfully")
        print(f"Result: {json.dumps(result, indent=2)}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    test_gfl_execution()
