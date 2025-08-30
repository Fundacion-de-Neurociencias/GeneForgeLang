from gfl.lexer import GFLLexer  # Importación necesaria para acceder a los tokens


class GFLParser:
    # Define los tokens que este parser reconocerá.
    tokens = GFLLexer.tokens

    # Define el símbolo de inicio de tu gramática GFL.
    start = "gfl_code"

    # Importante: No hay un método __init__ aquí que cree lexer o parser de PLY.
    # Esos se crean centralmente en gfl/parser.py.

    # --- Reglas de Producción de la Gramática GFL ---

    # Regla principal: un programa GFL es una secuencia de sentencias.
    def p_gfl_code(self, p):
        """gfl_code : statements"""
        p[0] = p[1]

    # Una secuencia de sentencias.
    def p_statements(self, p):
        """statements : statement
        | statements statement"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # Una sentencia puede ser de varios tipos.
    def p_statement(self, p):
        """statement : analyze_statement
        | experiment_statement
        | simulate_statement
        | branch_statement"""
        p[0] = p[1]

    # Sentencia ANALYZE
    def p_analyze_statement(self, p):
        """analyze_statement : ANALYZE LBRACE properties RBRACE"""
        p[0] = {"node_type": "analyze", "properties": p[3]}

    # Sentencia EXPERIMENT
    def p_experiment_statement(self, p):
        """experiment_statement : EXPERIMENT LBRACE properties RBRACE"""
        p[0] = {"node_type": "experiment", "properties": p[3]}

    # Sentencia SIMULATE
    def p_simulate_statement(self, p):
        """simulate_statement : SIMULATE IDENTIFIER
        | SIMULATE IDENTIFIER properties"""
        if len(p) == 3:
            p[0] = {"node_type": "simulate", "target": p[2]}
        else:
            p[0] = {"node_type": "simulate", "target": p[2], "properties": p[3]}

    # Sentencia BRANCH (IF-THEN-ELSE)
    def p_branch_statement(self, p):
        """branch_statement : BRANCH LBRACE IF COLON condition THEN COLON statements RBRACE
        | BRANCH LBRACE IF COLON condition THEN COLON statements ELSE COLON statements RBRACE
        """
        if len(p) == 10:  # Sin ELSE
            p[0] = {"node_type": "branch", "condition": p[5], "then_block": p[8]}
        elif len(p) == 13:  # Con ELSE
            p[0] = {
                "node_type": "branch",
                "condition": p[5],
                "then_block": p[8],
                "else_block": p[11],
            }

    # Definición de condiciones para las ramas.
    def p_condition(self, p):
        """condition : IDENTIFIER EQUALS value
        | IDENTIFIER NOT_EQUALS value
        | IDENTIFIER LT value
        | IDENTIFIER GT value
        | IDENTIFIER LTE value
        | IDENTIFIER GTE value
        | condition AND condition
        | condition OR condition
        | LPAREN condition RPAREN"""
        if len(p) == 4 and p[2] in ("==", "!=", "<", ">", "<=", ">="):
            p[0] = {"type": "comparison", "left": p[1], "operator": p[2], "right": p[3]}
        elif len(p) == 4 and p[2] in ("AND", "OR"):
            p[0] = {"type": "logical", "operator": p[2], "left": p[1], "right": p[3]}
        elif len(p) == 4 and p[1] == "(" and p[3] == ")":
            p[0] = p[2]  # Manejar paréntesis para agrupar condiciones
        else:
            p[0] = {"type": "identifier_condition", "value": p[1]}

    # Colección de propiedades: usa una lista de propiedades separadas por comas.
    def p_properties(self, p):
        """properties : property_list"""
        p[0] = p[1]

    # Lista de propiedades, permitiendo separación por comas.
    def p_property_list(self, p):
        """property_list : property
        | property_list COMMA property"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [
                p[3]
            ]  # p[1] es la lista existente, p[3] es la nueva propiedad después de la coma

    # Una propiedad individual: un identificador seguido de un valor.
    def p_property(self, p):
        """property : IDENTIFIER COLON value"""
        p[0] = {p[1]: p[3]}

    # Un valor puede ser un string, número, booleano, o un bloque de propiedades anidado.
    def p_value(self, p):
        """value : STRING
        | NUMBER
        | IDENTIFIER
        | TRUE
        | FALSE
        | LBRACE properties RBRACE"""
        if p[1] == "{":
            p[0] = p[2]  # Para propiedades anidadas
        else:
            p[0] = p[1]

    # Manejo de errores de sintaxis.
    def p_error(self, p):
        if p:
            print(f"Syntax error at '{p.value}', type '{p.type}' at line {p.lineno}")
        else:
            print("Syntax error at EOF (End of File)")
