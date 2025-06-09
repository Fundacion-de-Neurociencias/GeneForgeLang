import ply.yacc as yacc
from gfl.lexer import tokens

def p_program(p):
    'program : statements'
    p[0] = p[1]

def p_statements_multiple(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]

def p_statement_simulate(p):
    'statement : SIMULATE IDENTIFIER'
    p[0] = {'node_type': 'simulate', 'type': 'simulate', 'target': p[2]}

def p_statement_experiment_block(p):
    'statement : EXPERIMENT LBRACE experiment_body RBRACE'
    body = p[3]
    body['node_type'] = 'experiment'
    p[0] = body

def p_experiment_body(p):
    'experiment_body : experiment_fields'
    exp = {}
    for d in p[1]:
        exp.update(d)
    p[0] = exp

def p_experiment_fields_multiple(p):
    'experiment_fields : experiment_fields experiment_field'
    p[0] = p[1] + [p[2]]

def p_experiment_fields_single(p):
    'experiment_fields : experiment_field'
    p[0] = [p[1]]

def p_experiment_field_type(p):
    'experiment_field : TYPE COLON IDENTIFIER'
    p[0] = {'type': p[3]}

def p_experiment_field_tool(p):
    'experiment_field : TOOL COLON IDENTIFIER'
    p[0] = {'tool': p[3]}

def p_experiment_field_params(p):
    'experiment_field : PARAMS COLON param_dict'
    p[0] = {'params': p[3]}

def p_param_dict(p):
    'param_dict : LBRACE param_pairs RBRACE'
    p[0] = p[2]

def p_param_pairs_multiple(p):
    'param_pairs : param_pairs COMMA param_pair'
    d = p[1]
    d.update(p[3])
    p[0] = d

def p_param_pairs_single(p):
    'param_pairs : param_pair'
    p[0] = p[1]

def p_param_pair(p):
    'param_pair : IDENTIFIER COLON param_value'
    p[0] = {p[1]: p[3]}

def p_param_value_bool(p):
    '''param_value : TRUE
                   | FALSE'''
    p[0] = (p[1] == "true")

def p_param_value_number(p):
    'param_value : NUMBER'
    p[0] = p[1]

def p_param_value_string(p):
    'param_value : IDENTIFIER'
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}")
    else:
        print("Error de sintaxis desconocido.")

parser = yacc.yacc()
