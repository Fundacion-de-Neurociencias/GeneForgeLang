import ply.lex as lex

tokens = [
    'ID', 'NUMBER', 'LPAREN', 'RPAREN', 'COMMA', 'EQUALS'
]

reserved = {
    'prime_edit': 'PRIME_EDIT',
    'base_edit': 'BASE_EDIT',
    'prime_del': 'PRIME_DEL'
}

tokens += list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','
t_EQUALS = r'='
t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s' at line %d" % (t.value[0], t.lineno))
    t.lexer.skip(1)

lexer = lex.lex()
