"""Simple optimization plugin."""

import random
from typing import Any

from geneforgelang.plugins.base import BaseOptimizerPlugin
from geneforgelang.provenance import (
    Provenance,
    ProvenancedDict,
    register_simulated_component,
    warn_first_use,
)

PROVENANCE = Provenance(
    "simulated",
    "geneforgelang.plugins.builtin.simple_optimizer.SimpleOptimizer",
    "1.0.0",
)
register_simulated_component(
    "SimpleOptimizer",
    PROVENANCE,
    "src/geneforgelang/plugins/builtin/simple_optimizer.py",
    "An objective function backed by a real model or assay, with a test that the search beats chance",
)


class SimpleOptimizer(BaseOptimizerPlugin):
    """
    Simple optimization plugin for demonstration purposes.

    This implements a basic random search optimization strategy.
    For production use, more sophisticated methods like Bayesian
    optimization or genetic algorithms would be used.

    The score of every trial is a random draw, not an evaluation of the
    objective: the result is labelled ``simulated`` and decision paths refuse it
    unless ``allow_simulated=True``.
    """

    provenance = PROVENANCE

    def __init__(self):
        super().__init__()
        self.name = "SimpleOptimizer"
        self.description = "Basic random search optimizer"

    def optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Perform optimization using random search."""
        warn_first_use(self.name, PROVENANCE)

        search_space = params.get("search_space", {})
        max_iterations = params.get("max_iterations", 10)
        objective = params.get("objective", {})

        results = []
        best_score = float("-inf") if "maximize" in objective else float("inf")
        best_params = None

        for i in range(max_iterations):
            # Sample random parameters from search space
            trial_params = {}
            for param_name, param_range in search_space.items():
                if isinstance(param_range, dict) and "range" in param_range:
                    min_val, max_val = param_range["range"]
                    trial_params[param_name] = random.uniform(min_val, max_val)
                else:
                    trial_params[param_name] = random.choice(param_range)

            # Simulate objective function evaluation
            score = random.uniform(0, 1)  # Placeholder score

            results.append({"iteration": i + 1, "parameters": trial_params, "score": score})

            # Update best result
            if (
                "maximize" in objective
                and score > best_score
                or "minimize" in objective
                and score < best_score
            ):
                best_score = score
                best_params = trial_params

        return ProvenancedDict(
            {
                "best_parameters": best_params,
                "best_score": best_score,
                "all_results": results,
                "iterations": len(results),
                "method": "SimpleOptimizer",
            },
            PROVENANCE,
        )
