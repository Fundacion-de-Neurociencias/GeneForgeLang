# GeneForgeLang: A Domain-Specific Language for Computational Biology

## Overview
GeneForgeLang is a Domain-Specific Language (DSL) designed for biological researchers to describe complex data analysis and simulation workflows in an intuitive, readable, and reproducible manner. Our goal is to simplify interaction with bioinformatics tools and simulation engines, allowing users to focus on biology rather than complex syntax or pipeline management.

## Key Features
* **Intuitive Syntax:** Language designed to be close to the natural language of the biological domain.
* **Robust Lexical and Syntactic Analysis:** Processing GFL code into an Abstract Syntax Tree (AST).
* **Basic Workflow Evaluation:** Simulation of the execution of `analyze`, `experiment`, `simulate`, and `branch` operations.
* **AI-Generated GFL Post-processing:** Ability to standardize and validate GFL code originating from language models.
* **Enhanced Error and Warning Messages:** Clear, informative, and user-friendly feedback with specific suggestions.

## Roadmap (Next Steps)
Currently, the project is in **Phase 0 (Foundations and Proof of Concept)**. The next steps include:
* **Phase 1: Language Enrichment and Semantic Analysis:** Implementation of type validations, valid values, and contextual parameter compatibility.
* **Phase 2: Integration with Real Bioinformatics Tools:** Development of wrappers for tools like DESeq2, Scanpy, and connection with simulation engines.
* **Phase 3: Optimization and Development Tools:** Performance improvements, robust CLI, comprehensive documentation, and IDE support.

## Installation
# * (Add your installation instructions here, e.g.:)
# 1. Clone the repository: `git clone <REPO_URL>`
# 2. Navigate into the project directory: `cd GeneForgeLang`
# 3. Create and activate a virtual environment:
#    ```bash
#    python3 -m venv venv
#    source venv/bin/activate
#    ```
# 4. Install dependencies (if you have a `requirements.txt`):
#    ```bash
#    pip install -r requirements.txt
#    # Or install ply directly if it's the only one:
#    pip install ply
#    ```

## Usage
# * (Add examples of how to run the parser, evaluator, or demo here, e.g.:)
# To run the current demo:
# ```bash
# (venv) user@DESKTOP-MKJRNF0:~/GeneForgeLang$ PYTHONPATH=. python3 scripts/fix_and_demo.py
# ```
# To test the parser with a GFL file:
# ```bash
# (venv) user@DESKTOP-MKJRNF0:~/GeneForgeLang$ PYTHONPATH=. python3 gfl/parser.py gfl/gfl_example.gfl
# ```

## Project Structure
.
├── gfl/                  # Language core: lexer, parser, evaluator, AST
│   ├── init.py
│   ├── lexer.py          # Definition of tokens and lexical rules
│   ├── parser.py         # Grammar definition and AST construction
│   ├── evaluator.py      # Logic for AST evaluation (or where it will be moved)
│   └── gfl_example.gfl   # Example GFL code file
├── scripts/              # Utility scripts, demos, etc.
│   ├── init.py
│   └── fix_and_demo.py   # Main demonstration script (parsing, evaluation, post-processing)
├── venv/                 # Python virtual environment
├── .gitignore            # File for ignoring files in Git
├── README.md             # Main project documentation
└── requirements.txt      # Project dependencies


## Contribution
Contributions are welcome! Please refer to the [contribution guidelines](CONTRIBUTING.md) (if you create one).

## License
This project is licensed under the [MIT License](LICENSE) (or your chosen license).

## Contact
[Your Name/Email/GitHub]
