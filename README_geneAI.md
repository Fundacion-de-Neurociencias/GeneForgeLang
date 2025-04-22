# 🧬 GeneForgeLang + ProtGPT2 Integration

This repository demonstrates how to use **GeneForgeLang** symbolic expressions to guide the generation of realistic protein sequences using the **ProtGPT2** model.

---

## 📁 Files

- `generar_desde_frase.py`: Uses a fixed GeneForgeLang phrase to generate a seed and generate a protein.
- `generar_desde_frase_input.py`: Allows entering any GeneForgeLang phrase from the terminal.

---

## 🧪 How it works

1. GeneForgeLang phrase expresses your intention:
   ```
   ^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)
   ```

2. A small internal function maps that phrase to a **protein seed**:
   - `Dom(Kin)` → `"MKKK"`
   - `Mot(NLS)` → `"MPRRR"`
   - `*AcK` → `"MKQAK"`
   - `Localize(Nucleus)` → `"MPKRK"`
   - And others...

3. The `ProtGPT2` language model uses that seed to generate a **plausible protein sequence** that aligns with your design.

---

## ▶️ How to run

### Option A: Run the fixed script

```bash
python generar_desde_frase.py
```

This uses a default phrase and prints the generated protein.

---

### Option B: Run with your own phrase

```bash
python generar_desde_frase_input.py "^p:Dom(Kin)'-Mot(PEST)*P@120=Localize(Membrane)"
```

Replace the phrase with your own GeneForgeLang expression.

---

## 🔁 Extend the translator

The function `frase_a_semilla()` can be easily expanded to recognize new domains, motifs or logic from your language.

You can define biological behaviors with symbolic clarity and guide powerful generative models with them.

---

## 🧠 Why this matters

GeneForgeLang bridges:
- Symbolic design (human-readable, programmable)
- Generative AI (powerful, biological plausibility)
- Reproducible workflows (transparent input/output)

It empowers a new era of **semantic protein engineering**.

---

MIT License © Fundación de Neurociencias