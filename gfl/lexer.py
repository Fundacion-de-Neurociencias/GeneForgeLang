import ply.lex as lex


class GFLLexer:
    """
    Clase para el lexer de GeneForgeLang (GFL).
    Define los tokens y reglas léxicas para el lenguaje.
    """

    def __init__(self):
        # Construye el lexer
        self.lexer = lex.lex(module=self)

    # Lista de nombres de tokens (siempre necesaria)
    # NOTA IMPORTANTE: 'BOOLEAN' no se incluye aquí directamente,
    # ya que se añade a través de los valores de 'reserved'.
    tokens = [
        "ID",
        "NUMBER",
        "STRING",
        "COMMA",
        "COLON",
        "LCURLY",  # {
        "RCURLY",  # }
        "LBRACKET",  # [
        "RBRACKET",  # ]
        "STRATEGY",  # Token explícito para "strategy" (case-insensitive)
        "PARAMS",  # Token explícito para "params" (case-insensitive)
    ]

    # Palabras reservadas (keywords)
    # Estas palabras se tokenizarán como su tipo de token correspondiente (en mayúsculas)
    reserved = {
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "analyze": "ANALYZE",
        "experiment": "EXPERIMENT",
        "simulate": "SIMULATE",
        "branch": "BRANCH",
        "using": "USING",
        "with": "WITH",
        "true": "BOOLEAN",  # BOOLEAN se define aquí
        "false": "BOOLEAN",  # BOOLEAN se define aquí
        "and": "AND",  # Añadido para expresiones lógicas
        "or": "OR",  # Añadido para expresiones lógicas
    }

    # Agrega los valores del diccionario de palabras reservadas a la lista de tokens
    tokens += list(reserved.values())

    # Ignorar caracteres de espacio en blanco y tabulaciones
    t_ignore = " \t"

    # Reglas para tokens simples (expresiones regulares)
    t_COMMA = r","
    t_COLON = r":"
    t_LCURLY = r"{"
    t_RCURLY = r"}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"

    # Regla para números (enteros o flotantes)
    def t_NUMBER(self, t):
        r"\d+(\.\d*)?"
        t.value = float(t.value) if "." in t.value else int(t.value)
        return t

    # Regla para cadenas de texto (entre comillas dobles)
    def t_STRING(self, t):
        r'\"([^"\\]|\\.)*\"'
        t.value = t.value[1:-1]  # Elimina las comillas
        return t

    # Regla case-insensitive para "strategy"
    def t_STRATEGY(self, t):
        r"[Ss][Tt][Rr][Aa][Tt][Ee][Gg][Yy]"
        return t

    # Regla case-insensitive para "params"
    def t_PARAMS(self, t):
        r"[Pp][Aa][Rr][Aa][Mm][Ss]"
        return t

    # Regla para identificadores y palabras reservadas
    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        # Verifica si el identificador es una palabra reservada (case-insensitive para reservadas)
        # La conversión a minúsculas aquí es crucial para que coincida con las claves en 'reserved'
        t.type = self.reserved.get(t.value.lower(), "ID")
        return t

    # Regla para contar líneas
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # Regla de manejo de errores
    def t_error(self, t):
        print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
        t.lexer.skip(1)

    # Comentarios (ignorar líneas que empiezan con #)
    def t_COMMENT(self, t):
        r"\#.*"
        pass  # No devuelve ningún token
