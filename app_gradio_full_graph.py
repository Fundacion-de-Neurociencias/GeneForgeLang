import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import re
import tempfile

# Load symbolic phrase dictionary
with open("semillas.json", "r", encoding="utf-8") as f:
    diccionario_semillas = json.load(f)

def phrase_to_seed(phrase):
    phrase = phrase.lower()
    for key, seed in diccionario_semillas.items():
        if key.lower() in phrase:
            return seed
    return "M"

tokenizer = AutoTokenizer.from_pretrained("nferruz/ProtGPT2", do_lower_case=False)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained("nferruz/ProtGPT2")

def generate_protein_and_props(phrase):
    seed = phrase_to_seed(phrase)
    inputs = tokenizer(seed, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs.get("attention_mask", torch.ones_like(input_ids))

    with torch.no_grad():
        output = model.generate(
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

    seq = tokenizer.decode(output[0], skip_special_tokens=True)

    # Calculate properties
    length = len(seq)
    aa_count = {aa: seq.count(aa) for aa in "ACDEFGHIKLMNPQRSTVWY"}
    charge = sum([aa_count.get(a, 0) for a in "KR"]) - sum([aa_count.get(a, 0) for a in "DE"])
    mw = sum([aa_count[a]*w for a, w in {
        "A": 89.1, "C": 121.2, "D": 133.1, "E": 147.1, "F": 165.2,
        "G": 75.1, "H": 155.2, "I": 131.2, "K": 146.2, "L": 131.2,
        "M": 149.2, "N": 132.1, "P": 115.1, "Q": 146.2, "R": 174.2,
        "S": 105.1, "T": 119.1, "V": 117.1, "W": 204.2, "Y": 181.2
    }.items()])

    props = f"🧪 Seed: {seed}\n🧬 Protein: {seq}\n\n🔬 Properties:\n- Length: {length} aa\n- Charge: {charge}\n- MW: {mw:.1f} Da"
    
    # Save to FASTA
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta", mode="w", encoding="utf-8") as f:
        f.write(f">Generated_Protein\n{seq}\n")
        fasta_path = f.name

    return props, fasta_path

def sequence_to_phrase(seq):
    seq = seq.upper()
    tags = []
    if re.search(r"^M*K{3,}", seq):
        tags.append("Dom(Kin)")
    if re.search(r"[RK]{3,}", seq):
        tags.append("Mot(NLS)")
    if len(re.findall(r"E", seq)) >= 5 or "DEG" in seq:
        tags.append("Mot(PEST)")
    if re.search(r"KQAK|QAK", seq):
        tags.append("*AcK@X")
    if re.search(r"[RST]P", seq):
        tags.append("*P@X")
    if "PRKRK" in seq or "PKKKRKV" in seq:
        tags.append("Localize(Nucleus)")
    if re.search(r"(AILFL|LAGGAV|LVLL|AAVL)", seq):
        tags.append("Localize(Membrane)")
    return "^p:" + "-".join(sorted(set(tags))) if tags else "// No symbolic motifs found"

def phrase_to_description(phrase):
    phrase = phrase.replace("^p:", "")
    fragments = phrase.split("-")
    translation = {
        "Dom(Kin)": "a kinase domain",
        "Mot(NLS)": "a nuclear localization signal",
        "Mot(PEST)": "a PEST motif indicating protein degradation",
        "*AcK@X": "lysine acetylation at a specific position",
        "*P@X": "a phosphorylation site",
        "Localize(Nucleus)": "localizes to the cell nucleus",
        "Localize(Membrane)": "localizes to the cell membrane"
    }
    phrases = [translation.get(tag, tag) for tag in fragments if tag]
    if not phrases:
        return "No interpretable symbolic elements found."
    return "This protein contains " + ", ".join(phrases[:-1]) + (
        f", and {phrases[-1]}." if len(phrases) > 1 else f"{phrases[0]}.")

with gr.Blocks() as demo:
    gr.Markdown("# 🧬 GeneForgeLang AI Tools")
    gr.Markdown("Design, interpret, describe, and export proteins using symbolic language and AI.")

    with gr.Tab("🧠 Phrase → Protein"):
        inp = gr.Textbox(label="GeneForgeLang Phrase", placeholder="^p:Dom(Kin)-Mot(NLS)*AcK@147")
        out = gr.Textbox(label="Protein + Properties")
        fasta = gr.File(label="Download FASTA")
        btn = gr.Button("Generate")
        btn.click(fn=generate_protein_and_props, inputs=inp, outputs=[out, fasta])

    with gr.Tab("🧪 Protein → Phrase"):
        inp2 = gr.Textbox(label="Protein Sequence", placeholder="MKKKPRRRDEEGEK...")
        out2 = gr.Textbox(label="Interpreted GeneForgeLang")
        btn2 = gr.Button("Translate")
        btn2.click(fn=sequence_to_phrase, inputs=inp2, outputs=out2)

    
    with gr.Tab("🧬 Mutate Protein"):
        inp4 = gr.Textbox(label="GeneForgeLang Phrase", placeholder="^p:Dom(Kin)-Mot(NLS)*AcK@147")
        out4 = gr.Textbox(label="Mutated Protein")
        btn4 = gr.Button("Mutate")
        btn4.click(fn=generate_protein_and_props, inputs=inp4, outputs=[out4, gr.File(visible=False)])

    
    with gr.Tab("📊 Analyze Protein"):
        inp5 = gr.Textbox(label="Protein Sequence", placeholder="Paste sequence to analyze")
        out5 = gr.Image(label="Amino Acid Composition")
        btn5 = gr.Button("Analyze")
        def analyze_graph(seq): return generar_composicion_grafico(seq)
        btn5.click(fn=analyze_graph, inputs=inp5, outputs=out5)

    with gr.Tab("📖 Phrase → Natural Language"):
    
        inp3 = gr.Textbox(label="GeneForgeLang Phrase", placeholder="^p:Dom(Kin)-Mot(NLS)*AcK@147")
        out3 = gr.Textbox(label="Scientific Description")
        btn3 = gr.Button("Describe")
        btn3.click(fn=phrase_to_description, inputs=inp3, outputs=out3)

if __name__ == "__main__":
    demo.launch()