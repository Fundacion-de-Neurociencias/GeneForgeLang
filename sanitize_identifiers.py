import re
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    content = f.read()

# Reemplaza MT-ND1 por MT_ND1 y similares
content = re.sub(r"([a-zA-Z]+)-([a-zA-Z0-9]+)", r"\1_\2", content)

with open(sys.argv[1], "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Identificadores sanitizados (guiones → underscores)")
