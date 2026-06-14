import json
import os


def validate_with_rules(ast):
    rules_path = os.path.join(os.path.dirname(__file__), "rules.json")
    try:
        with open(rules_path, encoding="utf-8-sig") as f:
            rules = json.load(f)
    except FileNotFoundError:
        rules = {}

    for entry in ast:
        operation, args = entry
        op_rules = rules.get(operation, {})
        for key, expected in op_rules.items():
            if key not in args:
                print(f"❌ Missing argument '{key}' in {operation}.")
                return False
            if isinstance(expected, list) and args[key] not in expected:
                print(f"❌ Invalid value for '{key}' in {operation}: {args[key]}. Expected: {expected}")
                return False
    return True
