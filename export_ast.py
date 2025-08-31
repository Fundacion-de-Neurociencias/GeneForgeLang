import json
import sys

from gfl import parser
from gfl.semantic_validator import validate_ast


def run_export(file_path):
    print(f"\n📤 Exportando AST de: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
    ast = parser.parser.parse(code)
    if not ast:
        print("❌ AST nulo.")
        return
    print("✅ AST generado.")
    if validate_ast(ast):
        print("✅ Validación semántica OK.")
        with open("output_ast.json", "w", encoding="utf-8") as out:
            json.dump(ast, out, indent=2)
        print("📁 AST exportado a output_ast.json")
    else:
        print("❌ Validación semántica FALLIDA.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_export(sys.argv[1])
    else:
        print("⚠️ Proporcione el archivo .gfl a procesar")
