from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import sys

def frase_a_semilla(frase):
    frase = frase.lower()
    if "dom(kin)" in frase:
        return "MKKK"
    elif "mot(nls)" in frase:
        return "MPRRR"
    elif "mot(pest)" in frase:
        return "MDGQL"
    elif "tf(gata1)" in frase:
        return "MKTFG"
    elif "*ack" in frase or "*ac" in frase:
        return "MKQAK"
    elif "*p" in frase or "*phos" in frase:
        return "MKRP"
    elif "localize(nucleus)" in frase:
        return "MPKRK"
    elif "localize(membrane)" in frase:
        return "MAIFL"
    else:
        return "M"

if __name__ == "__main__":
    frase = "^p:Dom(Kin)'-Mot(NLS)*AcK@147=Localize(Nucleus)"
    semilla = frase_a_semilla(frase)
    print("🧪 Semilla generada desde la frase:", semilla)

    tokenizer = AutoTokenizer.from_pretrained("nferruz/ProtGPT2", do_lower_case=False)
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
            num_return_sequences=1
        )

    print("🧬 Proteína generada:")
    print(tokenizer.decode(salida[0], skip_special_tokens=True))