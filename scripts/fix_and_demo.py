import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gfl.lexer import lexer
from gfl.parser_rules import parser
from gfl.adaptive_reasoner import apply_adaptive_rules
from gfl.execution.experiment_runner import run_experiment
from pprint import pprint

def feedback_cycle(ast, max_cycles=3):
    cycle = 0
    ast_current = ast
    while cycle < max_cycles:
        print(f"\n== CICLO DE FEEDBACK #{cycle+1} ==")
        new_ast = []
        feedback_applied = False
        idx = 0
        while idx < len(ast_current):
            node = ast_current[idx]
            if (
                node.get("node_type") == "experiment"
                and not node.get("fixed")
                and not node.get("params", {}).get("imputation")
            ):
                print(f"  > Ejecutando experimento '{node.get('type')}' con {node.get('params')}")
                result = run_experiment(node)
                print(f"    ...resultado: {result}")
                if result["status"] == "bad_quality" and not feedback_applied:
                    imput_node = {
                        "node_type": "experiment",
                        "tool": node.get("tool", "scanpy"),
                        "type": node.get("type", "scRNA"),
                        "params": {"imputation": True},
                        "fixed": True
                    }
                    node = dict(node)
                    node["fixed"] = True
                    new_ast.append(node)
                    new_ast.append(imput_node)
                    print("    ...[IMPUTACIÓN INYECTADA EN PIPELINE]")
                    feedback_applied = True
                    idx += 1
                    continue
            new_ast.append(node)
            idx += 1
        if not feedback_applied:
            print("  ✔️  No se requiere más feedback adaptativo.")
            break
        ast_current = new_ast
        cycle += 1
    return ast_current

if __name__ == "__main__":
    # Asegúrate de que examples/example1.gfl existe y es válido
    with open("examples/example1.gfl") as f:
        source = f.read()
    ast = parser.parse(source, lexer=lexer)
    print("\n🧠 AST inicial:")
    pprint(ast)
    ast_adapted = apply_adaptive_rules(ast)
    print("\n🧠 AST tras adaptación inicial:")
    pprint(ast_adapted)
    ast_final = feedback_cycle(ast_adapted)
    print("\n🧠 AST final tras feedback loop:")
    pprint(ast_final)
