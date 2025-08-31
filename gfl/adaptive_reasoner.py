def apply_adaptive_rules(ast):
    """
    Añade un paso de imputación tras cada experimento con dropout > 0.3.
    """
    new_ast = []
    for node in ast:
        new_ast.append(node)
        if node.get("node_type") == "experiment":
            params = node.get("params", {})
            dropout = params.get("dropout")
            if dropout is not None and float(dropout) > 0.3:
                new_ast.append(
                    {
                        "node_type": "experiment",
                        "tool": node.get("tool", "scanpy"),
                        "type": node.get("type", "scRNA"),
                        "params": {"imputation": True},
                    }
                )
    return new_ast
