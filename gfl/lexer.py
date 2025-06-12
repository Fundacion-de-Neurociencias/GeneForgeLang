import ply.lex as lex
import logging

class GFLLexer:
    # Lista de nombres de tokens
    tokens = (
        'ANALYZE',
        'EXPERIMENT',
        'SIMULATE',
        'BRANCH',
        'IF',
        'THEN',
        'ELSE',        # Agregado para posible uso futuro
        'COLON',
        'LBRACE',
        'RBRACE',
        'STRING',
        'NUMBER',
        'IDENTIFIER',
        'TRUE',
        'FALSE',
        'EQUALS',      # ==
        'NOT_EQUALS',  # !=
        'LT',          # <
        'GT',          # >
        'LTE',         # <=
        'GTE',         # >=
        'AND',         # Lógico AND
        'OR',          # Lógico OR
        'LPAREN',      # (
        'RPAREN',      # )
        'COMMA',       # ,
        'COMMENT',     # Bloque de comentario /* ... */
        'LINE_COMMENT' # Comentario de línea // o #
    )

    # Reglas de expresiones regulares para tokens simples
    t_COLON = r':'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_EQUALS = r'=='
    t_NOT_EQUALS = r'!='
    t_LT = r'<'
    t_GT = r'>'
    t_LTE = r'<='
    t_GTE = r'>='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','

    # Palabras reservadas
    reserved = {
        'analyze': 'ANALYZE',
        'experiment': 'EXPERIMENT',
        'simulate': 'SIMULATE',
        'branch': 'BRANCH',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'true': 'TRUE',
        'false': 'FALSE',
        'AND': 'AND',
        'OR': 'OR',
    }

    # Regla para identificadores y palabras reservadas
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')  # Verifica palabras reservadas
        return t

    # Reglas para STRING (maneja comillas dobles y simples)
    def t_STRING(self, t):
        r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''
        t.value = t.value[1:-1] # Elimina las comillas
        return t

    # Reglas para NUMBER (enteros o flotantes)
    def t_NUMBER(self, t):
        r'\d+(\.\d*)?([eE][+-]?\d+)?'
        t.value = float(t.value) if '.' in t.value or 'e' in t.value or 'E' in t.value else int(t.value)
        return t

    # Reglas para comentarios de línea (// o #)
    def t_LINE_COMMENT(self, t):
        r'//.*|\#.*'  # ¡CORREGIDO: # ahora está escapado como \#!
        pass # No necesitamos devolver el comentario como un token

    # Regla para comentarios de bloque /* ... */
    def t_COMMENT(self, t):
        r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
        pass  # No necesitamos devolver el comentario como un token

    # Ignorar espacios y tabulaciones
    t_ignore = ' \t'

    # Regla para contar las líneas
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Manejo de errores de caracteres ilegales
    def t_error(self, t):
        print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lexer.lineno}")
        t.lexer.skip(1)

    # Constructor del lexer
    def __init__(self):
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     filename="lexer_debug.log",
        #     filemode="w",
        #     encoding="utf-8"
        # )
        # self.logger = logging.getLogger()
        self.lexer = lex.lex(module=self, debug=True, errorlog=logging.getLogger())

    # Método para tokenizar una cadena (opcional, si se llama directamente al lexer)
    def tokenize(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            # print(tok) # Para depuración
            yield tok
t_ignore_LINE_COMMENT = r'\#.*'
