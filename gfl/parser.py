import ply.yacc as yacc
from gfl.lexer import tokens

def p_statements(p):
    '''statements : statement
                  | statement statements'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_statement(p):
    '''statement : prime_edit
                 | base_edit
                 | prime_del
                 | peg
                 | nick_site
                 | reverse_transcriptase
                 | pirna
                 | transposon
                 | endogenous_retrovirus
                 | mitochondrial_gene'''
    p[0] = p[1]

def p_prime_edit(p):
    'prime_edit : PRIME_EDIT LPAREN arguments RPAREN'
    p[0] = ('prime_edit', p[3])

def p_base_edit(p):
    'base_edit : BASE_EDIT LPAREN arguments RPAREN'
    p[0] = ('base_edit', p[3])

def p_prime_del(p):
    'prime_del : PRIME_DEL LPAREN arguments RPAREN'
    p[0] = ('prime_del', p[3])

def p_peg(p):
    'peg : PEG LPAREN arguments RPAREN'
    p[0] = ('peg', p[3])

def p_nick_site(p):
    'nick_site : NICK_SITE LPAREN arguments RPAREN'
    p[0] = ('nick_site', p[3])

def p_reverse_transcriptase(p):
    'reverse_transcriptase : REVERSE_TRANSCRIPTASE LPAREN arguments RPAREN'
    p[0] = ('reverse_transcriptase', p[3])

def p_pirna(p):
    'pirna : PIRNA LPAREN arguments RPAREN'
    p[0] = ('pirna', p[3])

def p_transposon(p):
    'transposon : TRANSPOSON LPAREN arguments RPAREN'
    p[0] = ('transposon', p[3])

def p_endogenous_retrovirus(p):
    'endogenous_retrovirus : ENDOGENOUS_RETROVIRUS LPAREN arguments RPAREN'
    p[0] = ('endogenous_retrovirus', p[3])

def p_mitochondrial_gene(p):
    'mitochondrial_gene : MITOCHONDRIAL_GENE LPAREN arguments RPAREN'
    p[0] = ('mitochondrial_gene', p[3])

def p_arguments(p):
    '''arguments : argument
                 | argument COMMA arguments'''
    if len(p) == 2:
        p[0] = dict([p[1]])
    else:
        p[0] = dict([p[1]] + list(p[3].items()))

def p_argument(p):
    'argument : ID EQUALS ID'
    p[0] = (p[1], p[3])

def p_error(p):
    print(f"Syntax error at {p.value!r}")

parser = yacc.yacc(start='statements')
