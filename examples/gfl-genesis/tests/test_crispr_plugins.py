"""
Test script to validate CRISPR plugins functionality
"""

import sys
from pathlib import Path

# Add plugin directories to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "plugins" / "gfl-plugin-ontarget-scorer"))
sys.path.insert(0, str(project_root / "plugins" / "gfl-plugin-offtarget-scorer"))
sys.path.insert(0, str(project_root / "plugins" / "gfl-crispr-evaluator"))


def test_individual_plugins():
    """Test that individual plugins work correctly"""
    print("Testing individual plugins...")

    # Test on-target scorer
    from gfl_plugin_ontarget_scorer.plugin import OnTargetScorerPlugin

    ontarget_plugin = OnTargetScorerPlugin()

    test_data = {"sequences": ["GATTACA", "CGATTAC"]}
    result = ontarget_plugin.process(test_data)

    assert "on_target_scores" in result
    assert len(result["on_target_scores"]) == 2
    print("✓ On-target scorer plugin works correctly")

    # Test off-target scorer
    from gfl_plugin_offtarget_scorer.plugin import OffTargetScorerPlugin

    offtarget_plugin = OffTargetScorerPlugin()

    result = offtarget_plugin.process(test_data)

    assert "off_target_scores" in result
    assert len(result["off_target_scores"]) == 2
    print("✓ Off-target scorer plugin works correctly")


def test_evaluator_plugin():
    """Test that evaluator plugin orchestrates correctly"""
    print("Testing evaluator plugin...")

    from gfl_crispr_evaluator.plugin import CRISPREvaluatorPlugin

    evaluator_plugin = CRISPREvaluatorPlugin()

    test_data = {"sequences": ["GATTACA", "CGATTAC"]}
    result = evaluator_plugin.process(test_data)

    # Even without the other plugins available, it should return empty results
    assert "evaluation_table" in result
    assert "on_target_results" in result
    assert "off_target_results" in result
    print("✓ Evaluator plugin orchestrates correctly")


if __name__ == "__main__":
    test_individual_plugins()
    test_evaluator_plugin()
    print("\nAll CRISPR plugin tests passed!")
