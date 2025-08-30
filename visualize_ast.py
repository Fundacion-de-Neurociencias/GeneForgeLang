import json

import pandas as pd

with open("output_ast.json", encoding="utf-8") as f:
    data = json.load(f)

table = []
for item in data:
    op, args = item
    row = {"operation": op}
    row.update(args)
    table.append(row)

df = pd.DataFrame(table)
print(df.to_string(index=False))
