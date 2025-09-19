import os
import re

lexer_path = os.path.join("gfl", "lexer.py")

if not os.path.isfile(lexer_path):
    print(f"[ERROR] No se encontró: {lexer_path}")
    exit(1)

with open(lexer_path, "r", encoding="utf-8") as f:
    code = f.read()

pattern = r"def t_STRING\(t\):\n\s+r\'\\\"([^\\\n]|(\\.))*?\\\"\'\n\s+t\.value = t\.value\[1:-1\]\n\s+return t"
replacement = (
    "def t_STRING(t):\n"
    "    r'(\\'([^\\\\\\n]|(\\\\.))*?\\'|\\\"([^\\\\\\n]|(\\\\.))*?\\\")'\n"
    "    t.value = t.value[1:-1]\n"
    "    return t"
)

new_code, count = re.subn(pattern, replacement, code)

if count == 0:
    print("[WARN] No se encontró la definición clásica de t_STRING. Revisión manual recomendada.")
else:
    with open(lexer_path, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("[OK] Se ha parcheado 't_STRING' para aceptar comillas simples y dobles.")
