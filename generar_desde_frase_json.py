import json
import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Cargar semillas desde archivo externo
script_dir = os.path.dirname(os.path.abspath(__file__))
semillas_path = os.path.join(script_dir, "semillas.json")

with open(semillas_path, encoding="utf-8") as f:
    diccionario_semillas = json.load(f)


def frase_a_semilla(frase):
    frase = frase.lower()
    for clave, semilla in diccionario_semillas.items():
        if clave.lower() in frase:
            return semilla
    return "M"


if __name__ == "__main__":
    frase = sys.argv[1] if len(sys.argv) > 1 else "^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)"
    semilla = frase_a_semilla(frase)
    print("🧪 Semilla generada desde la frase:", semilla)

    tokenizer = AutoTokenizer.from_pretrained("nferruz/ProtGPT2", do_lower_case=False)
    tokenizer.pad_token = tokenizer.eos_token  # CORRECCIÓN CLAVE

    model = AutoModelForCausalLM.from_pretrained("nferruz/ProtGPT2")

    inputs = tokenizer(semilla, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs.get("attention_mask", torch.ones_like(input_ids))

    with torch.no_grad():
        salida = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=100,
            min_length=20,
            do_sample=True,
            top_k=50,
            temperature=0.9,
            pad_token_id=tokenizer.eos_token_id,
            num_return_sequences=1,
        )

    print("🧬 Proteína generada:")
    print(tokenizer.decode(salida[0], skip_special_tokens=True))
