"""Tests for enhanced error handling system."""

import pytest

from gfl.error_handling import (
    EnhancedValidationError,
    EnhancedValidationResult,
    ErrorCategory,
    ErrorCodes,
    ErrorFix,
    ErrorSeverity,
    SourceLocation,
    create_semantic_error,
    create_syntax_error,
    create_warning,
)


class TestSourceLocation:
    """Test SourceLocation functionality."""

    def test_create_basic_location(self):
        """Test creating a basic source location."""
        loc = SourceLocation(line=5, column=10)
        assert loc.line == 5
        assert loc.column == 10
        assert loc.file_path is None
        assert loc.length == 1

    def test_create_location_with_file(self):
        """Test creating location with file path."""
        loc = SourceLocation(line=5, column=10, file_path="/path/to/file.gfl", length=5)
        assert loc.line == 5
        assert loc.column == 10
        assert loc.file_path == "/path/to/file.gfl"
        assert loc.length == 5

    def test_location_string_representation(self):
        """Test string representation of location."""
        # Without file
        loc = SourceLocation(line=5, column=10)
        assert str(loc) == "5:10"

        # With file
        loc = SourceLocation(line=5, column=10, file_path="/path/to/file.gfl")
        assert str(loc) == "file.gfl:5:10"

    def test_unknown_location(self):
        """Test creating unknown location."""
        loc = SourceLocation.unknown()
        assert loc.line == 0
        assert loc.column == 0
        assert loc.file_path is None


class TestErrorFix:
    """Test ErrorFix functionality."""

    def test_create_simple_fix(self):
        """Test creating a simple fix."""
        fix = ErrorFix("Add missing semicolon")
        assert fix.description == "Add missing semicolon"
        assert fix.replacement_text is None
        assert fix.location is None

    def test_create_fix_with_replacement(self):
        """Test creating fix with replacement text."""
        loc = SourceLocation(line=5, column=10)
        fix = ErrorFix("Fix typo", "correct_spelling", loc)

        assert fix.description == "Fix typo"
        assert fix.replacement_text == "correct_spelling"
        assert fix.location == loc

    def test_fix_string_representation(self):
        """Test string representation of fix."""
        # Simple fix
        fix = ErrorFix("Add missing field")
        assert str(fix) == "Add missing field"

        # Fix with replacement
        loc = SourceLocation(line=5, column=10)
        fix = ErrorFix("Fix typo", "correct", loc)
        assert "Fix typo" in str(fix)
        assert "replace at 5:10" in str(fix)
        assert "correct" in str(fix)


class TestEnhancedValidationError:
    """Test EnhancedValidationError functionality."""

    def test_create_basic_error(self):
        """Test creating a basic error."""
        error = EnhancedValidationError(message="Test error message", code="TEST001")

        assert error.message == "Test error message"
        assert error.code == "SEMANTICTEST001"  # Auto-prefixed
        assert error.severity == ErrorSeverity.ERROR
        assert error.category == ErrorCategory.SEMANTIC

    def test_create_error_with_location(self):
        """Test creating error with location."""
        loc = SourceLocation(line=10, column=5, file_path="test.gfl")
        error = EnhancedValidationError(
            message="Syntax error",
            code="SYNTAX001",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYNTAX,
            location=loc,
        )

        assert error.location == loc
        assert error.severity == ErrorSeverity.CRITICAL
        assert error.category == ErrorCategory.SYNTAX

    def test_add_fix_to_error(self):
        """Test adding fixes to error."""
        error = EnhancedValidationError("Test error", "TEST001")

        # Add simple fix
        result = error.add_fix("Simple fix")
        assert result is error  # Should return self for chaining
        assert len(error.suggested_fixes) == 1
        assert error.suggested_fixes[0].description == "Simple fix"

        # Add fix with replacement
        loc = SourceLocation(line=5, column=10)
        error.add_fix("Replace text", "new_text", loc)
        assert len(error.suggested_fixes) == 2
        assert error.suggested_fixes[1].replacement_text == "new_text"

    def test_add_context_to_error(self):
        """Test adding context to error."""
        error = EnhancedValidationError("Test error", "TEST001")

        result = error.add_context("key1", "value1")
        assert result is error  # Should return self for chaining
        assert error.context["key1"] == "value1"

        error.add_context("key2", {"nested": "data"})
        assert error.context["key2"]["nested"] == "data"

    def test_error_string_representation(self):
        """Test comprehensive string representation."""
        loc = SourceLocation(line=10, column=5, file_path="test.gfl")
        error = EnhancedValidationError(
            message="Missing required field 'tool'",
            code="SEMANTIC001",
            severity=ErrorSeverity.ERROR,
            location=loc,
        )
        error.add_context("block", "experiment")
        error.add_fix("Add 'tool: CRISPR_cas9' to experiment block")

        error_str = str(error)
        assert "test.gfl:10:5:" in error_str
        assert "Missing required field 'tool'" in error_str
        assert "(SEMANTICSEMANTIC001)" in error_str
        assert "Context: block=experiment" in error_str
        assert "Suggested fixes:" in error_str
        assert "Add 'tool: CRISPR_cas9'" in error_str

    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        loc = SourceLocation(line=10, column=5, file_path="test.gfl")
        error = EnhancedValidationError(message="Test error", code="TEST001", location=loc)
        error.add_context("key", "value")
        error.add_fix("Fix description", "replacement", loc)

        error_dict = error.to_dict()

        assert error_dict["message"] == "Test error"
        assert error_dict["code"] == "SEMANTICTEST001"
        assert error_dict["location"]["line"] == 10
        assert error_dict["location"]["column"] == 5
        assert error_dict["location"]["file"] == "test.gfl"
        assert error_dict["context"]["key"] == "value"
        assert len(error_dict["suggested_fixes"]) == 1
        assert error_dict["suggested_fixes"][0]["description"] == "Fix description"


class TestEnhancedValidationResult:
    """Test EnhancedValidationResult functionality."""

    def test_create_empty_result(self):
        """Test creating empty validation result."""
        result = EnhancedValidationResult()
        assert len(result.errors) == 0
        assert result.file_path is None
        assert result.is_valid

    def test_add_error_to_result(self):
        """Test adding error to result."""
        result = EnhancedValidationResult()

        error = result.add_error("Test error", "TEST001", ErrorSeverity.ERROR, ErrorCategory.SEMANTIC)

        assert len(result.errors) == 1
        assert result.errors[0] is error
        assert not result.is_valid

    def test_error_categorization(self):
        """Test error categorization by severity."""
        result = EnhancedValidationResult()

        result.add_error("Critical", "C001", ErrorSeverity.CRITICAL)
        result.add_error("Error", "E001", ErrorSeverity.ERROR)
        result.add_error("Warning", "W001", ErrorSeverity.WARNING)
        result.add_error("Info", "I001", ErrorSeverity.INFO)
        result.add_error("Hint", "H001", ErrorSeverity.HINT)

        assert len(result.critical_errors) == 1
        assert len(result.semantic_errors) == 1
        assert len(result.warnings) == 1
        assert len(result.info_messages) == 1
        assert len(result.hints) == 1

        assert not result.is_valid  # Has critical and semantic errors
        assert result.has_warnings

    def test_get_errors_by_category(self):
        """Test getting errors by category."""
        result = EnhancedValidationResult()

        result.add_error("Syntax", "S001", category=ErrorCategory.SYNTAX)
        result.add_error("Semantic", "SE001", category=ErrorCategory.SEMANTIC)
        result.add_error("Plugin", "P001", category=ErrorCategory.PLUGIN)

        syntax_errors = result.get_errors_by_category(ErrorCategory.SYNTAX)
        assert len(syntax_errors) == 1
        assert syntax_errors[0].message == "Syntax"

        semantic_errors = result.get_errors_by_category(ErrorCategory.SEMANTIC)
        assert len(semantic_errors) == 1

    def test_get_statistics(self):
        """Test getting error statistics."""
        result = EnhancedValidationResult()

        result.add_error("Critical", "C001", ErrorSeverity.CRITICAL)
        result.add_error("Error1", "E001", ErrorSeverity.ERROR)
        result.add_error("Error2", "E002", ErrorSeverity.ERROR)
        result.add_error("Warning", "W001", ErrorSeverity.WARNING)

        stats = result.get_statistics()

        assert stats["critical"] == 1
        assert stats["errors"] == 2
        assert stats["warnings"] == 1
        assert stats["info"] == 0
        assert stats["hints"] == 0
        assert stats["total"] == 4

    def test_legacy_format_conversion(self):
        """Test conversion to legacy string list format."""
        result = EnhancedValidationResult()

        result.add_error("Critical error", "C001", ErrorSeverity.CRITICAL)
        result.add_error("Regular error", "E001", ErrorSeverity.ERROR)
        result.add_error("Warning", "W001", ErrorSeverity.WARNING)

        legacy_errors = result.to_legacy_format()

        # Should only include critical and errors, not warnings
        assert len(legacy_errors) == 2
        assert any("Critical error" in error for error in legacy_errors)
        assert any("Regular error" in error for error in legacy_errors)
        assert not any("Warning" in error for error in legacy_errors)

    def test_result_string_representation(self):
        """Test string representation of result."""
        result = EnhancedValidationResult()

        # Empty result
        assert str(result) == "No validation issues found."

        # Result with errors
        result.add_error("Error 1", "E001", ErrorSeverity.ERROR)
        result.add_error("Warning 1", "W001", ErrorSeverity.WARNING)

        result_str = str(result)
        assert "1 errors" in result_str
        assert "1 warnings" in result_str
        assert "ERROR (1):" in result_str
        assert "WARNING (1):" in result_str


class TestErrorCreationHelpers:
    """Test error creation helper functions."""

    def test_create_syntax_error(self):
        """Test creating syntax error."""
        loc = SourceLocation(line=5, column=10)
        error = create_syntax_error("Invalid YAML syntax", loc, ErrorCodes.SYNTAX_INVALID_YAML)

        assert error.severity == ErrorSeverity.CRITICAL
        assert error.category == ErrorCategory.SYNTAX
        assert error.code == ErrorCodes.SYNTAX_INVALID_YAML
        assert error.location == loc

    def test_create_semantic_error(self):
        """Test creating semantic error."""
        loc = SourceLocation(line=5, column=10)
        error = create_semantic_error("Missing required field", loc, ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD)

        assert error.severity == ErrorSeverity.ERROR
        assert error.category == ErrorCategory.SEMANTIC
        assert error.code == ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD
        assert error.location == loc

    def test_create_warning(self):
        """Test creating warning."""
        loc = SourceLocation(line=5, column=10)
        error = create_warning("Unknown tool", loc, ErrorCategory.SEMANTIC, "WARNING001")

        assert error.severity == ErrorSeverity.WARNING
        assert error.category == ErrorCategory.SEMANTIC
        assert error.code == "SEMANTICWARNING001"
        assert error.location == loc


class TestErrorCodes:
    """Test error code constants."""

    def test_error_code_format(self):
        """Test error code format consistency."""
        # Syntax codes
        assert ErrorCodes.SYNTAX_INVALID_YAML.startswith("SYNTAX")
        assert ErrorCodes.SYNTAX_INVALID_STRUCTURE.startswith("SYNTAX")

        # Semantic codes
        assert ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD.startswith("SEMANTIC")
        assert ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE.startswith("SEMANTIC")

        # Plugin codes
        assert ErrorCodes.PLUGIN_NOT_FOUND.startswith("PLUGIN")
        assert ErrorCodes.PLUGIN_LOAD_FAILED.startswith("PLUGIN")

    def test_error_code_uniqueness(self):
        """Test that error codes are unique."""
        codes = [
            ErrorCodes.SYNTAX_INVALID_YAML,
            ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ErrorCodes.PLUGIN_NOT_FOUND,
            ErrorCodes.SCHEMA_VALIDATION_FAILED,
        ]

        assert len(codes) == len(set(codes))  # All unique


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test integration with validation system."""

    def test_enhanced_error_in_validation_flow(self):
        """Test enhanced errors in validation workflow."""
        result = EnhancedValidationResult()

        # Simulate validation finding multiple issues
        error1 = result.add_error(
            "Missing required field 'tool'",
            ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            location=SourceLocation(line=2, column=1),
        )
        error1.add_fix("Add 'tool: CRISPR_cas9' to experiment block")
        error1.add_context("block", "experiment")

        error2 = result.add_error(
            "Unknown analysis strategy 'invalid_strategy'",
            ErrorCodes.SEMANTIC_UNKNOWN_STRATEGY,
            ErrorSeverity.WARNING,
            location=SourceLocation(line=5, column=12),
        )
        error2.add_fix("Use 'differential', 'pathway', or 'variant'")

        # Check comprehensive result
        assert len(result.errors) == 2
        assert len(result.semantic_errors) == 1
        assert len(result.warnings) == 1
        assert not result.is_valid
        assert result.has_warnings

        # Check that errors have rich information
        semantic_error = result.semantic_errors[0]
        assert len(semantic_error.suggested_fixes) == 1
        assert "tool: CRISPR_cas9" in semantic_error.suggested_fixes[0].description
        assert semantic_error.context["block"] == "experiment"

        warning = result.warnings[0]
        assert warning.location.line == 5
        assert warning.location.column == 12
