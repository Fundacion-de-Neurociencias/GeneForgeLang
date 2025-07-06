import ply.lex as lex

# Lista de nombres de tokens (debe estar a nivel de módulo para que funcione el import)
tokens = [
    'DEFINE', 'INVOKE', 'MESSAGE', 'IF', 'THEN', 'ELSE', 'END', 'BRANCH',
    'TRY', 'CATCH', 'AS', 'BASED_ON', 'NOT',
    'EQUALS_EQUALS', 'NOT_EQUALS', 'LTE', 'GTE', 'GREATER_THAN', 'LESS_THAN', # Operadores de comparación primero
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'DOT', 'AMPERSAND',
    'LPAREN', 'RPAREN', 'COMMA', 'COLON',
    'LBRACKET', 'RBRACKET', 'LCURLY', 'RCURLY',
    'AND', 'OR',
    'TRUE', 'FALSE',
    'ANALYZE', 'USING', 'WITH', 'STRATEGY', 'PARAMS', # New tokens for analyze statement
    'LINE_COMMENT',
    'BLOCK_COMMENT',
    'ID', 'STRING', 'NUMBER' # ID, STRING, NUMBER should be last and are handled by functions
]

# Reglas de expresiones regulares para tokens simples
t_PLUS          = r'\+'
t_MINUS         = r'-'
t_TIMES         = r'\*'
t_DIVIDE        = r'/'
t_EQUALS        = r'='
t_DOT           = r'\.'
t_AMPERSAND     = r'&'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_COMMA         = r','
t_COLON         = r':'
t_LBRACKET      = r'\['
t_RBRACKET      = r']'
t_LCURLY        = r'{'
t_RCURLY        = r'}'
t_EQUALS_EQUALS = r'=='
t_NOT_EQUALS    = r'!='
t_LTE           = r'<='
t_GTE           = r'>='
t_GREATER_THAN  = r'>'
t_LESS_THAN     = r'<'


# Palabras reservadas (ahora con los tokens de GFL)
reserved = {
    'DEFINE'    : 'DEFINE',
    'INVOKE'    : 'INVOKE',
    'MESSAGE'   : 'MESSAGE',
    'IF'        : 'IF',
    'THEN'      : 'THEN',
    'ELSE'      : 'ELSE',
    'END'       : 'END',
    'BRANCH'    : 'BRANCH',
    'TRY'       : 'TRY',
    'CATCH'     : 'CATCH',
    'AS'        : 'AS',
    'BASED_ON'  : 'BASED_ON',
    'AND'       : 'AND',
    'OR'        : 'OR',
    'NOT'       : 'NOT',
    'TRUE'      : 'TRUE',
    'FALSE'     : 'FALSE',
    'ANALYZE'   : 'ANALYZE',
    'USING'     : 'USING',
    'WITH'      : 'WITH',
    'STRATEGY'  : 'STRATEGY',
    'PARAMS'    : 'PARAMS',
}

# Regla para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.upper(), 'ID')
    return t

# Reglas para STRING (comillas dobles y simples)
def t_STRING(t):
    r'\"([^\\\n]|\\.)*?\"|\'([^\\\n]|\\.)*?\'' # Added support for single quotes too
    t.value = t.value[1:-1]
    return t

# Reglas para NUMBER (enteros o flotantes)
def t_NUMBER(t):
    r'\d+(\.\d*)?([eE][+-]?\d+)?'
    t.value = float(t.value) if '.' in t.value or 'e' in t.value or 'E' in t.value else int(t.value)
    return t

# Regla para comentarios de línea (// o #)
def t_LINE_COMMENT(t):
    r'//.*|\#.*'
    pass

# Regla para comentarios de bloque /* ... */
def t_BLOCK_COMMENT(t):
    r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    t.lexer.lineno += t.value.count('\n')
    pass

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Regla para contar las líneas (NEWLINE no es un token que el parser reciba directamente)
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()