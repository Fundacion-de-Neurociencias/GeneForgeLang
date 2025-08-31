"""
CRISPR Evaluator Plugin for GFL Genesis Project
"""
from gfl.plugins.interfaces import AnalyzerPlugin
from typing import Dict, Any, List
import pandas as pd

# Import the other plugins
from gfl_plugin_ontarget_scorer.plugin import OnTargetScorerPlugin
from gfl_plugin_offtarget_scorer.plugin import OffTargetScorerPlugin

class CRISPREvaluatorPlugin(AnalyzerPlugin):
    """
    Plugin to orchestrate CRISPR gRNA evaluation by calling on-target and off-target scorers
    """
    
    def __init__(self):
        super().__init__()
        self.name = "crispr_evaluator"
        self.version = "0.1.0"
        self.description = "Orchestrates CRISPR gRNA evaluation using on-target and off-target scorers"
        
        # Initialize the scorer plugins
        self.ontarget_scorer = OnTargetScorerPlugin()
        self.offtarget_scorer = OffTargetScorerPlugin()
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the evaluation of gRNA sequences
        
        Args:
            data: Dictionary containing gRNA sequences
            
        Returns:
            Dictionary with comprehensive evaluation results
        """
        # Extract gRNA sequences from input data
        grna_sequences = data.get("sequences", [])
        
        # Call on-target scorer
        on_target_results = self.ontarget_scorer.analyze({"sequences": grna_sequences})
        
        # Call off-target scorer
        off_target_results = self.offtarget_scorer.analyze({"sequences": grna_sequences})
        
        # Combine results into a comprehensive evaluation table
        evaluation_table = self._combine_results(
            on_target_results["on_target_scores"],
            off_target_results["off_target_scores"]
        )
        
        return {
            "evaluation_table": evaluation_table,
            "on_target_results": on_target_results,
            "off_target_results": off_target_results,
            "analysis_date": "2025-08-31"
        }
        
    def _combine_results(self, on_target_scores: List[Dict], off_target_scores: List[Dict]) -> List[Dict]:
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
        for sequence in on_target_dict.keys():
            combined_results.append({
                "sequence": sequence,
                "on_target_score": on_target_dict.get(sequence, 0.0),
                "off_target_risk": off_target_dict.get(sequence, 0.0),
                "composite_score": self._calculate_composite_score(
                    on_target_dict.get(sequence, 0.0),
                    off_target_dict.get(sequence, 0.0)
                )
            })
            
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
        return 0.7 * on_target_score - 0.3 * off_target_risk
        
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for the plugin
        """
        return "sequences" in data and isinstance(data["sequences"], list)
        
    def get_required_inputs(self) -> List[str]:
        """
        Get list of required input parameters
        """
        return ["sequences"]
        
    def get_output_format(self) -> Dict[str, str]:
        """
        Get description of output format
        """
        return {
            "evaluation_table": "List of dictionaries with sequence and combined scores",
            "on_target_results": "Full results from on-target scorer",
            "off_target_results": "Full results from off-target scorer",
            "analysis_date": "Date of analysis"
        }