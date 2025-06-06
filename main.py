﻿import sys
from gfl import parser
from gfl.semantic_validator import validate

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

    print("\n🔍 Validación semántica:")
    valid = validate(result)
    if not valid:
        print("❌ Validación fallida.")
        sys.exit(2)

if __name__ == "__main__":
    main()
