import json
import sys

from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator


def _validate_ast(ast: dict) -> bool:
    """Validate the AST using the canonical EnhancedSemanticValidator."""
    validator = EnhancedSemanticValidator()
    result = validator.validate_ast(ast)
    return result.is_valid


def run_export(file_path):
    print(f"\n📤 Exporting AST from: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
    ast = parse_gfl(code)
    if not ast:
        print("❌ AST nulo.")
        return
    print("✅ AST generado.")
    if _validate_ast(ast):
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
