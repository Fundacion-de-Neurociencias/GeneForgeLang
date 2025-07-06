import ply.yacc as yacc
import ply.lex as lex
from gfl.lexer import GFLLexer

class GFLParser:
    """
    Clase principal para el parser de GeneForgeLang (GFL).
    Utiliza PLY (Python Lex-Yacc) para construir el analizador sintáctico.
    """
    def __init__(self):
        self.lexer = GFLLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, start='program')

    def parse(self, code):
        """
        Analiza el código GFL proporcionado.
        """
        self.lexer.lexer.lineno = 1 # Reinicia el contador de líneas del lexer
        return self.parser.parse(code, lexer=self.lexer.lexer)

    # --- Reglas de Parsing ---

    def p_program(self, p):
        '''
        program : statements
                | empty
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = []

    def p_statements(self, p):
        '''
        statements : statement
                   | statements statement
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement(self, p):
        '''
        statement : analyze_statement
                  | experiment_statement
                  | simulate_statement
                  | branch_statement
                  | inline_analyze_statement
        '''
        p[0] = p[1]

    def p_analyze_statement(self, p):
        '''
        analyze_statement : ANALYZE LCURLY properties RCURLY
        '''
        p[0] = ('analyze', p[3])

    def p_experiment_statement(self, p):
        '''
        experiment_statement : EXPERIMENT LCURLY properties RCURLY
        '''
        p[0] = ('experiment', p[3])

    def p_simulate_statement(self, p):
        '''
        simulate_statement : SIMULATE ID
        '''
        p[0] = ('simulate', p[2])

    def p_branch_statement(self, p):
        '''
        branch_statement : BRANCH LCURLY \
                           IF COLON expression \
                           THEN COLON LCURLY statements RCURLY \
                           ELSE COLON LCURLY statements RCURLY RCURLY
        '''
        # ¡Corrección importante aquí!
        # El índice para el bloque 'else' es p[14], no p[13].
        # p[5] es la expresión 'if'
        # p[9] es el bloque de sentencias 'then'
        # p[14] es el bloque de sentencias 'else'
        p[0] = ('branch', p[5], p[9], p[14])

    def p_inline_analyze_statement(self, p):
        '''
        inline_analyze_statement : ANALYZE USING ID WITH STRATEGY ID PARAMS LCURLY properties RCURLY
        '''
        p[0] = ('analyze_inline', p[3], p[6], p[9])

    def p_properties(self, p):
        '''
        properties : property
                   | properties COMMA property
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = {**p[1], **p[3]}

    def p_property(self, p):
        '''
        property : ID COLON value
                 | STRATEGY COLON value
                 | PARAMS COLON value
        '''
        key_token_type = p.slice[1].type
        if key_token_type == 'ID':
            key = p[1]
        elif key_token_type in ['STRATEGY', 'PARAMS']:
            key = p.slice[1].value.lower()
        else:
            raise ValueError(f"Tipo de token inesperado como clave de propiedad: {key_token_type}")

        p[0] = {key: p[3]}

    def p_value(self, p):
        '''
        value : STRING
              | NUMBER
              | BOOLEAN
              | list_value
              | object_value
        '''
        p[0] = p[1]

    def p_list_value(self, p):
        '''
        list_value : LBRACKET elements RBRACKET
        '''
        p[0] = p[2]

    def p_elements(self, p):
        '''
        elements : value
                 | elements COMMA value
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_object_value(self, p):
        '''
        object_value : LCURLY properties RCURLY
        '''
        p[0] = p[2]

    def p_expression(self, p):
        '''
        expression : ID
                   | expression AND ID
                   | expression OR ID
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[2], p[1], p[3])

    def p_empty(self, p):
        '''
        empty :
        '''
        pass

    def p_error(self, p):
        if p:
            print(f"Error de sintaxis en el token '{p.value}' en la línea {p.lineno} en la posición {p.lexpos}.")
        else:
            print("Error de sintaxis en EOF (Fin de Archivo).")
