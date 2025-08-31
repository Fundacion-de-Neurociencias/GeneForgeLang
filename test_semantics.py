import json
import subprocess
import sys

from gfl import parser
from gfl.semantic_validator import validate_ast


def run_validation(file_path):
    print(f"\n🔎 Probando: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        code = f.read()

    ast = parser.parser.parse(code)
    if not ast:
        print("❌ AST nulo.")
        return

    print("✅ AST generado.")
    print("📤 AST:", ast)

    if validate_ast(ast):
        print("✅ Validación semántica OK.")
        with open("output_ast.json", "w", encoding="utf-8") as f:
            json.dump(ast, f, indent=2)
        subprocess.run(["python", "advanced_validator.py"], check=False)
    else:
        print("❌ Validación semántica FALLIDA.")


if len(sys.argv) > 1:
    run_validation(sys.argv[1])
else:
    run_validation("examples/test_valid_semantics.gfl")
    run_validation("examples/test_invalid_semantics.gfl")
