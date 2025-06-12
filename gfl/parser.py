import ply.lex as lex
import ply.yacc as yacc
import logging
import os
import sys

# Configuración del logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Desactivar mensajes de depuración de PLY si no estamos depurando
if not os.environ.get('GFL_DEBUG_PARSER'):
    logging.getLogger('ply.lex').setLevel(logging.WARNING)
    logging.getLogger('ply.yacc').setLevel(logging.WARNING)
else:
    logging.getLogger('ply.lex').setLevel(logging.INFO)
    logging.getLogger('ply.yacc').setLevel(logging.INFO)
# --- LEXER ---

# Lista de nombres de tokens
tokens = (
    'ANALYZE', 'EXPERIMENT', 'SIMULATE', 'BRANCH',
    'IF', 'THEN', 'ELSE',
    'COLON', 'LBRACE', 'RBRACE',
    'STRING', 'NUMBER', 'IDENTIFIER',
    'TRUE', 'FALSE',
    'EQUALS', 'NOT_EQUALS', 'LT', 'GT', 'LTE', 'GTE',
    'AND', 'OR', 'LPAREN', 'RPAREN', 'COMMA',
    'COMMENT', 'LINE_COMMENT'
)

# Palabras reservadas (keywords)
reserved = {
    'analyze': 'ANALYZE',
    'experiment': 'EXPERIMENT',
    'simulate': 'SIMULATE',
    'branch': 'BRANCH',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'true': 'TRUE',
    'false': 'FALSE',
    'AND': 'AND', # Operador lógico AND
    'OR': 'OR',   # Operador lógico OR
}

# Expresiones regulares para tokens simples
t_COLON = r':'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Operadores de comparación
t_EQUALS = r'=='
t_NOT_EQUALS = r'!='
t_LTE = r'<='
t_GTE = r'>='
t_LT = r'<'
t_GT = r'>'

# Un token para identificadores y palabras reservadas
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t

# Cadenas (strings)
t_STRING = r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''

# Números (integers y floats)
def t_NUMBER(t):
    r'\d+(\.\d*)?([eE][+-]?\d+)?'
    t.value = float(t.value) if '.' in t.value or 'e' in t.value or 'E' in t.value else int(t.value)
    return t

# Comentarios de una sola línea (// o #)
t_LINE_COMMENT = r'//.*|\#.*'

# Comentarios de varias líneas (/* ... */)
t_COMMENT = r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Contar saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores de lexer
def t_error(t):
    logger.error(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex(debug=bool(os.environ.get('GFL_DEBUG_PARSER')))
# --- PARSER ---

# Precedencia de operadores (para expresiones booleanas)
# De menor a mayor precedencia
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUALS', 'NOT_EQUALS', 'LT', 'GT', 'LTE', 'GTE'),
)


def p_program(p):
    '''program : statements'''
    p[0] = {'node_type': 'program', 'statements': p[1]}

def p_statements_list(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : analyze_statement
                 | experiment_statement
                 | simulate_statement
                 | branch_statement'''
    p[0] = p[1]

def p_analyze_statement(p):
    '''analyze_statement : ANALYZE LBRACE properties RBRACE'''
    p[0] = {'node_type': 'analyze', 'properties': p[3]}

def p_experiment_statement(p):
    '''experiment_statement : EXPERIMENT LBRACE properties RBRACE'''
    p[0] = {'node_type': 'experiment', 'properties': p[3]}

def p_simulate_statement(p):
    '''simulate_statement : SIMULATE IDENTIFIER'''
    p[0] = {'node_type': 'simulate', 'target': p[2]}

def p_branch_statement(p):
    '''branch_statement : BRANCH LBRACE IF COLON expression THEN COLON LBRACE statements RBRACE ELSE COLON LBRACE statements RBRACE RBRACE
                        | BRANCH LBRACE IF COLON expression THEN COLON LBRACE statements RBRACE RBRACE''' # Sin ELSE
    if len(p) == 16: # Con ELSE
        p[0] = {
            'node_type': 'branch',
            'if': p[5],
            'then': p[9],
            'else': p[14]
        }
    else: # Sin ELSE
        p[0] = {
            'node_type': 'branch',
            'if': p[5],
            'then': p[9]
        }
def p_expression(p):
    '''expression : term
                  | expression AND term
                  | expression OR term'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == 'AND':
        p[0] = {'op': 'AND', 'left': p[1], 'right': p[3]}
    elif p[2] == 'OR':
        p[0] = {'op': 'OR', 'left': p[1], 'right': p[3]}

def p_term(p):
    '''term : comparison
            | LPAREN expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2] # Handle parentheses for grouping

def p_comparison(p):
    '''comparison : IDENTIFIER
                  | STRING
                  | IDENTIFIER EQUALS value
                  | IDENTIFIER NOT_EQUALS value
                  | IDENTIFIER LT value
                  | IDENTIFIER GT value
                  | IDENTIFIER LTE value
                  | IDENTIFIER GTE value'''
    if len(p) == 2:
        # Handle IDENTIFIER or STRING directly as a boolean condition
        # If it's a string, we assume it's meant to be a boolean-like literal
        p[0] = {'type': 'boolean_literal', 'value': p[1]}
    else: # Comparison (IDENTIFIER OP value)
        p[0] = {
            'type': 'comparison',
            'left': p[1],
            'op': p[2],
            'right': p[3]
        }

def p_properties(p):
    '''properties : property_list'''
    p[0] = p[1]

def p_property_list(p):
    '''property_list : property
                     | property_list COMMA property
                     | property_list property''' # Added for flexibility if AI misses commas
    if len(p) == 2:
        p[0] = [p[1]]
    elif p[2] == ',':
        p[0] = p[1] + [p[3]]
    else: # Case for missing comma (property_list property)
        logger.warning(f"Advertencia de sintaxis: Coma faltante detectada entre propiedades en la línea {p.lineno}. El parser intentará corregir esto automáticamente. Se recomienda añadir la coma para mejorar la legibilidad de su código GFL.")
        p[0] = p[1] + [p[2]]

def p_property(p):
    '''property : IDENTIFIER COLON value'''
    p[0] = {p[1]: p[3]}

def p_value(p):
    '''value : STRING
             | NUMBER
             | IDENTIFIER
             | TRUE
             | FALSE
             | LBRACE properties RBRACE'''
    if p[1] == '{': # Nested properties block
        p[0] = p[2]
    else:
        # Ensure IDENTIFIER is treated as its raw value, not necessarily boolean from lexer
        if p.slice[1].type == 'TRUE':
            p[0] = True
        elif p.slice[1].type == 'FALSE':
            p[0] = False
        else:
            p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    if p:
        logger.error(f"Syntax error at '{p.value}', type '{p.type}' at line {p.lineno}")
    else:
        logger.error("Syntax error at EOF")

# Construir el parser
parser = yacc.yacc(debug=bool(os.environ.get('GFL_DEBUG_PARSER')))
def parse_gfl_code(code):
    """
    Parsea el código GFL y devuelve el Abstract Syntax Tree (AST).
    """
    logger.info("Iniciando parseo de código GFL...")
    try:
        # Resetea el lexer antes de cada parseo
        lexer.lineno = 1
        lexer.begin('INITIAL') # Asegura que el lexer esté en el estado inicial

        result = parser.parse(code, lexer=lexer)
        if result:
            logger.info("Parseo completado con éxito. AST generado.")
            return result
        else:
            logger.warning("El parseo no produjo un AST. Puede haber errores de sintaxis no capturados o código vacío.")
            return None
    except Exception as e: logger.error(f"Error durante el parseo: {e}")
    return None
# Si se ejecuta directamente (para pruebas)
if __name__ == '__main__':
    # Ejemplo de uso: Parsear un archivo GFL
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                gfl_code = f.read()
            ast = parse_gfl_code(gfl_code)
            if ast:
                import json
                print(json.dumps(ast, indent=4))
                logger.info(f"✅ AST generado para {file_path}")
            else:
                logger.error(f"❌ Fallo al generar AST para {file_path}")
        else:
            logger.error(f"Error: Archivo no encontrado en {file_path}")
    else:
        logger.info("Uso: python3 gfl/parser.py <ruta_a_archivo_gfl>")
        logger.info("Ejecutando con un ejemplo interno...")
        
        # Ejemplo de código GFL para pruebas internas
        gfl_test_code = """
analyze {
    strategy: "pathway_enrichment",
    thresholds: {
        FDR: 0.05
    }
}

experiment {
    tool: "DESeq2",
    type: "bulkRNA",
    params: {
        condition_group: "disease",
        control_group: "healthy"
    }
}

simulate cell_growth

branch {
    if: tumor_size_increased AND (cell_death_rate_high OR another_condition)
    then: {
        simulate apoptosis
        analyze {
            strategy: "clustering",
            thresholds: {
                resolution: 0.8
            }
        }
    }
    else: {
        simulate cell_division
    }
}
"""
        ast = parse_gfl_code(gfl_test_code)
        if ast:
            import json
            print("\n--- AST de ejemplo interno ---")
            print(json.dumps(ast, indent=4))
            logger.info("✅ AST de ejemplo interno generado correctamente.")
        else:
            logger.error("❌ Fallo al generar AST para el ejemplo interno.")
