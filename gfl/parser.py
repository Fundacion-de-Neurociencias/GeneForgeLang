from gfl.lexer import lexer
from gfl.parser_rules import parser

def parse_gfl_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    return parser.parse(data, lexer=lexer)
