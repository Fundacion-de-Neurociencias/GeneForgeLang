import ply.lex as lex

tokens = (
    'SIMULATE',
    'EXPERIMENT',
    'TYPE',
    'TOOL',
    'PARAMS',
    'IDENTIFIER',
    'NUMBER',
    'LBRACE',
    'RBRACE',
    'COLON',
    'COMMA',
    'TRUE',
    'FALSE'
)

t_SIMULATE = r'simulate'
t_EXPERIMENT = r'experiment'
t_TYPE = r'type'
t_TOOL = r'tool'
t_PARAMS = r'params'

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'
t_COMMA = r','

def t_TRUE(t):
    r'true'
    t.value = 'true'
    return t

def t_FALSE(t):
    r'false'
    t.value = 'false'
    return t

def t_NUMBER(t):
    r'\d+\.\d+|\d+'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z_0-9]*'
    if t.value in {'simulate', 'experiment', 'type', 'tool', 'params', 'true', 'false'}:
        t.type = t.value.upper()
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
