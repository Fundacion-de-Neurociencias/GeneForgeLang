"""CLI entry point for bridging GFL domain scripts into Graphify."""

import sys
from geneforgelang.core.grammar_graph import main_bridge_cli

if __name__ == "__main__":
    sys.exit(main_bridge_cli())
