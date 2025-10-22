import ply.lex as lex


class GFLLexer:
    """
    Clase para el lexer de GeneForgeLang (GFL).
    Define los tokens y reglas léxicas para el lenguaje.
    """

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self)

    # List of token names (always required)
    # IMPORTANT NOTE: 'BOOLEAN' is not included here directly,
    # as it is added through the 'reserved' values.
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
        "LPAREN",  # (
        "RPAREN",  # )
        "EQUALS",  # ==
        "NOT_EQUALS",  # !=
        "LT",  # <
        "GT",  # >
        "LTE",  # <=
        "GTE",  # >=
        "STRATEGY",  # Explicit token for "strategy" (case-insensitive)
        "PARAMS",  # Explicit token for "params" (case-insensitive)
    ]

    # Reserved words (keywords)
    # These words will be tokenized as their corresponding token type (in uppercase)
    reserved = {
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "analyze": "ANALYZE",
        "experiment": "EXPERIMENT",
        "design": "DESIGN",
        "optimize": "OPTIMIZE",
        "simulate": "SIMULATE",
        "branch": "BRANCH",
        "using": "USING",
        "with": "WITH",
        "true": "BOOLEAN",  # BOOLEAN defined here
        "false": "BOOLEAN",  # BOOLEAN defined here
        "and": "AND",  # Added for logical expressions
        "or": "OR",  # Added for logical expressions
        # New spatial genomic keywords
        "loci": "LOCI",
        "locus": "LOCUS",
        "rules": "RULES",
        "is_within": "IS_WITHIN",
        "distance_between": "DISTANCE_BETWEEN",
        "is_in_contact": "IS_IN_CONTACT",
        "set_activity": "SET_ACTIVITY",
        "get_activity": "GET_ACTIVITY",
        "move": "MOVE",
        "to": "TO",
        "level": "LEVEL",
        "chromosome": "CHROMOSOME",
        "start": "START",
        "end": "END",
        "elements": "ELEMENTS",
        "haplotype_panel": "HAPLOTYPE_PANEL",
        "type": "TYPE",
        "promoter": "PROMOTER",
        "enhancer": "ENHANCER",
        "gene": "GENE",
        "action": "ACTION",
        "query": "QUERY",
        "name": "NAME",
        "description": "DESCRIPTION",
        # Multi-omic keywords v2.0
        "transcripts": "TRANSCRIPTS",
        "transcript": "TRANSCRIPT",
        "proteins": "PROTEINS",
        "protein": "PROTEIN",
        "metabolites": "METABOLITES",
        "metabolite": "METABOLITE",
        "gene_source": "GENE_SOURCE",
        "exons": "EXONS",
        "exon": "EXON",
        "translates_from": "TRANSLATES_FROM",
        "domains": "DOMAINS",
        "domain": "DOMAIN",
        "formula": "FORMULA",
        "identifiers": "IDENTIFIERS",
        "identifier": "IDENTIFIER",
    }

    # Add the values from the reserved words dictionary to the token list
    tokens += list(reserved.values())

    # Ignore whitespace and tab characters
    t_ignore = " \t"

    # Reglas para tokens simples (expresiones regulares)
    t_COMMA = r","
    t_COLON = r":"
    t_LCURLY = r"{"
    t_RCURLY = r"}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_EQUALS = r"=="
    t_NOT_EQUALS = r"!="
    t_LT = r"<"
    t_GT = r">"
    t_LTE = r"<="
    t_GTE = r">="

    # Rule for numbers (integers or floats)
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

    # Rule for identifiers and reserved words
    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        # Check if the identifier is a reserved word (case-insensitive for reserved words)
        # Lowercasing here is crucial to match keys in 'reserved'
        t.type = self.reserved.get(t.value.lower(), "ID")
        return t

    # Rule for counting lines
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # Error handling rule
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' on line {t.lineno}")
        t.lexer.skip(1)

    # Comments (ignore lines starting with #)
    def t_COMMENT(self, t):
        r"\#.*"
        pass  # Does not return any token
