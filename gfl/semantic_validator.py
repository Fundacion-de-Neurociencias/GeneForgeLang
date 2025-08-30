"""Enhanced semantic validator for GeneForgeLang ASTs.

This module provides comprehensive semantic validation with enhanced error
reporting, including location tracking, error codes, and suggested fixes.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from gfl.error_handling import (
    EnhancedValidationResult,
    ErrorCodes,
    ErrorSeverity,
    SourceLocation,
)

logger = logging.getLogger(__name__)


class EnhancedSemanticValidator:
    """Enhanced semantic validator for GFL ASTs.

    Provides comprehensive semantic validation with rich error reporting,
    including location tracking, error codes, and suggested fixes.
    """

    def __init__(self, file_path: Optional[str] = None):
        """Initialize validator.

        Args:
            file_path: Optional path to the file being validated for error reporting.
        """
        self.symbol_table: Dict[str, Dict[str, Any]] = {}
        self.result = EnhancedValidationResult(file_path=file_path)
        self.current_block: Optional[str] = None
        self.nested_level = 0

    def validate_ast(self, ast: Dict[str, Any]) -> EnhancedValidationResult:
        """Validate a GFL AST and return enhanced validation result.

        Args:
            ast: The AST dictionary to validate.

        Returns:
            EnhancedValidationResult with detailed error information.
        """
        self.symbol_table.clear()
        self.result = EnhancedValidationResult(file_path=self.result.file_path)
        self.nested_level = 0

        try:
            self._validate_root_structure(ast)
            self._validate_blocks(ast)
        except Exception as e:
            error = self.result.add_error(
                f"Internal validation error: {e}",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.CRITICAL,
            )
            error.add_context("exception_type", type(e).__name__)

        return self.result

    def _validate_root_structure(self, ast: Dict[str, Any]) -> None:
        """Validate the root structure of the AST."""
        if not isinstance(ast, dict):
            self.result.add_error(
                "AST must be a dictionary",
                ErrorCodes.SYNTAX_INVALID_STRUCTURE,
                ErrorSeverity.CRITICAL,
            ).add_fix("Ensure the GFL document is properly formatted as YAML")
            return

        # Check for at least one main block
        main_blocks = {"experiment", "analyze", "simulate", "branch"}
        found_blocks = set(ast.keys()) & main_blocks

        if not found_blocks:
            error = self.result.add_error(
                "GFL document must contain at least one main block",
                ErrorCodes.SEMANTIC_MISSING_EXPERIMENT_BLOCK,
                ErrorSeverity.ERROR,
            )
            error.add_fix(
                "Add an 'experiment', 'analyze', 'simulate', or 'branch' block"
            )
            error.add_context("available_blocks", list(main_blocks))

        # Check for unknown top-level keys
        valid_top_level = main_blocks | {"metadata", "imports", "exports"}
        unknown_keys = set(ast.keys()) - valid_top_level

        for key in unknown_keys:
            error = self.result.add_error(
                f"Unknown top-level block '{key}'",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Remove '{key}' or move it to the metadata block")
            error.add_context("valid_blocks", list(valid_top_level))

    def _validate_blocks(self, ast: Dict[str, Any]) -> None:
        """Validate individual blocks in the AST."""
        for block_name, block_content in ast.items():
            self.current_block = block_name

            if block_name == "experiment":
                self._validate_experiment_block(block_content)
            elif block_name == "analyze":
                self._validate_analysis_block(block_content)
            elif block_name == "simulate":
                self._validate_simulate_block(block_content)
            elif block_name == "branch":
                self._validate_branch_block(block_content)
            elif block_name == "metadata":
                self._validate_metadata_block(block_content)

    def _validate_experiment_block(self, experiment: Any) -> None:
        """Validate experiment block structure and content."""
        if not isinstance(experiment, dict):
            self.result.add_error(
                "Experiment block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                location=SourceLocation(line=0, column=0),  # Would be filled by parser
            ).add_fix("Format the experiment block as a YAML dictionary")
            return

        # Required fields
        required_fields = ["tool", "type"]
        for field in required_fields:
            if field not in experiment:
                error = self.result.add_error(
                    f"Missing required field '{field}' in experiment block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the experiment block")
                error.add_context("block", "experiment")
                error.add_context("required_fields", required_fields)

        # Validate tool
        if "tool" in experiment:
            self._validate_tool_field(experiment["tool"])

        # Validate type
        if "type" in experiment:
            self._validate_experiment_type(experiment["type"])

        # Validate params if present
        if "params" in experiment:
            self._validate_experiment_params(experiment["params"])

        # Check tool-type compatibility
        if "tool" in experiment and "type" in experiment:
            self._validate_tool_type_compatibility(
                experiment["tool"], experiment["type"]
            )

    def _validate_tool_field(self, tool: Any) -> None:
        """Validate the tool field."""
        if not isinstance(tool, str):
            error = self.result.add_error(
                f"Tool must be a string, got {type(tool).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Change tool to a string value like 'CRISPR_cas9'")
            return

        # Known tools (could be extended with a registry)
        known_tools = {
            "CRISPR_cas9",
            "CRISPR_cas12",
            "CRISPR_base_editor",
            "CRISPR_prime_editor",
            "RNAseq",
            "ChIPseq",
            "ATACseq",
            "WGS",
            "WES",
            "targeted_seq",
        }

        if tool not in known_tools:
            error = self.result.add_error(
                f"Unknown tool '{tool}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use a known tool or ensure '{tool}' plugin is available")
            error.add_context("suggested_tools", list(known_tools))

    def _validate_experiment_type(self, exp_type: Any) -> None:
        """Validate the experiment type."""
        if not isinstance(exp_type, str):
            error = self.result.add_error(
                f"Experiment type must be a string, got {type(exp_type).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Change type to a string like 'gene_editing'")
            return

        valid_types = {
            "gene_editing",
            "sequencing",
            "analysis",
            "simulation",
            "validation",
        }

        if exp_type not in valid_types:
            error = self.result.add_error(
                f"Unknown experiment type '{exp_type}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(valid_types)}")
            error.add_context("valid_types", list(valid_types))

    def _validate_experiment_params(self, params: Any) -> None:
        """Validate experiment parameters."""
        if not isinstance(params, dict):
            self.result.add_error(
                f"Experiment params must be a dictionary, got {type(params).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format params as a YAML dictionary with key-value pairs")
            return

        # Validate specific parameter types
        type_validations = {
            "concentration": (float, int),
            "temperature": (float, int),
            "replicates": int,
            "target_gene": str,
            "guide_rna": str,
        }

        for param_name, param_value in params.items():
            if param_name in type_validations:
                expected_types = type_validations[param_name]
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)

                if not isinstance(param_value, expected_types):
                    type_names = " or ".join(t.__name__ for t in expected_types)
                    error = self.result.add_error(
                        f"Parameter '{param_name}' should be {type_names}, got {type(param_value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Change '{param_name}' to a {type_names} value")
                    error.add_context("parameter", param_name)
                    error.add_context("expected_type", type_names)

    def _validate_tool_type_compatibility(self, tool: str, exp_type: str) -> None:
        """Validate tool and type compatibility."""
        compatibility_matrix = {
            "CRISPR_cas9": ["gene_editing"],
            "CRISPR_cas12": ["gene_editing"],
            "CRISPR_base_editor": ["gene_editing"],
            "RNAseq": ["sequencing", "analysis"],
            "ChIPseq": ["sequencing", "analysis"],
            "ATACseq": ["sequencing", "analysis"],
        }

        if tool in compatibility_matrix:
            compatible_types = compatibility_matrix[tool]
            if exp_type not in compatible_types:
                error = self.result.add_error(
                    f"Tool '{tool}' is not compatible with type '{exp_type}'",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Use type: {' or '.join(compatible_types)}")
                error.add_context("tool", tool)
                error.add_context("compatible_types", compatible_types)

    def _validate_analysis_block(self, analysis: Any) -> None:
        """Validate analysis block."""
        if not isinstance(analysis, dict):
            self.result.add_error(
                "Analysis block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the analysis block as a YAML dictionary")
            return

        # Required strategy field
        if "strategy" not in analysis:
            error = self.result.add_error(
                "Missing required field 'strategy' in analysis block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'strategy: <analysis_type>' to the analysis block")
        else:
            self._validate_analysis_strategy(analysis["strategy"])

    def _validate_analysis_strategy(self, strategy: Any) -> None:
        """Validate analysis strategy."""
        if not isinstance(strategy, str):
            self.result.add_error(
                f"Analysis strategy must be a string, got {type(strategy).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'differential' for the strategy")
            return

        valid_strategies = {
            "differential",
            "pathway",
            "variant",
            "expression",
            "structural",
            "functional",
            "comparative",
            "longitudinal",
        }

        if strategy not in valid_strategies:
            error = self.result.add_error(
                f"Unknown analysis strategy '{strategy}'",
                ErrorCodes.SEMANTIC_UNKNOWN_STRATEGY,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_strategies))}")
            error.add_context("valid_strategies", list(valid_strategies))

    def _validate_simulate_block(self, simulate: Any) -> None:
        """Validate simulate block."""
        if not isinstance(simulate, bool):
            error = self.result.add_error(
                f"Simulate must be a boolean, got {type(simulate).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            )
            error.add_fix("Use 'true' or 'false' for the simulate value")

    def _validate_branch_block(self, branch: Any) -> None:
        """Validate branch block."""
        if not isinstance(branch, dict):
            self.result.add_error(
                "Branch block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix(
                "Format the branch block as a YAML dictionary with 'if' and 'then'"
            )
            return

        # Branch blocks need 'if' and 'then'
        if "if" not in branch:
            error = self.result.add_error(
                "Missing 'if' condition in branch block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'if: <condition>' to the branch block")

        if "then" not in branch:
            error = self.result.add_error(
                "Missing 'then' clause in branch block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'then: <actions>' to the branch block")

    def _validate_metadata_block(self, metadata: Any) -> None:
        """Validate metadata block."""
        if not isinstance(metadata, dict):
            self.result.add_error(
                "Metadata block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
                ErrorSeverity.WARNING,
            ).add_fix("Format metadata as key-value pairs")
            return

        # Suggest useful metadata fields if missing
        useful_fields = {"experiment_id", "researcher", "date", "description"}
        present_fields = set(metadata.keys())
        missing_useful = useful_fields - present_fields

        if missing_useful and len(present_fields) < 2:
            error = self.result.add_error(
                "Consider adding more descriptive metadata",
                "HINT001",
                ErrorSeverity.HINT,
            )
            error.add_fix(f"Consider adding: {', '.join(missing_useful)}")
            error.add_context("suggested_fields", list(missing_useful))


# Legacy validator for backward compatibility
class SemanticValidator:
    """Legacy semantic validator for backward compatibility.

    Maintains the original API while delegating to the enhanced validator.
    """

    def __init__(self):
        self.symbol_table = {}
        self.errors = []
        self._enhanced_validator = EnhancedSemanticValidator()

    def validate_program(self, ast):
        """Validate a program AST and return a list of error strings."""
        result = self._enhanced_validator.validate_ast(ast)
        return result.to_legacy_format()


# Global validator instances
_validator = SemanticValidator()
_enhanced_validator = EnhancedSemanticValidator()


def validate(
    ast: Dict[str, Any], enhanced: bool = False
) -> Union[List[str], EnhancedValidationResult]:
    """Validate a GFL AST and return validation results.

    Args:
        ast: The AST dictionary to validate.
        enhanced: If True, return EnhancedValidationResult. If False, return legacy string list.

    Returns:
        List of error strings (legacy) or EnhancedValidationResult (enhanced).
    """
    if enhanced:
        return _enhanced_validator.validate_ast(ast)
    else:
        return _validator.validate_program(ast)


__all__ = ["SemanticValidator", "EnhancedSemanticValidator", "validate"]
