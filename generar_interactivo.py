import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def frase_a_semilla(frase):
    semilla = "M"
    if "Dom(Kin)" in frase:
        semilla += "KKK"
    if "Mot(NLS)" in frase:
        semilla += "RRRR"
    if "TF(GATA)" in frase:
        semilla += "TFG"
    if "*AcK@" in frase:
        semilla += "AK"
    return semilla


frase = input("🔤 Escribe tu frase GeneForgeLang: ")
semilla = frase_a_semilla(frase)
print("🧪 Semilla generada:", semilla)

tokenizer = AutoTokenizer.from_pretrained("nferruz/ProtGPT2", do_lower_case=False)
model = AutoModelForCausalLM.from_pretrained("nferruz/ProtGPT2")

inputs = tokenizer(semilla, return_tensors="pt")
with torch.no_grad():
    salida = model.generate(
        inputs["input_ids"],
        max_length=100,
        do_sample=True,
        top_k=50,
        temperature=0.8,
        num_return_sequences=1,
    )

print("🧬 Proteína generada:")
print(tokenizer.decode(salida[0], skip_special_tokens=True))
