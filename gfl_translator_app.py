import os
from typing import Tuple

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

# Optional GFL validation/inference imports
try:
    from gfl.api import parse as gfl_parse, validate as gfl_validate, infer as gfl_infer
    from gfl.models.dummy import DummyGeneModel
except Exception:
    gfl_parse = None  # type: ignore
    gfl_validate = None  # type: ignore
    gfl_infer = None  # type: ignore
    DummyGeneModel = None  # type: ignore


load_dotenv()


def _configure_gemini() -> None:
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise KeyError("GOOGLE_API_KEY not found in environment (check your .env file)")
        genai.configure(api_key=api_key)
    except (KeyError, AttributeError) as e:
        # Keep message concise but actionable for users
        print(
            "ERROR: Google API key not found. Create a .env with GOOGLE_API_KEY='your_key'.\n"
            f"Detail: {e}"
        )
        raise


GFL_MASTER_PROMPT = (
    "Act as a senior bioinformatician and GeneForgeLang (GFL) core developer. "
    "Translate a high-level scientific request (EN/ES) into a valid GFL YAML-like script.\n\n"
    "Rules:\n"
    "1) Output only the GFL code. No explanations.\n"
    "2) Strict syntax. Indentation (2 spaces) matters.\n"
    "3) Infer parameter names from context (target_gene, p_value, strategy, etc.).\n"
    "4) If ambiguous, output a template and add '# TODO:' comments.\n"
    "5) If multi-step, compose a single coherent script in proper order.\n"
)


def _strip_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```gfl"):
        t = t[len("```gfl") :].strip()
    if t.endswith("```"):
        t = t[: -3].strip()
    return t


def translate_to_gfl(natural_language_input: str) -> Tuple[str, str, dict]:
    """Generate GFL from NL and provide validation feedback."""
    if not natural_language_input:
        return (
            "# Please describe an experiment to begin.",
            "Validation: waiting for input.",
            {},
        )

    # Configure Gemini and create model/chat per request to isolate context
    _configure_gemini()
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])

    try:
        prompt = f"{GFL_MASTER_PROMPT}\n\nUser:\n{natural_language_input}\n\nGFL:"
        response = chat.send_message(prompt)
        code = _strip_fences((response.text or "").strip())
    except Exception as e:
        return "# Error generating code.", f"Error contacting Gemini API: {e}", {}

    # Optional validation using local GFL modules if available
    inference: dict = {}
    if gfl_parse and gfl_validate:
        try:
            ast = gfl_parse(code)
            if ast is None:
                return code, "Validation: parse failed (invalid YAML or syntax).", {}
            errors = gfl_validate(ast) or []
            if errors:
                details = "\n".join(f"- {msg}" for msg in errors)
                return code, f"Validation: FAILED\n{details}", {}
            # Optional inference
            if gfl_infer and DummyGeneModel:
                try:
                    inference = gfl_infer(DummyGeneModel(), ast)
                except Exception as e:  # noqa: BLE001
                    inference = {"error": f"infer failed: {e}"}
            return code, "Validation: SUCCESS", inference
        except Exception as e:
            return code, f"Validation error: {e}", {}

    # If validation not available
    return code, "Validation: not available (install/enable gfl.api)", {}


iface = gr.Interface(
    fn=translate_to_gfl,
    inputs=gr.Textbox(lines=3, label="Describe your experiment (EN/ES)"),
    outputs=[
        gr.Code(language="yaml", label="Generated GeneForgeLang"),
        gr.Markdown(label="Validation"),
        gr.JSON(label="Inference"),
    ],
    title="Natural Language → GeneForgeLang Translator",
    description=(
        "Type a scientific goal; the app emits a valid GFL script and runs a local validation pass."
    ),
)


if __name__ == "__main__":
    iface.launch()
