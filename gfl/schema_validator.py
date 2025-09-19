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
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def validate_with_schema(data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> ValidationResult:
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
            return ValidationResult(errors=[ValidationError(message="GFL schema not found", code="SCHEMA_NOT_FOUND")])

    try:
        # Create validator
        validator = Draft202012Validator(schema)

        # Collect validation errors
        errors = []
        warnings = []

        for error in validator.iter_errors(data):
            # Determine location
            location = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"

            # Create validation error
            validation_error = ValidationError(
                message=error.message,
                location=location,
                severity="error",
                code="SCHEMA_VALIDATION",
            )

            # Categorize some errors as warnings
            if any(keyword in error.message.lower() for keyword in ["additional", "unknown"]):
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
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    info: List[ValidationError] = []

    # Check for required top-level blocks
    has_experiment = "experiment" in data
    has_analyze = "analyze" in data
    has_design = "design" in data
    has_optimize = "optimize" in data
    has_simulate = "simulate" in data
    has_branch = "branch" in data

    if not any([has_experiment, has_analyze, has_design, has_optimize, has_simulate, has_branch]):
        errors.append(
            ValidationError(
                message="GFL document must contain at least one of: experiment, analyze, design, optimize, simulate, branch",
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

    # Validate design block
    if has_design:
        design = data["design"]

        # Check for required fields
        required_design_fields = ["entity", "model", "objective", "count", "output"]
        for field in required_design_fields:
            if field not in design:
                errors.append(
                    ValidationError(
                        message=f"Missing required field '{field}' in design block",
                        location="design",
                        code="MISSING_REQUIRED_FIELD",
                    )
                )

        # Validate objective structure
        if "objective" in design:
            objective = design["objective"]
            if isinstance(objective, dict):
                has_maximize = "maximize" in objective
                has_minimize = "minimize" in objective

                if not (has_maximize or has_minimize):
                    warnings.append(
                        ValidationError(
                            message="Objective should contain either 'maximize' or 'minimize' key",
                            location="design.objective",
                            severity="warning",
                            code="OBJECTIVE_MISSING_DIRECTION",
                        )
                    )

                if has_maximize and has_minimize:
                    errors.append(
                        ValidationError(
                            message="Objective cannot have both 'maximize' and 'minimize' keys",
                            location="design.objective",
                            code="OBJECTIVE_CONFLICTING_DIRECTIONS",
                        )
                    )

        # Validate count field
        if "count" in design:
            count = design["count"]
            if isinstance(count, int):
                if count <= 0:
                    errors.append(
                        ValidationError(
                            message="Design count must be positive",
                            location="design.count",
                            code="INVALID_COUNT_VALUE",
                        )
                    )
                elif count > 1000:
                    warnings.append(
                        ValidationError(
                            message="Design count is very high, consider reducing for performance",
                            location="design.count",
                            severity="warning",
                            code="HIGH_COUNT_WARNING",
                        )
                    )

    # Validate optimize block
    if has_optimize:
        optimize = data["optimize"]

        # Check for required fields
        required_optimize_fields = ["search_space", "strategy", "objective", "budget", "run"]
        for field in required_optimize_fields:
            if field not in optimize:
                errors.append(
                    ValidationError(
                        message=f"Missing required field '{field}' in optimize block",
                        location="optimize",
                        code="MISSING_REQUIRED_FIELD",
                    )
                )

        # Validate search_space structure
        if "search_space" in optimize:
            search_space = optimize["search_space"]
            if isinstance(search_space, dict):
                if not search_space:
                    errors.append(
                        ValidationError(
                            message="Search space cannot be empty",
                            location="optimize.search_space",
                            code="EMPTY_SEARCH_SPACE",
                        )
                    )

                # Basic validation of parameter definitions
                for param_name, param_def in search_space.items():
                    if not isinstance(param_def, str):
                        errors.append(
                            ValidationError(
                                message=f"Parameter '{param_name}' definition must be a string",
                                location=f"optimize.search_space.{param_name}",
                                code="INVALID_PARAMETER_DEFINITION",
                            )
                        )
                    elif not (param_def.startswith("range(") or param_def.startswith("choice(")):
                        warnings.append(
                            ValidationError(
                                message=f"Parameter '{param_name}' should use range() or choice() syntax",
                                location=f"optimize.search_space.{param_name}",
                                severity="warning",
                                code="UNUSUAL_PARAMETER_SYNTAX",
                            )
                        )
            else:
                errors.append(
                    ValidationError(
                        message="Search space must be a dictionary",
                        location="optimize.search_space",
                        code="INVALID_SEARCH_SPACE_TYPE",
                    )
                )

        # Validate strategy structure
        if "strategy" in optimize:
            strategy = optimize["strategy"]
            if isinstance(strategy, dict):
                if "name" not in strategy:
                    errors.append(
                        ValidationError(
                            message="Strategy must have a 'name' field",
                            location="optimize.strategy",
                            code="MISSING_STRATEGY_NAME",
                        )
                    )
            else:
                errors.append(
                    ValidationError(
                        message="Strategy must be a dictionary",
                        location="optimize.strategy",
                        code="INVALID_STRATEGY_TYPE",
                    )
                )

        # Validate objective structure (similar to design block)
        if "objective" in optimize:
            objective = optimize["objective"]
            if isinstance(objective, dict):
                has_maximize = "maximize" in objective
                has_minimize = "minimize" in objective

                if not (has_maximize or has_minimize):
                    warnings.append(
                        ValidationError(
                            message="Objective should contain either 'maximize' or 'minimize' key",
                            location="optimize.objective",
                            severity="warning",
                            code="OBJECTIVE_MISSING_DIRECTION",
                        )
                    )

                if has_maximize and has_minimize:
                    errors.append(
                        ValidationError(
                            message="Objective cannot have both 'maximize' and 'minimize' keys",
                            location="optimize.objective",
                            code="OBJECTIVE_CONFLICTING_DIRECTIONS",
                        )
                    )
            else:
                errors.append(
                    ValidationError(
                        message="Objective must be a dictionary",
                        location="optimize.objective",
                        code="INVALID_OBJECTIVE_TYPE",
                    )
                )

        # Validate budget structure
        if "budget" in optimize:
            budget = optimize["budget"]
            if isinstance(budget, dict):
                if not budget:
                    errors.append(
                        ValidationError(
                            message="Budget cannot be empty",
                            location="optimize.budget",
                            code="EMPTY_BUDGET",
                        )
                    )

                # Check for common budget constraints
                for constraint, value in budget.items():
                    if constraint == "max_experiments":
                        if not isinstance(value, int) or value <= 0:
                            errors.append(
                                ValidationError(
                                    message=f"Budget constraint '{constraint}' must be a positive integer",
                                    location=f"optimize.budget.{constraint}",
                                    code="INVALID_BUDGET_VALUE",
                                )
                            )
                    elif constraint == "max_time":
                        if not isinstance(value, str):
                            errors.append(
                                ValidationError(
                                    message=f"Budget constraint '{constraint}' must be a time string (e.g., '24h', '7d')",
                                    location=f"optimize.budget.{constraint}",
                                    code="INVALID_BUDGET_VALUE",
                                )
                            )
                        else:
                            # Validate time format
                            import re

                            if not re.match(r"^\d+[smhd]$", value):
                                errors.append(
                                    ValidationError(
                                        message=f"Budget constraint '{constraint}' has invalid time format: {value}",
                                        location=f"optimize.budget.{constraint}",
                                        code="INVALID_BUDGET_VALUE",
                                    )
                                )
                    elif constraint in ["max_cost", "convergence_threshold"]:
                        if not isinstance(value, (int, float)) or value <= 0:
                            errors.append(
                                ValidationError(
                                    message=f"Budget constraint '{constraint}' must be a positive number",
                                    location=f"optimize.budget.{constraint}",
                                    code="INVALID_BUDGET_VALUE",
                                )
                            )
            else:
                errors.append(
                    ValidationError(
                        message="Budget must be a dictionary",
                        location="optimize.budget",
                        code="INVALID_BUDGET_TYPE",
                    )
                )

        # Validate run structure
        if "run" in optimize:
            run_block = optimize["run"]
            if isinstance(run_block, dict):
                nested_blocks = {"experiment", "analyze"}
                found_blocks = set(run_block.keys()) & nested_blocks

                if not found_blocks:
                    errors.append(
                        ValidationError(
                            message="Run block must contain an 'experiment' or 'analyze' block",
                            location="optimize.run",
                            code="MISSING_NESTED_BLOCK",
                        )
                    )
                elif len(found_blocks) > 1:
                    errors.append(
                        ValidationError(
                            message="Run block can only contain one nested block",
                            location="optimize.run",
                            code="MULTIPLE_NESTED_BLOCKS",
                        )
                    )
            else:
                errors.append(
                    ValidationError(
                        message="Run block must be a dictionary",
                        location="optimize.run",
                        code="INVALID_RUN_TYPE",
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
