GeneForgeLang: A Domain-Specific Language for Bio-simulation WorkflowsGeneForgeLang (GFL) is a custom Domain-Specific Language (DSL) designed to simplify and automate complex bio-simulation and analysis workflows. It provides a human-readable syntax to describe multi-step processes involving experimental design, data analysis, and biological simulations.Table of ContentsFeaturesProject StructureGetting StartedPrerequisitesSetupRunning the DemoGFL Language SyntaxAnalyze StatementExperiment StatementSimulate StatementBranch StatementCommentsError Handling and ValidationRoadmap (Next Steps)ContributingLicenseContactFeaturesGeneForgeLang's compiler (lexer and parser) is built using PLY (Python Lex-Yacc) and features:Intuitive Syntax: Language designed to be close to the natural language of the biological domain.Robust Lexical Analysis (Lexer):Tokenizes GFL source code, breaking it down into meaningful units (keywords, identifiers, literals, operators, etc.).Handles and ignores whitespace.Dedicated Pre-processor:A component (gfl/preprocessor.py) that specifically removes both single-line (//, #) and multi-line (/* ... */) comments from the GFL code before it is passed to the lexer. This simplifies the lexer's responsibilities and maintains a clean token stream.Syntactic Analysis (Parser):Constructs an Abstract Syntax Tree (AST) from the token stream, rigorously validating the code against the defined GFL grammar.Supports complex nested structures for analyze, experiment, and branch statements.Basic Workflow Evaluation & Validation: The parser implicitly performs initial workflow evaluation by logging actions and implements basic validation rules for parameters and simulation targets (e.g., checking for valid simulation targets or unknown parameters for specific tools). It also flags some contextual parameter compatibility issues.Structured Output: The parser generates a list of operations (representing the AST) that can then be interpreted or executed by a backend system.Enhanced Error and Warning Messages: Provides clear, informative, and user-friendly feedback with specific suggestions, aiding in debugging GFL code.AI-Generated GFL Post-processing (Implicit): The compiler's design supports the standardization and validation of GFL code, making it suitable for integration with language models that generate GFL.Project StructureGeneForgeLang/
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

Getting StartedFollow these steps to set up the project and run the demo.PrerequisitesPython 3.8+ installed on your system.venv module (usually comes with Python 3).pip (Python package installer).SetupNavigate to your project directory:cd "$HOME/GeneForgeLang"
If you don't have this directory, create it and navigate into it:mkdir -p "$HOME/GeneForgeLang"
cd "$HOME/GeneForgeLang"
Create and activate a Python virtual environment:python3 -m venv venv
source venv/bin/activate
Your terminal prompt should now show (venv) at the beginning, indicating the virtual environment is active.Install PLY:pip install ply
Create / Update project files manually:It's crucial that all .py and .gfl files have the correct and complete content. Use nano (or your preferred text editor) to create/update each file with the content provided in our previous conversation.gfl/preprocessor.py:nano gfl/preprocessor.py
# Paste content from the artifact "final_preprocessor_code_for_user"
# Ctrl+O, Enter, Ctrl+X
gfl/lexer.py:nano gfl/lexer.py
# Paste content from the artifact "final_lexer_code_for_user"
# Ctrl+O, Enter, Ctrl+X
gfl/parser.py:nano gfl/parser.py
# Paste content from the artifact "final_parser_code_fixed_grammar"
# Ctrl+O, Enter, Ctrl+X
gfl/gfl_example.gfl:nano gfl/gfl_example.gfl
# Paste content from the artifact "final_gfl_example_code_for_user"
# Ctrl+O, Enter, Ctrl+X
scripts/fix_and_demo.py:nano scripts/fix_and_demo.py
# Paste content from the artifact "final_demo_script_code_for_user"
# Ctrl+O, Enter, Ctrl+X
UsageTo run the current demo which parses gfl/gfl_example.gfl and simulated AI outputs:PYTHONPATH=. python3 scripts/fix_and_demo.py
This command will:Initialize the lexer and parser.Parse the gfl/gfl_example.gfl file.Demonstrate the parsing of several simulated AI-generated GFL code snippets.Output the generated Abstract Syntax Tree (AST) for each successfully parsed section and report any parsing errors or validation warnings.GFL Language SyntaxHere's a brief overview of the GFL language syntax elements:Analyze StatementUsed to define data analysis tasks.Block Form:analyze {
    strategy: "pathway_enrichment",
    thresholds: {
        FDR: 0.05
    }
}
Inline Form (using a specific tool):analyze using DESeq2 with strategy differential_expression params {
    threshold: 0.05,
    log2FC: 1.0
}
Experiment StatementUsed to configure experimental setups or data types.experiment {
    tool: "DESeq2",
    type: "bulkRNA",
    params: {
        condition_group: "disease",
        control_group: "healthy"
    }
}
Simulate StatementUsed to specify biological simulation targets.simulate cell_growth
Branch StatementIntroduces conditional logic based on a boolean expression.With then and else blocks:branch {
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
With only a then block:branch {
    if: another_condition
    then: {
        simulate mutation_rate
    }
}
CommentsGFL supports both single-line and multi-line comments. These are removed by the pre-processor before parsing.// This is a single-line comment using double slash
# This is another single-line comment using a hash

/*
This is a multi-line comment.
It can span several lines.
*/
analyze {
    strategy: "example_strategy" // Inline comment
}
Error Handling and ValidationThe compiler includes logging for various stages (lexer, parser, pre-processor). The parser also has basic validation logic embedded within its production rules to flag common issues like unrecognized simulation targets or invalid parameters for specific tools. Errors are logged to the console, providing clear and informative feedback.Roadmap (Next Steps)Currently, the project is in Phase 0 (Foundations and Proof of Concept). The next steps include:Phase 1: Language Enrichment and Semantic Analysis: Implementation of type validations, valid values, and contextual parameter compatibility. This will build upon the basic validation already present.Phase 2: Integration with Real Bioinformatics Tools: Development of wrappers for tools like DESeq2, Scanpy, and connection with simulation engines. This phase will bring GFL closer to real-world application.Phase 3: Optimization and Development Tools: Performance improvements, robust Command Line Interface (CLI), comprehensive documentation, and Integrated Development Environment (IDE) support to enhance user experience and developer productivity.ContributingContributions are welcome! If you're interested in contributing, please feel free to fork this repository, open issues to discuss new features or bugs, and submit pull requests.LicenseThis project is licensed under the MIT License. A copy of the license details can be found in the LICENSE file within the project root directory.ContactFor any inquiries or further information, please reach out via GitHub issues or your preferred contact method.
