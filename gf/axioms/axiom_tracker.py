axioms = []


def register_axiom_candidates(ast):
    """
    Registra axiomas a partir de nodos AST del tipo 'simulate'
    """
    for node in ast:
        if isinstance(node, dict) and node.get("type") == "simulate":
            axioms.append({"expr": node["target"], "weight": 1})


def show_axioms():
    print("=== Axiomas registrados ===")
    if not axioms:
        print("(ninguno)")
    for ax in axioms:
        print(f"• {ax['expr']} (peso: {ax['weight']})")
