import json
from pathlib import Path


def validate_with_rules(ast):
    rules_path = Path(__file__).resolve().parent.parent.parent / "rules.json"
    with open(rules_path, encoding="utf-8-sig") as f:
        rules = json.load(f)

    for entry in ast:
        operation, args = entry
        op_rules = rules.get(operation, {})
        for key, expected in op_rules.items():
            if key not in args:
                print(f"❌ Falta el argumento '{key}' en {operation}.")
                return False
            if isinstance(expected, list) and args[key] not in expected:
                print(f"❌ Valor inválido para '{key}' en {operation}: {args[key]}. Esperado: {expected}")
                return False
    return True
