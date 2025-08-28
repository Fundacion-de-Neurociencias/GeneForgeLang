# GeneForgeLang

GeneForgeLang (GFL) is a domain-specific language designed for specifying and executing complex genomic workflows. It provides a high-level, human-readable syntax for defining genetic experiments, data processing pipelines, and analytical tasks.

## Project Structure

```
GeneForgeLang/
├── __init__.py
├── .gitattributes
├── .gitignore
├── advanced_validator.py
├── alphagenenome_plugin.py
├── app_gradio_full_graph.py
├── app.py
├── bfg.jar
├── CITATION.cff
├── Ejecutando
├── example1.gfl
├── export_ast.py
├── geneforge_grammar_v1.2.json
├── geneforge_grammar_v1.3.json
├── geneforge_syntax_v1.2.md
├── geneforgegrammar.json
├── generar_desde_frase_input_v2.py
├── generar_desde_frase_json.py
├── generar_desde_frase_v2.py
├── generar_interactivo.py
├── gfl_benchmark_tasks.md
├── gfl_example.gfl
├── gfl_examples.gfl
├── gfl_to_vcf.py
├── grammar.md
├── license
├── main.py
├── old_parser_root.py
├── ontology.md
├── output_ast.json
├── paper.bib
├── paper.md
├── parselog.txt
├── parser_notebook.ipynb
├── pytest test_parser.py
├── README.md
├── requirements.txt
├── rules.json
├── run_axiom_demo.py
├── sanitize_identifiers.py
├── semillas.json
├── summarize_ast.py
├── syntax_v1.2.md
├── syntax.md
├── test_gfl_logic.gfl
├── test_semantics.py
├── translate_to_geneforgelang.py
├── variant_simulation_plugin.py
├── visualize_ast.py
├── whitepaper.md
├── ..bfg-report/
│   └── 2025-06-08/
│       ├── 23-48-11/
│       │   ├── cache-stats.txt
│       │   ├── deleted-files.txt
│       │   └── object-id-map.old-new.txt
│       ├── 23-48-12/
│       │   ├── cache-stats.txt
│       │   ├── deleted-files.txt
│       │   └── object-id-map.old-new.txt
│       ├── 23-48-13/
│       │   ├── cache-stats.txt
│       │   ├── deleted-files.txt
│       │   └── object-id-map.old-new.txt
│       └── 23-48-17/
│           ├── cache-stats.txt
│           └── object-id-map.old-new.txt
├── .git/...
├── applications/
│   ├── launch_pipeline.py
│   └── pipeline_basic_scRNA.gfl
├── bench/
│   ├── coverage.py
│   ├── expectations.json
│   ├── test_corpus.py
│   └── corpus/
│       ├── 22q11_high_level.gfl
│       ├── 22q11_iPSC_ASO.gfl
│       ├── 22q11_miRNA_pathway.gfl
│       └── 22q11_mouse_ASO.gfl
├── cases/
│   ├── KJ_CRISPR2_GFL_case.md
│   ├── KJ_CRISPR2.yaml
│   └── examples/
│       ├── example_rna_transport.gfl
│       └── stanford_rna_neuron.gfl
├── data/
│   └── example.h5ad
├── docs/
│   ├── Enhancer_Module_Spec.md
│   └── reasoning.md
├── Downloads/
│   └── GeneForgeLang/
│       └── tests/
│           └── test_basic.py
├── examples/
│   ├── example1.gfl
│   ├── example2.gfl
│   ├── gfl_training_data.txt
│   ├── test_editing.gfl
│   ├── test_invalid_semantics.gfl
│   ├── test_multi_editing.gfl
│   └── test_valid_semantics.gfl
├── gf/
│   ├── axioms/
│   │   ├── axiom_store.json
│   │   ├── axiom_tracker.py
│   │   ├── axiom_utils.py
│   │   ├── README.md
│   │   └── __pycache__/
│   └── reasoning/
│       └── engine.py
├── gfl/
│   ├── __init__.py
│   ├── adaptive_reasoner.py
│   ├── axiom_hooks.py
│   ├── evaluator.py
│   ├── gfl_example.gfl
│   ├── grammar_syntax.md
│   ├── grammar.md
│   ├── inference_engine.py
│   ├── interpreter.py
│   ├── lexer.py
│   ├── manual_and_examples.md
│   ├── parser_rules.py
│   ├── parser.py
│   ├── prob_rules.py
│   ├── semantic_validator.py
│   ├── temp_lexer.py
│   ├── test_lexer.py
│   ├── translate_lstm.py
│   ├── validation_pipeline.py
│   ├── validation_registry.py
│   ├── __pycache__/
│   ├── examples/
│   │   ├── axiom_demo.gfl
│   │   └── example1.gfl
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── experiment_runner.py
│   │   └── scanpy_interface.py
│   └── plugins/
│       ├── __init__.py
│       └── plugin_registry.py
├── roadmap_phase_3/
│   ├── .gitignore
│   ├── analyze_long_peaks.py
│   ├── bfg.jar
│   ├── geneforge_grammar_v2.json
│   ├── geneforge_grammar.json
│   ├── process_datasets.py
│   ├── README_reasoning_driven.md
│   ├── syntax_extended.md
│   ├── syntax_v2.md
│   ├── syntax.md
│   └── benchmarking/
│       └── plot_long_peaks.py
├── scripts/
│   ├── clean_requirements.py
│   ├── fix_and_demo.py
│   ├── generate_gfl_data.py
│   ├── patch_lexer_quotes.py
│   ├── train_gfl_model.py
│   └── update_requirements.py
└── venv/
    ├── bin/...
    ├── include/...
    └── lib/...
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/GeneForgeLang.git
    cd GeneForgeLang
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running GFL Scripts

You can execute GFL scripts using the `main.py` interpreter:

```bash
python main.py your_script.gfl
```

### Examples

Explore the `examples/` directory for various GFL code examples.

```gfl
DEFINE GeneSet my_genes = {
    "BRCA1",
    "TP53",
    "EGFR"
};

MESSAGE "Analyzing gene set: " + my_genes.name;

IF my_genes.size > 2 THEN
    MESSAGE "Gene set is large. Performing detailed analysis.";
ELSE
    MESSAGE "Gene set is small. Performing quick analysis.";
END

BRANCH on my_genes.type {
    CASE "oncogenes":
        INVOKE analyze_oncogenes(my_genes);
    CASE "tumor_suppressors":
        INVOKE analyze_tumor_suppressors(my_genes);
    DEFAULT:
        MESSAGE "Unknown gene set type.";
}

TRY
    INVOKE process_data(my_genes);
CATCH err:
    MESSAGE "Error processing data: " + err.message;
FINALLY
    MESSAGE "Data processing attempt completed.";
END
```

## Development

### Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

### Code Style

We adhere to PEP 8 guidelines. Please use a linter (e.g., `flake8` or `ruff`) to ensure your code conforms to the style.

## Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines on how to submit pull requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact

For questions or support, please open an issue on the GitHub repository.
