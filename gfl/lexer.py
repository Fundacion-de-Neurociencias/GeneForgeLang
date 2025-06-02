import ply.lex as lex

# Palabras reservadas que queremos reconocer explícitamente
reserved = {
    'prime_edit': 'PRIME_EDIT',
    'base_edit': 'BASE_EDIT',
    'prime_del': 'PRIME_DEL',
}

# Tokens básicos
tokens = [
    'ID', 'EQUALS', 'COMMA',
    'LPAREN', 'RPAREN',
    'NUMBER', 'STRING',
] + list(reserved.values())

t_EQUALS = r'='
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Identificadores
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Números
def t_NUMBER(t):
    r'\+?-?\d+'
    t.value = int(t.value)
    return t

# Strings entre comillas dobles
def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value.strip('"')
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t\r'

# Contar líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Errores
def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()
