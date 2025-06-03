import json
from collections import defaultdict

with open("output_ast.json", encoding="utf-8") as f:
    ast = json.load(f)

summary = defaultdict(list)
for op, args in ast:
    for k, v in args.items():
        summary[k].append(v)

print("📊 Resumen de argumentos en el AST:\n")
for key, values in summary.items():
    values = sorted(set(values))
    print(f"🔹 {key}: {', '.join(values)}")
