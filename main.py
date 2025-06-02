import sys
from gfl import parser
from gfl.semantic_validator import validate_node

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo.gfl>")
        sys.exit(1)

    gfl_path = sys.argv[1]

    try:
        with open(gfl_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"❌ No se pudo abrir el archivo: {gfl_path}")
        sys.exit(1)

    result = parser.parser.parse(code)

    print("✅ AST generado:")
    print(result)

    print("\n🔎 Validación semántica:")
    errors = validate_node(result)
    if errors:
        print("❌ Errores encontrados:")
        for e in errors:
            print(" -", e)
    else:
        print("✅ Validación semántica correcta.")

if __name__ == "__main__":
    main()
