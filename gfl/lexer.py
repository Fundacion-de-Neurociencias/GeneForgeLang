import ply.lex as lex

tokens = [
    'ID', 'STRING', 'NUMBER', 'LPAREN', 'RPAREN', 'COMMA', 'EQUALS', 'PLUS', 'MINUS'
]

reserved = {
    'prime_edit': 'PRIME_EDIT',
    'base_edit': 'BASE_EDIT',
    'prime_del': 'PRIME_DEL',
    'peg': 'PEG'
}

tokens += list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','
t_EQUALS = r'='
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_ignore = ' \t'

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'[+-]?\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
