import ply.yacc as yacc
from lexer import tokens
import logging

logger = logging.getLogger(__name__)

# Precedencia de operadores (de menor a mayor)
# Esto es crucial para que las expresiones se evalúen correctamente
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQUALS_EQUALS', 'NOT_EQUALS', 'GREATER_THAN', 'LESS_THAN', 'LTE', 'GTE'), # Comparaciones
    ('left', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'AMPERSAND'), # Aritméticos y concatenación
    ('right', 'UNARY_MINUS'), # Menos unario (para números negativos)
    ('left', 'DOT'), # Acceso a miembros
)

# Reglas de la gramática

def p_program(p):
    '''program : statements'''
    p[0] = {'type': 'program', 'body': p[1]}

def p_statements(p):
    '''
    statements : statement
               | statements statement
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''
    statement : define_statement
              | invoke_statement
              | message_statement
              | if_statement
              | branch_statement
              | analyze_statement
              | try_catch_block
    '''
    p[0] = p[1]

def p_define_statement(p):
    '''define_statement : DEFINE ID EQUALS expression'''
    p[0] = {'type': 'define_statement', 'id': p[2], 'value': p[4]}

def p_invoke_statement(p):
    '''invoke_statement : INVOKE ID LPAREN arguments RPAREN'''
    p[0] = {'type': 'invoke_statement', 'id': p[2], 'arguments': p[4]}

def p_arguments(p):
    '''
    arguments : expression_list
              | empty
    '''
    p[0] = p[1] if p[1] is not None else []

def p_expression_list(p):
    '''
    expression_list : expression
                    | expression_list COMMA expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_message_statement(p):
    '''message_statement : MESSAGE expression'''
    p[0] = {'type': 'message_statement', 'value': p[2]}

def p_if_statement(p):
    '''
    if_statement : IF expression THEN statements END
                 | IF expression THEN statements ELSE statements END
    '''
    if len(p) == 6:
        p[0] = {'type': 'if_statement', 'condition': p[2], 'then_branch': p[4]}
    else:
        p[0] = {'type': 'if_else_statement', 'condition': p[2], 'then_branch': p[4], 'else_branch': p[6]}

def p_branch_statement(p):
    '''
    branch_statement : BRANCH ID LCURLY statements RCURLY
    '''
    p[0] = {'type': 'branch_statement', 'id': p[2], 'body': p[4]}


def p_try_catch_block(p):
    '''try_catch_block : TRY statements CATCH ID AS ID statements END'''
    p[0] = {'type': 'try_catch_block', 'try_body': p[2], 'exception_type': p[4], 'exception_var': p[6], 'catch_body': p[7]}

def p_analyze_statement(p):
    '''analyze_statement : ANALYZE ID BASED_ON ID'''
    p[0] = {'type': 'analyze_statement', 'target': p[2], 'source': p[4]}

# Expresiones
def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression AMPERSAND expression
               | expression GREATER_THAN expression
               | expression LESS_THAN expression
               | expression EQUALS_EQUALS expression
               | expression NOT_EQUALS expression
               | expression LTE expression
               | expression GTE expression
               | expression AND expression
               | expression OR expression
    '''
    p[0] = {'type': 'binary_expression', 'operator': p[2], 'left': p[1], 'right': p[3]}

def p_expression_unop(p):
    '''
    expression : NOT expression %prec NOT
               | MINUS expression %prec UNARY_MINUS
    '''
    p[0] = {'type': 'unary_expression', 'operator': p[1], 'operand': p[2]}

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = {'type': 'literal', 'value': p[1]}

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = {'type': 'literal', 'value': p[1]}

def p_expression_id(p):
    '''expression : ID'''
    p[0] = {'type': 'identifier', 'value': p[1]}

def p_expression_boolean(p):
    '''
    expression : TRUE
               | FALSE
    '''
    p[0] = {'type': 'literal', 'value': p[1].upper()}

def p_expression_member_access(p):
    '''expression : expression DOT ID'''
    p[0] = {'type': 'member_access', 'object': p[1], 'property': p[3]}

def p_empty(p):
    '''empty :'''
    pass

# Manejo de errores
def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.value}' en la línea {p.lineno} en la posición {p.lexpos}")
        logger.error(f"Error de sintaxis en el token '{p.value}' en la línea {p.lineno} en la posición {p.lexpos}")
    else:
        print("Error de sintaxis al final del archivo.")
        logger.error("Error de sintaxis al final del archivo.")

# Construir el parser
parser = yacc.yacc()

def parse_code(code, lexer_instance):
    try:
        # Pasa el lexer ya construido a parser.parse()
        ast = parser.parse(code, lexer=lexer_instance)
        return ast
    except Exception as e:
        logger.error(f"Error durante el parseo: {e}")
        return None

if __name__ == '__main__':
    import lexer
    test_code = r"""
DEFINE myAge = 30
MESSAGE "Mi edad es: " & myAge
IF myAge > 25 THEN   # <--- ¡IMPORTANTE! El ">" aquí, no "GREATER_THAN"
    MESSAGE "Eres mayor que 25."
ELSE
    MESSAGE "Eres 25 o menor."
END

BRANCH validate_input {
    INVOKE process_data()
}
TRY
    INVOKE process_data()
CATCH InvalidInput AS err
    MESSAGE "Error de entrada: " & err
END
ANALYZE security_log BASED_ON user_activity
    """

    parsed_ast = parse_code(test_code, lexer.lexer)

    print("\nÁrbol de Sintaxis Abstracta (AST) generado:")
    if parsed_ast:
        import json
        print(json.dumps(parsed_ast, indent=2))
    else:
        print("No se pudo generar el AST (puede haber errores de sintaxis).")
