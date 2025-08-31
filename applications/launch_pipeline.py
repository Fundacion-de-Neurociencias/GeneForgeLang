import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pprint import pprint

from gfl.adaptive_reasoner import apply_adaptive_rules
from gfl.lexer import lexer
from gfl.parser_rules import parser

if __name__ == "__main__":
    with open("applications/pipeline_basic_scRNA.gfl") as f:
        source = f.read()
    ast = parser.parse(source, lexer=lexer)
    print("\\n🧠 AST inicial:")
    pprint(ast)
    ast_adapted = apply_adaptive_rules(ast)
    print("\\n🧠 AST tras adaptación inicial:")
    pprint(ast_adapted)
    # Optionally, call feedback_cycle here if needed
