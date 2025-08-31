"""Enhanced JSON Schema validation for GeneForgeLang.

This module provides comprehensive JSON Schema validation with enhanced error
reporting, IDE integration support, and autocompletion capabilities.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import ValidationError as JsonSchemaError

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None
    Draft202012Validator = None
    JsonSchemaError = Exception
    HAS_JSONSCHEMA = False

from gfl.error_handling import (
    EnhancedValidationResult,
    ErrorCategory,
    ErrorCodes,
    ErrorSeverity,
    SourceLocation,
)

logger = logging.getLogger(__name__)


class EnhancedSchemaValidator:
    """Enhanced JSON Schema validator with rich error reporting."""

    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize the schema validator.

        Args:
            schema_path: Optional custom path to schema file.
        """
        self.schema_path = schema_path or self._get_default_schema_path()
        self._schema: Optional[Dict[str, Any]] = None
        self._validator: Optional[Draft202012Validator] = None

    def _get_default_schema_path(self) -> Path:
        """Get the default GFL schema path."""
        return Path(__file__).parent.parent / "schema" / "gfl.schema.json"

    def _load_schema(self) -> Dict[str, Any]:
        """Load and cache the JSON schema."""
        if self._schema is not None:
            return self._schema

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self._schema = json.load(f)
                return self._schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON schema: {e}")

    def _get_validator(self) -> Draft202012Validator:
        """Get the cached JSON schema validator."""
        if self._validator is None:
            schema = self._load_schema()
            self._validator = Draft202012Validator(schema)
        return self._validator

    def validate(
        self, data: Dict[str, Any], file_path: Optional[str] = None
    ) -> EnhancedValidationResult:
        """Validate GFL data against the JSON schema.

        Args:
            data: GFL data dictionary to validate.
            file_path: Optional file path for error reporting.

        Returns:
            EnhancedValidationResult with detailed validation information.
        """
        result = EnhancedValidationResult(file_path=file_path)

        if not HAS_JSONSCHEMA:
            error = result.add_error(
                "JSON Schema validation unavailable - install jsonschema package",
                ErrorCodes.SCHEMA_VALIDATION_FAILED,
                ErrorSeverity.WARNING,
                ErrorCategory.SCHEMA,
            )
            error.add_fix("Install with: pip install jsonschema")
            return result

        try:
            validator = self._get_validator()

            # Perform validation and collect errors
            for json_error in validator.iter_errors(data):
                self._convert_json_schema_error(json_error, result)

        except Exception as e:
            error = result.add_error(
                f"Schema validation failed: {e}",
                ErrorCodes.SCHEMA_VALIDATION_FAILED,
                ErrorSeverity.CRITICAL,
                ErrorCategory.SCHEMA,
            )
            error.add_context("exception", str(e))
            error.add_context("exception_type", type(e).__name__)

        return result

    def _convert_json_schema_error(
        self, json_error: JsonSchemaError, result: EnhancedValidationResult
    ) -> None:
        """Convert JSON Schema validation error to enhanced format."""
        # Build location path
        location_parts = []
        for part in json_error.absolute_path:
            location_parts.append(str(part))
        location_str = ".".join(location_parts) if location_parts else "root"

        # Create source location (would need parser integration for line/column)
        location = SourceLocation.unknown()

        # Determine error severity and provide helpful messages
        message = json_error.message
        severity = ErrorSeverity.ERROR
        code = ErrorCodes.SCHEMA_VALIDATION_FAILED

        # Handle specific validation cases
        if json_error.validator == "required":
            code = ErrorCodes.SCHEMA_MISSING_PROPERTY
            missing_prop = (
                json_error.message.split("'")[1]
                if "'" in json_error.message
                else "unknown"
            )
            message = f"Missing required property '{missing_prop}'"

        elif json_error.validator == "enum":
            code = ErrorCodes.SCHEMA_INVALID_FORMAT
            if hasattr(json_error, "schema") and "enum" in json_error.schema:
                valid_values = json_error.schema["enum"]
                message = f"Invalid value. Must be one of: {', '.join(str(v) for v in valid_values)}"

        elif json_error.validator == "type":
            code = ErrorCodes.TYPE_INVALID_TYPE
            expected_type = json_error.schema.get("type", "unknown")
            message = f"Invalid type. Expected {expected_type}"

        elif json_error.validator == "additionalProperties":
            severity = ErrorSeverity.WARNING
            code = "SCHEMA_WARNING001"

        elif json_error.validator in ["minimum", "maximum"]:
            code = ErrorCodes.SCHEMA_INVALID_FORMAT

        # Add the error
        error = result.add_error(
            message, code, severity, ErrorCategory.SCHEMA, location
        )

        # Add context and suggestions
        error.add_context("schema_path", location_str)
        error.add_context("validator", json_error.validator)

        if hasattr(json_error, "schema"):
            schema = json_error.schema

            # Add specific suggestions based on schema information
            if json_error.validator == "enum" and "enum" in schema:
                values = schema["enum"][:5]  # Show first 5 options
                error.add_fix(f"Use one of: {', '.join(str(v) for v in values)}")

            elif json_error.validator == "required":
                missing_prop = (
                    json_error.message.split("'")[1]
                    if "'" in json_error.message
                    else ""
                )
                if missing_prop and "properties" in json_error.schema:
                    prop_schema = json_error.schema["properties"].get(missing_prop, {})
                    if "examples" in prop_schema and prop_schema["examples"]:
                        example = prop_schema["examples"][0]
                        error.add_fix(f"Add '{missing_prop}: {example}'")
                    else:
                        error.add_fix(f"Add required property '{missing_prop}'")

            elif json_error.validator == "type":
                expected_type = schema.get("type", "unknown")
                if "examples" in schema and schema["examples"]:
                    example = schema["examples"][0]
                    error.add_fix(f"Use {expected_type} value like: {example}")
                else:
                    error.add_fix(f"Change value to {expected_type} type")

    def get_completion_suggestions(
        self, data: Dict[str, Any], cursor_path: List[str]
    ) -> List[Dict[str, Any]]:
        """Get autocompletion suggestions for the given cursor position.

        Args:
            data: Current GFL data.
            cursor_path: Path to cursor position (e.g., ['experiment', 'params']).

        Returns:
            List of completion suggestions with metadata.
        """
        suggestions = []

        if not HAS_JSONSCHEMA:
            return suggestions

        try:
            schema = self._load_schema()
            current_schema = schema

            # Navigate to the current schema location
            for part in cursor_path:
                if (
                    "properties" in current_schema
                    and part in current_schema["properties"]
                ):
                    current_schema = current_schema["properties"][part]
                elif "items" in current_schema:
                    current_schema = current_schema["items"]
                else:
                    break

            # Generate suggestions based on current schema
            if "properties" in current_schema:
                for prop, prop_schema in current_schema["properties"].items():
                    suggestion = {
                        "name": prop,
                        "type": prop_schema.get("type", "unknown"),
                        "description": prop_schema.get("description", ""),
                        "required": prop in current_schema.get("required", []),
                    }

                    # Add examples if available
                    if "examples" in prop_schema:
                        suggestion["examples"] = prop_schema["examples"]

                    # Add enum values if available
                    if "enum" in prop_schema:
                        suggestion["enum"] = prop_schema["enum"]

                    suggestions.append(suggestion)

            # Add enum suggestions if current schema has enum
            elif "enum" in current_schema:
                for value in current_schema["enum"]:
                    suggestions.append(
                        {
                            "name": str(value),
                            "type": "enum_value",
                            "description": f"Valid value: {value}",
                            "required": False,
                        }
                    )

        except Exception as e:
            logger.warning(f"Failed to generate completions: {e}")

        return suggestions

    def validate_property(
        self, value: Any, property_path: List[str]
    ) -> EnhancedValidationResult:
        """Validate a specific property value against its schema.

        Args:
            value: The value to validate.
            property_path: Path to the property (e.g., ['experiment', 'tool']).

        Returns:
            EnhancedValidationResult for the specific property.
        """
        result = EnhancedValidationResult()

        if not HAS_JSONSCHEMA:
            return result

        try:
            schema = self._load_schema()
            current_schema = schema

            # Navigate to property schema
            for part in property_path:
                if (
                    "properties" in current_schema
                    and part in current_schema["properties"]
                ):
                    current_schema = current_schema["properties"][part]
                else:
                    # Property not found in schema
                    result.add_error(
                        f"Property '{'.'.join(property_path)}' not defined in schema",
                        ErrorCodes.SCHEMA_VALIDATION_FAILED,
                        ErrorSeverity.WARNING,
                        ErrorCategory.SCHEMA,
                    )
                    return result

            # Validate the value against the property schema
            validator = Draft202012Validator(current_schema)
            for json_error in validator.iter_errors(value):
                self._convert_json_schema_error(json_error, result)

        except Exception as e:
            result.add_error(
                f"Property validation failed: {e}",
                ErrorCodes.SCHEMA_VALIDATION_FAILED,
                ErrorSeverity.ERROR,
                ErrorCategory.SCHEMA,
            )

        return result


# Global validator instance
_schema_validator = EnhancedSchemaValidator()


def validate_with_enhanced_schema(
    data: Dict[str, Any], file_path: Optional[str] = None
) -> EnhancedValidationResult:
    """Validate GFL data with enhanced schema validation.

    Args:
        data: GFL data to validate.
        file_path: Optional file path for error reporting.

    Returns:
        EnhancedValidationResult with detailed schema validation.
    """
    return _schema_validator.validate(data, file_path)


def get_autocompletion_suggestions(
    data: Dict[str, Any], cursor_path: List[str]
) -> List[Dict[str, Any]]:
    """Get IDE autocompletion suggestions.

    Args:
        data: Current GFL data.
        cursor_path: Path to cursor position.

    Returns:
        List of completion suggestions.
    """
    return _schema_validator.get_completion_suggestions(data, cursor_path)


def validate_property_value(
    value: Any, property_path: List[str]
) -> EnhancedValidationResult:
    """Validate a specific property value.

    Args:
        value: Value to validate.
        property_path: Path to the property in schema.

    Returns:
        EnhancedValidationResult for the property.
    """
    return _schema_validator.validate_property(value, property_path)


__all__ = [
    "EnhancedSchemaValidator",
    "validate_with_enhanced_schema",
    "get_autocompletion_suggestions",
    "validate_property_value",
]
