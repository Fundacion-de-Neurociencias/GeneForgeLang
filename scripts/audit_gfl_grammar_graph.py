"""CLI entry point for GFL static AST grammar audit."""

import sys
from geneforgelang.core.grammar_graph import main_audit_cli

if __name__ == "__main__":
    sys.exit(main_audit_cli())
