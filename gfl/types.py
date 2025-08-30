"""Type definitions for GeneForgeLang AST structures.

This module provides stable, typed representations of GFL AST nodes using
dataclasses and TypedDict. These types ensure API stability and enable
better IDE support, static analysis, and documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

# Type aliases for clarity
GFLValue = Union[str, int, float, bool, None]
GFLDict = Dict[str, Any]


class ExperimentType(str, Enum):
    """Valid experiment types in GFL."""

    GENE_EDITING = "gene_editing"
    SEQUENCING = "sequencing"
    ANALYSIS = "analysis"
    SIMULATION = "simulation"
    VALIDATION = "validation"


class AnalysisStrategy(str, Enum):
    """Valid analysis strategies."""

    DIFFERENTIAL = "differential"
    PATHWAY = "pathway"
    VARIANT = "variant"
    EXPRESSION = "expression"
    STRUCTURAL = "structural"


# Validation result types
@dataclass
class ValidationError:
    """Represents a validation error."""

    message: str
    location: Optional[str] = None
    severity: Literal["error", "warning", "info"] = "error"
    code: Optional[str] = None

    def __str__(self) -> str:
        """String representation of the error."""
        parts = []
        if self.severity != "error":
            parts.append(f"[{self.severity.upper()}]")
        if self.location:
            parts.append(f"{self.location}:")
        parts.append(self.message)
        if self.code:
            parts.append(f"({self.code})")
        return " ".join(parts)


@dataclass
class ValidationResult:
    """Result of AST validation."""

    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if no errors (warnings are allowed)."""
        return len(self.errors) == 0

    @property
    def all_messages(self) -> List[ValidationError]:
        """All validation messages combined."""
        return self.errors + self.warnings + self.info

    def to_string_list(self) -> List[str]:
        """Convert to list of strings for backward compatibility."""
        return [str(msg) for msg in self.all_messages]


# Inference result types
@dataclass
class InferenceResult:
    """Result of probabilistic inference."""

    predictions: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "predictions": self.predictions,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


# Simple dataclass versions for core structures
@dataclass
class ExperimentParams:
    """Parameters for experiment configuration."""

    target_gene: Optional[str] = None
    sequence: Optional[str] = None
    guide_rna: Optional[str] = None
    vector: Optional[str] = None
    concentration: Optional[float] = None
    temperature: Optional[float] = None
    duration: Optional[str] = None
    replicates: Optional[int] = None

    # Allow arbitrary additional parameters
    extra: Dict[str, GFLValue] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}
        for key, value in self.__dict__.items():
            if key != "extra" and value is not None:
                result[key] = value
        result.update(self.extra)
        return result


@dataclass
class Experiment:
    """Experiment block representation."""

    tool: str
    type: str  # Using string instead of enum for simplicity
    params: ExperimentParams = field(default_factory=ExperimentParams)
    strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"tool": self.tool, "type": self.type, "params": self.params.to_dict()}
        if self.strategy is not None:
            result["strategy"] = self.strategy
        return result


@dataclass
class Analysis:
    """Analysis block representation."""

    strategy: str
    data: Optional[str] = None
    thresholds: Dict[str, Any] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)
    operations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"strategy": self.strategy}
        if self.data is not None:
            result["data"] = self.data
        if self.thresholds:
            result["thresholds"] = self.thresholds
        if self.filters:
            result["filters"] = self.filters
        if self.operations:
            result["operations"] = self.operations
        return result


@dataclass
class GFLAST:
    """Root GFL AST representation."""

    experiment: Optional[Experiment] = None
    analyze: Optional[Analysis] = None
    simulate: Optional[bool] = None
    branch: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for backward compatibility."""
        result = {}
        if self.experiment is not None:
            result["experiment"] = self.experiment.to_dict()
        if self.analyze is not None:
            result["analyze"] = self.analyze.to_dict()
        if self.simulate is not None:
            result["simulate"] = self.simulate
        if self.branch is not None:
            result["branch"] = self.branch
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GFLAST:
        """Create GFLAST from dictionary representation."""
        ast = cls()

        if "experiment" in data:
            exp_data = data["experiment"]
            params_data = exp_data.get("params", {})

            # Create experiment params
            params = ExperimentParams(
                target_gene=params_data.get("target_gene"),
                sequence=params_data.get("sequence"),
                guide_rna=params_data.get("guide_rna"),
                vector=params_data.get("vector"),
                concentration=params_data.get("concentration"),
                temperature=params_data.get("temperature"),
                duration=params_data.get("duration"),
                replicates=params_data.get("replicates"),
                extra={
                    k: v
                    for k, v in params_data.items()
                    if k
                    not in {
                        "target_gene",
                        "sequence",
                        "guide_rna",
                        "vector",
                        "concentration",
                        "temperature",
                        "duration",
                        "replicates",
                    }
                },
            )

            ast.experiment = Experiment(
                tool=exp_data["tool"],
                type=exp_data["type"],
                params=params,
                strategy=exp_data.get("strategy"),
            )

        if "analyze" in data:
            analyze_data = data["analyze"]
            ast.analyze = Analysis(
                strategy=analyze_data["strategy"],
                data=analyze_data.get("data"),
                thresholds=analyze_data.get("thresholds", {}),
                filters=analyze_data.get("filters", []),
                operations=analyze_data.get("operations", []),
            )

        if "simulate" in data:
            ast.simulate = data["simulate"]

        if "branch" in data:
            ast.branch = data["branch"]

        if "metadata" in data:
            ast.metadata = data["metadata"]

        return ast


# Export all public types
__all__ = [
    # Enums
    "ExperimentType",
    "AnalysisStrategy",
    # Dataclasses
    "ExperimentParams",
    "Experiment",
    "Analysis",
    "GFLAST",
    # Validation types
    "ValidationError",
    "ValidationResult",
    # Inference types
    "InferenceResult",
    # Type aliases
    "GFLValue",
    "GFLDict",
]
