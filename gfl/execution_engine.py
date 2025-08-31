"""Execution engine for GeneForgeLang workflow blocks.

This module provides the core execution engine that orchestrates the execution
of GFL workflow blocks by dispatching to appropriate plugins based on block
types and configurations.

The engine integrates:
1. Design block execution via GeneratorPlugin instances
2. Optimize block execution via OptimizerPlugin instances  
3. Result aggregation and workflow state management
4. Error handling and recovery mechanisms
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from .plugins import (
    DesignCandidate,
    ExperimentResult,
    GeneratorPlugin,
    OptimizationStep,
    OptimizerPlugin,
    get_available_generators,
    get_available_optimizers,
)
from .plugins.plugin_registry import plugin_registry

logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Exception raised during GFL block execution."""
    
    def __init__(self, message: str, block_type: str, plugin_name: Optional[str] = None):
        super().__init__(message)
        self.block_type = block_type
        self.plugin_name = plugin_name


class WorkflowState:
    """Manages state across workflow execution."""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.current_block: Optional[str] = None
        
    def set_variable(self, name: str, value: Any) -> None:
        """Set a workflow variable."""
        self.variables[name] = value
        
    def get_variable(self, name: str) -> Any:
        """Get a workflow variable."""
        return self.variables.get(name)
        
    def add_execution_record(self, block_type: str, block_config: Dict[str, Any], result: Any) -> None:
        """Add execution record to history."""
        record = {
            "block_type": block_type,
            "config": block_config,
            "result": result,
            "timestamp": time.time()
        }
        self.execution_history.append(record)


class GFLExecutionEngine:
    """Core execution engine for GFL workflow blocks."""
    
    def __init__(self):
        self.state = WorkflowState()
        
    def execute_design_block(self, design_config: Dict[str, Any]) -> List[DesignCandidate]:
        """Execute a design block using appropriate GeneratorPlugin.
        
        Args:
            design_config: Design block configuration from GFL AST
            
        Returns:
            List of generated DesignCandidate objects
            
        Raises:
            ExecutionError: If design execution fails
        """
        try:
            # Extract design parameters
            entity = design_config["entity"]
            model_name = design_config["model"]
            objective = design_config["objective"]
            count = design_config["count"]
            output_var = design_config["output"]
            constraints = design_config.get("constraints", [])
            
            # Find appropriate generator plugin
            generators = get_available_generators()
            
            if model_name not in generators:
                available = ", ".join(generators.keys())
                raise ExecutionError(
                    f"Generator model '{model_name}' not found. Available: {available}",
                    "design",
                    model_name
                )
            
            generator = generators[model_name]
            
            # Validate plugin supports the requested entity type
            if not self._validate_entity_support(generator, entity):
                supported = [e.value for e in generator.supported_entities]
                raise ExecutionError(
                    f"Generator '{model_name}' does not support entity '{entity}'. "
                    f"Supported: {supported}",
                    "design",
                    model_name
                )
            
            # Validate objective and constraints
            obj_errors = generator.validate_objective(objective)
            constraint_errors = generator.validate_constraints(constraints)
            
            if obj_errors or constraint_errors:
                error_msg = "Validation failed: " + "; ".join(obj_errors + constraint_errors)
                raise ExecutionError(error_msg, "design", model_name)
            
            logger.info(f"Executing design block with {model_name} for {count} {entity} candidates")
            
            # Execute generation
            start_time = time.time()
            candidates = generator.generate(
                entity=entity,
                objective=objective,
                constraints=constraints,
                count=count
            )
            execution_time = time.time() - start_time
            
            # Store results in workflow state
            self.state.set_variable(output_var, candidates)
            
            # Record execution
            self.state.add_execution_record("design", design_config, {
                "candidate_count": len(candidates),
                "execution_time": execution_time,
                "output_variable": output_var
            })
            
            logger.info(f"Design block completed: generated {len(candidates)} candidates in {execution_time:.2f}s")
            
            return candidates
            
        except Exception as e:
            if isinstance(e, ExecutionError):
                raise
            raise ExecutionError(f"Design block execution failed: {e}", "design", design_config.get("model"))
    
    def execute_optimize_block(self, optimize_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an optimize block using appropriate OptimizerPlugin.
        
        Args:
            optimize_config: Optimize block configuration from GFL AST
            
        Returns:
            Dictionary containing optimization results and final parameters
            
        Raises:
            ExecutionError: If optimization execution fails
        """
        try:
            # Extract optimization parameters
            search_space = optimize_config["search_space"]
            strategy = optimize_config["strategy"]
            objective = optimize_config["objective"]
            budget = optimize_config["budget"]
            run_config = optimize_config["run"]
            
            strategy_name = strategy["name"]
            
            # Find appropriate optimizer plugin
            optimizers = get_available_optimizers()
            
            # Match strategy to available optimizers
            compatible_optimizer = None
            for opt_name, optimizer in optimizers.items():
                if any(s.value == strategy_name for s in optimizer.supported_strategies):
                    compatible_optimizer = optimizer
                    break
            
            if not compatible_optimizer:
                available_strategies = []
                for optimizer in optimizers.values():
                    available_strategies.extend([s.value for s in optimizer.supported_strategies])
                raise ExecutionError(
                    f"No optimizer found for strategy '{strategy_name}'. "
                    f"Available strategies: {available_strategies}",
                    "optimize"
                )
            
            logger.info(f"Executing optimize block with strategy '{strategy_name}' using {compatible_optimizer.name}")
            
            # Setup optimizer
            compatible_optimizer.setup(search_space, strategy, objective, budget)
            
            # Execute optimization loop
            experiment_history: List[ExperimentResult] = []
            iteration = 0
            max_iterations = budget.get("max_experiments", 100)
            
            while iteration < max_iterations:
                # Get next parameters to try
                try:
                    step = compatible_optimizer.suggest_next(experiment_history)
                except StopIteration:
                    logger.info("Optimization terminated by algorithm")
                    break
                
                # Check stopping conditions
                if compatible_optimizer.should_stop(experiment_history, budget):
                    logger.info("Optimization stopping criteria met")
                    break
                
                # Execute experiment with suggested parameters
                try:
                    result = self._execute_experiment_step(run_config, step.parameters)
                    experiment_history.append(result)
                    
                    logger.debug(f"Optimization iteration {iteration + 1}: "
                               f"objective = {result.objective_value:.4f}")
                    
                except Exception as e:
                    # Record failed experiment
                    failed_result = ExperimentResult(
                        parameters=step.parameters,
                        objective_value=0.0,
                        success=False,
                        error_message=str(e)
                    )
                    experiment_history.append(failed_result)
                    logger.warning(f"Experiment failed at iteration {iteration + 1}: {e}")
                
                iteration += 1
            
            # Compile optimization results
            if experiment_history:
                best_result = max(experiment_history, key=lambda r: r.objective_value if r.success else -float('inf'))
                convergence_info = self._analyze_convergence(experiment_history)
            else:
                raise ExecutionError("No successful experiments in optimization", "optimize")
            
            optimization_results = {
                "best_parameters": best_result.parameters,
                "best_objective_value": best_result.objective_value,
                "total_experiments": len(experiment_history),
                "successful_experiments": sum(1 for r in experiment_history if r.success),
                "convergence_info": convergence_info,
                "experiment_history": experiment_history
            }
            
            # Record execution
            self.state.add_execution_record("optimize", optimize_config, optimization_results)
            
            logger.info(f"Optimize block completed: {iteration} experiments, "
                       f"best objective = {best_result.objective_value:.4f}")
            
            return optimization_results
            
        except Exception as e:
            if isinstance(e, ExecutionError):
                raise
            raise ExecutionError(f"Optimize block execution failed: {e}", "optimize")
    
    def _validate_entity_support(self, generator: GeneratorPlugin, entity: str) -> bool:
        """Validate that generator supports the requested entity type."""
        return any(e.value == entity for e in generator.supported_entities)
    
    def _execute_experiment_step(self, run_config: Dict[str, Any], parameters: Dict[str, Any]) -> ExperimentResult:
        """Execute a single experiment step with given parameters.
        
        This method handles parameter injection into the run block and simulates
        experiment execution. In a real implementation, this would dispatch to
        the appropriate experimental execution system.
        """
        # Simulate parameter injection
        injected_config = self._inject_parameters(run_config, parameters)
        
        # Simulate experiment execution (in practice, this would call actual tools)
        objective_value = self._simulate_experiment_execution(injected_config, parameters)
        
        return ExperimentResult(
            parameters=parameters,
            objective_value=objective_value,
            success=True
        )
    
    def _inject_parameters(self, config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Inject optimization parameters into run block configuration."""
        import copy
        import re
        
        injected_config = copy.deepcopy(config)
        
        def replace_parameters(obj):
            if isinstance(obj, str):
                # Replace ${parameter} syntax
                for param, value in parameters.items():
                    pattern = f"${{?{param}}}?"
                    if f"${{{param}}}" in obj:
                        obj = obj.replace(f"${{{param}}}", str(value))
                return obj
            elif isinstance(obj, dict):
                return {k: replace_parameters(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_parameters(item) for item in obj]
            else:
                return obj
        
        return replace_parameters(injected_config)
    
    def _simulate_experiment_execution(self, config: Dict[str, Any], parameters: Dict[str, Any]) -> float:
        """Simulate experiment execution and return objective value.
        
        This is a placeholder that simulates realistic experimental results.
        In practice, this would dispatch to actual experimental execution systems.
        """
        import random
        import math
        
        # Simulate realistic experimental objective functions
        
        # Example: CRISPR optimization (efficiency based on temperature and concentration)
        if "experiment" in config and config["experiment"].get("tool") == "CRISPR_cas9":
            temp = float(parameters.get("temperature", 37))
            conc = float(parameters.get("guide_concentration", 50))
            
            # Optimal temperature around 37°C, concentration around 75 nM
            temp_effect = math.exp(-0.01 * (temp - 37) ** 2)
            conc_effect = math.exp(-0.0002 * (conc - 75) ** 2)
            
            base_efficiency = temp_effect * conc_effect
            
            # Add realistic noise
            noise = random.gauss(0, 0.05)
            objective_value = max(0, min(1, base_efficiency + noise))
            
        else:
            # Generic simulation: quadratic function with optimum around 0.5 for each parameter
            objective_value = 1.0
            for param, value in parameters.items():
                if isinstance(value, (int, float)):
                    # Normalize to [0, 1] range and compute quadratic
                    normalized = float(value) / 100.0  # Assume typical range 0-100
                    normalized = max(0, min(1, normalized))
                    objective_value *= (1 - 4 * (normalized - 0.5) ** 2)
            
            # Add noise
            noise = random.gauss(0, 0.03)
            objective_value = max(0, min(1, objective_value + noise))
        
        return objective_value
    
    def _analyze_convergence(self, experiment_history: List[ExperimentResult]) -> Dict[str, Any]:
        """Analyze optimization convergence characteristics."""
        if len(experiment_history) < 3:
            return {"converged": False, "reason": "insufficient_data"}
        
        # Get successful experiments
        successful = [r for r in experiment_history if r.success]
        if len(successful) < 3:
            return {"converged": False, "reason": "insufficient_successful_experiments"}
        
        # Analyze objective value progression
        objective_values = [r.objective_value for r in successful]
        
        # Check for improvement stagnation
        recent_values = objective_values[-5:]  # Last 5 experiments
        if len(recent_values) >= 3:
            improvement = max(recent_values) - min(recent_values)
            if improvement < 0.01:  # Default convergence threshold
                return {"converged": True, "reason": "stagnation", "improvement": improvement}
        
        # Check for consistent improvement trend
        if len(objective_values) >= 5:
            recent_trend = sum(objective_values[-3:]) / 3 - sum(objective_values[-6:-3]) / 3
            if recent_trend < 0.001:
                return {"converged": True, "reason": "trend_flattening", "trend": recent_trend}
        
        return {"converged": False, "reason": "still_improving"}
    
    def get_workflow_state(self) -> WorkflowState:
        """Get current workflow state."""
        return self.state
    
    def reset_workflow_state(self) -> None:
        """Reset workflow state for new execution."""
        self.state = WorkflowState()


# Convenience functions for integration with existing GFL API
def execute_gfl_ast(ast: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a complete GFL AST.
    
    Args:
        ast: Parsed GFL AST dictionary
        
    Returns:
        Dictionary containing execution results for each block
    """
    engine = GFLExecutionEngine()
    results = {}
    
    try:
        # Execute design blocks
        if "design" in ast:
            design_result = engine.execute_design_block(ast["design"])
            results["design"] = {
                "candidates": design_result,
                "count": len(design_result)
            }
        
        # Execute optimize blocks
        if "optimize" in ast:
            optimize_result = engine.execute_optimize_block(ast["optimize"])
            results["optimize"] = optimize_result
        
        # Add workflow state information
        results["workflow_state"] = {
            "variables": engine.state.variables,
            "execution_history": engine.state.execution_history
        }
        
        return results
        
    except ExecutionError as e:
        logger.error(f"GFL execution failed in {e.block_type} block: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during GFL execution: {e}")
        raise ExecutionError(f"Execution failed: {e}", "unknown")


def validate_execution_requirements(ast: Dict[str, Any]) -> List[str]:
    """Validate that required plugins are available for AST execution.
    
    Args:
        ast: Parsed GFL AST dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check design block requirements
    if "design" in ast:
        model_name = ast["design"].get("model")
        if model_name:
            generators = get_available_generators()
            if model_name not in generators:
                available = ", ".join(generators.keys())
                errors.append(f"Design model '{model_name}' not available. Available: {available}")
    
    # Check optimize block requirements  
    if "optimize" in ast:
        strategy_name = ast["optimize"].get("strategy", {}).get("name")
        if strategy_name:
            optimizers = get_available_optimizers()
            
            # Check if any optimizer supports the strategy
            strategy_supported = False
            for optimizer in optimizers.values():
                if any(s.value == strategy_name for s in optimizer.supported_strategies):
                    strategy_supported = True
                    break
            
            if not strategy_supported:
                available_strategies = []
                for optimizer in optimizers.values():
                    available_strategies.extend([s.value for s in optimizer.supported_strategies])
                errors.append(f"Optimization strategy '{strategy_name}' not supported. "
                            f"Available: {available_strategies}")
    
    return errors