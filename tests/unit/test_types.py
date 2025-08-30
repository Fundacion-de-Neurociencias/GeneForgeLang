"""Unit tests for the GFL types module.

Tests cover:
- Dataclass creation and validation
- Type conversion and serialization
- AST construction from dictionaries
- Backward compatibility with dict-based API
"""

import pytest
from typing import Dict, Any

from gfl.types import (
    GFLAST,
    Analysis,
    AnalysisStrategy,
    Experiment,
    ExperimentParams,
    ExperimentType,
    InferenceResult,
    ValidationError,
    ValidationResult,
)


class TestExperimentParams:
    """Test ExperimentParams dataclass."""

    def test_create_empty_params(self):
        """Test creating empty experiment parameters."""
        params = ExperimentParams()
        assert params.target_gene is None
        assert params.concentration is None
        assert params.extra == {}

    def test_create_params_with_values(self):
        """Test creating parameters with specific values."""
        params = ExperimentParams(
            target_gene="TP53",
            concentration=50.0,
            temperature=37.0,
            replicates=3,
        )

        assert params.target_gene == "TP53"
        assert params.concentration == 50.0
        assert params.temperature == 37.0
        assert params.replicates == 3

    def test_params_extra_dict(self):
        """Test extra parameters dictionary."""
        params = ExperimentParams(
            target_gene="TP53", extra={"custom_param": "custom_value", "buffer": "PBS"}
        )

        assert params.extra["custom_param"] == "custom_value"
        assert params.extra["buffer"] == "PBS"

    def test_params_to_dict(self):
        """Test conversion of parameters to dictionary."""
        params = ExperimentParams(
            target_gene="TP53", concentration=50.0, extra={"custom_param": "value"}
        )

        result = params.to_dict()

        assert result["target_gene"] == "TP53"
        assert result["concentration"] == 50.0
        assert result["custom_param"] == "value"
        assert "extra" not in result  # Should be flattened

    def test_params_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        params = ExperimentParams(target_gene="TP53")
        result = params.to_dict()

        assert "target_gene" in result
        assert "concentration" not in result
        assert "temperature" not in result


class TestExperiment:
    """Test Experiment dataclass."""

    def test_create_minimal_experiment(self):
        """Test creating minimal experiment."""
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing")

        assert exp.tool == "CRISPR_cas9"
        assert exp.type == "gene_editing"
        assert isinstance(exp.params, ExperimentParams)
        assert exp.strategy is None

    def test_create_experiment_with_params(self):
        """Test creating experiment with parameters."""
        params = ExperimentParams(target_gene="TP53", concentration=50.0)
        exp = Experiment(
            tool="CRISPR_cas9", type="gene_editing", params=params, strategy="knockout"
        )

        assert exp.params.target_gene == "TP53"
        assert exp.strategy == "knockout"

    def test_experiment_to_dict(self):
        """Test experiment conversion to dictionary."""
        params = ExperimentParams(target_gene="TP53")
        exp = Experiment(
            tool="CRISPR_cas9", type="gene_editing", params=params, strategy="knockout"
        )

        result = exp.to_dict()

        assert result["tool"] == "CRISPR_cas9"
        assert result["type"] == "gene_editing"
        assert result["strategy"] == "knockout"
        assert isinstance(result["params"], dict)
        assert result["params"]["target_gene"] == "TP53"

    def test_experiment_to_dict_no_strategy(self):
        """Test experiment to_dict without strategy."""
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing")
        result = exp.to_dict()

        assert "strategy" not in result


class TestAnalysis:
    """Test Analysis dataclass."""

    def test_create_minimal_analysis(self):
        """Test creating minimal analysis."""
        analysis = Analysis(strategy="differential")

        assert analysis.strategy == "differential"
        assert analysis.data is None
        assert analysis.thresholds == {}
        assert analysis.filters == []
        assert analysis.operations == []

    def test_create_analysis_with_all_fields(self):
        """Test creating analysis with all fields."""
        analysis = Analysis(
            strategy="pathway",
            data="results.csv",
            thresholds={"p_value": 0.05, "fold_change": 2.0},
            filters=["normalize", "remove_low_counts"],
            operations=[{"type": "sort", "field": "p_value"}],
        )

        assert analysis.strategy == "pathway"
        assert analysis.data == "results.csv"
        assert analysis.thresholds["p_value"] == 0.05
        assert "normalize" in analysis.filters
        assert analysis.operations[0]["type"] == "sort"

    def test_analysis_to_dict(self):
        """Test analysis conversion to dictionary."""
        analysis = Analysis(
            strategy="differential", data="results.csv", thresholds={"p_value": 0.05}
        )

        result = analysis.to_dict()

        assert result["strategy"] == "differential"
        assert result["data"] == "results.csv"
        assert result["thresholds"]["p_value"] == 0.05

    def test_analysis_to_dict_excludes_empty(self):
        """Test that to_dict excludes empty collections."""
        analysis = Analysis(strategy="differential")
        result = analysis.to_dict()

        assert "data" not in result
        assert "thresholds" not in result  # Empty dict
        assert "filters" not in result  # Empty list
        assert "operations" not in result  # Empty list


class TestGFLAST:
    """Test GFLAST dataclass."""

    def test_create_empty_ast(self):
        """Test creating empty AST."""
        ast = GFLAST()

        assert ast.experiment is None
        assert ast.analyze is None
        assert ast.simulate is None
        assert ast.branch is None
        assert ast.metadata == {}

    def test_create_ast_with_experiment(self):
        """Test creating AST with experiment."""
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing")
        ast = GFLAST(experiment=exp)

        assert ast.experiment is not None
        assert ast.experiment.tool == "CRISPR_cas9"

    def test_create_ast_with_all_fields(self):
        """Test creating AST with all fields."""
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing")
        analysis = Analysis(strategy="differential")
        ast = GFLAST(
            experiment=exp,
            analyze=analysis,
            simulate=True,
            branch={"if": "condition"},
            metadata={"experiment_id": "EXP001"},
        )

        assert ast.experiment is not None
        assert ast.analyze is not None
        assert ast.simulate is True
        assert ast.branch["if"] == "condition"
        assert ast.metadata["experiment_id"] == "EXP001"

    def test_ast_to_dict(self):
        """Test AST conversion to dictionary."""
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing")
        ast = GFLAST(experiment=exp, simulate=False)

        result = ast.to_dict()

        assert "experiment" in result
        assert result["experiment"]["tool"] == "CRISPR_cas9"
        assert result["simulate"] is False
        assert "analyze" not in result  # None values excluded

    def test_ast_from_dict_minimal(self):
        """Test creating AST from minimal dictionary."""
        data = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": {"target_gene": "TP53"},
            }
        }

        ast = GFLAST.from_dict(data)

        assert ast.experiment is not None
        assert ast.experiment.tool == "CRISPR_cas9"
        assert ast.experiment.params.target_gene == "TP53"

    def test_ast_from_dict_complete(self):
        """Test creating AST from complete dictionary."""
        data = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "strategy": "knockout",
                "params": {
                    "target_gene": "TP53",
                    "concentration": 50.0,
                    "custom_param": "custom_value",
                },
            },
            "analyze": {
                "strategy": "differential",
                "data": "results.csv",
                "thresholds": {"p_value": 0.05},
                "filters": ["normalize"],
                "operations": [{"type": "sort"}],
            },
            "simulate": True,
            "branch": {"if": "condition"},
            "metadata": {"experiment_id": "EXP001"},
        }

        ast = GFLAST.from_dict(data)

        # Test experiment
        assert ast.experiment is not None
        assert ast.experiment.tool == "CRISPR_cas9"
        assert ast.experiment.strategy == "knockout"
        assert ast.experiment.params.target_gene == "TP53"
        assert ast.experiment.params.concentration == 50.0
        assert ast.experiment.params.extra["custom_param"] == "custom_value"

        # Test analysis
        assert ast.analyze is not None
        assert ast.analyze.strategy == "differential"
        assert ast.analyze.data == "results.csv"
        assert ast.analyze.thresholds["p_value"] == 0.05
        assert "normalize" in ast.analyze.filters
        assert ast.analyze.operations[0]["type"] == "sort"

        # Test other fields
        assert ast.simulate is True
        assert ast.branch is not None and ast.branch["if"] == "condition"
        assert ast.metadata["experiment_id"] == "EXP001"

    def test_ast_roundtrip_conversion(self):
        """Test roundtrip conversion: dict -> AST -> dict."""
        original_data = {
            "experiment": {
                "tool": "RNAseq",
                "type": "sequencing",
                "params": {
                    "sample_type": "tissue",
                    "read_length": 150,
                    "paired_end": True,
                },
            },
            "analyze": {"strategy": "pathway", "thresholds": {"fdr": 0.01}},
            "metadata": {"batch": "B001"},
        }

        # Convert to AST and back
        ast = GFLAST.from_dict(original_data)
        result_data = ast.to_dict()

        # Verify key data is preserved
        assert result_data["experiment"]["tool"] == "RNAseq"
        assert result_data["experiment"]["params"]["sample_type"] == "tissue"
        assert result_data["experiment"]["params"]["read_length"] == 150
        assert result_data["experiment"]["params"]["paired_end"] is True
        assert result_data["analyze"]["strategy"] == "pathway"
        assert result_data["analyze"]["thresholds"]["fdr"] == 0.01
        assert result_data["metadata"]["batch"] == "B001"


class TestValidationTypes:
    """Test validation-related types."""

    def test_validation_error_creation(self):
        """Test creating ValidationError."""
        error = ValidationError(
            message="Test error message",
            location="experiment.tool",
            severity="error",
            code="E001",
        )

        assert error.message == "Test error message"
        assert error.location == "experiment.tool"
        assert error.severity == "error"
        assert error.code == "E001"

    def test_validation_error_string_representation(self):
        """Test ValidationError string representation."""
        error = ValidationError(
            message="Missing required field", location="experiment", code="E001"
        )

        error_str = str(error)
        assert "Missing required field" in error_str
        assert "experiment" in error_str
        assert "E001" in error_str

    def test_validation_error_minimal(self):
        """Test ValidationError with minimal fields."""
        error = ValidationError(message="Simple error")
        error_str = str(error)
        assert error_str == "Simple error"

    def test_validation_result_creation(self):
        """Test creating ValidationResult."""
        errors = [ValidationError(message="Error 1")]
        warnings = [ValidationError(message="Warning 1", severity="warning")]
        info = [ValidationError(message="Info 1", severity="info")]

        result = ValidationResult(errors=errors, warnings=warnings, info=info)

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.info) == 1

    def test_validation_result_is_valid(self):
        """Test ValidationResult.is_valid property."""
        # Valid result (no errors)
        result = ValidationResult()
        assert result.is_valid

        # Invalid result (has errors)
        result_with_errors = ValidationResult(errors=[ValidationError(message="Error")])
        assert not result_with_errors.is_valid

        # Still valid with warnings
        result_with_warnings = ValidationResult(
            warnings=[ValidationError(message="Warning", severity="warning")]
        )
        assert result_with_warnings.is_valid

    def test_validation_result_all_messages(self):
        """Test ValidationResult.all_messages property."""
        errors = [ValidationError(message="Error 1")]
        warnings = [ValidationError(message="Warning 1", severity="warning")]
        info = [ValidationError(message="Info 1", severity="info")]

        result = ValidationResult(errors=errors, warnings=warnings, info=info)
        all_messages = result.all_messages

        assert len(all_messages) == 3
        assert any(msg.message == "Error 1" for msg in all_messages)
        assert any(msg.message == "Warning 1" for msg in all_messages)
        assert any(msg.message == "Info 1" for msg in all_messages)

    def test_validation_result_to_string_list(self):
        """Test ValidationResult.to_string_list method."""
        errors = [
            ValidationError(message="Error 1", location="exp"),
            ValidationError(message="Warning 1", severity="warning"),
        ]

        result = ValidationResult(errors=errors)
        string_list = result.to_string_list()

        assert len(string_list) == 2
        assert all(isinstance(s, str) for s in string_list)


class TestInferenceResult:
    """Test InferenceResult dataclass."""

    def test_create_inference_result(self):
        """Test creating InferenceResult."""
        result = InferenceResult(
            predictions={"label": "benign", "score": 0.85},
            confidence=0.92,
            metadata={"model": "test_model", "version": "1.0"},
        )

        assert result.predictions["label"] == "benign"
        assert result.predictions["score"] == 0.85
        assert result.confidence == 0.92
        assert result.metadata["model"] == "test_model"

    def test_inference_result_to_dict(self):
        """Test InferenceResult conversion to dictionary."""
        result = InferenceResult(predictions={"outcome": "positive"}, confidence=0.88)

        result_dict = result.to_dict()

        assert result_dict["predictions"]["outcome"] == "positive"
        assert result_dict["confidence"] == 0.88
        assert result_dict["metadata"] == {}


class TestEnums:
    """Test enum types."""

    def test_experiment_type_enum(self):
        """Test ExperimentType enum values."""
        assert ExperimentType.GENE_EDITING == "gene_editing"
        assert ExperimentType.SEQUENCING == "sequencing"
        assert ExperimentType.ANALYSIS == "analysis"
        assert ExperimentType.SIMULATION == "simulation"
        assert ExperimentType.VALIDATION == "validation"

    def test_analysis_strategy_enum(self):
        """Test AnalysisStrategy enum values."""
        assert AnalysisStrategy.DIFFERENTIAL == "differential"
        assert AnalysisStrategy.PATHWAY == "pathway"
        assert AnalysisStrategy.VARIANT == "variant"
        assert AnalysisStrategy.EXPRESSION == "expression"
        assert AnalysisStrategy.STRUCTURAL == "structural"

    def test_enum_string_behavior(self):
        """Test that enums behave as strings."""
        exp_type = ExperimentType.GENE_EDITING
        analysis_strategy = AnalysisStrategy.DIFFERENTIAL

        # Should work as strings
        assert str(exp_type) == "gene_editing"
        assert str(analysis_strategy) == "differential"

        # Should be comparable to strings
        assert exp_type == "gene_editing"
        assert analysis_strategy == "differential"


@pytest.mark.performance
class TestTypesPerformance:
    """Test performance of type operations."""

    @pytest.mark.slow
    def test_large_ast_creation_performance(self):
        """Test performance of creating large AST from dict."""
        import time

        # Create large parameter set
        large_params = {f"param_{i}": f"value_{i}" for i in range(1000)}

        data = {
            "experiment": {
                "tool": "CRISPR_cas9",
                "type": "gene_editing",
                "params": large_params,
            }
        }

        start_time = time.time()
        ast = GFLAST.from_dict(data)
        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second
        assert ast.experiment is not None
        assert len(ast.experiment.params.extra) == 1000

    @pytest.mark.slow
    def test_large_ast_to_dict_performance(self):
        """Test performance of converting large AST to dict."""
        import time

        # Create AST with large parameter set
        large_extra: Dict[str, Any] = {f"param_{i}": f"value_{i}" for i in range(1000)}
        params = ExperimentParams(target_gene="TP53", extra=large_extra)
        exp = Experiment(tool="CRISPR_cas9", type="gene_editing", params=params)
        ast = GFLAST(experiment=exp)

        start_time = time.time()
        result = ast.to_dict()
        end_time = time.time()

        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second
        assert len(result["experiment"]["params"]) >= 1000
