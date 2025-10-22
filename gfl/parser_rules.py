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
        | branch_statement
        | loci_statement
        | rules_statement
        | transcripts_statement
        | proteins_statement
        | metabolites_statement"""
        p[0] = p[1]

    # Sentencia ANALYZE
    def p_analyze_statement(self, p):
        """analyze_statement : ANALYZE LBRACE properties RBRACE"""
        p[0] = {"node_type": "analyze", "properties": p[3]}

    # Sentencia EXPERIMENT
    def p_experiment_statement(self, p):
        """experiment_statement : EXPERIMENT LBRACE properties RBRACE"""
        p[0] = {"node_type": "experiment", "properties": p[3]}

    # Sentencia SIMULATE - Enhanced for spatial genomic reasoning
    def p_simulate_statement(self, p):
        """simulate_statement : SIMULATE IDENTIFIER
        | SIMULATE IDENTIFIER properties
        | SIMULATE LBRACE simulation_properties RBRACE"""
        if len(p) == 3:
            p[0] = {"node_type": "simulate", "target": p[2]}
        elif len(p) == 4:
            p[0] = {"node_type": "simulate", "target": p[2], "properties": p[3]}
        else:
            p[0] = {"node_type": "simulate", "properties": p[3]}

    def p_simulation_properties(self, p):
        """simulation_properties : simulation_property
        | simulation_properties COMMA simulation_property"""
        if len(p) == 2:
            p[0] = {p[1][0]: p[1][1]}
        else:
            p[0] = {**p[1], p[3][0]: p[3][1]}

    def p_simulation_property(self, p):
        """simulation_property : NAME COLON STRING
        | ACTION COLON action
        | QUERY COLON query_list
        | DESCRIPTION COLON STRING"""
        if p[1] == "name":
            p[0] = ("name", p[3])
        elif p[1] == "action":
            p[0] = ("action", p[3])
        elif p[1] == "query":
            p[0] = ("query", p[3])
        elif p[1] == "description":
            p[0] = ("description", p[3])
        else:
            p[0] = (p[1], p[3])

    def p_query_list(self, p):
        """query_list : query_item
        | query_list COMMA query_item"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_query_item(self, p):
        """query_item : GET_ACTIVITY LPAREN ID RPAREN
        | GET_ACTIVITY LPAREN ID COMMA LEVEL COLON STRING RPAREN"""
        if len(p) == 5:
            p[0] = {"type": "get_activity", "element": p[3]}
        else:
            p[0] = {"type": "get_activity", "element": p[3], "level": p[6]}

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
            p[0] = p[1] + [p[3]]  # p[1] es la lista existente, p[3] es la nueva propiedad después de la coma

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

    # Sentencia LOCI - Define regiones genómicas y coordenadas
    def p_loci_statement(self, p):
        """loci_statement : LOCI LBRACE loci_list RBRACE"""
        p[0] = {"node_type": "loci", "loci": p[3]}

    def p_loci_list(self, p):
        """loci_list : locus_definition
        | loci_list COMMA locus_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_locus_definition(self, p):
        """locus_definition : LBRACE locus_properties RBRACE"""
        p[0] = p[2]

    def p_locus_properties(self, p):
        """locus_properties : locus_property
        | locus_properties COMMA locus_property"""
        if len(p) == 2:
            p[0] = {p[1][0]: p[1][1]}
        else:
            p[0] = {**p[1], p[3][0]: p[3][1]}

    def p_locus_property(self, p):
        """locus_property : ID COLON value
        | CHROMOSOME COLON STRING
        | START COLON NUMBER
        | END COLON NUMBER
        | ELEMENTS COLON LBRACKET elements_list RBRACKET
        | HAPLOTYPE_PANEL COLON STRING"""
        if p[1] == "chromosome":
            p[0] = ("chromosome", p[3])
        elif p[1] == "start":
            p[0] = ("start", p[3])
        elif p[1] == "end":
            p[0] = ("end", p[3])
        elif p[1] == "elements":
            p[0] = ("elements", p[4])
        elif p[1] == "haplotype_panel":
            p[0] = ("haplotype_panel", p[3])
        else:
            p[0] = (p[1], p[3])

    def p_elements_list(self, p):
        """elements_list : element_definition
        | elements_list COMMA element_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_element_definition(self, p):
        """element_definition : LBRACE element_properties RBRACE"""
        p[0] = p[2]

    def p_element_properties(self, p):
        """element_properties : element_property
        | element_properties COMMA element_property"""
        if len(p) == 2:
            p[0] = {p[1][0]: p[1][1]}
        else:
            p[0] = {**p[1], p[3][0]: p[3][1]}

    def p_element_property(self, p):
        """element_property : ID COLON value
        | TYPE COLON STRING"""
        if p[1] == "type":
            p[0] = ("type", p[3])
        else:
            p[0] = (p[1], p[3])

    # Sentencia RULES - Define reglas con predicados espaciales
    def p_rules_statement(self, p):
        """rules_statement : RULES LBRACE rules_list RBRACE"""
        p[0] = {"node_type": "rules", "rules": p[3]}

    def p_rules_list(self, p):
        """rules_list : rule_definition
        | rules_list COMMA rule_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_rule_definition(self, p):
        """rule_definition : LBRACE rule_properties RBRACE"""
        p[0] = p[2]

    def p_rule_properties(self, p):
        """rule_properties : rule_property
        | rule_properties COMMA rule_property"""
        if len(p) == 2:
            p[0] = {p[1][0]: p[1][1]}
        else:
            p[0] = {**p[1], p[3][0]: p[3][1]}

    def p_rule_property(self, p):
        """rule_property : ID COLON value
        | DESCRIPTION COLON STRING
        | IF COLON spatial_condition
        | THEN COLON action_list"""
        if p[1] == "description":
            p[0] = ("description", p[3])
        elif p[1] == "if":
            p[0] = ("if", p[3])
        elif p[1] == "then":
            p[0] = ("then", p[3])
        else:
            p[0] = (p[1], p[3])

    def p_spatial_condition(self, p):
        """spatial_condition : IS_WITHIN LPAREN ID COMMA ID RPAREN
        | DISTANCE_BETWEEN LPAREN ID COMMA ID RPAREN
        | IS_IN_CONTACT LPAREN ID COMMA ID COMMA USING COLON STRING RPAREN
        | spatial_condition AND spatial_condition
        | spatial_condition OR spatial_condition
        | NOT spatial_condition
        | LPAREN spatial_condition RPAREN"""
        if len(p) == 7 and p[1] == "is_within":
            p[0] = {"type": "is_within", "element": p[3], "locus": p[5]}
        elif len(p) == 7 and p[1] == "distance_between":
            p[0] = {"type": "distance_between", "element_a": p[3], "element_b": p[5]}
        elif len(p) == 10 and p[1] == "is_in_contact":
            p[0] = {"type": "is_in_contact", "element_a": p[3], "element_b": p[5], "hic_map": p[8]}
        elif len(p) == 4 and p[1] == "not":
            p[0] = {"type": "not", "condition": p[2]}
        elif len(p) == 4 and p[2] in ("and", "or"):
            p[0] = {"type": "logical", "operator": p[2], "left": p[1], "right": p[3]}
        elif len(p) == 4 and p[1] == "(" and p[3] == ")":
            p[0] = p[2]
        else:
            p[0] = {"type": "unknown", "raw": p}

    def p_action_list(self, p):
        """action_list : action
        | action_list COMMA action"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_action(self, p):
        """action : SET_ACTIVITY LPAREN ID COMMA LEVEL COLON STRING RPAREN
        | MOVE LPAREN ID COMMA TO COLON STRING RPAREN"""
        if p[1] == "set_activity":
            p[0] = {"type": "set_activity", "element": p[3], "level": p[6]}
        elif p[1] == "move":
            p[0] = {"type": "move", "element": p[3], "destination": p[6]}

    # Multi-omic statements v2.0
    def p_transcripts_statement(self, p):
        """transcripts_statement : TRANSCRIPTS LBRACE transcript_list RBRACE"""
        p[0] = {"node_type": "transcripts", "transcripts": p[3]}

    def p_transcript_list(self, p):
        """transcript_list : transcript_definition
        | transcript_list COMMA transcript_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_transcript_definition(self, p):
        """transcript_definition : ID COLON LBRACE transcript_properties RBRACE"""
        p[0] = {"id": p[1], "properties": p[4]}

    def p_transcript_properties(self, p):
        """transcript_properties : transcript_property
        | transcript_properties COMMA transcript_property"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_transcript_property(self, p):
        """transcript_property : GENE_SOURCE COLON STRING
        | EXONS COLON LBRACKET exon_list RBRACKET
        | IDENTIFIERS COLON LBRACE identifier_dict RBRACE"""
        if p[1] == "gene_source":
            p[0] = {"type": "gene_source", "value": p[3]}
        elif p[1] == "exons":
            p[0] = {"type": "exons", "value": p[4]}
        elif p[1] == "identifiers":
            p[0] = {"type": "identifiers", "value": p[4]}

    def p_exon_list(self, p):
        """exon_list : NUMBER
        | exon_list COMMA NUMBER"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_proteins_statement(self, p):
        """proteins_statement : PROTEINS LBRACE protein_list RBRACE"""
        p[0] = {"node_type": "proteins", "proteins": p[3]}

    def p_protein_list(self, p):
        """protein_list : protein_definition
        | protein_list COMMA protein_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_protein_definition(self, p):
        """protein_definition : ID COLON LBRACE protein_properties RBRACE"""
        p[0] = {"id": p[1], "properties": p[4]}

    def p_protein_properties(self, p):
        """protein_properties : protein_property
        | protein_properties COMMA protein_property"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_protein_property(self, p):
        """protein_property : TRANSLATES_FROM COLON TRANSCRIPT LPAREN ID RPAREN
        | DOMAINS COLON LBRACKET domain_list RBRACKET
        | IDENTIFIERS COLON LBRACE identifier_dict RBRACE"""
        if p[1] == "translates_from":
            p[0] = {"type": "translates_from", "value": p[5]}
        elif p[1] == "domains":
            p[0] = {"type": "domains", "value": p[4]}
        elif p[1] == "identifiers":
            p[0] = {"type": "identifiers", "value": p[4]}

    def p_domain_list(self, p):
        """domain_list : domain_definition
        | domain_list COMMA domain_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_domain_definition(self, p):
        """domain_definition : LBRACE domain_properties RBRACE"""
        p[0] = p[2]

    def p_domain_properties(self, p):
        """domain_properties : domain_property
        | domain_properties COMMA domain_property"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_domain_property(self, p):
        """domain_property : ID COLON STRING
        | START COLON NUMBER
        | END COLON NUMBER"""
        if p[1] == "id":
            p[0] = {"type": "id", "value": p[3]}
        elif p[1] == "start":
            p[0] = {"type": "start", "value": p[3]}
        elif p[1] == "end":
            p[0] = {"type": "end", "value": p[3]}

    def p_metabolites_statement(self, p):
        """metabolites_statement : METABOLITES LBRACE metabolite_list RBRACE"""
        p[0] = {"node_type": "metabolites", "metabolites": p[3]}

    def p_metabolite_list(self, p):
        """metabolite_list : metabolite_definition
        | metabolite_list COMMA metabolite_definition"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_metabolite_definition(self, p):
        """metabolite_definition : ID COLON LBRACE metabolite_properties RBRACE"""
        p[0] = {"id": p[1], "properties": p[4]}

    def p_metabolite_properties(self, p):
        """metabolite_properties : metabolite_property
        | metabolite_properties COMMA metabolite_property"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_metabolite_property(self, p):
        """metabolite_property : FORMULA COLON STRING
        | IDENTIFIERS COLON LBRACE identifier_dict RBRACE"""
        if p[1] == "formula":
            p[0] = {"type": "formula", "value": p[3]}
        elif p[1] == "identifiers":
            p[0] = {"type": "identifiers", "value": p[4]}

    def p_identifier_dict(self, p):
        """identifier_dict : ID COLON STRING
        | identifier_dict COMMA ID COLON STRING"""
        if len(p) == 4:
            p[0] = {p[1]: p[3]}
        else:
            p[0] = p[1]
            p[0][p[3]] = p[5]

    # Manejo de errores de sintaxis.
    def p_error(self, p):
        if p:
            print(f"Syntax error at '{p.value}', type '{p.type}' at line {p.lineno}")
        else:
            print("Syntax error at EOF (End of File)")
