"""GFL Execution Engine with proper plugin integration."""

from typing import Any, Dict, List

from gfl.container_executor import ContainerExecutionError, ContainerExecutor
from gfl.plugins.plugin_registry import plugin_registry


class ExecutionError(Exception):
    """Exception raised during workflow execution."""

    pass


class GFLExecutionEngine:
    """Engine for executing GFL workflows."""

    def __init__(self):
        self.workflow_state = {}
        self.container_executor = ContainerExecutor()

    def execute_design_block(self, design_block: dict[str, Any]) -> dict[str, Any]:
        """Execute a design block."""
        model_name = design_block.get("model")
        if not model_name:
            raise ExecutionError("Design block missing 'model' parameter")

        try:
            # Check if there's a container image for this plugin
            container_image = plugin_registry.get_container_image(model_name)

            params = {
                "count": design_block.get("count", 10),
                "entity": design_block.get("entity", "ProteinSequence"),
                "objective": design_block.get("objective", {}),
                "length": design_block.get("length", 100),
            }

            if container_image and self.container_executor.is_container_execution_available():
                # Execute in container
                try:
                    result = self.container_executor.execute_plugin_method_in_container(
                        container_image, "generator", "generate", params
                    )
                    if "parsed_result" in result:
                        result = result["parsed_result"]
                    else:
                        raise ExecutionError(f"Failed to parse container execution result: {result}")
                except ContainerExecutionError as e:
                    raise ExecutionError(f"Container execution failed: {e}")
            else:
                # Execute locally
                generator = plugin_registry.get_generator(model_name)
                result = generator.generate(params)

            # Store in workflow state if output specified
            output_var = design_block.get("output")
            if output_var:
                self.workflow_state[output_var] = result

            return result

        except ValueError as e:
            available = plugin_registry.list_generators()
            raise ExecutionError(f"Design model '{model_name}' not available. Available: {available}")

    def execute_optimize_block(self, optimize_block: dict[str, Any]) -> dict[str, Any]:
        """Execute an optimize block."""
        strategy = optimize_block.get("strategy", {})
        strategy_name = strategy.get("name") if isinstance(strategy, dict) else strategy

        if not strategy_name:
            raise ExecutionError("Optimize block missing strategy name")

        try:
            # Check if there's a container image for this plugin
            container_image = plugin_registry.get_container_image(strategy_name)

            params = {
                "search_space": optimize_block.get("search_space", {}),
                "objective": optimize_block.get("objective", {}),
                "budget": optimize_block.get("budget", {}),
                "max_iterations": optimize_block.get("budget", {}).get("max_experiments", 10),
            }

            if container_image and self.container_executor.is_container_execution_available():
                # Execute in container
                try:
                    result = self.container_executor.execute_plugin_method_in_container(
                        container_image, "optimizer", "optimize", params
                    )
                    if "parsed_result" in result:
                        result = result["parsed_result"]
                    else:
                        raise ExecutionError(f"Failed to parse container execution result: {result}")
                except ContainerExecutionError as e:
                    raise ExecutionError(f"Container execution failed: {e}")
            else:
                # Execute locally
                optimizer = plugin_registry.get_optimizer(strategy_name)
                result = optimizer.optimize(params)

            return result

        except ValueError as e:
            available = plugin_registry.list_optimizers()
            raise ExecutionError(f"Optimization strategy '{strategy_name}' not supported. Available: {available}")


def execute_gfl_ast(ast: dict[str, Any]) -> dict[str, Any]:
    """Execute a complete GFL AST."""
    engine = GFLExecutionEngine()
    results = {}

    # Execute design blocks
    if "design" in ast:
        results["design"] = engine.execute_design_block(ast["design"])

    # Execute optimize blocks
    if "optimize" in ast:
        results["optimize"] = engine.execute_optimize_block(ast["optimize"])

    results["workflow_state"] = engine.workflow_state
    return results


def validate_execution_requirements(ast: dict[str, Any]) -> list[str]:
    """Validate that required plugins are available."""
    errors = []

    # Check design block requirements
    if "design" in ast:
        model_name = ast["design"].get("model")
        if model_name:
            available_generators = plugin_registry.list_generators()
            if model_name not in available_generators:
                errors.append(f"Design model '{model_name}' not available. Available: {available_generators}")

    # Check optimize block requirements
    if "optimize" in ast:
        strategy = ast["optimize"].get("strategy", {})
        strategy_name = strategy.get("name") if isinstance(strategy, dict) else strategy
        if strategy_name:
            available_optimizers = plugin_registry.list_optimizers()
            if strategy_name not in available_optimizers:
                errors.append(
                    f"Optimization strategy '{strategy_name}' not supported. Available: {available_optimizers}"
                )

    return errors
