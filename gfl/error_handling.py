"""Enhanced error handling system for GeneForgeLang.

This module provides comprehensive error tracking with source locations,
error codes, severity levels, and suggested fixes to improve debugging
and user experience.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    CRITICAL = "critical"  # Prevents parsing/execution
    ERROR = "error"  # Semantic errors that should be fixed
    WARNING = "warning"  # Issues that might cause problems
    INFO = "info"  # Informational messages
    HINT = "hint"  # Optimization or style suggestions


class ErrorCategory(str, Enum):
    """Error categories for classification."""

    SYNTAX = "syntax"  # YAML/parsing syntax errors
    SEMANTIC = "semantic"  # Semantic validation errors
    TYPE = "type"  # Type checking errors
    PLUGIN = "plugin"  # Plugin-related errors
    SCHEMA = "schema"  # Schema validation errors
    PERFORMANCE = "performance"  # Performance warnings
    SECURITY = "security"  # Security-related issues


@dataclass(frozen=True)
class SourceLocation:
    """Represents a location in source code."""

    line: int
    column: int
    file_path: Optional[str] = None
    length: int = 1

    def __str__(self) -> str:
        """String representation of location."""
        location = f"{self.line}:{self.column}"
        if self.file_path:
            path = Path(self.file_path).name  # Just filename, not full path
            location = f"{path}:{location}"
        return location

    @classmethod
    def from_yaml_mark(cls, mark) -> SourceLocation:
        """Create location from YAML parser mark."""
        return cls(
            line=mark.line + 1,  # YAML uses 0-based lines
            column=mark.column + 1,  # YAML uses 0-based columns
            length=1,
        )

    @classmethod
    def unknown(cls) -> SourceLocation:
        """Create an unknown location."""
        return cls(line=0, column=0)


@dataclass
class ErrorFix:
    """Represents a suggested fix for an error."""

    description: str
    replacement_text: Optional[str] = None
    location: Optional[SourceLocation] = None

    def __str__(self) -> str:
        """String representation of the fix."""
        if self.replacement_text and self.location:
            return f"{self.description} (replace at {self.location} with '{self.replacement_text}')"
        return self.description


@dataclass
class EnhancedValidationError:
    """Enhanced validation error with rich context and suggestions."""

    message: str
    code: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.SEMANTIC
    location: Optional[SourceLocation] = None
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fixes: List[ErrorFix] = field(default_factory=list)
    related_errors: List[str] = field(default_factory=list)  # Error codes

    def __post_init__(self):
        """Validate error after initialization."""
        if not self.code.startswith(self.category.value.upper()):
            # Auto-prefix with category if needed
            self.code = f"{self.category.value.upper()}{self.code}"

    def add_fix(
        self,
        description: str,
        replacement: Optional[str] = None,
        location: Optional[SourceLocation] = None,
    ) -> EnhancedValidationError:
        """Add a suggested fix to this error."""
        fix = ErrorFix(
            description=description,
            replacement_text=replacement,
            location=location or self.location,
        )
        self.suggested_fixes.append(fix)
        return self

    def add_context(self, key: str, value: Any) -> EnhancedValidationError:
        """Add context information to this error."""
        self.context[key] = value
        return self

    def __str__(self) -> str:
        """Comprehensive string representation."""
        parts = []

        # Severity indicator
        if self.severity != ErrorSeverity.ERROR:
            parts.append(f"[{self.severity.value.upper()}]")

        # Location
        if self.location:
            parts.append(f"{self.location}:")

        # Main message
        parts.append(self.message)

        # Error code
        parts.append(f"({self.code})")

        result = " ".join(parts)

        # Add context if available
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            result += f"\n  Context: {context_str}"

        # Add suggested fixes
        if self.suggested_fixes:
            result += "\n  Suggested fixes:"
            for fix in self.suggested_fixes:
                result += f"\n    - {fix}"

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": self.message,
            "code": self.code,
            "severity": self.severity.value,
            "category": self.category.value,
            "location": {
                "line": self.location.line,
                "column": self.location.column,
                "file": self.location.file_path,
                "length": self.location.length,
            }
            if self.location
            else None,
            "context": self.context,
            "suggested_fixes": [
                {
                    "description": fix.description,
                    "replacement": fix.replacement_text,
                    "location": {
                        "line": fix.location.line,
                        "column": fix.location.column,
                        "file": fix.location.file_path,
                    }
                    if fix.location
                    else None,
                }
                for fix in self.suggested_fixes
            ],
            "related_errors": self.related_errors,
        }


@dataclass
class EnhancedValidationResult:
    """Enhanced validation result with categorized errors and statistics."""

    errors: List[EnhancedValidationError] = field(default_factory=list)
    file_path: Optional[str] = None
    # Dynamic attributes that can be set after construction
    ast: Optional[Dict[str, Any]] = field(default=None)
    _syntax_errors: Optional[List[EnhancedValidationError]] = field(default=None, repr=False)
    _semantic_errors: Optional[List[EnhancedValidationError]] = field(default=None, repr=False)
    _schema_errors: Optional[List[EnhancedValidationError]] = field(default=None, repr=False)

    def add_error(
        self,
        message: str,
        code: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.SEMANTIC,
        location: Optional[SourceLocation] = None,
    ) -> EnhancedValidationError:
        """Add an error and return it for chaining."""
        error = EnhancedValidationError(
            message=message,
            code=code,
            severity=severity,
            category=category,
            location=location,
        )
        self.errors.append(error)
        return error

    @property
    def critical_errors(self) -> List[EnhancedValidationError]:
        """Get critical errors only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]

    @property
    def syntax_errors(self) -> List[EnhancedValidationError]:
        """Get syntax errors only (for backward compatibility)."""
        if self._syntax_errors is not None:
            return self._syntax_errors
        return [e for e in self.errors if e.category == ErrorCategory.SYNTAX]

    @syntax_errors.setter
    def syntax_errors(self, value: List[EnhancedValidationError]) -> None:
        """Set syntax errors."""
        self._syntax_errors = value
        # Also add to main errors list if not already there
        for error in value:
            if error not in self.errors:
                self.errors.append(error)

    @property
    def semantic_errors(self) -> List[EnhancedValidationError]:
        """Get semantic errors only."""
        if self._semantic_errors is not None:
            return self._semantic_errors
        return [e for e in self.errors if e.severity == ErrorSeverity.ERROR and e.category == ErrorCategory.SEMANTIC]

    @semantic_errors.setter
    def semantic_errors(self, value: List[EnhancedValidationError]) -> None:
        """Set semantic errors."""
        self._semantic_errors = value
        # Also add to main errors list if not already there
        for error in value:
            if error not in self.errors:
                self.errors.append(error)

    @property
    def warnings(self) -> List[EnhancedValidationError]:
        """Get warnings only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.WARNING]

    @property
    def info_messages(self) -> List[EnhancedValidationError]:
        """Get info messages only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.INFO]

    @property
    def hints(self) -> List[EnhancedValidationError]:
        """Get hints only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.HINT]

    @property
    def is_valid(self) -> bool:
        """True if no critical or semantic errors."""
        return len(self.critical_errors) == 0 and len(self.semantic_errors) == 0

    @property
    def has_warnings(self) -> bool:
        """True if there are warnings."""
        return len(self.warnings) > 0

    def get_errors_by_category(self, category: ErrorCategory) -> List[EnhancedValidationError]:
        """Get errors by category."""
        return [e for e in self.errors if e.category == category]

    def get_statistics(self) -> Dict[str, int]:
        """Get error statistics."""
        return {
            "critical": len(self.critical_errors),
            "errors": len(self.semantic_errors),
            "warnings": len(self.warnings),
            "info": len(self.info_messages),
            "hints": len(self.hints),
            "total": len(self.errors),
        }

    def to_legacy_format(self) -> List[str]:
        """Convert to legacy string list format for backward compatibility."""
        return [str(error) for error in self.errors if error.severity in (ErrorSeverity.CRITICAL, ErrorSeverity.ERROR)]

    def __str__(self) -> str:
        """Comprehensive string representation."""
        if not self.errors:
            return "No validation issues found."

        lines = []
        stats = self.get_statistics()

        # Summary
        summary_parts = []
        if stats["critical"] > 0:
            summary_parts.append(f"{stats['critical']} critical")
        if stats["errors"] > 0:
            summary_parts.append(f"{stats['errors']} errors")
        if stats["warnings"] > 0:
            summary_parts.append(f"{stats['warnings']} warnings")

        if summary_parts:
            lines.append(f"Validation found: {', '.join(summary_parts)}")
            lines.append("")

        # Group errors by severity
        for severity in [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO,
            ErrorSeverity.HINT,
        ]:
            severity_errors = [e for e in self.errors if e.severity == severity]
            if severity_errors:
                lines.append(f"{severity.value.upper()} ({len(severity_errors)}):")
                for error in severity_errors:
                    lines.append(f"  {error}")
                lines.append("")

        return "\n".join(lines).strip()


# Error code constants for common validation issues
class ErrorCodes:
    """Standard error codes for GFL validation."""

    # Syntax errors (SYNTAX001-SYNTAX099)
    SYNTAX_INVALID_YAML = "SYNTAX001"
    SYNTAX_INVALID_STRUCTURE = "SYNTAX002"
    SYNTAX_UNEXPECTED_CHARACTER = "SYNTAX003"

    # Semantic errors (SEMANTIC001-SEMANTIC099)
    SEMANTIC_MISSING_REQUIRED_FIELD = "SEMANTIC001"
    SEMANTIC_INVALID_FIELD_TYPE = "SEMANTIC002"
    SEMANTIC_UNKNOWN_TOOL = "SEMANTIC003"
    SEMANTIC_UNKNOWN_STRATEGY = "SEMANTIC004"
    SEMANTIC_INVALID_PARAMETER = "SEMANTIC005"
    SEMANTIC_MISSING_EXPERIMENT_BLOCK = "SEMANTIC006"
    SEMANTIC_VARIABLE_REDEFINITION = "SEMANTIC007"
    SEMANTIC_UNDEFINED_VARIABLE = "SEMANTIC008"
    SEMANTIC_UNDEFINED_HYPOTHESIS = "SEMANTIC009"  # New error code for undefined hypothesis
    SEMANTIC_UNDEFINED_ENTITY_REFERENCE = "SEMANTIC010"  # New error code for undefined entity references

    # IO Contract errors (SEMANTIC100-SEMANTIC199)
    SEMANTIC_INVALID_CONTRACT = "SEMANTIC100"
    SEMANTIC_CONTRACT_MISMATCH = "SEMANTIC101"
    SEMANTIC_MISSING_CONTRACT = "SEMANTIC102"

    # Schema Registry errors (SEMANTIC200-SEMANTIC299)
    SEMANTIC_INVALID_SCHEMA_FILE = "SEMANTIC200"
    SEMANTIC_SCHEMA_NOT_FOUND = "SEMANTIC201"
    SEMANTIC_INVALID_SCHEMA_DEFINITION = "SEMANTIC202"

    # Type errors (TYPE001-TYPE099)
    TYPE_INVALID_TYPE = "TYPE001"
    TYPE_MISSING_TYPE_INFO = "TYPE002"
    TYPE_INCOMPATIBLE_TYPES = "TYPE003"

    # Plugin errors (PLUGIN001-PLUGIN099)
    PLUGIN_NOT_FOUND = "PLUGIN001"
    PLUGIN_LOAD_FAILED = "PLUGIN002"
    PLUGIN_INVALID_METHOD = "PLUGIN003"
    PLUGIN_EXECUTION_FAILED = "PLUGIN004"

    # Schema errors (SCHEMA001-SCHEMA099)
    SCHEMA_VALIDATION_FAILED = "SCHEMA001"
    SCHEMA_MISSING_PROPERTY = "SCHEMA002"
    SCHEMA_INVALID_FORMAT = "SCHEMA003"

    # Performance warnings (PERFORMANCE001-PERFORMANCE099)
    PERFORMANCE_LARGE_DATASET = "PERFORMANCE001"
    PERFORMANCE_INEFFICIENT_OPERATION = "PERFORMANCE002"

    # Security issues (SECURITY001-SECURITY099)
    SECURITY_UNSAFE_OPERATION = "SECURITY001"
    SECURITY_UNTRUSTED_INPUT = "SECURITY002"


def create_syntax_error(
    message: str,
    location: Optional[SourceLocation] = None,
    code: str = ErrorCodes.SYNTAX_INVALID_YAML,
) -> EnhancedValidationError:
    """Create a syntax error with standard formatting."""
    return EnhancedValidationError(
        message=message,
        code=code,
        severity=ErrorSeverity.CRITICAL,
        category=ErrorCategory.SYNTAX,
        location=location,
    )


def create_semantic_error(
    message: str,
    location: Optional[SourceLocation] = None,
    code: str = ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
) -> EnhancedValidationError:
    """Create a semantic error with standard formatting."""
    return EnhancedValidationError(
        message=message,
        code=code,
        severity=ErrorSeverity.ERROR,
        category=ErrorCategory.SEMANTIC,
        location=location,
    )


def create_warning(
    message: str,
    location: Optional[SourceLocation] = None,
    category: ErrorCategory = ErrorCategory.SEMANTIC,
    code: str = "WARNING001",
) -> EnhancedValidationError:
    """Create a warning with standard formatting."""
    return EnhancedValidationError(
        message=message,
        code=code,
        severity=ErrorSeverity.WARNING,
        category=category,
        location=location,
    )


__all__ = [
    "ErrorSeverity",
    "ErrorCategory",
    "SourceLocation",
    "ErrorFix",
    "EnhancedValidationError",
    "EnhancedValidationResult",
    "ErrorCodes",
    "create_syntax_error",
    "create_semantic_error",
    "create_warning",
]
