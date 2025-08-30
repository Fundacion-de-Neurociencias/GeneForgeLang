import os

from gf.axioms.axiom_utils import load_axiom_store
from gfl import parser
from gfl.axiom_hooks import register_axiom_candidates

example_path = os.path.join("gfl", "examples", "example1.gfl")
with open(example_path, "r", encoding="utf-8") as f:
    source = f.read()

# Parsear el archivo usando el parser de GFL
ast = parser.parser.parse(source)

print("🧠 AST generado:\n", ast)

# Registrar axiomas desde el AST
register_axiom_candidates(ast)

print("\n📘 Axiomas actuales:")
store = load_axiom_store()
for k, v in store.items():
    print(f"- {k} → {v}")
