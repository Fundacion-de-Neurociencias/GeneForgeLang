import os

from gf.axioms.axiom_utils import load_axiom_store

from geneforgelang.core.parser import parse_gfl

example_path = os.path.join("gfl", "examples", "example1.gfl")
with open(example_path, encoding="utf-8") as f:
    source = f.read()

# Parse the GFL file using the canonical parse_gfl function
ast = parse_gfl(source)

print("🧠 Generated AST:\n", ast)

# Register axioms from el AST
register_axiom_candidates(ast)

print("\n📘 Axiomas actuales:")
store = load_axiom_store()
for k, v in store.items():
    print(f"- {k} → {v}")
