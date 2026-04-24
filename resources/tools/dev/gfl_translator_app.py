import json
import os
import tempfile
from typing import Tuple

import google.generativeai as genai
import gradio as gr
from dotenv import load_dotenv

# Optional GFL validation/inference imports
try:
    from gfl.api import infer as gfl_infer
    from gfl.api import parse as gfl_parse
    from gfl.api import validate as gfl_validate
    from gfl.models.dummy import DummyGeneModel
    from gfl.models.simple import SimpleHeuristicModel
except Exception:
    gfl_parse = None  # type: ignore
    gfl_validate = None  # type: ignore
    gfl_infer = None  # type: ignore
    DummyGeneModel = None  # type: ignore
    SimpleHeuristicModel = None  # type: ignore


load_dotenv()


def _configure_gemini() -> None:
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise KeyError("GOOGLE_API_KEY not found in environment (check your .env file)")
        genai.configure(api_key=api_key)
    except (KeyError, AttributeError) as e:
        # Keep message concise but actionable for users
        print("ERROR: Google API key not found. Create a .env with GOOGLE_API_KEY='your_key'.\n" f"Detail: {e}")
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
        t = t[:-3].strip()
    return t


def _format_inference_summary(inf: dict) -> str:
    if not inf:
        return ""
    if "error" in inf:
        return f"### Inference\n- Error: {inf['error']}"
    label = inf.get("label", "unknown")
    conf = inf.get("confidence")
    exp = inf.get("explanation")
    conf_str = f"{conf*100:.0f}%" if isinstance(conf, (int, float)) else str(conf)
    parts = ["### Inference", f"- Label: **{label}**", f"- Confidence: **{conf_str}**"]
    if exp:
        parts.append(f"- Explanation: {exp}")
    return "\n".join(parts)


def _status_banner_html(status: str) -> str:
    status_lower = status.lower()
    if "success" in status_lower:
        color = "#e7f8ec"  # green-ish
        border = "#2ea44f"
    elif "failed" in status_lower or "parse failed" in status_lower or "error" in status_lower:
        color = "#fdecea"  # red-ish
        border = "#d73a49"
    else:
        color = "#fff8e1"  # amber-ish
        border = "#c69026"
    return f'<div style="padding:10px;border:1px solid {border};background:{color};border-radius:6px;">{status}</div>'


def _pick_model(model_name: str):
    if model_name == "SimpleHeuristicModel" and SimpleHeuristicModel:
        return SimpleHeuristicModel()
    # default
    if DummyGeneModel:
        return DummyGeneModel()
    return None


def translate_to_gfl(
    natural_language_input: str, model_name: str, selected_model_state: str
) -> Tuple[str, str, str, str, dict, str, str, str]:
    """Generate GFL from NL and provide validation feedback."""
    if not natural_language_input:
        status = "Validation: waiting for input."
        return (
            _status_banner_html(status),
            "# Please describe an experiment to begin.",
            status,
            "",
            {},
            (model_name or selected_model_state or "DummyGeneModel"),
            "",
            "",
        )

    # Configure Gemini and create model/chat per request to isolate context
    _configure_gemini()
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])

    try:
        prompt = f"{GFL_MASTER_PROMPT}\n\nUser:\n{natural_language_input}\n\nGFL:"
        response = chat.send_message(prompt)
        code = _strip_fences((response.text or "").strip())
    except Exception:
        status = "Validation: not available (generation error)"
        return (
            _status_banner_html(status),
            "# Error generating code.",
            status,
            "",
            {},
            (model_name or selected_model_state or "DummyGeneModel"),
            "",
            "",
        )

    # Optional validation using local GFL modules if available
    inference: dict = {}
    if gfl_parse and gfl_validate:
        try:
            ast = gfl_parse(code)
            if ast is None:
                status = "Validation: parse failed (invalid YAML or syntax)."
                return (
                    _status_banner_html(status),
                    code,
                    status,
                    "",
                    {},
                    (model_name or selected_model_state or "DummyGeneModel"),
                    "",
                    "",
                )
            errors = gfl_validate(ast) or []
            if errors:
                details = "\n".join(f"- {msg}" for msg in errors)
                status = "Validation: FAILED"
                return (
                    _status_banner_html(status),
                    code,
                    f"{status}\n{details}",
                    "",
                    {},
                    (model_name or selected_model_state or "DummyGeneModel"),
                    "",
                    "",
                )
            # Optional inference
            if gfl_infer:
                try:
                    model = _pick_model(model_name)
                    if model is not None:
                        inference = gfl_infer(model, ast)
                except Exception as e:  # noqa: BLE001
                    inference = {"error": f"infer failed: {e}"}
            # Prepare downloadable files
            code_path = ""
            inf_path = ""
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".gfl", delete=False, encoding="utf-8") as f:
                    f.write(code)
                    code_path = f.name
                with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                    json.dump(inference or {}, f, ensure_ascii=False, indent=2)
                    inf_path = f.name
            except Exception:
                pass

            status = "Validation: SUCCESS"
            return (
                _status_banner_html(status),
                code,
                status,
                _format_inference_summary(inference),
                inference,
                (model_name or selected_model_state or "DummyGeneModel"),
                code_path,
                inf_path,
            )
        except Exception as e:
            status = "Validation: error"
            return (
                _status_banner_html(status),
                code,
                f"Validation error: {e}",
                "",
                {},
                (model_name or selected_model_state or "DummyGeneModel"),
                "",
                "",
            )

    # If validation not available
    status = "Validation: not available (install/enable gfl.api)"
    return (
        _status_banner_html(status),
        code,
        status,
        "",
        {},
        (model_name or selected_model_state or "DummyGeneModel"),
        "",
        "",
    )


iface = gr.Interface(
    fn=translate_to_gfl,
    inputs=[
        gr.Textbox(lines=3, label="Describe your experiment (EN/ES)"),
        gr.Dropdown(
            choices=["DummyGeneModel", "SimpleHeuristicModel"],
            value="DummyGeneModel",
            label="Model",
        ),
        gr.State(value="DummyGeneModel"),
    ],
    outputs=[
        gr.HTML(label="Validation Status"),
        gr.Code(language="yaml", label="Generated GeneForgeLang"),
        gr.Markdown(label="Validation Details"),
        gr.Markdown(label="Inference Summary"),
        gr.JSON(label="Inference (raw)"),
        gr.State(),
        gr.File(label="Download GFL"),
        gr.File(label="Download Inference JSON"),
    ],
    title="Natural Language → GeneForgeLang Translator",
    description=(
        "Type a scientific goal; the app emits a valid GFL script, validates it, and runs inference using the selected model."
    ),
)


if __name__ == "__main__":
    iface.launch()
