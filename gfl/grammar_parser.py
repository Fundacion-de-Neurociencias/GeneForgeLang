"""Advanced grammar-based GFL parser using PLY.

This module provides a comprehensive grammar-based parser for GeneForgeLang
that supports advanced syntax features, better error handling, and integration
with the performance optimization system.

Features:
- Enhanced lexical analysis with better token recognition
- Comprehensive grammar rules for all GFL constructs
- Integration with enhanced error handling system
- Performance optimization through caching
- Support for advanced syntax features (expressions, nested structures)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional

# Check for PLY availability
try:
    import ply.lex as lex
    import ply.yacc as yacc

    HAS_PLY = True
except ImportError:
    HAS_PLY = False
    lex = None
    yacc = None

# Import error handling components individually to avoid circular imports
try:
    from .error_handling import (
        EnhancedValidationError,
        EnhancedValidationResult,
        ErrorCategory,
        ErrorSeverity,
        SourceLocation,
        ErrorFix,
    )
except ImportError:
    # Fallback for testing outside package context
    from gfl.error_handling import (
        EnhancedValidationError,
        EnhancedValidationResult,
        ErrorCategory,
        ErrorSeverity,
        SourceLocation,
        ErrorFix,
    )

# Import performance components with fallback
try:
    from .performance import cached, get_monitor
except ImportError:
    # Provide fallback implementations
    def cached(cache_name=None, ttl=None, max_size=None):
        def decorator(func):
            return func

        return decorator

    class MockMonitor:
        def time_operation(self, name):
            class MockContext:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    pass

            return MockContext()

    def get_monitor():
        return MockMonitor()


logger = logging.getLogger(__name__)


class GFLSyntaxError(Exception):
    """Exception raised for GFL syntax errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location
        super().__init__(message)


class AdvancedGFLLexer:
    """Enhanced lexer for GeneForgeLang with comprehensive token support."""

    # Reserved words
    reserved = {
        # Core blocks
        "experiment": "EXPERIMENT",
        "analyze": "ANALYZE",
        "analyse": "ANALYZE",  # British spelling
        "design": "DESIGN",
        "optimize": "OPTIMIZE",
        "simulate": "SIMULATE",
        "branch": "BRANCH",
        "metadata": "METADATA",
        # Control flow
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "elif": "ELIF",
        "while": "WHILE",
        "for": "FOR",
        "in": "IN",
        # Logical operators
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        # Keywords
        "tool": "TOOL",
        "type": "TYPE",
        "strategy": "STRATEGY",
        "params": "PARAMS",
        "parameters": "PARAMS",  # Alias
        "data": "DATA",
        "output": "OUTPUT",
        "input": "INPUT",
        "using": "USING",
        "with": "WITH",
        "as": "AS",
        "from": "FROM",
        "import": "IMPORT",
        # Boolean values
        "true": "BOOLEAN",
        "false": "BOOLEAN",
        "yes": "BOOLEAN",
        "no": "BOOLEAN",
        "on": "BOOLEAN",
        "off": "BOOLEAN",
        # Null values
        "null": "NULL",
        "none": "NULL",
        "nil": "NULL",
    }

    # List of token names
    tokens = [
        # Literals
        "IDENTIFIER",
        "NUMBER",
        "STRING",
        "BOOLEAN",
        "NULL",
        # Operators
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "MODULO",
        "POWER",
        "EQUALS",
        "NOT_EQUALS",
        "LESS_THAN",
        "GREATER_THAN",
        "LESS_EQUAL",
        "GREATER_EQUAL",
        "ASSIGN",
        "PLUS_ASSIGN",
        "MINUS_ASSIGN",
        # Delimiters
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COMMA",
        "SEMICOLON",
        "COLON",
        "DOT",
        "ARROW",
        "PIPE",
        # Special
        "NEWLINE",
        "INDENT",
        "DEDENT",
    ] + list(reserved.values())

    # Token rules
    t_PLUS = r"\\+"
    t_MINUS = r"-"
    t_TIMES = r"\\*"
    t_DIVIDE = r"/"
    t_MODULO = r"%"
    t_POWER = r"\\*\\*"

    t_EQUALS = r"=="
    t_NOT_EQUALS = r"!="
    t_LESS_THAN = r"<"
    t_GREATER_THAN = r">"
    t_LESS_EQUAL = r"<="
    t_GREATER_EQUAL = r">="

    t_ASSIGN = r"="
    t_PLUS_ASSIGN = r"\\+="
    t_MINUS_ASSIGN = r"-="

    t_LPAREN = r"\\("
    t_RPAREN = r"\\)"
    t_LBRACE = r"\\{"
    t_RBRACE = r"\\}"
    t_LBRACKET = r"\\["
    t_RBRACKET = r"\\]"

    t_COMMA = r","
    t_SEMICOLON = r";"
    t_COLON = r":"
    t_DOT = r"\\."
    t_ARROW = r"->"
    t_PIPE = r"\\|"

    # Ignored characters (spaces and tabs)
    t_ignore = " \\t"

    def __init__(self):
        self.lexer = None
        self._build()

    def _build(self):
        """Build the lexer."""
        self.lexer = lex.lex(module=self, debug=False)

    def t_COMMENT(self, t):
        r"\\#.*"
        # Comments are ignored
        pass

    def t_MULTILINE_COMMENT(self, t):
        r"/\\*[^*]*\\*+([^/*][^*]*\\*+)*/"
        # Multi-line comments are ignored
        t.lexer.lineno += t.value.count("\\n")

    def t_NUMBER(self, t):
        r"\\d+(\\.\\d*)?([eE][+-]?\\d+)?"
        try:
            if "." in t.value or "e" in t.value.lower():
                t.value = float(t.value)
            else:
                t.value = int(t.value)
        except ValueError:
            logger.warning(f"Invalid number format: {t.value}")
            t.value = 0
        return t

    def t_STRING(self, t):
        r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\' '
        # Remove quotes and handle escape sequences
        t.value[0]
        content = t.value[1:-1]

        # Basic escape sequence handling
        content = content.replace("\\\\n", "\\n")
        content = content.replace("\\\\t", "\\t")
        content = content.replace("\\\\r", "\\r")
        content = content.replace('\\\\"', '"')
        content = content.replace("\\\\'", "'")
        content = content.replace("\\\\\\\\", "\\\\")

        t.value = content
        return t

    def t_IDENTIFIER(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        # Check for reserved words (case insensitive)
        t.type = self.reserved.get(t.value.lower(), "IDENTIFIER")

        # Handle boolean values
        if t.type == "BOOLEAN":
            t.value = t.value.lower() in ("true", "yes", "on")

        return t

    def t_NEWLINE(self, t):
        r"\\n+"
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        """Handle lexical errors."""
        logger.error(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def tokenize(self, data: str) -> List[Any]:
        """Tokenize input data and return list of tokens."""
        self.lexer.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens


class AdvancedGFLParser:
    """Advanced parser for GeneForgeLang with comprehensive grammar support."""

    def __init__(self, lexer: Optional[AdvancedGFLLexer] = None):
        self.lexer = lexer or AdvancedGFLLexer()
        self.tokens = self.lexer.tokens
        self.parser = None
        self.errors: List[EnhancedValidationError] = []
        self._build()

    def _build(self):
        """Build the parser."""
        # Create parser output directory
        parser_dir = Path(__file__).parent / "parser_cache"
        parser_dir.mkdir(exist_ok=True)

        self.parser = yacc.yacc(
            module=self,
            debug=False,
            outputdir=str(parser_dir),
            debugfile="gfl_parser.out",
        )

    # Precedence and associativity rules
    precedence = (
        ("left", "OR"),
        ("left", "AND"),
        ("left", "NOT"),
        ("left", "EQUALS", "NOT_EQUALS"),
        ("left", "LESS_THAN", "GREATER_THAN", "LESS_EQUAL", "GREATER_EQUAL"),
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE", "MODULO"),
        ("right", "UMINUS", "UPLUS"),
        ("left", "POWER"),
    )

    # Grammar rules
    def p_program(self, p):
        """program : statement_list"""
        p[0] = {
            "type": "program",
            "statements": p[1] if p[1] else [],
            "location": self._get_location(p, 1),
        }

    def p_statement_list(self, p):
        """statement_list : statement_list statement
        | statement
        | empty"""
        if len(p) == 3:
            p[0] = (p[1] or []) + [p[2]]
        elif len(p) == 2 and p[1]:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_statement(self, p):
        """statement : experiment_statement
        | analyze_statement
        | simulate_statement
        | branch_statement
        | metadata_statement
        | assignment_statement"""
        p[0] = p[1]

    def p_experiment_statement(self, p):
        """experiment_statement : EXPERIMENT COLON experiment_body"""
        p[0] = {
            "type": "experiment",
            "body": p[3],
            "location": self._get_location(p, 1),
        }

    def p_experiment_body(self, p):
        """experiment_body : LBRACE property_list RBRACE
        | property_list"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_analyze_statement(self, p):
        """analyze_statement : ANALYZE COLON analyze_body"""
        p[0] = {"type": "analyze", "body": p[3], "location": self._get_location(p, 1)}

    def p_analyze_body(self, p):
        """analyze_body : LBRACE property_list RBRACE
        | property_list"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_simulate_statement(self, p):
        """simulate_statement : SIMULATE COLON boolean_value
        | SIMULATE COLON simulate_body"""
        p[0] = {"type": "simulate", "value": p[3], "location": self._get_location(p, 1)}

    def p_simulate_body(self, p):
        """simulate_body : LBRACE property_list RBRACE
        | property_list"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_branch_statement(self, p):
        """branch_statement : BRANCH COLON LBRACE branch_body RBRACE"""
        p[0] = {"type": "branch", "body": p[4], "location": self._get_location(p, 1)}

    def p_branch_body(self, p):
        """branch_body : IF COLON expression NEWLINE statement_list
        | IF COLON expression NEWLINE statement_list ELSE COLON statement_list"""
        if len(p) == 6:
            p[0] = {"condition": p[3], "then_statements": p[5]}
        else:
            p[0] = {"condition": p[3], "then_statements": p[5], "else_statements": p[8]}

    def p_metadata_statement(self, p):
        """metadata_statement : METADATA COLON metadata_body"""
        p[0] = {"type": "metadata", "body": p[3], "location": self._get_location(p, 1)}

    def p_metadata_body(self, p):
        """metadata_body : LBRACE property_list RBRACE
        | property_list"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_assignment_statement(self, p):
        """assignment_statement : IDENTIFIER ASSIGN expression"""
        p[0] = {
            "type": "assignment",
            "identifier": p[1],
            "value": p[3],
            "location": self._get_location(p, 1),
        }

    def p_property_list(self, p):
        """property_list : property_list NEWLINE property
        | property_list COMMA property
        | property
        | empty"""
        if len(p) == 4:
            p[0] = p[1] or {}
            p[0].update(p[3] or {})
        elif len(p) == 2 and p[1]:
            p[0] = p[1]
        else:
            p[0] = {}

    def p_property(self, p):
        """property : IDENTIFIER COLON value"""
        p[0] = {p[1]: p[3]}

    def p_value(self, p):
        """value : expression
        | object_literal
        | array_literal"""
        p[0] = p[1]

    def p_object_literal(self, p):
        """object_literal : LBRACE property_list RBRACE
        | LBRACE RBRACE"""
        if len(p) == 4:
            p[0] = p[2] or {}
        else:
            p[0] = {}

    def p_array_literal(self, p):
        """array_literal : LBRACKET expression_list RBRACKET
        | LBRACKET RBRACKET"""
        if len(p) == 4:
            p[0] = p[2] or []
        else:
            p[0] = []

    def p_expression_list(self, p):
        """expression_list : expression_list COMMA expression
        | expression
        | empty"""
        if len(p) == 4:
            p[0] = (p[1] or []) + [p[3]]
        elif len(p) == 2 and p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_expression(self, p):
        """expression : logical_expression"""
        p[0] = p[1]

    def p_logical_expression(self, p):
        """logical_expression : logical_expression AND comparison_expression
        | logical_expression OR comparison_expression
        | comparison_expression"""
        if len(p) == 4:
            p[0] = {
                "type": "binary_op",
                "operator": p[2],
                "left": p[1],
                "right": p[3],
                "location": self._get_location(p, 2),
            }
        else:
            p[0] = p[1]

    def p_comparison_expression(self, p):
        """comparison_expression : arithmetic_expression EQUALS arithmetic_expression
        | arithmetic_expression NOT_EQUALS arithmetic_expression
        | arithmetic_expression LESS_THAN arithmetic_expression
        | arithmetic_expression GREATER_THAN arithmetic_expression
        | arithmetic_expression LESS_EQUAL arithmetic_expression
        | arithmetic_expression GREATER_EQUAL arithmetic_expression
        | arithmetic_expression"""
        if len(p) == 4:
            p[0] = {
                "type": "binary_op",
                "operator": p[2],
                "left": p[1],
                "right": p[3],
                "location": self._get_location(p, 2),
            }
        else:
            p[0] = p[1]

    def p_arithmetic_expression(self, p):
        """arithmetic_expression : arithmetic_expression PLUS term
        | arithmetic_expression MINUS term
        | term"""
        if len(p) == 4:
            p[0] = {
                "type": "binary_op",
                "operator": p[2],
                "left": p[1],
                "right": p[3],
                "location": self._get_location(p, 2),
            }
        else:
            p[0] = p[1]

    def p_term(self, p):
        """term : term TIMES factor
        | term DIVIDE factor
        | term MODULO factor
        | factor"""
        if len(p) == 4:
            p[0] = {
                "type": "binary_op",
                "operator": p[2],
                "left": p[1],
                "right": p[3],
                "location": self._get_location(p, 2),
            }
        else:
            p[0] = p[1]

    def p_factor(self, p):
        """factor : MINUS factor %prec UMINUS
        | PLUS factor %prec UPLUS
        | NOT factor
        | power"""
        if len(p) == 3:
            p[0] = {
                "type": "unary_op",
                "operator": p[1],
                "operand": p[2],
                "location": self._get_location(p, 1),
            }
        else:
            p[0] = p[1]

    def p_power(self, p):
        """power : atom POWER factor
        | atom"""
        if len(p) == 4:
            p[0] = {
                "type": "binary_op",
                "operator": p[2],
                "left": p[1],
                "right": p[3],
                "location": self._get_location(p, 2),
            }
        else:
            p[0] = p[1]

    def p_atom(self, p):
        """atom : LPAREN expression RPAREN
        | literal
        | IDENTIFIER"""
        if len(p) == 4:
            p[0] = p[2]  # Remove parentheses
        elif len(p) == 2 and isinstance(p[1], str):
            p[0] = {
                "type": "identifier",
                "value": p[1],
                "location": self._get_location(p, 1),
            }
        else:
            p[0] = p[1]

    def p_literal(self, p):
        """literal : NUMBER
        | STRING
        | boolean_value
        | NULL"""
        if p[1] is None:  # NULL
            p[0] = {"type": "null", "value": None, "location": self._get_location(p, 1)}
        else:
            p[0] = {
                "type": "literal",
                "value": p[1],
                "location": self._get_location(p, 1),
            }

    def p_boolean_value(self, p):
        """boolean_value : BOOLEAN"""
        p[0] = {"type": "boolean", "value": p[1], "location": self._get_location(p, 1)}

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        """Handle syntax errors."""
        if p:
            location = SourceLocation(
                line=p.lineno,
                column=getattr(p, "lexpos", 0),
                filename=getattr(self, "current_file", "<input>"),
            )
            error = EnhancedValidationError(
                message=f"Unexpected token '{p.value}' of type '{p.type}'",
                code="SYNTAX_ERROR",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SYNTAX,
                location=location,
                suggested_fixes=[
                    ErrorFix(
                        description=f"Remove or replace the unexpected token '{p.value}'",
                        code="REMOVE_TOKEN",
                    )
                ],
            )
        else:
            error = EnhancedValidationError(
                message="Unexpected end of input",
                code="UNEXPECTED_EOF",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.SYNTAX,
                suggested_fixes=[
                    ErrorFix(
                        description="Check for missing closing brackets, braces, or statements",
                        code="CHECK_SYNTAX",
                    )
                ],
            )

        self.errors.append(error)
        logger.error(f"Syntax error: {error.message}")

    def _get_location(self, p, index: int) -> SourceLocation:
        """Get source location for a parser token."""
        if hasattr(p, "lineno") and hasattr(p, "lexpos"):
            return SourceLocation(
                line=p.lineno(index)
                if callable(p.lineno)
                else getattr(p.slice[index], "lineno", 1),
                column=getattr(p.slice[index], "lexpos", 0),
                filename=getattr(self, "current_file", "<input>"),
            )
        return SourceLocation(line=1, column=0, filename="<input>")

    @cached(cache_name="grammar_parse", ttl=300.0, max_size=100)
    def parse(self, data: str, filename: str = "<input>") -> EnhancedValidationResult:
        """Parse GFL code and return enhanced validation result."""
        with get_monitor().time_operation("grammar_parse"):
            self.errors.clear()
            self.current_file = filename

            try:
                # Parse the input
                ast = self.parser.parse(data, lexer=self.lexer.lexer, debug=False)

                # Create result
                result = EnhancedValidationResult(
                    is_valid=len(self.errors) == 0,
                    syntax_errors=self.errors.copy(),
                    semantic_errors=[],
                    schema_errors=[],
                )

                if result.is_valid:
                    result.ast = ast

                return result

            except Exception as e:
                logger.exception(f"Parse error in {filename}: {e}")

                error = EnhancedValidationError(
                    message=f"Parse failed: {str(e)}",
                    code="PARSE_FAILED",
                    severity=ErrorSeverity.ERROR,
                    category=ErrorCategory.SYNTAX,
                )

                return EnhancedValidationResult(
                    is_valid=False,
                    syntax_errors=[error],
                    semantic_errors=[],
                    schema_errors=[],
                )


# Factory functions
def create_lexer() -> AdvancedGFLLexer:
    """Create a new GFL lexer instance."""
    return AdvancedGFLLexer()


def create_parser(lexer: Optional[AdvancedGFLLexer] = None) -> AdvancedGFLParser:
    """Create a new GFL parser instance."""
    return AdvancedGFLParser(lexer)


# Convenience function
def parse_gfl_grammar(code: str, filename: str = "<input>") -> EnhancedValidationResult:
    """Parse GFL code using the grammar-based parser."""
    parser = create_parser()
    return parser.parse(code, filename)
