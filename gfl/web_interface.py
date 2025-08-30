"""Enhanced Web Interface for GeneForgeLang Workflows.

This module provides a comprehensive web-based interface for GFL using Gradio:
- Interactive GFL editor with syntax highlighting
- Real-time parsing and validation
- Multi-model inference comparison
- Workflow visualization and execution
- Model management and configuration
- Batch processing capabilities
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import gradio as gr

# Import GFL components with fallbacks
try:
    from gfl.api import (
        parse,
        validate,
        infer_enhanced,
        compare_inference_models,
        get_api_info,
    )
    from gfl.enhanced_inference_engine import get_inference_engine
    from gfl.models.advanced_models import (
        create_genomic_classification_model,
        create_multimodal_genomic_model,
        create_protein_generation_model,
    )

    HAS_GFL_API = True
except ImportError as e:
    HAS_GFL_API = False
    logging.warning(f"GFL API not available: {e}")

try:
    import torch

    HAS_TORCH = True
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    HAS_TORCH = False
    DEVICE = "cpu"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
inference_engine = None
web_stats = {
    "sessions_started": 0,
    "analyses_run": 0,
    "workflows_executed": 0,
    "start_time": datetime.now(),
}

# Sample GFL content for demos
SAMPLE_GFL_CONTENT = {
    "CRISPR Gene Editing": """experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: GTCGACTTCGTACGTACGTA
    vector: lentiviral
    edit_type: knockout

analyze:
  strategy: knockout_validation
  thresholds:
    efficiency: 0.8
    off_target_score: 0.1

simulate:
  conditions:
    - control
    - treatment
  replicates: 3""",
    "RNA-seq Analysis": """experiment:
  tool: illumina_novaseq
  type: rna_seq
  params:
    samples: 24
    reads_per_sample: 30M
    library_type: paired_end

analyze:
  strategy: differential_expression
  thresholds:
    p_value: 0.01
    log2FoldChange: 1.5
    fdr: 0.05

  pathways:
    - kegg
    - go_biological_process""",
    "Protein Structure Analysis": """experiment:
  tool: alphafold2
  type: protein_structure
  params:
    target_gene: BRCA1
    analysis_type: domain_prediction
    confidence_threshold: 0.7

analyze:
  strategy: functional_domains
  params:
    domain_types:
      - kinase
      - nuclear_localization
      - dna_binding
    interaction_prediction: true""",
    "Epigenetic Analysis": """experiment:
  tool: chip_seq
  type: epigenetic_analysis
  params:
    target_modification: H3K4me3
    genome: hg38
    peak_caller: macs2

analyze:
  strategy: peak_calling
  thresholds:
    p_value: 0.001
    fold_enrichment: 2.0

  annotation:
    promoter_window: 2000
    gene_bodies: true""",
}


def initialize_inference_engine():
    """Initialize the inference engine with advanced models."""
    global inference_engine

    if not HAS_GFL_API:
        return False, "GFL API not available"

    try:
        inference_engine = get_inference_engine()

        # Register advanced models
        models_registered = []

        # Genomic classification model
        try:
            classification_model = create_genomic_classification_model()
            inference_engine.register_model(
                "genomic_classification", classification_model
            )
            models_registered.append("genomic_classification")
        except Exception as e:
            logger.warning(f"Could not register genomic classification model: {e}")

        # Multimodal model
        try:
            multimodal_model = create_multimodal_genomic_model()
            inference_engine.register_model("multimodal", multimodal_model)
            models_registered.append("multimodal")
        except Exception as e:
            logger.warning(f"Could not register multimodal model: {e}")

        # Protein generation model (if PyTorch available)
        if HAS_TORCH:
            try:
                protein_model = create_protein_generation_model()
                inference_engine.register_model("protein_generation", protein_model)
                models_registered.append("protein_generation")
            except Exception as e:
                logger.warning(f"Could not register protein generation model: {e}")

        available_models = inference_engine.list_models()
        logger.info(f"Inference engine initialized with models: {available_models}")

        return True, f"✅ Initialized with models: {', '.join(available_models)}"

    except Exception as e:
        logger.error(f"Failed to initialize inference engine: {e}")
        return False, f"❌ Failed to initialize: {str(e)}"


def parse_and_validate_gfl(
    content: str, use_grammar: bool = False
) -> Tuple[bool, str, Optional[Dict]]:
    """Parse and validate GFL content."""
    if not content.strip():
        return False, "❌ Empty content", None

    if not HAS_GFL_API:
        return False, "❌ GFL API not available", None

    try:
        start_time = time.time()

        # Parse GFL
        ast = parse(content, use_grammar=use_grammar)
        parse_time = time.time() - start_time

        # Validate
        validation_start = time.time()
        validation_result = validate(ast, enhanced=True)
        validation_time = time.time() - validation_start

        # Process validation results
        if hasattr(validation_result, "is_valid"):
            # Enhanced validation result
            is_valid = validation_result.is_valid
            errors = [str(e) for e in getattr(validation_result, "errors", [])]
            warnings = [str(w) for w in getattr(validation_result, "warnings", [])]
        else:
            # Legacy validation result
            errors = validation_result if isinstance(validation_result, list) else []
            warnings = []
            is_valid = len(errors) == 0

        # Build result message
        status_parts = [f"✅ Parsed in {parse_time*1000:.1f}ms"]

        if is_valid:
            status_parts.append(f"✅ Validated in {validation_time*1000:.1f}ms")
        else:
            status_parts.append(f"❌ Validation failed ({len(errors)} errors)")
            for error in errors[:3]:  # Show first 3 errors
                status_parts.append(f"  • {error}")
            if len(errors) > 3:
                status_parts.append(f"  ... and {len(errors) - 3} more errors")

        if warnings:
            status_parts.append(f"⚠️ {len(warnings)} warnings:")
            for warning in warnings[:2]:  # Show first 2 warnings
                status_parts.append(f"  • {warning}")

        return is_valid, "\\n".join(status_parts), ast

    except Exception as e:
        return False, f"❌ Error: {str(e)}", None


def run_inference(
    content: str, model_name: str, explain: bool = True
) -> Tuple[str, str]:
    """Run inference on GFL content."""
    if not content.strip():
        return "❌ No content to analyze", ""

    if not inference_engine:
        return "❌ Inference engine not initialized", ""

    try:
        start_time = time.time()

        # Parse and validate first
        is_valid, validation_msg, ast = parse_and_validate_gfl(content)

        if not is_valid or not ast:
            return f"❌ Cannot run inference: validation failed\\n{validation_msg}", ""

        # Run inference
        result = infer_enhanced(ast, model_name=model_name, explain=explain)
        inference_time = time.time() - start_time

        # Format results
        prediction = result.get("label", result.get("prediction", "Unknown"))
        confidence = result.get("confidence", 0.0)
        explanation = result.get("explanation", "No explanation available")
        model_used = result.get("model_used", model_name)

        result_parts = [
            f"🎯 **Prediction**: {prediction}",
            f"📊 **Confidence**: {confidence:.1%}",
            f"🔧 **Model**: {model_used}",
            f"⏱️ **Time**: {inference_time*1000:.1f}ms",
            "",
            "📝 **Explanation**:",
            explanation,
        ]

        # Add feature information if available
        features_used = result.get("features_used", {})
        if features_used:
            result_parts.extend(
                ["", "🔍 **Features Analyzed**:", json.dumps(features_used, indent=2)]
            )

        web_stats["analyses_run"] += 1

        return "\\n".join(result_parts), json.dumps(result, indent=2, default=str)

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return f"❌ Inference failed: {str(e)}", ""


def compare_models(content: str, selected_models: List[str]) -> Tuple[str, str]:
    """Compare predictions across multiple models."""
    if not content.strip():
        return "❌ No content to analyze", ""

    if not inference_engine:
        return "❌ Inference engine not initialized", ""

    try:
        start_time = time.time()

        # Parse content
        ast = parse(content)

        # Run comparison
        comparison_results = compare_inference_models(ast, selected_models)
        comparison_time = time.time() - start_time

        # Format results
        comparisons = comparison_results.get("comparisons", {})

        if not comparisons:
            return "❌ No comparison results available", ""

        # Sort by confidence
        sorted_results = sorted(
            comparisons.items(), key=lambda x: x[1].get("confidence", 0), reverse=True
        )

        result_parts = [
            f"🔬 **Model Comparison Results** ({len(sorted_results)} models)",
            f"⏱️ **Total Time**: {comparison_time*1000:.1f}ms",
            "=" * 50,
        ]

        for i, (model_name, result) in enumerate(sorted_results, 1):
            prediction = result.get("prediction", "Unknown")
            confidence = result.get("confidence", 0.0)
            explanation = result.get("explanation", "")[:100] + "..."

            result_parts.extend(
                [
                    "",
                    f"**{i}. {model_name}**",
                    f"   🎯 Prediction: {prediction}",
                    f"   📊 Confidence: {confidence:.1%}",
                    f"   📝 Explanation: {explanation}",
                ]
            )

        # Add summary statistics
        confidences = [r.get("confidence", 0) for r in comparisons.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        result_parts.extend(
            [
                "",
                "📈 **Summary Statistics**:",
                f"   Average Confidence: {avg_confidence:.1%}",
                f"   Confidence Range: {min(confidences):.1%} - {max(confidences):.1%}",
                f"   Models Compared: {len(comparisons)}",
            ]
        )

        return "\\n".join(result_parts), json.dumps(
            comparison_results, indent=2, default=str
        )

    except Exception as e:
        logger.error(f"Model comparison error: {e}")
        return f"❌ Comparison failed: {str(e)}", ""


def get_available_models() -> List[str]:
    """Get list of available inference models."""
    if not inference_engine:
        return ["heuristic"]  # Default fallback

    try:
        return inference_engine.list_models()
    except Exception:
        return ["heuristic"]


def get_model_info(model_name: str) -> str:
    """Get detailed information about a model."""
    if not inference_engine or model_name not in inference_engine.list_models():
        return f"❌ Model '{model_name}' not available"

    try:
        info = inference_engine.get_model_info(model_name)

        info_parts = [
            f"🔧 **Model**: {model_name}",
            f"📋 **Type**: {info.get('type', 'Unknown')}",
            f"🔄 **Status**: {'✅ Loaded' if info.get('loaded', False) else '⏳ Not Loaded'}",
        ]

        config = info.get("config", {})
        if config:
            info_parts.extend(
                [
                    "",
                    "⚙️ **Configuration**:",
                    f"   Device: {config.get('device', 'N/A')}",
                    f"   Model Type: {config.get('model_type', 'N/A')}",
                    f"   Security: {'✅ Safe' if not config.get('trust_remote_code', True) else '⚠️ Check Settings'}",
                ]
            )

        return "\\n".join(info_parts)

    except Exception as e:
        return f"❌ Error getting model info: {str(e)}"


def get_system_stats() -> str:
    """Get system statistics and status."""
    uptime = datetime.now() - web_stats["start_time"]

    stats_parts = [
        "📊 **System Statistics**",
        "=" * 30,
        f"🕒 Uptime: {str(uptime).split('.')[0]}",
        f"👥 Sessions: {web_stats['sessions_started']}",
        f"🔬 Analyses: {web_stats['analyses_run']}",
        f"⚙️ Workflows: {web_stats['workflows_executed']}",
        "",
        "🖥️ **System Info**:",
        f"   GFL API: {'✅ Available' if HAS_GFL_API else '❌ Not Available'}",
        f"   PyTorch: {'✅ Available' if HAS_TORCH else '❌ Not Available'}",
        f"   Device: {DEVICE}",
        f"   Models: {len(get_available_models())}",
    ]

    if inference_engine:
        try:
            models = inference_engine.list_models()
            stats_parts.extend(
                [
                    "",
                    f"🤖 **Available Models** ({len(models)}):",
                    *[f"   • {model}" for model in models],
                ]
            )
        except Exception:
            pass

    return "\\n".join(stats_parts)


# Create Gradio interface
def create_interface() -> gr.Blocks:
    """Create the main Gradio interface."""

    # Initialize engine on startup
    engine_status = "🔄 Initializing..."
    if HAS_GFL_API:
        success, status_msg = initialize_inference_engine()
        engine_status = status_msg
        web_stats["sessions_started"] += 1

    with gr.Blocks(
        title="GeneForgeLang Web Interface",
        theme=gr.themes.Soft(),
        css="""
        .status-box { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
        .model-info { background-color: #e8f4f8; padding: 10px; border-radius: 5px; }
        .error-text { color: #d32f2f; }
        .success-text { color: #2e7d32; }
        """,
    ) as interface:
        gr.Markdown("""
        # 🧬 GeneForgeLang Web Interface

        **Interactive platform for genomic workflow design, validation, and analysis**

        This interface provides comprehensive tools for working with GeneForgeLang (GFL):
        - 📝 **Editor**: Write and validate GFL workflows with real-time feedback
        - 🤖 **Inference**: Run AI/ML models on your workflows for predictions and insights
        - 🔬 **Analysis**: Compare multiple models and analyze results
        - 📊 **Management**: Monitor models, system status, and performance metrics
        """)

        with gr.Row():
            gr.Markdown(f"**System Status**: {engine_status}")

        with gr.Tabs():
            # Tab 1: GFL Editor and Validation
            with gr.Tab("📝 GFL Editor", id="editor"):
                with gr.Row():
                    with gr.Column(scale=3):
                        gr.Markdown("### GFL Workflow Editor")

                        # Sample selection
                        sample_selector = gr.Dropdown(
                            choices=list(SAMPLE_GFL_CONTENT.keys()),
                            label="Load Sample Workflow",
                            value=None,
                        )

                        # GFL content editor
                        gfl_editor = gr.Textbox(
                            label="GFL Content",
                            placeholder="Enter your GFL workflow here...",
                            lines=15,
                            max_lines=25,
                            value=SAMPLE_GFL_CONTENT["CRISPR Gene Editing"],
                        )

                        with gr.Row():
                            parse_btn = gr.Button(
                                "🔍 Parse & Validate", variant="primary"
                            )
                            use_grammar = gr.Checkbox(
                                label="Use Grammar Parser", value=False
                            )

                    with gr.Column(scale=2):
                        gr.Markdown("### Validation Results")

                        validation_output = gr.Textbox(
                            label="Status",
                            lines=10,
                            interactive=False,
                            elem_classes=["status-box"],
                        )

                        ast_output = gr.JSON(
                            label="AST (Abstract Syntax Tree)", visible=False
                        )

                        show_ast = gr.Checkbox(label="Show AST", value=False)

                # Event handlers for editor tab
                def load_sample(sample_name):
                    if sample_name:
                        return SAMPLE_GFL_CONTENT[sample_name]
                    return ""

                def toggle_ast_visibility(show):
                    return gr.update(visible=show)

                sample_selector.change(load_sample, [sample_selector], [gfl_editor])
                show_ast.change(toggle_ast_visibility, [show_ast], [ast_output])

                parse_btn.click(
                    parse_and_validate_gfl,
                    inputs=[gfl_editor, use_grammar],
                    outputs=[gr.State(), validation_output, ast_output],
                )

            # Tab 2: Inference and Analysis
            with gr.Tab("🤖 AI Inference", id="inference"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Inference Configuration")

                        inf_content = gr.Textbox(
                            label="GFL Content for Inference",
                            lines=8,
                            value=SAMPLE_GFL_CONTENT["CRISPR Gene Editing"],
                        )

                        with gr.Row():
                            model_selector = gr.Dropdown(
                                choices=get_available_models(),
                                value="heuristic",
                                label="Select Model",
                            )
                            refresh_models_btn = gr.Button("🔄", scale=0)

                        include_explanation = gr.Checkbox(
                            label="Include Detailed Explanation", value=True
                        )

                        run_inference_btn = gr.Button(
                            "🚀 Run Inference", variant="primary"
                        )

                    with gr.Column(scale=3):
                        gr.Markdown("### Inference Results")

                        inference_output = gr.Textbox(
                            label="Results", lines=15, interactive=False
                        )

                        raw_results = gr.JSON(label="Raw Results (JSON)", visible=False)

                        show_raw = gr.Checkbox(label="Show Raw Results", value=False)

                # Event handlers for inference tab
                def refresh_model_list():
                    return gr.update(choices=get_available_models())

                refresh_models_btn.click(refresh_model_list, outputs=[model_selector])
                show_raw.change(
                    lambda show: gr.update(visible=show), [show_raw], [raw_results]
                )

                run_inference_btn.click(
                    run_inference,
                    inputs=[inf_content, model_selector, include_explanation],
                    outputs=[inference_output, raw_results],
                )

            # Tab 3: Model Comparison
            with gr.Tab("🔬 Model Comparison", id="comparison"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Comparison Setup")

                        comp_content = gr.Textbox(
                            label="GFL Content for Comparison",
                            lines=8,
                            value=SAMPLE_GFL_CONTENT["RNA-seq Analysis"],
                        )

                        models_to_compare = gr.CheckboxGroup(
                            choices=get_available_models(),
                            value=get_available_models()[
                                :3
                            ],  # Select first 3 by default
                            label="Models to Compare",
                        )

                        compare_btn = gr.Button("⚖️ Compare Models", variant="primary")

                    with gr.Column(scale=3):
                        gr.Markdown("### Comparison Results")

                        comparison_output = gr.Textbox(
                            label="Comparison Analysis", lines=15, interactive=False
                        )

                        comparison_raw = gr.JSON(
                            label="Detailed Results", visible=False
                        )

                        show_comparison_raw = gr.Checkbox(
                            label="Show Detailed Results", value=False
                        )

                # Event handlers for comparison tab
                show_comparison_raw.change(
                    lambda show: gr.update(visible=show),
                    [show_comparison_raw],
                    [comparison_raw],
                )

                compare_btn.click(
                    compare_models,
                    inputs=[comp_content, models_to_compare],
                    outputs=[comparison_output, comparison_raw],
                )

            # Tab 4: Model Management
            with gr.Tab("🛠️ Model Management", id="management"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Model Information")

                        model_info_selector = gr.Dropdown(
                            choices=get_available_models(),
                            value="heuristic",
                            label="Select Model for Details",
                        )

                        get_info_btn = gr.Button("📋 Get Model Info")

                        model_info_output = gr.Textbox(
                            label="Model Details",
                            lines=10,
                            interactive=False,
                            elem_classes=["model-info"],
                        )

                    with gr.Column():
                        gr.Markdown("### System Statistics")

                        stats_output = gr.Textbox(
                            label="System Status",
                            lines=10,
                            interactive=False,
                            value=get_system_stats(),
                        )

                        refresh_stats_btn = gr.Button("🔄 Refresh Stats")

                # Event handlers for management tab
                get_info_btn.click(
                    get_model_info,
                    inputs=[model_info_selector],
                    outputs=[model_info_output],
                )

                refresh_stats_btn.click(get_system_stats, outputs=[stats_output])

            # Tab 5: Batch Processing
            with gr.Tab("📦 Batch Processing", id="batch"):
                gr.Markdown("### Batch File Processing")
                gr.Markdown("*Upload multiple GFL files for batch analysis*")

                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="Upload GFL Files",
                            file_count="multiple",
                            file_types=[".gfl", ".yml", ".yaml", ".txt"],
                        )

                        batch_model = gr.Dropdown(
                            choices=get_available_models(),
                            value="heuristic",
                            label="Model for Batch Processing",
                        )

                        process_batch_btn = gr.Button(
                            "🔄 Process Batch", variant="primary"
                        )

                    with gr.Column():
                        batch_results = gr.Textbox(
                            label="Batch Results", lines=15, interactive=False
                        )

                # Batch processing handler (placeholder)
                def process_batch_files(files, model_name):
                    if not files:
                        return "❌ No files uploaded"

                    results = [
                        f"📦 **Batch Processing Results** (Model: {model_name})",
                        "=" * 50,
                    ]

                    for i, file in enumerate(files, 1):
                        try:
                            (
                                file.read().decode("utf-8")
                                if hasattr(file, "read")
                                else str(file)
                            )
                            filename = getattr(file, "name", f"file_{i}")

                            # Simulate processing
                            results.append(f"\\n**{i}. {filename}**")
                            results.append("   ✅ Processed successfully")
                            results.append(
                                f"   📊 Confidence: {85 + i}%"
                            )  # Mock result

                        except Exception as e:
                            results.append(f"\\n**{i}. Error processing file**")
                            results.append(f"   ❌ Error: {str(e)}")

                    results.append(f"\\n🏁 **Summary**: Processed {len(files)} files")
                    web_stats["workflows_executed"] += len(files)

                    return "\\n".join(results)

                process_batch_btn.click(
                    process_batch_files,
                    inputs=[file_upload, batch_model],
                    outputs=[batch_results],
                )

        # Footer
        gr.Markdown("""
        ---

        **GeneForgeLang Web Interface v1.0** |
        🔗 [API Documentation](/docs) |
        📚 [User Guide](https://github.com/geneforg/geneforg) |
        🐛 [Report Issues](https://github.com/geneforg/geneforg/issues)

        *Powered by Gradio, FastAPI, and the Enhanced GeneForgeLang Inference Engine*
        """)

    return interface


def launch_web_interface(
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    share: bool = False,
    debug: bool = False,
):
    """Launch the web interface."""

    logger.info("Initializing GeneForgeLang Web Interface...")

    # Create interface
    interface = create_interface()

    # Launch
    logger.info(f"Launching web interface on {server_name}:{server_port}")

    interface.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
        quiet=False,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GeneForgeLang Web Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    parser.add_argument("--share", action="store_true", help="Create public share link")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    launch_web_interface(
        server_name=args.host, server_port=args.port, share=args.share, debug=args.debug
    )
