"""
CRISPR Evaluator Plugin for GFL Genesis Project
"""

import datetime
from typing import Any

from gfl.plugins.plugin_registry import BaseGFLPlugin


class CRISPREvaluatorPlugin(BaseGFLPlugin):
    """
    Plugin to orchestrate CRISPR gRNA evaluation by calling on-target and off-target scorers
    """

    def __init__(self):
        super().__init__()
        # Initialize the scorer plugins if available
        self._try_import_scorer_plugins()

    def _try_import_scorer_plugins(self):
        """Try to import and initialize the scorer plugins."""
        try:
            from gfl.plugins.plugin_registry import get_plugin

            self.ontarget_scorer = get_plugin("ontarget_scorer")
            self.offtarget_scorer = get_plugin("offtarget_scorer")
            self._plugins_available = True
        except Exception:
            # Fallback if plugins are not directly importable
            self._plugins_available = False
            self.ontarget_scorer = None
            self.offtarget_scorer = None

    @property
    def name(self) -> str:
        """Plugin name."""
        return "crispr_evaluator"

    @property
    def version(self) -> str:
        """Plugin version."""
        return "0.1.0"

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Orchestrate the evaluation of gRNA sequences

        Args:
            data: Dictionary containing gRNA sequences

        Returns:
            Dictionary with comprehensive evaluation results
        """
        # Extract gRNA sequences from input data
        grna_sequences = data.get("sequences", [])

        # Initialize empty results
        on_target_results = {"on_target_scores": []}
        off_target_results = {"off_target_scores": []}

        # Call on-target scorer if available
        if self._plugins_available and self.ontarget_scorer:
            on_target_results = self.ontarget_scorer.process({"sequences": grna_sequences})

            # Call off-target scorer if available
            if self.offtarget_scorer:
                off_target_results = self.offtarget_scorer.process({"sequences": grna_sequences})

        # Combine results into a comprehensive evaluation table
        evaluation_table = self._combine_results(
            on_target_results["on_target_scores"], off_target_results["off_target_scores"]
        )

        return {
            "evaluation_table": evaluation_table,
            "on_target_results": on_target_results,
            "off_target_results": off_target_results,
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        }

    def _combine_results(self, on_target_scores: list, off_target_scores: list) -> list:
        """
        Combine on-target and off-target scores into a comprehensive evaluation table

        Args:
            on_target_scores: List of on-target scores
            off_target_scores: List of off-target scores

        Returns:
            List of combined evaluation results
        """
        # Create dictionaries for easier lookup
        on_target_dict = {item["sequence"]: item["efficiency_score"] for item in on_target_scores}
        off_target_dict = {item["sequence"]: item["off_target_risk"] for item in off_target_scores}

        # Combine results
        combined_results = []
        all_sequences = set(on_target_dict.keys()) | set(off_target_dict.keys())
        for sequence in all_sequences:
            combined_results.append(
                {
                    "sequence": sequence,
                    "on_target_score": on_target_dict.get(sequence, 0.0),
                    "off_target_risk": off_target_dict.get(sequence, 0.0),
                    "composite_score": self._calculate_composite_score(
                        on_target_dict.get(sequence, 0.0), off_target_dict.get(sequence, 0.0)
                    ),
                }
            )

        # Sort by composite score (higher is better)
        combined_results.sort(key=lambda x: x["composite_score"], reverse=True)

        return combined_results

    def _calculate_composite_score(self, on_target_score: float, off_target_risk: float) -> float:
        """
        Calculate a composite score that balances on-target efficiency and off-target risk

        Args:
            on_target_score: On-target efficiency score (0-1, higher is better)
            off_target_risk: Off-target risk score (0-1, lower is better)

        Returns:
            Composite score (higher is better)
        """
        # Simple weighted combination - can be made more sophisticated
        return max(0.0, 0.7 * on_target_score - 0.3 * off_target_risk)

    def validate_input(self, data: dict[str, Any]) -> bool:
        """
        Validate input data for the plugin
        """
        return "sequences" in data and isinstance(data["sequences"], list)

    def get_required_inputs(self) -> list[str]:
        """
        Get list of required input parameters
        """
        return ["sequences"]

    def get_output_format(self) -> dict[str, str]:
        """
        Get description of output format
        """
        return {
            "evaluation_table": "List of dictionaries with sequence and combined scores",
            "on_target_results": "Full results from on-target scorer",
            "off_target_results": "Full results from off-target scorer",
            "analysis_date": "Date of analysis",
        }
