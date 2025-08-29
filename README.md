GeneForgeLang (GFL)

GFL is a domain-specific language for specifying, validating, and reasoning about genomic workflows and experiments. It is intended primarily as a library for other applications to embed, with a few small demo apps included.

What GFL provides
- Parser: YAML-like DSL parsed into a stable, JSON-serializable AST.
- Validator: Minimal semantic checks (symbols, branches, plugin calls).
- Interpreter: Simple AST walker with optional plugin invocation.
- Probabilistic layer: Likelihood-ratio rules to post-process model outputs.
- Extensibility: Plugin registry for external tools and domain integrations.

Install
- Python 3.9+
- Recommended: `pip install -e .` using the provided `pyproject.toml`.
- Optional extras: `pip install -e .[apps]` for demo apps (Gradio + Gemini), `.[lexer]` for PLY-based experiments, `.[ml]` for heavy ML stacks.

Quick start
- Parse and validate
  - from gfl.api import parse, validate
  - ast = parse("""
    experiment:
      tool: CRISPR_cas9
      type: gene_editing
      params:
        target_gene: TP53
    """)
  - errors = validate(ast)
  - assert not errors

- Reasoning with your model
  - from gfl.api import infer
  - class DummyModel:
      def predict(self, feats): return {"label": "benign"}
  - result = infer(DummyModel(), ast)

Repository layout
- gfl/: core library (parser, validator, interpreter, rules, plugins, execution)
- applications/: demos and sample apps
- integrations/: placeholders for Java/JS integrations (not used by core)
- docs/: design notes and deeper language docs
- examples/: sample GFL scripts
- bench/: corpus and benchmarking helpers

Stability and API
- Public API: `gfl/api.py` exposes parse/validate/infer and is kept stable.
- Internals may evolve. Use the API from third-party apps.
- AST shape: dictionary-based; fields are stable for core constructs.

Design notes (high level)
- Language: YAML-like, declarative; key blocks: `experiment`, `analyze`, `simulate`, `branch` (with if/then[/else]).
- Validation: minimal and permissive; meant to catch obvious misuses.
- Reasoning: optional probabilistic post-processing via simple LR rules.
- Plugins: registry-based; demo plugins auto-register if importable.

Demo apps
- Natural language → GFL translator (Gemini/Gradio): `applications/translator_app/app.py`
  - Requires `GOOGLE_API_KEY` in `.env` (see file header).

Roadmap (proposed)
- Language
  - Modules/namespaces and imports for reusable building blocks
  - Types and schemas for entities (Gene, Variant, Vector, CellType)
  - Stronger branching/guards; pattern-matching on assay results
  - IO contracts: typed inputs/outputs on `experiment/analyze/simulate`
  - Validation linting rules and severity levels
  - VCF/ANN fields as first-class references; provenance annotations

- Reasoning
  - Probabilistic facts and rule learning from corpora
  - Explanation graph enriched with evidence and confidence traces

- Tooling / repo
  - Package via `pyproject.toml` (done); optional extras split
  - Tests under `tests/` with fixtures for examples and bench corpora
  - CI, pre-commit hooks (black, isort, ruff) [not included here]
  - Clear plugin interface docs + typed stubs

Contributing
- See `CONTRIBUTING.MD`. Please prefer English in new code and docs.

License
- MIT (see `license`).

