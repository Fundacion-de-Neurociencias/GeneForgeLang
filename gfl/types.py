"""Type definitions for GeneForgeLang AST structures.

This module provides stable, typed representations of GFL AST nodes using
dataclasses and TypedDict. These types ensure API stability and enable
better IDE support, static analysis, and documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Type aliases for clarity
GFLValue = Union[str, int, float, bool, None]
GFLDict = Dict[str, Any]


class DataType(str, Enum):
    """Valid data types for IO contracts."""
    
    # Sequence data types
    FASTA = "FASTA"
    FASTQ = "FASTQ"
    BAM = "BAM"
    SAM = "SAM"
    VCF = "VCF"
    
    # General data types
    CSV = "CSV"
    JSON = "JSON"
    TEXT = "TEXT"
    BINARY = "BINARY"
    
    # Custom types
    CUSTOM = "CUSTOM"


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


@dataclass
class IOContract:
    """IO Contract definition for data validation."""
    
    # Data type specification
    type: str  # DataType enum value or custom type
    
    # Optional attributes for type specification
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "attributes": self.attributes
        }


@dataclass
class BlockContract:
    """Contract definition for a GFL block's inputs and outputs."""
    
    # Input contracts (data consumed by this block)
    inputs: Dict[str, IOContract] = field(default_factory=dict)
    
    # Output contracts (data produced by this block)
    outputs: Dict[str, IOContract] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "inputs": {name: contract.to_dict() for name, contract in self.inputs.items()},
            "outputs": {name: contract.to_dict() for name, contract in self.outputs.items()}
        }


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
        result: Dict[str, Any] = {"strategy": self.strategy}
        if self.data is not None:
            result["data"] = self.data
        if self.thresholds:
            result["thresholds"] = dict(self.thresholds)
        if self.filters:
            result["filters"] = list(self.filters)
        if self.operations:
            result["operations"] = [dict(op) for op in self.operations]
        return result


@dataclass
class Design:
    """Design block representation for generative hypothesis tasks."""

    entity: str  # Type of biological entity to design
    model: str  # Generative model plugin to use
    objective: Dict[str, Any]  # Optimization objective (maximize/minimize)
    count: int  # Number of candidates to generate
    output: str  # Output variable name for generated candidates
    constraints: Optional[List[str]] = None  # Optional design constraints

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "entity": self.entity,
            "model": self.model,
            "objective": self.objective,
            "count": self.count,
            "output": self.output,
        }
        if self.constraints is not None:
            result["constraints"] = self.constraints
        return result


@dataclass
class Optimize:
    """Optimize block representation for intelligent experimental loops."""

    search_space: Dict[str, str]  # Parameters to explore and their ranges
    strategy: Dict[str, Any]  # Optimization strategy configuration
    objective: Dict[str, Any]  # Optimization objective (maximize/minimize)
    budget: Dict[str, Any]  # Stopping criteria (e.g., max_experiments)
    run: Dict[str, Any]  # Nested experiment or analyze block to execute

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "search_space": self.search_space,
            "strategy": self.strategy,
            "objective": self.objective,
            "budget": self.budget,
            "run": self.run,
        }


@dataclass
class GFLAST:
    """Root GFL AST representation."""

    experiment: Optional[Experiment] = None
    analyze: Optional[Analysis] = None
    design: Optional[Design] = None
    optimize: Optional[Optimize] = None
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
        if self.design is not None:
            result["design"] = self.design.to_dict()
        if self.optimize is not None:
            result["optimize"] = self.optimize.to_dict()
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
                tool=str(exp_data["tool"]),
                type=str(exp_data["type"]),
                params=params,
                strategy=exp_data.get("strategy"),
            )

        if "analyze" in data:
            analyze_data = data["analyze"]
            ast.analyze = Analysis(
                strategy=str(analyze_data["strategy"]),
                data=analyze_data.get("data"),
                thresholds=analyze_data.get("thresholds", {}),
                filters=list(analyze_data.get("filters", [])),
                operations=list(analyze_data.get("operations", [])),
            )

        if "design" in data:
            design_data = data["design"]
            ast.design = Design(
                entity=str(design_data["entity"]),
                model=str(design_data["model"]),
                objective=dict(design_data["objective"]),
                count=int(design_data["count"]),
                output=str(design_data["output"]),
                constraints=list(design_data["constraints"]) if "constraints" in design_data else None,
            )

        if "optimize" in data:
            optimize_data = data["optimize"]
            ast.optimize = Optimize(
                search_space=dict(optimize_data["search_space"]),
                strategy=dict(optimize_data["strategy"]),
                objective=dict(optimize_data["objective"]),
                budget=dict(optimize_data["budget"]),
                run=dict(optimize_data["run"]),
            )

        if "simulate" in data:
            ast.simulate = bool(data["simulate"])

        if "branch" in data:
            ast.branch = dict(data["branch"])

        if "metadata" in data:
            ast.metadata = dict(data["metadata"])

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
    "Design",
    "Optimize",
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
