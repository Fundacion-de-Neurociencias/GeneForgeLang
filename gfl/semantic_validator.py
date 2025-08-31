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
        main_blocks = {"experiment", "analyze", "simulate", "branch", "design", "optimize"}
        found_blocks = set(ast.keys()) & main_blocks

        if not found_blocks:
            error = self.result.add_error(
                "GFL document must contain at least one main block",
                ErrorCodes.SEMANTIC_MISSING_EXPERIMENT_BLOCK,
                ErrorSeverity.ERROR,
            )
            error.add_fix(
                "Add an 'experiment', 'analyze', 'simulate', 'design', 'optimize', or 'branch' block"
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
            elif block_name == "design":
                self._validate_design_block(block_content)
            elif block_name == "optimize":
                self._validate_optimize_block(block_content)
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
            # Skip validation for parameter injection (${...} syntax)
            if isinstance(param_value, str) and param_value.startswith("${") and param_value.endswith("}"):
                continue
                
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

    def _validate_design_block(self, design: Any) -> None:
        """Validate design block structure and content."""
        if not isinstance(design, dict):
            self.result.add_error(
                "Design block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the design block as a YAML dictionary")
            return

        # Required fields
        required_fields = ["entity", "model", "objective", "count", "output"]
        for field in required_fields:
            if field not in design:
                error = self.result.add_error(
                    f"Missing required field '{field}' in design block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the design block")
                error.add_context("block", "design")
                error.add_context("required_fields", required_fields)

        # Validate entity field
        if "entity" in design:
            self._validate_design_entity(design["entity"])

        # Validate model field
        if "model" in design:
            self._validate_design_model(design["model"])

        # Validate objective field
        if "objective" in design:
            self._validate_design_objective(design["objective"])

        # Validate count field
        if "count" in design:
            self._validate_design_count(design["count"])

        # Validate output field
        if "output" in design:
            self._validate_design_output(design["output"])

        # Validate constraints field if present
        if "constraints" in design:
            self._validate_design_constraints(design["constraints"])

    def _validate_design_entity(self, entity: Any) -> None:
        """Validate the entity field in design block."""
        if not isinstance(entity, str):
            self.result.add_error(
                f"Design entity must be a string, got {type(entity).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ProteinSequence' for the entity")
            return

        valid_entities = {
            "ProteinSequence",
            "DNASequence", 
            "RNASequence",
            "SmallMolecule",
            "Peptide",
            "Antibody",
        }

        if entity not in valid_entities:
            error = self.result.add_error(
                f"Unknown design entity '{entity}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_entities))}")
            error.add_context("valid_entities", list(valid_entities))

    def _validate_design_model(self, model: Any) -> None:
        """Validate the model field in design block."""
        if not isinstance(model, str):
            self.result.add_error(
                f"Design model must be a string, got {type(model).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ProteinGeneratorVAE' for the model")
            return

        # Known generative models (could be extended with a registry)
        known_models = {
            "ProteinGeneratorVAE",
            "DNADesignerGAN",
            "MoleculeTransformer",
            "SequenceOptimizer",
            "StructurePredictor",
        }

        if model not in known_models:
            error = self.result.add_error(
                f"Unknown generative model '{model}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Ensure '{model}' plugin is available or use a known model")
            error.add_context("suggested_models", list(known_models))

    def _validate_design_objective(self, objective: Any) -> None:
        """Validate the objective field in design block."""
        if not isinstance(objective, dict):
            self.result.add_error(
                f"Design objective must be a dictionary, got {type(objective).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format objective as '{maximize: metric}' or '{minimize: metric}'")
            return

        # Must have exactly one of maximize or minimize
        has_maximize = "maximize" in objective
        has_minimize = "minimize" in objective

        if not (has_maximize or has_minimize):
            error = self.result.add_error(
                "Objective must contain either 'maximize' or 'minimize' key",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'maximize: binding_affinity' or 'minimize: toxicity'")

        if has_maximize and has_minimize:
            error = self.result.add_error(
                "Objective cannot have both 'maximize' and 'minimize' keys",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Choose either 'maximize' or 'minimize', not both")

        # Validate metric names
        if has_maximize:
            self._validate_objective_metric(objective["maximize"], "maximize")
        if has_minimize:
            self._validate_objective_metric(objective["minimize"], "minimize")

    def _validate_objective_metric(self, metric: Any, direction: str) -> None:
        """Validate an objective metric."""
        if not isinstance(metric, str):
            self.result.add_error(
                f"Objective metric must be a string, got {type(metric).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix(f"Use a string like 'binding_affinity' for {direction}")
            return

        # Common metrics for different entity types
        valid_metrics = {
            "binding_affinity",
            "stability", 
            "solubility",
            "toxicity",
            "activity",
            "selectivity",
            "permeability",
            "expression_level",
        }

        if metric not in valid_metrics:
            error = self.result.add_error(
                f"Unknown objective metric '{metric}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(valid_metrics))}")
            error.add_context("valid_metrics", list(valid_metrics))

    def _validate_design_count(self, count: Any) -> None:
        """Validate the count field in design block."""
        if not isinstance(count, int):
            self.result.add_error(
                f"Design count must be an integer, got {type(count).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use an integer like 10 for the count")
            return

        if count <= 0:
            error = self.result.add_error(
                f"Design count must be positive, got {count}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use a positive integer like 10 for the count")

        if count > 1000:
            error = self.result.add_error(
                f"Design count {count} seems very high, consider reducing",
                "HINT002",
                ErrorSeverity.HINT,
            )
            error.add_fix("Consider using a smaller count for faster generation")

    def _validate_design_output(self, output: Any) -> None:
        """Validate the output field in design block."""
        if not isinstance(output, str):
            self.result.add_error(
                f"Design output must be a string, got {type(output).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string identifier like 'designed_candidates'")
            return

        # Validate identifier format
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', output):
            error = self.result.add_error(
                f"Invalid output identifier '{output}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use a valid identifier like 'designed_candidates' or 'output_seqs'")

    def _validate_design_constraints(self, constraints: Any) -> None:
        """Validate the constraints field in design block."""
        if not isinstance(constraints, list):
            self.result.add_error(
                f"Design constraints must be a list, got {type(constraints).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format constraints as a list of constraint expressions")
            return

        for i, constraint in enumerate(constraints):
            if not isinstance(constraint, str):
                error = self.result.add_error(
                    f"Constraint {i+1} must be a string, got {type(constraint).__name__}",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix(f"Convert constraint {i+1} to a string expression")

    def _validate_optimize_block(self, optimize: Any) -> None:
        """Validate optimize block structure and content."""
        if not isinstance(optimize, dict):
            self.result.add_error(
                "Optimize block must be a dictionary",
                ErrorCodes.SEMANTIC_INVALID_FIELD_TYPE,
            ).add_fix("Format the optimize block as a YAML dictionary")
            return

        # Required fields
        required_fields = ["search_space", "strategy", "objective", "budget", "run"]
        for field in required_fields:
            if field not in optimize:
                error = self.result.add_error(
                    f"Missing required field '{field}' in optimize block",
                    ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
                )
                error.add_fix(f"Add '{field}: <value>' to the optimize block")
                error.add_context("block", "optimize")
                error.add_context("required_fields", required_fields)

        # Validate individual fields
        if "search_space" in optimize:
            self._validate_optimize_search_space(optimize["search_space"])

        if "strategy" in optimize:
            self._validate_optimize_strategy(optimize["strategy"])

        if "objective" in optimize:
            self._validate_optimize_objective(optimize["objective"])

        if "budget" in optimize:
            self._validate_optimize_budget(optimize["budget"])

        if "run" in optimize:
            self._validate_optimize_run(optimize["run"])

    def _validate_optimize_search_space(self, search_space: Any) -> None:
        """Validate the search_space field in optimize block."""
        if not isinstance(search_space, dict):
            self.result.add_error(
                f"Search space must be a dictionary, got {type(search_space).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format search_space as parameter_name: range() or choice() expressions")
            return

        if not search_space:
            self.result.add_error(
                "Search space cannot be empty",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add at least one parameter with range() or choice() syntax")
            return

        # Validate each parameter definition
        for param_name, param_def in search_space.items():
            self._validate_search_space_parameter(param_name, param_def)

    def _validate_search_space_parameter(self, param_name: str, param_def: Any) -> None:
        """Validate a single parameter in search space."""
        if not isinstance(param_def, str):
            self.result.add_error(
                f"Parameter '{param_name}' definition must be a string, got {type(param_def).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix(f"Use 'range(min, max)' or 'choice([...])' for '{param_name}'")
            return

        # Validate parameter name format
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param_name):
            error = self.result.add_error(
                f"Invalid parameter name '{param_name}'",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use valid identifier like 'promoter_strength' or 'temperature'")

        # Validate parameter definition syntax
        if param_def.startswith('range(') and param_def.endswith(')'):
            self._validate_range_syntax(param_name, param_def)
        elif param_def.startswith('choice([') and param_def.endswith('])'):
            self._validate_choice_syntax(param_name, param_def)
        else:
            error = self.result.add_error(
                f"Invalid syntax for parameter '{param_name}': {param_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use 'range(min, max)' or 'choice([val1, val2, ...])' syntax")

    def _validate_range_syntax(self, param_name: str, range_def: str) -> None:
        """Validate range(min, max) syntax."""
        try:
            # Extract content between parentheses
            content = range_def[6:-1].strip()  # Remove 'range(' and ')'
            parts = [p.strip() for p in content.split(',')]
            
            if len(parts) != 2:
                error = self.result.add_error(
                    f"Range for '{param_name}' must have exactly 2 values: range(min, max)",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Use 'range(0.1, 1.0)' format for '{param_name}'")
                return
                
            # Try to parse as numbers
            try:
                min_val = float(parts[0])
                max_val = float(parts[1])
                
                if min_val >= max_val:
                    error = self.result.add_error(
                        f"Range minimum ({min_val}) must be less than maximum ({max_val}) for '{param_name}'",
                        ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    )
                    error.add_fix(f"Ensure min < max in range() for '{param_name}'")
            except ValueError:
                error = self.result.add_error(
                    f"Range values for '{param_name}' must be numbers",
                    ErrorCodes.TYPE_INVALID_TYPE,
                )
                error.add_fix(f"Use numeric values like 'range(0.1, 1.0)' for '{param_name}'")
                
        except Exception:
            error = self.result.add_error(
                f"Invalid range syntax for '{param_name}': {range_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix(f"Use correct format: 'range(min, max)' for '{param_name}'")

    def _validate_choice_syntax(self, param_name: str, choice_def: str) -> None:
        """Validate choice([...]) syntax."""
        try:
            # Extract content between square brackets inside choice([...])
            # Find the opening [ and closing ]
            start_bracket = choice_def.find('[')
            end_bracket = choice_def.rfind(']')
            
            if start_bracket == -1 or end_bracket == -1 or start_bracket >= end_bracket:
                error = self.result.add_error(
                    f"Invalid choice syntax for '{param_name}': {choice_def}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Use correct format: 'choice([val1, val2, ...])' for '{param_name}'")
                return
                
            content = choice_def[start_bracket + 1:end_bracket].strip()
            
            if not content:
                error = self.result.add_error(
                    f"Choice for '{param_name}' cannot be empty",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix(f"Add at least one choice value for '{param_name}'")
                return
                
            # Simple validation - should contain comma-separated values
            choices = [c.strip() for c in content.split(',') if c.strip()]
            
            if len(choices) < 2:
                error = self.result.add_error(
                    f"Choice for '{param_name}' should have at least 2 options",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Add more choice options for '{param_name}'")
                
        except Exception:
            error = self.result.add_error(
                f"Invalid choice syntax for '{param_name}': {choice_def}",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix(f"Use correct format: 'choice([val1, val2, ...])' for '{param_name}'")

    def _validate_optimize_strategy(self, strategy: Any) -> None:
        """Validate the strategy field in optimize block."""
        if not isinstance(strategy, dict):
            self.result.add_error(
                f"Strategy must be a dictionary, got {type(strategy).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format strategy as '{name: StrategyName, ...}'")
            return

        # Must have a name field
        if "name" not in strategy:
            error = self.result.add_error(
                "Strategy must have a 'name' field",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'name: ActiveLearning' to strategy")
            return

        strategy_name = strategy["name"]
        if not isinstance(strategy_name, str):
            self.result.add_error(
                f"Strategy name must be a string, got {type(strategy_name).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Use a string like 'ActiveLearning' for strategy name")
            return

        # Known optimization strategies
        known_strategies = {
            "ActiveLearning",
            "BayesianOptimization", 
            "GeneticAlgorithm",
            "SimulatedAnnealing",
            "RandomSearch",
            "GridSearch",
        }

        if strategy_name not in known_strategies:
            error = self.result.add_error(
                f"Unknown optimization strategy '{strategy_name}'",
                ErrorCodes.SEMANTIC_UNKNOWN_TOOL,
                ErrorSeverity.WARNING,
            )
            error.add_fix(f"Use one of: {', '.join(sorted(known_strategies))}")
            error.add_context("available_strategies", list(known_strategies))

    def _validate_optimize_objective(self, objective: Any) -> None:
        """Validate the objective field in optimize block."""
        if not isinstance(objective, dict):
            self.result.add_error(
                f"Objective must be a dictionary, got {type(objective).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format objective as '{maximize: metric}' or '{minimize: metric}'")
            return

        # Must have exactly one of maximize or minimize
        has_maximize = "maximize" in objective
        has_minimize = "minimize" in objective

        if not (has_maximize or has_minimize):
            error = self.result.add_error(
                "Objective must contain either 'maximize' or 'minimize' key",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'maximize: gene_expression_level' or 'minimize: cost'")

        if has_maximize and has_minimize:
            error = self.result.add_error(
                "Objective cannot have both 'maximize' and 'minimize' keys",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Choose either 'maximize' or 'minimize', not both")

        # Validate metric names
        if has_maximize:
            self._validate_objective_metric(objective["maximize"], "maximize")
        if has_minimize:
            self._validate_objective_metric(objective["minimize"], "minimize")

    def _validate_optimize_budget(self, budget: Any) -> None:
        """Validate the budget field in optimize block."""
        if not isinstance(budget, dict):
            self.result.add_error(
                f"Budget must be a dictionary, got {type(budget).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format budget as '{max_experiments: 50}' or similar")
            return

        if not budget:
            self.result.add_error(
                "Budget cannot be empty",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            ).add_fix("Add at least one budget constraint like 'max_experiments: 50'")
            return

        # Validate budget constraints
        valid_constraints = {
            "max_experiments", 
            "max_time", 
            "max_cost", 
            "convergence_threshold",
        }

        for constraint, value in budget.items():
            if constraint not in valid_constraints:
                error = self.result.add_error(
                    f"Unknown budget constraint '{constraint}'",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    ErrorSeverity.WARNING,
                )
                error.add_fix(f"Use one of: {', '.join(sorted(valid_constraints))}")
                error.add_context("valid_constraints", list(valid_constraints))

            # Validate constraint values
            if constraint == "max_experiments":
                if not isinstance(value, int) or value <= 0:
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a positive integer, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use a positive integer for '{constraint}'")
            elif constraint == "max_time":
                if not isinstance(value, str):
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a string with time format, got {type(value).__name__}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use time format like '24h', '7d' for '{constraint}'")
                else:
                    # Validate time format
                    import re
                    if not re.match(r'^\d+[smhd]$', value):
                        error = self.result.add_error(
                            f"Budget constraint '{constraint}' has invalid time format: {value}",
                            ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                        )
                        error.add_fix(f"Use format like '24h', '7d', '30m' for '{constraint}'")
            elif constraint in ["max_cost", "convergence_threshold"]:
                if not isinstance(value, (int, float)) or value <= 0:
                    error = self.result.add_error(
                        f"Budget constraint '{constraint}' must be a positive number, got {value}",
                        ErrorCodes.TYPE_INVALID_TYPE,
                    )
                    error.add_fix(f"Use a positive number for '{constraint}'")

    def _validate_optimize_run(self, run: Any) -> None:
        """Validate the run field in optimize block."""
        if not isinstance(run, dict):
            self.result.add_error(
                f"Run block must be a dictionary, got {type(run).__name__}",
                ErrorCodes.TYPE_INVALID_TYPE,
            ).add_fix("Format run as a nested experiment or analyze block")
            return

        # Must contain exactly one of: experiment, analyze
        valid_nested_blocks = {"experiment", "analyze"}
        found_blocks = set(run.keys()) & valid_nested_blocks

        if not found_blocks:
            error = self.result.add_error(
                "Run block must contain an 'experiment' or 'analyze' block",
                ErrorCodes.SEMANTIC_MISSING_REQUIRED_FIELD,
            )
            error.add_fix("Add 'experiment: {...}' or 'analyze: {...}' to the run block")
            error.add_context("valid_nested_blocks", list(valid_nested_blocks))

        if len(found_blocks) > 1:
            error = self.result.add_error(
                "Run block can only contain one nested block",
                ErrorCodes.SEMANTIC_INVALID_PARAMETER,
            )
            error.add_fix("Use either 'experiment' or 'analyze', not both")

        # Validate the nested block
        if "experiment" in run:
            self._validate_experiment_block(run["experiment"])
            self._validate_parameter_injection(run["experiment"])
        elif "analyze" in run:
            self._validate_analysis_block(run["analyze"])
            self._validate_parameter_injection(run["analyze"])

    def _validate_parameter_injection(self, block: dict) -> None:
        """Validate ${...} parameter injection syntax in nested blocks."""
        # Recursively check all values in the block for parameter injection
        self._check_parameter_injection_recursive(block, "")

    def _check_parameter_injection_recursive(self, obj: Any, path: str) -> None:
        """Recursively check for parameter injection patterns."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                self._check_parameter_injection_recursive(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                self._check_parameter_injection_recursive(item, new_path)
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            # This is a parameter injection - validate the parameter name
            param_name = obj[2:-1]  # Remove ${}
            if not param_name:
                error = self.result.add_error(
                    f"Empty parameter injection at {path}",
                    ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                )
                error.add_fix("Specify a parameter name like ${parameter_name}")
            else:
                # Validate parameter name format
                import re
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param_name):
                    error = self.result.add_error(
                        f"Invalid parameter name '{param_name}' in injection at {path}",
                        ErrorCodes.SEMANTIC_INVALID_PARAMETER,
                    )
                    error.add_fix("Use valid identifier like ${valid_param_name}")


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
