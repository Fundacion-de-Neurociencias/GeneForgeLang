from gfl.lexer import tokens
from gf.axioms import axiom_tracker

# Ejemplo: validador muy simple
def validate_node(node):
    if isinstance(node, dict) and "type" in node:
        event = f"{node['type']}({node.get('name', 'unknown')})"
        axiom_tracker.add_event(event, weight=1.0)
        return True
    return False

def validate_ast(ast):
    if isinstance(ast, list):
        for node in ast:
            validate_node(node)
    elif isinstance(ast, dict):
        validate_node(ast)
