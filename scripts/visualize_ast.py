import json

import pandas as pd

with open("output_ast.json", encoding="utf-8") as f:
    data = json.load(f)

table = []
for op, args in data.items():
    row = {"operation": op}
    row.update(args)
    table.append(row)

df = pd.DataFrame(table)
print(df.to_string(index=False))
