import sys
import os

# Add the parent directory to the Python path to allow importing 'gfl'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gfl.lexer import lexer # Import the lexer instance directly
from gfl.parser import GFLParser

def run_parser_demo(parser, code_snippets):
    """Runs the parser on a list of GFL code snippets."""
    print("\n--- GFL Parser Demo ---")
    for i, (name, gfl_code) in enumerate(code_snippets):
        print(f"\nParsing {name} (Snippet {i+1}):")
        print("----------------------------------------")
        print(gfl_code)
        print("----------------------------------------")

        # Parse the code directly without preprocessing for now
        operations = parser.parse(gfl_code)

        if parser.errors:
            print("\nParsing Errors/Warnings:")
            for error in parser.errors:
                print(f"  - {error}")
            parser.errors = [] # Clear errors for next snippet
        else:
            print("\nSuccessfully Parsed! Generated AST (Operations):")
            if operations:
                for op in operations:
                    print(f"  {op}")
            else:
                print("  No operations generated (empty or only comments).")

if __name__ == "__main__":
    # Initialize the lexer and parser
    # Pass the lexer instance directly
    gfl_parser = GFLParser(lexer)

    # 1. Parse gfl_example.gfl
    gfl_example_path = os.path.join(os.path.dirname(__file__), '..', 'gfl', 'gfl_example.gfl')
    try:
        with open(gfl_example_path, 'r') as f:
            gfl_example_code = f.read()
        run_parser_demo(gfl_parser, [("gfl/gfl_example.gfl", gfl_example_code)])
    except FileNotFoundError:
        print(f"Error: gfl_example.gfl not found at {gfl_example_path}. Please ensure it exists.")

    # 2. Simulate AI-generated GFL code snippets
    ai_snippets = [
        ("AI-Generated Scenario 1 (Simple Analyze)",
         """analyze {
             strategy: "pathway_enrichment",
             thresholds: {
                 FDR: 0.05
             }
         }"""
        ),
        ("AI-Generated Scenario 2 (Complex Branch)",
         """branch {
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
         }"""
        ),
        ("AI-Generated Scenario 3 (Experiment and Simulate)",
         """experiment {
             tool: "CRISPR",
             type: "gene_knockout",
             params: {
                 target_gene: "TP53",
                 guide_RNA: "AGCTAGCTAGCTAGCT"
             }
         }
         simulate gene_expression"""
        ),
        ("AI-Generated Scenario 4 (Phenotype Analyze)",
         """ANALYZE {
             strategy: "few_shot_diagnosis",
             tool: "SHEPHERD",
             phenotype_terms: ["ataxia", "epilepsy", "microcephaly"],
             candidate_genes: ["SCN2A", "ATM", "MECP2"]
         }"""
        ),
        ("AI-Generated Scenario 5 (Analyze with new inline syntax)",
         """analyze using DESeq2 with strategy differential_expression params {
             threshold: 0.05,
             log2FC: 1.0,
             condition_group: "treated",
             control_group: "untreated"
         }"""
        ),
        ("AI-Generated Scenario 6 (Analyze with another new inline syntax)",
         """analyze using Scanpy with strategy clustering params {
             resolution: 0.7,
             method: "leiden"
         }"""
        ),
        ("AI-Generated Scenario 7 (Invalid Tool/Strategy)",
         """analyze using UnknownTool with strategy invalid_strategy params {
             param1: "value1"
         }"""
        ),
        ("AI-Generated Scenario 8 (Invalid Parameter for Strategy)",
         """analyze using DESeq2 with strategy differential_expression params {
             threshold: 0.05,
             invalid_param: "error_value"
         }"""
        )
    ]
    run_parser_demo(gfl_parser, ai_snippets)