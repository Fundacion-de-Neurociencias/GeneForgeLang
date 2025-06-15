# GeneForgeLang: A Domain-Specific Language for Bio-simulation Workflows

GeneForgeLang (GFL) is a custom Domain-Specific Language (DSL) designed to simplify and automate complex bio-simulation and analysis workflows. It provides a human-readable syntax to describe multi-step processes involving experimental design, data analysis, and biological simulations.

## Table of Contents
* [Features](#features)
* [Project Structure](#project-structure)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Setup](#setup)
  * [Running the Demo](#running-the-demo)
* [GFL Language Syntax](#gfl-language-syntax)
  * [Analyze Statement](#analyze-statement)
  * [Experiment Statement](#experiment-statement)
  * [Simulate Statement](#simulate-statement)
  * [Branch Statement](#branch-statement)
  * [Comments](#comments)
* [Error Handling and Validation](#error-handling-and-validation)
* [Roadmap (Next Steps)](#roadmap-next-steps)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

---

## Features

GeneForgeLang's compiler (lexer and parser) is built using **PLY (Python Lex-Yacc)** and features:

* **Intuitive Syntax:** Language designed to be close to the natural language of the biological domain.
* **Robust Lexical Analysis (Lexer):**
    * Tokenizes GFL source code, breaking it down into meaningful units (keywords, identifiers, literals, operators, etc.).
    * Handles and ignores whitespace.
* **Dedicated Pre-processor:**
    * A component (`gfl/preprocessor.py`) that specifically removes both single-line (`//`, `#`) and multi-line (`/* ... */`) comments from the GFL code *before* it is passed to the lexer. This simplifies the lexer's responsibilities and maintains a clean token stream.
* **Syntactic Analysis (Parser):**
    * Constructs an Abstract Syntax Tree (AST) from the token stream, rigorously validating the code against the defined GFL grammar.
    * Supports complex nested structures for `analyze`, `experiment`, and `branch` statements.
* **Basic Workflow Evaluation & Validation:** The parser implicitly performs initial workflow evaluation by logging actions and implements basic validation rules for parameters and simulation targets (e.g., checking for valid simulation targets or unknown parameters for specific tools). It also flags some contextual parameter compatibility issues.
* **Structured Output:** The parser generates a list of operations (representing the AST) that can then be interpreted or executed by a backend system.
* **Enhanced Error and Warning Messages:** Provides clear, informative, and user-friendly feedback with specific suggestions, aiding in debugging GFL code.
* **AI-Generated GFL Post-processing (Implicit):** The compiler's design supports the standardization and validation of GFL code, making it suitable for integration with language models that generate GFL.

---

## Project Structure

```
GeneForgeLang/
├── venv/                      # Python virtual environment
├── gfl/
│   ├── __init__.py            # Makes 'gfl' a Python package
│   ├── lexer.py               # Lexical analyzer for GFL (defines tokens)
│   ├── parser.py              # Syntactic analyzer for GFL (defines grammar & builds AST)
│   ├── preprocessor.py        # Handles comment removal from GFL code
│   ├── evaluator.py           # Placeholder for future AST evaluation logic
│   └── gfl_example.gfl        # Example GFL code file
└── scripts/
    ├── __init__.py            # Makes 'scripts' a Python package
    └── fix_and_demo.py        # Main script to run the compiler demo

```

---

## Getting Started

Follow these steps to set up the project and run the demo.

### Prerequisites

* Python 3.8+ installed on your system.
* `venv` module (usually comes with Python 3).
* `pip` (Python package installer).

### Setup

1.  **Navigate to your project directory:**
    ```bash
    cd "$HOME/GeneForgeLang"
    ```
    If you don't have this directory, create it and navigate into it:
    ```bash
    mkdir -p "$HOME/GeneForgeLang"
    cd "$HOME/GeneForgeLang"
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Your terminal prompt should now show `(venv)` at the beginning, indicating the virtual environment is active.

3.  **Install PLY:**
    ```bash
    pip install ply
    ```

4.  **Create / Update project files manually:**
    It's crucial that all `.py` and `.gfl` files have the correct and complete content. Use `nano` (or your preferred text editor) to create/update each file with the content provided in our previous conversation.

    * **`gfl/preprocessor.py`**:
        ```bash
        nano gfl/preprocessor.py
        # Paste content from the artifact "final_preprocessor_code_for_user"
        # Ctrl+O, Enter, Ctrl+X
        ```
    * **`gfl/lexer.py`**:
        ```bash
        nano gfl/lexer.py
        # Paste content from the artifact "final_lexer_code_for_user"
        # Ctrl+O, Enter, Ctrl+X
        ```
    * **`gfl/parser.py`**:
        ```bash
        nano gfl/parser.py
        # Paste content from the artifact "final_parser_code_fixed_grammar"
        # Ctrl+O, Enter, Ctrl+X
        ```
    * **`gfl/gfl_example.gfl`**:
        ```bash
        nano gfl/gfl_example.gfl
        # Paste content from the artifact "final_gfl_example_code_for_user"
        # Ctrl+O, Enter, Ctrl+X
        ```
    * **`scripts/fix_and_demo.py`**:
        ```bash
        nano scripts/fix_and_demo.py
        # Paste content from the artifact "final_demo_script_code_for_user"
        # Ctrl+O, Enter, Ctrl+X
        ```

---

## Usage

To run the current demo which parses `gfl/gfl_example.gfl` and simulated AI outputs:

```bash
PYTHONPATH=. python3 scripts/fix_and_demo.py
```

This command will:
1.  Initialize the lexer and parser.
2.  Parse the `gfl/gfl_example.gfl` file.
3.  Demonstrate the parsing of several simulated AI-generated GFL code snippets.
4.  Output the generated Abstract Syntax Tree (AST) for each successfully parsed section and report any parsing errors or validation warnings.

---

## GFL Language Syntax

Here's a brief overview of the GFL language syntax elements:

### Analyze Statement

Used to define data analysis tasks.

**Block Form:**
```gfl
analyze {
    strategy: "pathway_enrichment",
    thresholds: {
        FDR: 0.05
    }
}
```

**Inline Form (using a specific tool):**
```gfl
analyze using DESeq2 with strategy differential_expression params {
    threshold: 0.05,
    log2FC: 1.0
}
```

### Experiment Statement

Used to configure experimental setups or data types.

```gfl
experiment {
    tool: "DESeq2",
    type: "bulkRNA",
    params: {
        condition_group: "disease",
        control_group: "healthy"
    }
}
```

### Simulate Statement

Used to specify biological simulation targets.

```gfl
simulate cell_growth
```

### Branch Statement

Introduces conditional logic based on a boolean expression.

**With `then` and `else` blocks:**
```gfl
branch {
    if: tumor_size_increased AND cell_death_rate_high
    then: {
        simulate apoptosis
        analyze {
            strategy: "clustering",
            thresholds: {
                resolution: 0.8
            }
        }
    }
    else: {
        simulate cell_division
    }
}
```

**With only a `then` block:**
```gfl
branch {
    if: another_condition
    then: {
        simulate mutation_rate
    }
}
```

### Comments

GFL supports both single-line and multi-line comments. These are removed by the pre-processor before parsing.

```gfl
// This is a single-line comment using double slash
# This is another single-line comment using a hash

/*
This is a multi-line comment.
It can span several lines.
*/
analyze {
    strategy: "example_strategy" // Inline comment
}
```

---

## Error Handling and Validation

The compiler includes logging for various stages (lexer, parser, pre-processor). The parser also has basic validation logic embedded within its production rules to flag common issues like unrecognized simulation targets or invalid parameters for specific tools. Errors are logged to the console, providing clear and informative feedback.

---

## Roadmap (Next Steps)

Currently, the project is in **Phase 0 (Foundations and Proof of Concept)**. The next steps include:

* **Phase 1: Language Enrichment and Semantic Analysis:** Implementation of type validations, valid values, and contextual parameter compatibility. This will build upon the basic validation already present.
* **Phase 2: Integration with Real Bioinformatics Tools:** Development of wrappers for tools like DESeq2, Scanpy, and connection with simulation engines. This phase will bring GFL closer to real-world application.
* **Phase 3: Optimization and Development Tools:** Performance improvements, robust Command Line Interface (CLI), comprehensive documentation, and Integrated Development Environment (IDE) support to enhance user experience and developer productivity.

---

## Contributing

Contributions are welcome! If you're interested in contributing, please feel free to fork this repository, open issues to discuss new features or bugs, and submit pull requests.

---

## License

This project is licensed under the MIT License. A copy of the license details can be found in the `LICENSE` file within the project root directory.

---

## Contact

For any inquiries or further information, please reach out via GitHub issues or your preferred contact method.
