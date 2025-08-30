"""JSON Schema validation for GFL documents.

This module provides schema-based validation using the official GFL JSON Schema.
It complements the semantic validator by checking structural and format constraints.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import jsonschema
    from jsonschema import Draft202012Validator

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

from gfl.types import ValidationError, ValidationResult


def get_schema_path() -> Path:
    """Get path to the GFL JSON schema."""
    return Path(__file__).parent.parent / "schema" / "gfl.schema.json"


def load_schema() -> Optional[Dict[str, Any]]:
    """Load the GFL JSON schema.

    Returns:
        Schema dictionary or None if not found
    """
    schema_path = get_schema_path()
    if not schema_path.exists():
        return None

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def validate_with_schema(
    data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """Validate GFL data against JSON schema.

    Args:
        data: GFL data to validate
        schema: Schema to use (defaults to official GFL schema)

    Returns:
        ValidationResult with schema validation errors
    """
    if not HAS_JSONSCHEMA:
        return ValidationResult(
            warnings=[
                ValidationError(
                    message="jsonschema not available - install with: pip install jsonschema",
                    code="SCHEMA_VALIDATOR_UNAVAILABLE",
                )
            ]
        )

    if schema is None:
        schema = load_schema()
        if schema is None:
            return ValidationResult(
                errors=[
                    ValidationError(
                        message="GFL schema not found", code="SCHEMA_NOT_FOUND"
                    )
                ]
            )

    try:
        # Create validator
        validator = Draft202012Validator(schema)

        # Collect validation errors
        errors = []
        warnings = []

        for error in validator.iter_errors(data):
            # Determine location
            location = (
                ".".join(str(p) for p in error.absolute_path)
                if error.absolute_path
                else "root"
            )

            # Create validation error
            validation_error = ValidationError(
                message=error.message,
                location=location,
                severity="error",
                code="SCHEMA_VALIDATION",
            )

            # Categorize some errors as warnings
            if any(
                keyword in error.message.lower()
                for keyword in ["additional", "unknown"]
            ):
                warnings.append(validation_error)
            else:
                errors.append(validation_error)

        return ValidationResult(errors=errors, warnings=warnings)

    except Exception as e:
        return ValidationResult(
            errors=[
                ValidationError(
                    message=f"Schema validation failed: {str(e)}",
                    code="SCHEMA_VALIDATION_ERROR",
                )
            ]
        )


def validate_gfl_format(data: Dict[str, Any]) -> ValidationResult:
    """Validate GFL format and structure.

    This performs format-specific validation beyond JSON schema,
    including GFL-specific constraints and conventions.

    Args:
        data: GFL data to validate

    Returns:
        ValidationResult with format validation errors
    """
    errors = []
    warnings = []
    info = []

    # Check for required top-level blocks
    has_experiment = "experiment" in data
    has_analyze = "analyze" in data
    has_simulate = "simulate" in data
    has_branch = "branch" in data

    if not any([has_experiment, has_analyze, has_simulate, has_branch]):
        errors.append(
            ValidationError(
                message="GFL document must contain at least one of: experiment, analyze, simulate, branch",
                location="root",
                code="MISSING_REQUIRED_BLOCK",
            )
        )

    # Validate experiment block
    if has_experiment:
        exp = data["experiment"]

        # Check tool-type compatibility
        tool = exp.get("tool", "")
        exp_type = exp.get("type", "")

        # Define compatible tool-type combinations
        tool_type_compat = {
            "CRISPR_cas9": ["gene_editing"],
            "CRISPR_cas12": ["gene_editing"],
            "RNAseq": ["sequencing", "analysis"],
            "ChIPseq": ["sequencing", "analysis"],
            "ATACseq": ["sequencing", "analysis"],
        }

        if tool in tool_type_compat:
            if exp_type not in tool_type_compat[tool]:
                warnings.append(
                    ValidationError(
                        message=f"Tool '{tool}' may not be compatible with type '{exp_type}'",
                        location="experiment",
                        severity="warning",
                        code="TOOL_TYPE_MISMATCH",
                    )
                )

    return ValidationResult(errors=errors, warnings=warnings, info=info)


def comprehensive_validate(data: Dict[str, Any]) -> ValidationResult:
    """Perform comprehensive validation combining schema and format checks.

    Args:
        data: GFL data to validate

    Returns:
        Combined validation results
    """
    # Schema validation
    schema_result = validate_with_schema(data)

    # Format validation
    format_result = validate_gfl_format(data)

    # Combine results
    return ValidationResult(
        errors=schema_result.errors + format_result.errors,
        warnings=schema_result.warnings + format_result.warnings,
        info=schema_result.info + format_result.info,
    )


__all__ = [
    "validate_with_schema",
    "validate_gfl_format",
    "comprehensive_validate",
    "load_schema",
    "get_schema_path",
]
