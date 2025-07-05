import ply.lex as lex

# Lista de nombres de tokens (debe estar a nivel de módulo para que funcione el import)
tokens = [
    'DEFINE', 'INVOKE', 'MESSAGE', 'IF', 'THEN', 'ELSE', 'END', 'BRANCH',
    'TRY', 'CATCH', 'AS', 'BASED_ON', 'NOT', # 'NOT' es un operador lógico
    'ID', 'STRING', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'DOT', 'AMPERSAND', # '&' para concatenación
    'LPAREN', 'RPAREN', 'COMMA', 'COLON',
    'LBRACKET', 'RBRACKET', 'LCURLY', 'RCURLY',
    'GREATER_THAN', 'LESS_THAN', 'EQUALS_EQUALS', # Operadores de comparación
    'AND', 'OR', # Operadores lógicos
    'NEWLINE', # Para manejar saltos de línea en el parser si es necesario
    'LINE_COMMENT', # Comentario de línea // o #
    'BLOCK_COMMENT' # Comentario de bloque /* ... */
]

# Reglas de expresiones regulares para tokens simples
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_EQUALS    = r'=' # Para la asignación (DEFINE x = y)
t_DOT       = r'\.'
t_AMPERSAND = r'&' # Para concatenación de strings o listas
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','
t_COLON     = r':'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_LCURLY    = r'\{'
t_RCURLY    = r'\}'
t_GREATER_THAN = r'>'
t_LESS_THAN    = r'<'
t_EQUALS_EQUALS = r'==' # Para comparación de igualdad

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
    'NOT'       : 'NOT', # Operador lógico
}

# Regla para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.upper(),'ID')    # Verifica palabras reservadas (insensible a mayúsculas para las palabras reservadas)
    return t

# Reglas para STRING (comillas dobles y simples)
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''
    t.value = t.value[1:-1] # Elimina las comillas
    return t

# Reglas para NUMBER (enteros o flotantes)
def t_NUMBER(t):
    r'\d+(\.\d*)?([eE][+-]?\d+)?'
    t.value = float(t.value) if '.' in t.value or 'e' in t.value or 'E' in t.value else int(t.value)
    return t

# Regla para comentarios de línea (// o #)
def t_LINE_COMMENT(t):
    r'//.*|\#.*'
    pass # No necesitamos devolver el comentario como un token

# Regla para comentarios de bloque /* ... */
def t_BLOCK_COMMENT(t):
    r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    t.lexer.lineno += t.value.count('\n')
    pass # No necesitamos devolver el comentario como un token

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Regla para contar las líneas
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    # No es necesario retornar el token NEWLINE a menos que el parser lo use explícitamente para el flujo.
    # Por ahora, simplemente actualizamos el número de línea.
    # Si el parser necesita NEWLINE, se activa 't.type = "NEWLINE"'

# Manejo de errores de caracteres ilegales
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# Construir el lexer
# Se puede pasar un objeto de módulo, pero si las reglas están en el ámbito global,
# ply.lex.lex() puede crearlo directamente sin un argumento 'module'.
lexer = lex.lex()
