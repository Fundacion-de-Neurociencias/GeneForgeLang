#!/usr/bin/env python3
"""Simple test for the grammar parser."""

try:
    from gfl.grammar_parser import parse_gfl_grammar

    # Test simple experiment
    code = """experiment: {
        tool: "CRISPR_cas9",
        type: "gene_editing"
    }"""

    print("Testing grammar parser...")
    result = parse_gfl_grammar(code)

    print(f"Parse successful: {result.is_valid}")

    if result.is_valid:
        print(f"AST type: {result.ast.get('type')}")
        statements = result.ast.get("statements", [])
        print(f"Number of statements: {len(statements)}")
        if statements:
            print(f"First statement type: {statements[0].get('type')}")
    else:
        print(f"Syntax errors: {len(result.syntax_errors)}")
        for error in result.syntax_errors[:3]:  # Show first 3 errors
            print(f"  - {error.message}")

except ImportError as e:
    print(f"Import error: {e}")
    print("PLY might not be installed. Install with: pip install ply")
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
