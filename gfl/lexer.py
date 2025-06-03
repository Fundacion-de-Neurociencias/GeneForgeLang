import ply.lex as lex

tokens = (
    'PRIME_EDIT',
    'BASE_EDIT',
    'PRIME_DEL',
    'PEG',
    'NICK_SITE',
    'REVERSE_TRANSCRIPTASE',
    'PIRNA',
    'TRANSPOSON',
    'ENDOGENOUS_RETROVIRUS',
    'MITOCHONDRIAL_GENE',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'EQUALS',
    'ID',
    'STRING',
    'NUMBER'
)

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_EQUALS = r'='
t_ignore = ' \t\r\n'

def t_PRIME_EDIT(t): r'prime_edit'; return t
def t_BASE_EDIT(t): r'base_edit'; return t
def t_PRIME_DEL(t): r'prime_del'; return t
def t_PEG(t): r'peg'; return t
def t_NICK_SITE(t): r'nick_site'; return t
def t_REVERSE_TRANSCRIPTASE(t): r'reverse_transcriptase'; return t
def t_PIRNA(t): r'pirna'; return t
def t_TRANSPOSON(t): r'transposon'; return t
def t_ENDOGENOUS_RETROVIRUS(t): r'endogenous_retrovirus'; return t
def t_MITOCHONDRIAL_GENE(t): r'mitochondrial_gene'; return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\-]*'
    return t

def t_error(t):
    print(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)

lexer = lex.lex()
