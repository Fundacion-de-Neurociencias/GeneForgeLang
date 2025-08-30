import os

import google.generativeai as genai
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("Missing GOOGLE_API_KEY. Create a .env with GOOGLE_API_KEY=...")
genai.configure(api_key=api_key)


GFL_MASTER_PROMPT = """
Act as a senior bioinformatician and core developer of GeneForgeLang (GFL).
Your only job is to translate high-level experimental goals written in natural
language (English or Spanish) into perfectly-formed, logically valid GFL code.

Rules:
1) Output only the GFL code block. No explanations.
2) Strict syntax. Indentation (2 spaces) matters. YAML-like DSL.
3) Infer parameter names (target_gene, p_value, strategy, etc.) from context.
4) If ambiguous, emit a template and add '# TODO:' comments for missing info.
5) If multi-step, compose a single coherent script in proper order.

Keywords: experiment, simulate, analyze, branch (with if/then[/else]).
"""

model = genai.GenerativeModel("gemini-pro")


def translate_to_gfl(nl_request: str) -> str:
    chat = model.start_chat(history=[])
    full_prompt = f"{GFL_MASTER_PROMPT}\n\nUser:\n{nl_request}\n\nGFL:"
    response = chat.send_message(full_prompt)
    cleaned = (response.text or "").strip()
    if cleaned.startswith("```gfl"):
        cleaned = cleaned[len("```gfl") :].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned


iface = gr.Interface(
    fn=translate_to_gfl,
    inputs=gr.Textbox(lines=3, label="Describe your experiment (EN/ES)"),
    outputs=gr.Code(language="yaml", label="Generated GeneForgeLang"),
    title="Natural Language → GeneForgeLang Translator",
    description="Type a scientific goal; the app emits a valid GFL script (Gemini Pro).",
)


if __name__ == "__main__":
    iface.launch()
