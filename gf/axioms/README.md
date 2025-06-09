# Axiom Inference Module (Experimental)

This module tracks high-frequency reasoning events (from LLM↔GFL interaction) and promotes them to axioms when thresholds are met.

## Files
- `axiom_tracker.py`: Tracks events and decides promotion.
- `axiom_store.json`: Persistent store of axioms.
- `axiom_utils.py`: Utility functions.

## Usage
```python
from gf.axioms.axiom_tracker import add_event, promote_axioms_to_store

add_event("simulate(cell_death)", weight=1.0)
promote_axioms_to_store(threshold=5, weight_threshold=3.0)


---

## ✅ PASO 2. Actualizar el `README.md` de la raíz del proyecto

```bash
echo "" >> README.md
echo "### 🧠 Axiom Inference Engine (Experimental)" >> README.md
echo "" >> README.md
echo "The \`gf/axioms/\` module tracks recurrent patterns during GFL parsing and reasoning." >> README.md
echo "After a configurable threshold, patterns are promoted to axioms and persisted in \`axiom_store.json\`." >> README.md
echo "" >> README.md
echo "Example axiom:" >> README.md
echo "" >> README.md
echo '\`\`\`json' >> README.md
echo '{' >> README.md
echo '  "axiom": "simulate(cell_death)",' >> README.md
echo '  "count": 9,' >> README.md
echo '  "weight": 7.2,' >> README.md
echo '  "confidence": 0.88' >> README.md
echo '}' >> README.md
echo '\`\`\`' >> README.md

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Fundación de Neurociencias

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software...

[... resto del MIT ...]

This repository includes a module for probabilistic axiom inference.
All code, including `gf/axioms/`, remains under the MIT License.
