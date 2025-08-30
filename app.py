
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Cargar el modelo solo una vez
model = AutoModelForCausalLM.from_pretrained("nferruz/ProtGPT2")
tokenizer = AutoTokenizer.from_pretrained("nferruz/ProtGPT2")
tokenizer.pad_token = tokenizer.eos_token

# Traducción entre moléculas
def transcode_phrase(phrase, src, dst):
    if src == dst:
        return "⚠️ Source and target are the same."
    if src == "DNA" and dst == "RNA":
        return phrase.replace("~d:", ":r:").replace("Exon", "Ex").replace("Intr", "removed")
    elif src == "RNA" and dst == "Protein":
        return phrase.replace(":r:", "^p:").replace("Ex1", "Dom(Kin)").replace("Ex2", "Mot(NLS)")
    elif src == "Protein" and dst == "DNA":
        return phrase.replace("^p:", "~d:").replace("Dom(Kin)", "Exon1").replace("Mot(NLS)", "Exon2")
    else:
        return "❌ Translation not implemented."

# Generar proteína a partir de frase
semillas = {
    "^p:Dom(Kin)-Mot(NLS)*AcK@147=Localize(Nucleus)": "MKKK",
    "^p:Mot(NLS)-Mot(PEST)*P@120": "MKSP",
    "^p:Dom(ZnF)-Mot(NLS)*UbK@42": "MKHG",
}

def generar_desde_frase(frase):
    semilla = semillas.get(frase, "MKKK")
    inputs = tokenizer(semilla, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs, max_length=200, do_sample=True, top_k=950, temperature=1.5, num_return_sequences=1)
    secuencia = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return f"🧪 Seed: {semilla}
🧬 Generated Protein:
{secuencia}"

# Interfaz Gradio
with gr.Blocks() as demo:
    with gr.Tab("Phrase → Protein"):
        gr.Markdown("### Generate Protein Sequence from GeneForgeLang Phrase")
        input_frase = gr.Textbox(label="Input Phrase")
        output_prot = gr.Textbox(label="Generated Protein")
        boton_gen = gr.Button("Generate")
        boton_gen.click(fn=generar_desde_frase, inputs=input_frase, outputs=output_prot)

    with gr.Tab("Transcode Across Molecules"):
        gr.Markdown("### Convert between DNA, RNA, and Protein symbolic phrases")
        input_phrase = gr.Textbox(label="Input GeneForgeLang Phrase")
        src_select = gr.Radio(choices=["DNA", "RNA", "Protein"], label="Translate From", value="DNA")
        dst_select = gr.Radio(choices=["DNA", "RNA", "Protein"], label="Translate To", value="RNA")
        output = gr.Textbox(label="Translated Phrase")
        trans_btn = gr.Button("Translate")
        trans_btn.click(fn=transcode_phrase, inputs=[input_phrase, src_select, dst_select], outputs=output)

demo.launch()
