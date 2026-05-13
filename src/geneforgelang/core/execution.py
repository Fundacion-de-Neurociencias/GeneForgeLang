"""GFL Execution Engine with proper plugin integration."""

from typing import Any, Dict, List

from geneforgelang.plugins.plugin_registry import PluginRegistry


class ExecutionError(Exception):
    """Exception raised during workflow execution."""

    pass


class GFLExecutionEngine:
    """Engine for executing GFL workflows."""

    def __init__(self):
        self.workflow_state = {}

    def execute_design_block(self, design_block: dict[str, Any], registry: PluginRegistry) -> dict[str, Any]:
        """Execute a design block."""
        print(design_block)
        model_name = design_block.get("model")
        if not model_name:
            raise ExecutionError("Design block missing 'model' parameter")

        try:
            generator = registry.get_generator(model_name)
            result = generator.generate(
                entity=design_block.get("entity", "ProteinSequence"), 
                objective=design_block.get("objective", {}), 
                constraints=design_block.get("constraints", []), 
                count=design_block.get("count", 10))

            # Store in workflow state if output specified
            output_var = design_block.get("output")
            if output_var:
                self.workflow_state[output_var] = result

            return result

        except ValueError as e:
            available = registry.list_generators()
            raise ExecutionError(
                f"Design model '{model_name}' not available. Available: {available}"
            )

    def execute_optimize_block(self, optimize_block: dict[str, Any], registry: PluginRegistry   ) -> dict[str, Any]:
        """Execute an optimize block."""
        strategy = optimize_block.get("strategy", {})
        strategy_name = strategy.get("name") if isinstance(strategy, dict) else strategy

        if not strategy_name:
            raise ExecutionError("Optimize block missing strategy name")

        try:
            optimizer = registry.get_optimizer(strategy_name)
            params = {
                "search_space": optimize_block.get("search_space", {}),
                "objective": optimize_block.get("objective", {}),
                "budget": optimize_block.get("budget", {}),
                "max_iterations": optimize_block.get("budget", {}).get("max_experiments", 10),
            }

            result = optimizer.optimize(params)
            return result

        except ValueError as e:
            available = registry.list_optimizers()
            raise ExecutionError(
                f"Optimization strategy '{strategy_name}' not supported. Available: {available}"
            )


def execute_gfl_ast(ast: dict[str, Any], registry: PluginRegistry) -> dict[str, Any]:
    """Execute a complete GFL AST."""
    engine = GFLExecutionEngine()
    results = {}

    # Execute design blocks
    if "design" in ast:
        results["design"] = engine.execute_design_block(ast["design"], registry)

    # Execute optimize blocks
    if "optimize" in ast:
        results["optimize"] = engine.execute_optimize_block(ast["optimize"], registry)

    results["workflow_state"] = engine.workflow_state
    return results


def validate_execution_requirements(ast: dict[str, Any], registry: PluginRegistry) -> list[str]:
    """Validate that required plugins are available."""
    errors = []

    # Check design block requirements
    if "design" in ast:
        model_name = ast["design"].get("model")
        if model_name:
            available_generators = registry.list_generators()
            if model_name not in available_generators:
                errors.append(
                    f"Design model '{model_name}' not available. Available: {available_generators}"
                )

    # Check optimize block requirements
    if "optimize" in ast:
        strategy = ast["optimize"].get("strategy", {})
        strategy_name = strategy.get("name") if isinstance(strategy, dict) else strategy
        if strategy_name:
            available_optimizers = registry.list_optimizers()
            if strategy_name not in available_optimizers:
                errors.append(
                    f"Optimization strategy '{strategy_name}' not supported. Available: {available_optimizers}"
                )

    return errors
