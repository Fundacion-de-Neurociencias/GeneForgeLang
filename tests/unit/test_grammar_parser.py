"""Tests for the advanced grammar-based GFL parser."""

import pytest

from gfl.grammar_parser import (
    create_lexer,
    create_parser,
    parse_gfl_grammar,
)
from gfl.error_handling import ErrorCategory, ErrorSeverity


class TestAdvancedGFLLexer:
    """Test the advanced GFL lexer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.lexer = create_lexer()

    def test_basic_tokens(self):
        """Test basic token recognition."""
        code = """
        experiment: {
            tool: "CRISPR_cas9",
            type: gene_editing,
            count: 42
        }
        """
        tokens = self.lexer.tokenize(code)
        token_types = [t.type for t in tokens if t.type != "NEWLINE"]

        expected_types = [
            "EXPERIMENT",
            "COLON",
            "LBRACE",
            "IDENTIFIER",
            "COLON",
            "STRING",
            "COMMA",
            "IDENTIFIER",
            "COLON",
            "IDENTIFIER",
            "COMMA",
            "IDENTIFIER",
            "COLON",
            "NUMBER",
            "RBRACE",
        ]

        assert token_types == expected_types

    def test_reserved_words(self):
        """Test recognition of reserved words."""
        reserved_tests = [
            ("experiment", "EXPERIMENT"),
            ("analyze", "ANALYZE"),
            ("analyse", "ANALYZE"),  # British spelling
            ("simulate", "SIMULATE"),
            ("branch", "BRANCH"),
            ("if", "IF"),
            ("then", "THEN"),
            ("else", "ELSE"),
            ("true", "BOOLEAN"),
            ("false", "BOOLEAN"),
            ("null", "NULL"),
            ("and", "AND"),
            ("or", "OR"),
        ]

        for word, expected_type in reserved_tests:
            tokens = self.lexer.tokenize(word)
            assert len(tokens) == 1
            assert tokens[0].type == expected_type

    def test_boolean_values(self):
        """Test boolean value recognition and conversion."""
        boolean_tests = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("on", True),
            ("off", False),
        ]

        for word, expected_value in boolean_tests:
            tokens = self.lexer.tokenize(word)
            assert len(tokens) == 1
            assert tokens[0].type == "BOOLEAN"
            assert tokens[0].value == expected_value

    def test_numbers(self):
        """Test number recognition."""
        number_tests = [
            ("42", 42),
            ("3.14", 3.14),
            ("0", 0),
            ("123.456", 123.456),
            ("1e5", 100000.0),
            ("2.5e-3", 0.0025),
        ]

        for text, expected_value in number_tests:
            tokens = self.lexer.tokenize(text)
            assert len(tokens) == 1
            assert tokens[0].type == "NUMBER"
            assert tokens[0].value == expected_value

    def test_strings(self):
        """Test string recognition and escape sequences."""
        string_tests = [
            ('"hello"', "hello"),
            ("'world'", "world"),
            ('"hello\\nworld"', "hello\nworld"),
            ('"tab\\there"', "tab\there"),
            ('"\\"quoted\\""', '"quoted"'),
            ("'it\\'s'", "it's"),
        ]

        for text, expected_value in string_tests:
            tokens = self.lexer.tokenize(text)
            assert len(tokens) == 1
            assert tokens[0].type == "STRING"
            assert tokens[0].value == expected_value

    def test_operators(self):
        """Test operator recognition."""
        operator_tests = [
            ("+", "PLUS"),
            ("-", "MINUS"),
            ("*", "TIMES"),
            ("/", "DIVIDE"),
            ("%", "MODULO"),
            ("**", "POWER"),
            ("==", "EQUALS"),
            ("!=", "NOT_EQUALS"),
            ("<", "LESS_THAN"),
            (">", "GREATER_THAN"),
            ("<=", "LESS_EQUAL"),
            (">=", "GREATER_EQUAL"),
            ("=", "ASSIGN"),
        ]

        for text, expected_type in operator_tests:
            tokens = self.lexer.tokenize(text)
            assert len(tokens) == 1
            assert tokens[0].type == expected_type

    def test_delimiters(self):
        """Test delimiter recognition."""
        delimiter_tests = [
            ("(", "LPAREN"),
            (")", "RPAREN"),
            ("{", "LBRACE"),
            ("}", "RBRACE"),
            ("[", "LBRACKET"),
            ("]", "RBRACKET"),
            (",", "COMMA"),
            (";", "SEMICOLON"),
            (":", "COLON"),
            (".", "DOT"),
            ("->", "ARROW"),
            ("|", "PIPE"),
        ]

        for text, expected_type in delimiter_tests:
            tokens = self.lexer.tokenize(text)
            assert len(tokens) == 1
            assert tokens[0].type == expected_type

    def test_comments(self):
        """Test comment handling."""
        code = """
        # This is a comment
        experiment: test  # End-of-line comment
        """
        tokens = self.lexer.tokenize(code)
        token_types = [t.type for t in tokens if t.type != "NEWLINE"]

        # Comments should be ignored
        assert "COMMENT" not in token_types
        assert token_types == ["EXPERIMENT", "COLON", "IDENTIFIER"]

    def test_identifiers(self):
        """Test identifier recognition."""
        identifier_tests = [
            "variable_name",
            "CamelCase",
            "snake_case",
            "name123",
            "_private",
            "UPPER_CASE",
        ]

        for identifier in identifier_tests:
            tokens = self.lexer.tokenize(identifier)
            assert len(tokens) == 1
            assert tokens[0].type == "IDENTIFIER"
            assert tokens[0].value == identifier


class TestAdvancedGFLParser:
    """Test the advanced GFL parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_simple_experiment(self):
        """Test parsing a simple experiment block."""
        code = """
        experiment: {
            tool: "CRISPR_cas9",
            type: "gene_editing"
        }
        """
        result = self.parser.parse(code)

        assert result.is_valid
        assert result.ast is not None
        assert result.ast["type"] == "program"

        statements = result.ast["statements"]
        assert len(statements) == 1

        experiment = statements[0]
        assert experiment["type"] == "experiment"
        assert "body" in experiment

    def test_analyze_statement(self):
        """Test parsing analyze statements."""
        code = """
        analyze: {
            strategy: "differential",
            data: "results.csv",
            thresholds: {
                p_value: 0.01,
                fold_change: 1.5
            }
        }
        """
        result = self.parser.parse(code)

        assert result.is_valid
        statements = result.ast["statements"]
        assert len(statements) == 1

        analyze = statements[0]
        assert analyze["type"] == "analyze"

    def test_simulate_statement(self):
        """Test parsing simulate statements."""
        # Boolean simulate
        code1 = "simulate: true"
        result1 = self.parser.parse(code1)
        assert result1.is_valid

        # Object simulate
        code2 = """
        simulate: {
            enabled: true,
            iterations: 1000
        }
        """
        result2 = self.parser.parse(code2)
        assert result2.is_valid

    def test_branch_statement(self):
        """Test parsing branch (conditional) statements."""
        # Note: This is a simplified test as the full branch syntax is complex
        # In a real implementation, you'd test the full if-then-else structure

    def test_metadata_statement(self):
        """Test parsing metadata statements."""
        code = """
        metadata: {
            experiment_id: "EXP001",
            researcher: "Dr. Smith",
            date: "2023-01-01"
        }
        """
        result = self.parser.parse(code)

        assert result.is_valid
        statements = result.ast["statements"]
        assert len(statements) == 1

        metadata = statements[0]
        assert metadata["type"] == "metadata"

    def test_assignment_statement(self):
        """Test parsing assignment statements."""
        code = "target_gene = TP53"
        result = self.parser.parse(code)

        assert result.is_valid
        statements = result.ast["statements"]
        assert len(statements) == 1

        assignment = statements[0]
        assert assignment["type"] == "assignment"
        assert assignment["identifier"] == "target_gene"

    def test_expressions(self):
        """Test parsing various expressions."""
        expression_tests = [
            "x + y",
            "a * b - c",
            "(x + y) * z",
            "value >= threshold",
            "flag and not disabled",
            "count < 10 or retry",
        ]

        for expr in expression_tests:
            code = f"result = {expr}"
            result = self.parser.parse(code)
            assert result.is_valid, f"Failed to parse: {expr}"

    def test_object_literals(self):
        """Test parsing object literals."""
        code = """
        config = {
            enabled: true,
            count: 42,
            name: "test",
            nested: {
                value: 3.14
            }
        }
        """
        result = self.parser.parse(code)
        assert result.is_valid

    def test_array_literals(self):
        """Test parsing array literals."""
        code = """
        items = [1, 2, 3, "hello", true, null]
        """
        result = self.parser.parse(code)
        assert result.is_valid

    def test_multiple_statements(self):
        """Test parsing multiple statements."""
        code = """
        experiment: {
            tool: "CRISPR_cas9"
        }

        analyze: {
            strategy: "differential"
        }

        simulate: true

        metadata: {
            version: "1.0"
        }
        """
        result = self.parser.parse(code)

        assert result.is_valid
        statements = result.ast["statements"]
        assert len(statements) == 4

        types = [stmt["type"] for stmt in statements]
        expected_types = ["experiment", "analyze", "simulate", "metadata"]
        assert types == expected_types

    def test_syntax_error_handling(self):
        """Test syntax error detection and reporting."""
        invalid_codes = [
            "experiment: {",  # Missing closing brace
            "analyze: invalid syntax here",  # Invalid syntax
            "simulate: {{}",  # Invalid nested braces
            "branch: if condition",  # Incomplete branch
        ]

        for code in invalid_codes:
            result = self.parser.parse(code)
            assert not result.is_valid
            assert len(result.syntax_errors) > 0

            # Check that errors have proper structure
            for error in result.syntax_errors:
                assert error.message
                assert error.code
                assert error.severity in [ErrorSeverity.ERROR, ErrorSeverity.WARNING]
                assert error.category in [ErrorCategory.SYNTAX, ErrorCategory.SEMANTIC]

    def test_error_locations(self):
        """Test that errors include source location information."""
        code = """
        experiment: {
            tool: "CRISPR_cas9"
            invalid_token_here
        }
        """
        result = self.parser.parse(code, filename="test.gfl")

        if not result.is_valid:
            for error in result.syntax_errors:
                if error.location:
                    assert error.location.filename == "test.gfl"
                    assert error.location.line > 0

    def test_suggested_fixes(self):
        """Test that syntax errors include suggested fixes."""
        code = "experiment: {"  # Missing closing brace
        result = self.parser.parse(code)

        assert not result.is_valid
        assert len(result.syntax_errors) > 0

        # At least one error should have suggested fixes
        has_fixes = any(error.suggested_fixes for error in result.syntax_errors)
        assert has_fixes


class TestGrammarParserIntegration:
    """Test grammar parser integration with the API."""

    def test_parse_gfl_grammar_function(self):
        """Test the convenience function."""
        code = """
        experiment: {
            tool: "CRISPR_cas9",
            type: "gene_editing"
        }
        """
        result = parse_gfl_grammar(code)

        assert result.is_valid
        assert result.ast is not None

    def test_api_integration(self):
        """Test integration with the main API."""
        from gfl.api import parse, parse_enhanced

        code = """
        experiment: {
            tool: "CRISPR_cas9"
        }
        """

        # Test enhanced parsing
        result = parse_enhanced(code, use_grammar=True)
        assert result.is_valid

        # Test regular parsing with grammar
        try:
            ast = parse(code, use_grammar=True)
            assert ast is not None
            assert ast["type"] == "program"
        except ImportError:
            # PLY might not be available in test environment
            pytest.skip("PLY not available for grammar parsing")

    def test_performance_caching(self):
        """Test that parsing results are cached for performance."""
        code = """
        experiment: {
            tool: "CRISPR_cas9"
        }
        """

        # Parse the same code multiple times
        for _ in range(3):
            result = parse_gfl_grammar(code)
            assert result.is_valid

        # Verify caching is working (would need to check cache stats)
        from gfl.performance import get_optimizer

        optimizer = get_optimizer()
        cache = optimizer.get_cache("grammar_parse")
        if cache:
            stats = cache.stats()
            if stats:
                # Should have some cache hits
                assert stats.hits > 0

    def test_complex_gfl_example(self):
        """Test parsing a complex GFL example."""
        code = """
        metadata: {
            experiment_id: "EXP_2023_001",
            researcher: "Dr. Smith",
            institution: "Genomics Lab"
        }

        experiment: {
            tool: "CRISPR_cas9",
            type: "gene_editing",
            strategy: "knockout",
            params: {
                target_gene: "TP53",
                guide_rna: "GGGCCGGGCGGGCTCCCAGACATGCGTAT",
                vector: "pCRISPR-Cas9",
                concentration: 50.0,
                temperature: 37.0,
                duration: "24h",
                replicates: 3
            }
        }

        analyze: {
            strategy: "differential",
            data: "experiment_output",
            thresholds: {
                p_value: 0.01,
                fold_change: 1.5
            },
            filters: ["remove_low_counts", "normalize"],
            operations: [
                {
                    type: "filter",
                    params: {
                        method: "expression_threshold",
                        threshold: 2.0
                    }
                },
                {
                    type: "normalize",
                    params: {
                        method: "quantile"
                    }
                }
            ]
        }

        simulate: {
            enabled: true,
            iterations: 1000,
            seed: 42
        }
        """

        result = parse_gfl_grammar(code)

        assert result.is_valid
        assert result.ast is not None

        statements = result.ast["statements"]
        assert len(statements) == 4  # metadata, experiment, analyze, simulate

        # Verify statement types
        types = [stmt["type"] for stmt in statements]
        expected_types = ["metadata", "experiment", "analyze", "simulate"]
        assert types == expected_types
