"""Type definitions for GeneForgeLang AST structures.

This module provides stable, typed representations of GFL AST nodes using
dataclasses and TypedDict. These types ensure API stability and enable
better IDE support, static analysis, and documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Union

if TYPE_CHECKING:
    pass

# Type aliases for clarity
GFLValue = Union[str, int, float, bool, None]
GFLDict = dict[str, Any]


class DataType(str, Enum):
    """Valid data types for IO contracts."""

    # Sequence data types
    FASTA = "FASTA"
    FASTQ = "FASTQ"
    BAM = "BAM"
    SAM = "SAM"
    VCF = "VCF"

    # Tensor and Geometric AI data types (BioTorch / Structural Biology AI)
    TENSOR = "TENSOR"
    DISTANCE_MATRIX = "DISTANCE_MATRIX"
    BACKBONE_FRAMES = "BACKBONE_FRAMES"
    CONTACT_MAP = "CONTACT_MAP"
    SEQUENCE_EMBEDDING = "SEQUENCE_EMBEDDING"
    ATTENTION_MAP = "ATTENTION_MAP"
    BOLTZMANN_ENSEMBLE = "BOLTZMANN_ENSEMBLE"
    CONFORMATIONAL_LANDSCAPE = "CONFORMATIONAL_LANDSCAPE"

    # General data types
    CSV = "CSV"
    JSON = "JSON"
    TEXT = "TEXT"
    BINARY = "BINARY"

    # Custom types
    CUSTOM = "CUSTOM"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


class ExperimentType(str, Enum):
    """Valid experiment types in GFL."""

    GENE_EDITING = "gene_editing"
    SEQUENCING = "sequencing"
    ANALYSIS = "analysis"
    SIMULATION = "simulation"
    VALIDATION = "validation"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


class AnalysisStrategy(str, Enum):
    """Valid analysis strategies."""

    DIFFERENTIAL = "differential"
    PATHWAY = "pathway"
    VARIANT = "variant"
    EXPRESSION = "expression"
    STRUCTURAL = "structural"
    CONTRASTIVE_ALIGNMENT = "contrastive_alignment"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


@dataclass
class IOContract:
    """IO Contract definition for data validation."""

    # Data type specification
    type: str  # DataType enum value or custom type

    # Optional attributes for type specification
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {"type": self.type, "attributes": self.attributes}


@dataclass
class TensorContract(IOContract):
    """Specialized IO contract for biological tensor operations and geometric representations.

    Standardizes tensor shapes, invariant dimensions, and coordinate frames
    inspired by BioTorch and structural biology foundation models (AlphaFold, ESMFold).
    """

    shape: list[str | int] = field(default_factory=list)
    dtype: str = "float32"
    coordinate_frame: str | None = None  # e.g., 'SE3', 'SO3', 'local_residue_frame'
    invariant_dimensions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Inject tensor attributes into base attributes dictionary."""
        if not self.type:
            self.type = DataType.TENSOR.value
        self.attributes.setdefault("shape", self.shape)
        self.attributes.setdefault("dtype", self.dtype)
        if self.coordinate_frame:
            self.attributes.setdefault("coordinate_frame", self.coordinate_frame)
        if self.invariant_dimensions:
            self.attributes.setdefault("invariant_dimensions", self.invariant_dimensions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res = super().to_dict()
        res.update(
            {
                "shape": self.shape,
                "dtype": self.dtype,
                "coordinate_frame": self.coordinate_frame,
                "invariant_dimensions": self.invariant_dimensions,
            }
        )
        return res


@dataclass
class BlockContract:
    """Contract definition for a GFL block's inputs and outputs."""

    # Input contracts (data consumed by this block)
    inputs: dict[str, IOContract] = field(default_factory=dict)

    # Output contracts (data produced by this block)
    outputs: dict[str, IOContract] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "inputs": {name: contract.to_dict() for name, contract in self.inputs.items()},
            "outputs": {name: contract.to_dict() for name, contract in self.outputs.items()},
        }


# Validation result types
@dataclass
class ValidationError:
    """Represents a validation error."""

    message: str
    location: str | None = None
    severity: Literal["error", "warning", "info"] = "error"
    code: str | None = None

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

    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    info: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if no errors (warnings are allowed)."""
        return len(self.errors) == 0

    @property
    def all_messages(self) -> list[ValidationError]:
        """All validation messages combined."""
        return self.errors + self.warnings + self.info

    def to_string_list(self) -> list[str]:
        """Convert to list of strings for backward compatibility."""
        return [str(msg) for msg in self.all_messages]


# Inference result types
@dataclass
class InferenceResult:
    """Result of probabilistic inference."""

    predictions: dict[str, Any]
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

    target_gene: str | None = None
    sequence: str | None = None
    guide_rna: str | None = None
    vector: str | None = None
    concentration: float | None = None
    temperature: float | None = None
    duration: str | None = None
    replicates: int | None = None

    # Allow arbitrary additional parameters
    extra: dict[str, GFLValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
    strategy: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"tool": self.tool, "type": self.type, "params": self.params.to_dict()}
        if self.strategy is not None:
            result["strategy"] = self.strategy
        return result


@dataclass
class Analysis:
    """Analysis block representation."""

    strategy: str
    data: str | None = None
    thresholds: dict[str, Any] = field(default_factory=dict)
    filters: list[str] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"strategy": self.strategy}
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
    objective: dict[str, Any]  # Optimization objective (maximize/minimize)
    count: int  # Number of candidates to generate
    output: str  # Output variable name for generated candidates
    constraints: list[str] | None = None  # Optional design constraints

    def to_dict(self) -> dict[str, Any]:
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

    search_space: dict[str, str]  # Parameters to explore and their ranges
    strategy: dict[str, Any]  # Optimization strategy configuration
    objective: dict[str, Any]  # Optimization objective (maximize/minimize)
    budget: dict[str, Any]  # Stopping criteria (e.g., max_experiments)
    run: dict[str, Any]  # Nested experiment or analyze block to execute

    def to_dict(self) -> dict[str, Any]:
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

    experiment: Experiment | None = None
    analyze: Analysis | None = None
    design: Design | None = None
    optimize: Optimize | None = None
    simulate: bool | None = None
    branch: dict[str, Any] | None = None
    decision: DecisionContract | dict[str, Any] | None = None
    tape_recorder: TapeRecorderContract | dict[str, Any] | None = None
    regulatory_profile: Any | None = None
    protocol: Any | None = None
    somatic_instability: Any | None = None
    ensemble: Any | None = None
    cryptic_pocket: Any | None = None
    thermodynamic_binding: Any | None = None
    bacteriophage: Any | None = None
    virtual_cell: Any | None = None
    force_field_engine: Any | None = None
    dna_viewer: Any | None = None
    perturbation_atlas: Any | None = None
    biosecurity_watermark: Any | None = None
    genomic_llm: Any | None = None
    protok: Any | None = None
    dna_dynamics: Any | None = None
    single_cell_regulation: Any | None = None
    verifiable_dna: Any | None = None
    autonomous_execution: Any | None = None
    bioc_reference: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation for backward compatibility."""
        result: dict[str, Any] = {}
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
        if self.decision is not None:
            result["decision"] = self.decision.to_dict() if hasattr(self.decision, "to_dict") else self.decision
        if self.tape_recorder is not None:
            result["tape_recorder"] = (
                self.tape_recorder.to_dict() if hasattr(self.tape_recorder, "to_dict") else self.tape_recorder
            )
        if self.regulatory_profile is not None:
            result["regulatory_profile"] = (
                self.regulatory_profile.to_dict()
                if hasattr(self.regulatory_profile, "to_dict")
                else self.regulatory_profile
            )
        if self.protocol is not None:
            result["protocol"] = self.protocol.to_dict() if hasattr(self.protocol, "to_dict") else self.protocol
        if self.somatic_instability is not None:
            result["somatic_instability"] = (
                self.somatic_instability.to_dict()
                if hasattr(self.somatic_instability, "to_dict")
                else self.somatic_instability
            )
        if self.ensemble is not None:
            result["ensemble"] = self.ensemble.to_dict() if hasattr(self.ensemble, "to_dict") else self.ensemble
        if self.cryptic_pocket is not None:
            result["cryptic_pocket"] = (
                self.cryptic_pocket.to_dict() if hasattr(self.cryptic_pocket, "to_dict") else self.cryptic_pocket
            )
        if self.thermodynamic_binding is not None:
            result["thermodynamic_binding"] = (
                self.thermodynamic_binding.to_dict()
                if hasattr(self.thermodynamic_binding, "to_dict")
                else self.thermodynamic_binding
            )
        if self.bacteriophage is not None:
            result["bacteriophage"] = (
                self.bacteriophage.to_dict() if hasattr(self.bacteriophage, "to_dict") else self.bacteriophage
            )
        if self.virtual_cell is not None:
            result["virtual_cell"] = (
                self.virtual_cell.to_dict() if hasattr(self.virtual_cell, "to_dict") else self.virtual_cell
            )
        if self.force_field_engine is not None:
            result["force_field_engine"] = (
                self.force_field_engine.to_dict()
                if hasattr(self.force_field_engine, "to_dict")
                else self.force_field_engine
            )
        if self.dna_viewer is not None:
            result["dna_viewer"] = self.dna_viewer.to_dict() if hasattr(self.dna_viewer, "to_dict") else self.dna_viewer
        if self.perturbation_atlas is not None:
            result["perturbation_atlas"] = (
                self.perturbation_atlas.to_dict()
                if hasattr(self.perturbation_atlas, "to_dict")
                else self.perturbation_atlas
            )
        if self.biosecurity_watermark is not None:
            result["biosecurity_watermark"] = (
                self.biosecurity_watermark.to_dict()
                if hasattr(self.biosecurity_watermark, "to_dict")
                else self.biosecurity_watermark
            )
        if self.genomic_llm is not None:
            result["genomic_llm"] = (
                self.genomic_llm.to_dict() if hasattr(self.genomic_llm, "to_dict") else self.genomic_llm
            )
        if self.protok is not None:
            result["protok"] = self.protok.to_dict() if hasattr(self.protok, "to_dict") else self.protok
        if self.dna_dynamics is not None:
            result["dna_dynamics"] = (
                self.dna_dynamics.to_dict() if hasattr(self.dna_dynamics, "to_dict") else self.dna_dynamics
            )
        if self.single_cell_regulation is not None:
            result["single_cell_regulation"] = (
                self.single_cell_regulation.to_dict()
                if hasattr(self.single_cell_regulation, "to_dict")
                else self.single_cell_regulation
            )
        if self.verifiable_dna is not None:
            result["verifiable_dna"] = (
                self.verifiable_dna.to_dict() if hasattr(self.verifiable_dna, "to_dict") else self.verifiable_dna
            )
        if self.autonomous_execution is not None:
            result["autonomous_execution"] = (
                self.autonomous_execution.to_dict()
                if hasattr(self.autonomous_execution, "to_dict")
                else self.autonomous_execution
            )
        if self.bioc_reference is not None:
            result["bioc_reference"] = (
                self.bioc_reference.to_dict() if hasattr(self.bioc_reference, "to_dict") else self.bioc_reference
            )
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GFLAST:
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
                constraints=(list(design_data["constraints"]) if "constraints" in design_data else None),
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

        if "decision" in data:
            dec_data = data["decision"]
            if isinstance(dec_data, DecisionContract):
                ast.decision = dec_data
            elif isinstance(dec_data, dict):
                strategy_val = dec_data.get("strategy", DecisionStrategy.SYSTEM_1_CALIBRATED)
                if isinstance(strategy_val, str):
                    try:
                        strategy_enum = DecisionStrategy(strategy_val.lower())
                    except ValueError:
                        strategy_enum = DecisionStrategy.SYSTEM_1_CALIBRATED
                else:
                    strategy_enum = strategy_val

                mode_val = dec_data.get("mode", DecisionMode.CHOICE)
                if isinstance(mode_val, str):
                    try:
                        mode_enum = DecisionMode(mode_val.lower())
                    except ValueError:
                        mode_enum = DecisionMode.CHOICE
                else:
                    mode_enum = mode_val
                raw_space = dec_data.get("allowed_space")
                if raw_space is None:
                    raw_space = dec_data.get("allowed_options", [])
                allowed = [str(opt) for opt in raw_space]

                raw_thresh = dec_data.get("threshold")
                if raw_thresh is None:
                    raw_thresh = dec_data.get("confidence_threshold", 0.85)
                thresh = float(raw_thresh)

                ast.decision = DecisionContract(
                    task_id=str(dec_data.get("task_id", dec_data.get("name", "decision_task"))),
                    allowed_options=allowed,
                    allowed_space=allowed,
                    confidence_threshold=thresh,
                    threshold=thresh,
                    fallback_strategy=str(dec_data.get("fallback_strategy", "ESCALATE_TO_SYSTEM2")),
                    strategy=strategy_enum,
                    engine=str(dec_data.get("engine", "biodecision-4b")),
                    latency_budget_ms=float(dec_data.get("latency_budget_ms", 50.0)),
                    calibration_error_max=float(dec_data.get("calibration_error_max", 0.08)),
                    mode=mode_enum,
                )

        if "tape_recorder" in data:
            tr_data = data["tape_recorder"]
            if isinstance(tr_data, TapeRecorderContract):
                ast.tape_recorder = tr_data
            elif isinstance(tr_data, dict):
                arch_raw = tr_data.get("cassette_architecture", CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL)
                if isinstance(arch_raw, str):
                    try:
                        arch_enum = CassetteArchitecture(arch_raw)
                    except ValueError:
                        arch_enum = CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL
                else:
                    arch_enum = arch_raw

                sigs_raw = tr_data.get("edit_signature_alphabet", [])
                sigs = [str(s) for s in sigs_raw]

                ast.tape_recorder = TapeRecorderContract(
                    recorder_id=str(tr_data.get("recorder_id", tr_data.get("name", "TapeRecorder"))),
                    cassette_architecture=arch_enum,
                    tape_capacity_sites=int(tr_data.get("tape_capacity_sites", 50)),
                    recording_interval_hours=float(tr_data.get("recording_interval_hours", 6.0)),
                    edit_signature_alphabet=sigs,
                    target_organism=str(tr_data["target_organism"]) if "target_organism" in tr_data else None,
                    developmental_window=str(tr_data["developmental_window"])
                    if "developmental_window" in tr_data
                    else None,
                    readout_modality=str(tr_data["readout_modality"]) if "readout_modality" in tr_data else None,
                )

        if "regulatory_profile" in data:
            rp_data = data["regulatory_profile"]
            if isinstance(rp_data, RegulatoryProfileContract):
                ast.regulatory_profile = rp_data
            elif isinstance(rp_data, dict):
                ast.regulatory_profile = RegulatoryProfileContract.from_dict(rp_data)

        if "protocol" in data:
            proto_data = data["protocol"]
            if isinstance(proto_data, SomaticInstabilityContract):
                ast.protocol = proto_data
            elif isinstance(proto_data, dict):
                ast.protocol = SomaticInstabilityContract.from_dict(proto_data)

        if "somatic_instability" in data:
            si_data = data["somatic_instability"]
            if isinstance(si_data, SomaticInstabilityContract):
                ast.somatic_instability = si_data
            elif isinstance(si_data, dict):
                ast.somatic_instability = SomaticInstabilityContract.from_dict(si_data)

        if "ensemble" in data:
            ens_data = data["ensemble"]
            if isinstance(ens_data, BoltzmannEnsembleContract):
                ast.ensemble = ens_data
            elif isinstance(ens_data, dict):
                ast.ensemble = BoltzmannEnsembleContract.from_dict(ens_data)

        if "cryptic_pocket" in data:
            cp_data = data["cryptic_pocket"]
            if isinstance(cp_data, CrypticPocketContract):
                ast.cryptic_pocket = cp_data
            elif isinstance(cp_data, dict):
                ast.cryptic_pocket = CrypticPocketContract.from_dict(cp_data)

        if "thermodynamic_binding" in data:
            tb_data = data["thermodynamic_binding"]
            if isinstance(tb_data, ThermodynamicBindingContract):
                ast.thermodynamic_binding = tb_data
            elif isinstance(tb_data, dict):
                ast.thermodynamic_binding = ThermodynamicBindingContract.from_dict(tb_data)

        if "bacteriophage" in data:
            phage_data = data["bacteriophage"]
            if isinstance(phage_data, BacteriophageTherapyContract):
                ast.bacteriophage = phage_data
            elif isinstance(phage_data, dict):
                ast.bacteriophage = BacteriophageTherapyContract.from_dict(phage_data)

        if "virtual_cell" in data:
            vc_data = data["virtual_cell"]
            if isinstance(vc_data, VirtualCellPerturbationContract):
                ast.virtual_cell = vc_data
            elif isinstance(vc_data, dict):
                ast.virtual_cell = VirtualCellPerturbationContract.from_dict(vc_data)

        if "force_field_engine" in data:
            ffe_data = data["force_field_engine"]
            if isinstance(ffe_data, ForceFieldEngineContract):
                ast.force_field_engine = ffe_data
            elif isinstance(ffe_data, dict):
                ast.force_field_engine = ForceFieldEngineContract.from_dict(ffe_data)

        if "dna_viewer" in data:
            dv_data = data["dna_viewer"]
            if isinstance(dv_data, DNAViewerContract):
                ast.dna_viewer = dv_data
            elif isinstance(dv_data, dict):
                ast.dna_viewer = DNAViewerContract.from_dict(dv_data)

        if "perturbation_atlas" in data:
            pa_data = data["perturbation_atlas"]
            if isinstance(pa_data, PerturbationAtlasContract):
                ast.perturbation_atlas = pa_data
            elif isinstance(pa_data, dict):
                ast.perturbation_atlas = PerturbationAtlasContract.from_dict(pa_data)

        if "biosecurity_watermark" in data:
            bw_data = data["biosecurity_watermark"]
            if isinstance(bw_data, BiosecurityWatermarkContract):
                ast.biosecurity_watermark = bw_data
            elif isinstance(bw_data, dict):
                ast.biosecurity_watermark = BiosecurityWatermarkContract.from_dict(bw_data)
        elif "synth_provenance" in data:
            bw_data = data["synth_provenance"]
            if isinstance(bw_data, BiosecurityWatermarkContract):
                ast.biosecurity_watermark = bw_data
            elif isinstance(bw_data, dict):
                ast.biosecurity_watermark = BiosecurityWatermarkContract.from_dict(bw_data)

        if "genomic_llm" in data:
            gl_data = data["genomic_llm"]
            if isinstance(gl_data, GenomicLLMContract):
                ast.genomic_llm = gl_data
            elif isinstance(gl_data, dict):
                ast.genomic_llm = GenomicLLMContract.from_dict(gl_data)
        elif "carbonx" in data:
            gl_data = data["carbonx"]
            if isinstance(gl_data, GenomicLLMContract):
                ast.genomic_llm = gl_data
            elif isinstance(gl_data, dict):
                ast.genomic_llm = GenomicLLMContract.from_dict(gl_data)

        if "protok" in data:
            pk_data = data["protok"]
            if isinstance(pk_data, ProTokContract):
                ast.protok = pk_data
            elif isinstance(pk_data, dict):
                ast.protok = ProTokContract.from_dict(pk_data)
        elif "unified_protein_stream" in data:
            pk_data = data["unified_protein_stream"]
            if isinstance(pk_data, ProTokContract):
                ast.protok = pk_data
            elif isinstance(pk_data, dict):
                ast.protok = ProTokContract.from_dict(pk_data)

        if "dna_dynamics" in data:
            dd_data = data["dna_dynamics"]
            if isinstance(dd_data, DNADynamicsContract):
                ast.dna_dynamics = dd_data
            elif isinstance(dd_data, dict):
                ast.dna_dynamics = DNADynamicsContract.from_dict(dd_data)
        elif "breathing" in data:
            dd_data = data["breathing"]
            if isinstance(dd_data, DNADynamicsContract):
                ast.dna_dynamics = dd_data
            elif isinstance(dd_data, dict):
                ast.dna_dynamics = DNADynamicsContract.from_dict(dd_data)

        if "single_cell_regulation" in data:
            sc_data = data["single_cell_regulation"]
            if isinstance(sc_data, SingleCellRegulatoryContract):
                ast.single_cell_regulation = sc_data
            elif isinstance(sc_data, dict):
                ast.single_cell_regulation = SingleCellRegulatoryContract.from_dict(sc_data)
        elif "sc_regulation" in data:
            sc_data = data["sc_regulation"]
            if isinstance(sc_data, SingleCellRegulatoryContract):
                ast.single_cell_regulation = sc_data
            elif isinstance(sc_data, dict):
                ast.single_cell_regulation = SingleCellRegulatoryContract.from_dict(sc_data)
        elif "cellular_context" in data:
            sc_data = data["cellular_context"]
            if isinstance(sc_data, SingleCellRegulatoryContract):
                ast.single_cell_regulation = sc_data
            elif isinstance(sc_data, dict):
                ast.single_cell_regulation = SingleCellRegulatoryContract.from_dict(sc_data)

        if "verifiable_dna" in data:
            vd_data = data["verifiable_dna"]
            if isinstance(vd_data, VerifiableRewardContract):
                ast.verifiable_dna = vd_data
            elif isinstance(vd_data, dict):
                ast.verifiable_dna = VerifiableRewardContract.from_dict(vd_data)
        elif "rlvr_verifier" in data:
            vd_data = data["rlvr_verifier"]
            if isinstance(vd_data, VerifiableRewardContract):
                ast.verifiable_dna = vd_data
            elif isinstance(vd_data, dict):
                ast.verifiable_dna = VerifiableRewardContract.from_dict(vd_data)

        if "autonomous_execution" in data:
            ae_data = data["autonomous_execution"]
            if isinstance(ae_data, AutonomousExecutionContract):
                ast.autonomous_execution = ae_data
            elif isinstance(ae_data, dict):
                ast.autonomous_execution = AutonomousExecutionContract.from_dict(ae_data)
        elif "wet_lab_dispatch" in data:
            ae_data = data["wet_lab_dispatch"]
            if isinstance(ae_data, AutonomousExecutionContract):
                ast.autonomous_execution = ae_data
            elif isinstance(ae_data, dict):
                ast.autonomous_execution = AutonomousExecutionContract.from_dict(ae_data)
        elif "laboratory_protocol" in data:
            ae_data = data["laboratory_protocol"]
            if isinstance(ae_data, AutonomousExecutionContract):
                ast.autonomous_execution = ae_data
            elif isinstance(ae_data, dict):
                ast.autonomous_execution = AutonomousExecutionContract.from_dict(ae_data)

        if "bioc_reference" in data:
            br_data = data["bioc_reference"]
            if isinstance(br_data, BiocIceContract):
                ast.bioc_reference = br_data
            elif isinstance(br_data, dict):
                ast.bioc_reference = BiocIceContract.from_dict(br_data)
        elif "lakehouse_reference" in data:
            br_data = data["lakehouse_reference"]
            if isinstance(br_data, BiocIceContract):
                ast.bioc_reference = br_data
            elif isinstance(br_data, dict):
                ast.bioc_reference = BiocIceContract.from_dict(br_data)
        elif "bioc_on_ice" in data:
            br_data = data["bioc_on_ice"]
            if isinstance(br_data, BiocIceContract):
                ast.bioc_reference = br_data
            elif isinstance(br_data, dict):
                ast.bioc_reference = BiocIceContract.from_dict(br_data)

        if "metadata" in data:
            ast.metadata = dict(data["metadata"])

        return ast


# Somatic Repeat Instability & Catastrophe Cliff Contracts (Neurodiagnoses Ecosystem)
class SomaticDriftModel(str, Enum):
    """Stochastic models of repeat tract somatic length drift over time."""

    STOCHASTIC_EXPANSION = "stochastic_expansion"  # Forward-biased expansion drift (MSH3/MLH1-driven)
    LOGNORMAL_POPULATION = "lognormal_population"  # Lognormal distribution across cellular sub-populations
    POISSON_JUMP_DIFFUSION = "poisson_jump_diffusion"  # Jump-diffusion slip process during transcription/repair


@dataclass
class SomaticDriftSimulationContract:
    """Stochastic simulation parameters for somatic repeat expansion and catastrophe cliff."""

    time_horizon_years: float = 65.0  # Age or observation window in years
    toxicity_cliff_threshold: int = 150  # Repeat length where cell death / collapse occurs
    stochastic_drift_rate_per_year: float = 2.3  # Mean repeat units gained per year
    stochastic_dispersion: float = 0.25  # Dispersion / variance parameter
    drift_model: SomaticDriftModel = SomaticDriftModel.STOCHASTIC_EXPANSION

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "time_horizon_years": self.time_horizon_years,
            "toxicity_cliff_threshold": self.toxicity_cliff_threshold,
            "toxicity_cliff_cag": self.toxicity_cliff_threshold,
            "stochastic_drift_rate_per_year": self.stochastic_drift_rate_per_year,
            "stochastic_dispersion": self.stochastic_dispersion,
            "drift_model": str(self.drift_model.value if hasattr(self.drift_model, "value") else self.drift_model),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SomaticDriftSimulationContract:
        """Instantiate SomaticDriftSimulationContract from dictionary."""
        model_val = data.get("drift_model", SomaticDriftModel.STOCHASTIC_EXPANSION)
        try:
            model_enum = SomaticDriftModel(str(model_val).lower())
        except ValueError:
            model_enum = SomaticDriftModel.STOCHASTIC_EXPANSION

        cliff_val = data.get("toxicity_cliff_threshold")
        if cliff_val is None:
            cliff_val = data.get("toxicity_cliff_cag", 150)

        return cls(
            time_horizon_years=float(data.get("time_horizon_years", 65.0)),
            toxicity_cliff_threshold=int(cliff_val),
            stochastic_drift_rate_per_year=float(data.get("stochastic_drift_rate_per_year", 2.3)),
            stochastic_dispersion=float(data.get("stochastic_dispersion", 0.25)),
            drift_model=model_enum,
        )


@dataclass
class SomaticInstabilityContract:
    """Formal GFL IO Contract for Microsatellite Somatic Instability and Toxicity Cliff Gating.

    Formalized in collaboration with Neurodiagnoses:
    - Models the tissue-specific, stochastic somatic expansion distribution of tandem repeats.
    - Decouples static germline repeat lengths from dynamic cellular distributions in vulnerable neurons.
    - Computes catastrophe cliff probability for System 1 fast gating (e.g. SUB_THRESHOLD_LATENT vs CLIFF_COLLAPSE_IMMINENT).
    """

    target_gene: str = "HTT"
    locus: str = "chr4:3074877-3074933"
    repeat_unit: str = "CAG"
    germline_repeat_count: int = 42
    cell_type: str = "striatal_projection_neuron"
    modifiers: dict[str, Any] = field(default_factory=dict)
    simulation: SomaticDriftSimulationContract = field(default_factory=SomaticDriftSimulationContract)
    protocol_name: str | None = None

    def calculate_projected_distribution(self) -> dict[str, float]:
        """Calculate analytical projection of repeat tract length distribution at time_horizon_years.

        E[length(t)] = germline_repeat_count + drift_rate * t * modifier_factor.
        Returns:
            Dictionary containing mean_projected_repeat, std_dev, and cliff_exceedance_probability.
        """
        import math

        # Modifiers impact drift rate
        mod_factor = 1.0
        if "mlh1_expression" in self.modifiers:
            try:
                mod_factor *= float(self.modifiers["mlh1_expression"])
            except (ValueError, TypeError):
                pass
        if "msh3_genotype" in self.modifiers:
            geno = str(self.modifiers["msh3_genotype"]).lower()
            if "risk" in geno or "rs1805355" in geno:
                mod_factor *= 1.25

        years = self.simulation.time_horizon_years
        effective_drift = self.simulation.stochastic_drift_rate_per_year * mod_factor
        mean_projected = self.germline_repeat_count + (effective_drift * years)

        # Standard deviation proportional to sqrt(years) and dispersion
        std_dev = max(1.0, math.sqrt(max(1.0, years)) * self.simulation.stochastic_dispersion * effective_drift)

        cliff = float(self.simulation.toxicity_cliff_threshold)
        # Z-score for catastrophe threshold
        z = (cliff - mean_projected) / std_dev

        # Cumulative Gaussian tail P(Repeat >= cliff) = 0.5 * erfc(z / sqrt(2))
        cliff_prob = 0.5 * math.erfc(z / math.sqrt(2.0))
        cliff_prob = max(0.0, min(1.0, float(cliff_prob)))

        return {
            "mean_projected_repeat": float(mean_projected),
            "std_dev_projected_repeat": float(std_dev),
            "cliff_exceedance_probability": float(cliff_prob),
            "effective_drift_rate": float(effective_drift),
        }

    def evaluate_neurodegeneration_state(self, threshold: float = 0.85) -> str:
        """Classify biological tipping point according to Neurodiagnoses criteria."""
        stats = self.calculate_projected_distribution()
        prob = stats["cliff_exceedance_probability"]
        if prob >= threshold:
            return "CLIFF_COLLAPSE_IMMINENT"
        return "SUB_THRESHOLD_LATENT"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "target_gene": self.target_gene,
            "locus": self.locus,
            "repeat_unit": self.repeat_unit,
            "germline_repeat_count": self.germline_repeat_count,
            "germline_cag_repeat": self.germline_repeat_count,
            "cell_type": self.cell_type,
            "modifiers": dict(self.modifiers),
            "simulation": self.simulation.to_dict(),
        }
        if self.protocol_name:
            res["protocol_name"] = self.protocol_name
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SomaticInstabilityContract:
        """Instantiate SomaticInstabilityContract from dictionary."""
        sim_data = data.get("simulation")
        if sim_data is None:
            sim_data = data.get("SomaticDrift", {})

        sim_contract = (
            sim_data
            if isinstance(sim_data, SomaticDriftSimulationContract)
            else SomaticDriftSimulationContract.from_dict(sim_data if isinstance(sim_data, dict) else {})
        )

        germline_count = data.get("germline_repeat_count")
        if germline_count is None:
            germline_count = data.get("germline_cag_repeat", 42)

        return cls(
            target_gene=str(data.get("target_gene", "HTT")),
            locus=str(data.get("locus", "chr4:3074877-3074933")),
            repeat_unit=str(data.get("repeat_unit", "CAG")),
            germline_repeat_count=int(germline_count),
            cell_type=str(data.get("cell_type", "striatal_projection_neuron")),
            modifiers=dict(data.get("modifiers", {})),
            simulation=sim_contract,
            protocol_name=str(data.get("protocol_name", data.get("name", ""))) or None,
        )


# Regulatory Genomics Dual-Head Contracts (BPNet & AtacWorks - MIT 6.874)
class SignalModality(str, Enum):
    """Epistemic modality of genomic signal representation."""

    DE_NOVO_SEQUENCE_DIRECT = "de_novo_sequence_direct"  # BPNet, Enformer, AlphaGenome (Sequence -> Profile)
    SIGNAL_DENOISED_ENRICHED = "signal_denoised_enriched"  # AtacWorks, deepTools (Signal -> Denoised Signal)
    EXPERIMENTAL_EMPIRICAL = "experimental_empirical"  # ChIP-nexus, ATAC-seq, CUT&RUN raw reads


class EpistemicLevel(str, Enum):
    """Epistemic status of a regulatory prediction or claim."""

    PREDICTIVE_GUIDANCE = "predictive_guidance"  # Actionable guide for experiments, non-mechanistic
    HYPOTHESIS_GENERATING = "hypothesis_generating"  # In silico hypothesis pending orthogonal test
    ORTHOGONALLY_SUPPORTED = "orthogonally_supported"  # Supported by cross-assay or in silico mutagenesis
    VALIDATED_MECHANISM = "validated_mechanism"  # Causally established biological mechanism


class ProfileResolution(str, Enum):
    """Spatial resolution of binding/accessibility profile head."""

    BASE_PAIR = "base_pair"  # 1 bp single-nucleotide base resolution (BPNet/ChIP-nexus)
    BINNED_10BP = "binned_10bp"  # 10 bp binned resolution
    BINNED_128BP = "binned_128bp"  # 128 bp binned resolution (Enformer)
    PEAK_LEVEL = "peak_level"  # Coarse peak-level binary/scalar summary


class ProfileLossMetric(str, Enum):
    """Loss/divergence metric between predicted and observed profile tracks."""

    MULTINOMIAL_NLL = "multinomial_nll"  # Negative log-likelihood under multinomial profile model
    JENSEN_SHANNON_DIVERGENCE = "jensen_shannon_divergence"  # Symmetric KL profile divergence [0.0, 1.0]
    POISSON_NLL = "poisson_nll"  # Poisson count/profile loss
    MEAN_SQUARED_ERROR = "mean_squared_error"  # Continuous MSE


class StrandMode(str, Enum):
    """Strand specification for regulatory tracks."""

    UNSTRANDED = "unstranded"
    STRANDED_PLUS_MINUS = "stranded_plus_minus"  # e.g., ChIP-nexus positive and negative strand reads


@dataclass
class CountHeadContract:
    """Contract for global signal magnitude (total count prediction head)."""

    expected_total_counts: float | None = None
    tolerance_fold: float = 1.5  # Allowed ratio fold-change deviation
    dispersion: float = 0.1  # Negative binomial dispersion parameter
    loss_model: str = "negative_binomial"  # negative_binomial or log_poisson

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "expected_total_counts": self.expected_total_counts,
            "tolerance_fold": self.tolerance_fold,
            "dispersion": self.dispersion,
            "loss_model": self.loss_model,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CountHeadContract:
        """Instantiate CountHeadContract from dictionary."""
        return cls(
            expected_total_counts=(
                float(data["expected_total_counts"]) if data.get("expected_total_counts") is not None else None
            ),
            tolerance_fold=float(data.get("tolerance_fold", 1.5)),
            dispersion=float(data.get("dispersion", 0.1)),
            loss_model=str(data.get("loss_model", "negative_binomial")),
        )


@dataclass
class ProfileHeadContract:
    """Contract for base-resolution spatial distribution (profile shape head)."""

    resolution: ProfileResolution = ProfileResolution.BASE_PAIR
    loss_metric: ProfileLossMetric = ProfileLossMetric.MULTINOMIAL_NLL
    max_jsd_threshold: float = 0.20  # Maximum acceptable Jensen-Shannon Divergence
    strand_mode: StrandMode = StrandMode.UNSTRANDED
    smoothing_window_bp: int = 0  # Optional smoothing window (0 = raw base resolution)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "resolution": str(self.resolution.value if hasattr(self.resolution, "value") else self.resolution),
            "loss_metric": str(self.loss_metric.value if hasattr(self.loss_metric, "value") else self.loss_metric),
            "max_jsd_threshold": self.max_jsd_threshold,
            "strand_mode": str(self.strand_mode.value if hasattr(self.strand_mode, "value") else self.strand_mode),
            "smoothing_window_bp": self.smoothing_window_bp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfileHeadContract:
        """Instantiate ProfileHeadContract from dictionary."""
        res_val = data.get("resolution", ProfileResolution.BASE_PAIR)
        try:
            res_enum = ProfileResolution(str(res_val).lower())
        except ValueError:
            res_enum = ProfileResolution.BASE_PAIR

        metric_val = data.get("loss_metric", ProfileLossMetric.MULTINOMIAL_NLL)
        try:
            metric_enum = ProfileLossMetric(str(metric_val).lower())
        except ValueError:
            metric_enum = ProfileLossMetric.MULTINOMIAL_NLL

        strand_val = data.get("strand_mode", StrandMode.UNSTRANDED)
        try:
            strand_enum = StrandMode(str(strand_val).lower())
        except ValueError:
            strand_enum = StrandMode.UNSTRANDED

        return cls(
            resolution=res_enum,
            loss_metric=metric_enum,
            max_jsd_threshold=float(data.get("max_jsd_threshold", 0.20)),
            strand_mode=strand_enum,
            smoothing_window_bp=int(data.get("smoothing_window_bp", 0)),
        )


@dataclass
class RegulatoryTrackContract:
    """Contract for an experimental or enhanced regulatory track (e.g. AtacWorks denoised)."""

    track_id: str
    modality: SignalModality = SignalModality.DE_NOVO_SEQUENCE_DIRECT
    source_measurement: str | None = None  # Raw experiment or input BAM/BigWig
    denoiser_model: str | None = None  # e.g. "AtacWorks-v2"
    peak_classification_threshold: float = 0.50  # Probability threshold for accessible peak classification
    min_snr: float = 2.0  # Minimum signal-to-noise ratio

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "track_id": self.track_id,
            "modality": str(self.modality.value if hasattr(self.modality, "value") else self.modality),
            "source_measurement": self.source_measurement,
            "denoiser_model": self.denoiser_model,
            "peak_classification_threshold": self.peak_classification_threshold,
            "min_snr": self.min_snr,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegulatoryTrackContract:
        """Instantiate RegulatoryTrackContract from dictionary."""
        mod_val = data.get("modality", SignalModality.DE_NOVO_SEQUENCE_DIRECT)
        try:
            mod_enum = SignalModality(str(mod_val).lower())
        except ValueError:
            mod_enum = SignalModality.DE_NOVO_SEQUENCE_DIRECT

        return cls(
            track_id=str(data.get("track_id", data.get("name", "track_01"))),
            modality=mod_enum,
            source_measurement=str(data["source_measurement"]) if "source_measurement" in data else None,
            denoiser_model=str(data["denoiser_model"]) if "denoiser_model" in data else None,
            peak_classification_threshold=float(data.get("peak_classification_threshold", 0.50)),
            min_snr=float(data.get("min_snr", 2.0)),
        )


@dataclass
class RegulatoryProfileContract:
    """Formal GFL IO Contract for Regulatory Genomics Dual-Head predictions (BPNet & AtacWorks).

    Grounding from MIT 6.874 (Deep Learning in the Life Sciences):
    - Addresses the fundamental loss of spatial information when reducing genomic signal to one scalar.
    - Decouples global total count head from base-resolution profile shape head.
    - Enforces the Epistemic Barrier separating actionable experimental guidance from causal mechanisms.
    """

    profile_id: str
    target_factor: str  # e.g., "OCT4", "SOX2", "NANOG", "CTCF"
    locus: str  # Genomic coordinates, e.g., "chr7:27142000-27143000"
    cell_type: str = "K562"
    modality: SignalModality = SignalModality.DE_NOVO_SEQUENCE_DIRECT
    count_head: CountHeadContract = field(default_factory=CountHeadContract)
    profile_head: ProfileHeadContract = field(default_factory=ProfileHeadContract)
    epistemic_level: EpistemicLevel = EpistemicLevel.PREDICTIVE_GUIDANCE
    orthogonal_validation_required: bool = True
    orthogonal_validation_confirmed: bool = False
    source_model: str = "BPNet"

    @staticmethod
    def compute_multinomial_nll(observed_counts: list[int | float], predicted_probs: list[float]) -> float:
        """Compute the Multinomial negative log-likelihood (NLL) profile loss.

        Formula: -log P(k_1, ..., k_L | n, p_1, ..., p_L) where profile term is:
        - sum_{i} k_i * ln(p_i) + log_gamma(n + 1) - sum_{i} log_gamma(k_i + 1).
        Consistent with MIT 6.874 Lecture 7.
        """
        import math

        if len(observed_counts) != len(predicted_probs):
            raise ValueError(
                f"Observed counts ({len(observed_counts)}) and predicted probs ({len(predicted_probs)}) length mismatch"
            )

        n = sum(observed_counts)
        if n == 0:
            return 0.0

        # Profile term: - sum_i k_i * ln(p_i)
        loss = 0.0
        # Normalization constant (multinomial coefficient)
        multinomial_coeff_log = math.lgamma(n + 1.0)

        for k, p in zip(observed_counts, predicted_probs):
            if k > 0:
                p_safe = max(p, 1e-12)
                loss -= k * math.log(p_safe)
                multinomial_coeff_log -= math.lgamma(k + 1.0)

        loss -= multinomial_coeff_log
        return float(loss)

    @staticmethod
    def compute_jsd(p: list[float], q: list[float]) -> float:
        """Compute the Jensen-Shannon Divergence between two normalized probability vectors.

        JSD(P || Q) = 0.5 * D_KL(P || M) + 0.5 * D_KL(Q || M) where M = 0.5 * (P + Q).
        Bounded in [0.0, 1.0] when computed with log base 2.
        """
        import math

        if len(p) != len(q):
            raise ValueError(f"Vectors length mismatch: {len(p)} vs {len(q)}")

        # Normalize to probability distributions
        sum_p = sum(p) or 1.0
        sum_q = sum(q) or 1.0
        p_norm = [max(x / sum_p, 1e-12) for x in p]
        q_norm = [max(y / sum_q, 1e-12) for y in q]

        m: list[float] = [0.5 * (px + qx) for px, qx in zip(p_norm, q_norm)]

        kl_pm = sum(px * math.log2(px / mx) for px, mx in zip(p_norm, m) if px > 0)
        kl_qm = sum(qx * math.log2(qx / mx) for qx, mx in zip(q_norm, m) if qx > 0)

        return float(0.5 * kl_pm + 0.5 * kl_qm)

    def validates_epistemic_barrier(self) -> tuple[bool, str]:
        """Verify the Epistemic Barrier invariant.

        A claim of VALIDATED_MECHANISM cannot be asserted without confirmed orthogonal validation.
        """
        if self.epistemic_level == EpistemicLevel.VALIDATED_MECHANISM and not self.orthogonal_validation_confirmed:
            return (
                False,
                "EPISTEMIC BARRIER VIOLATION: A regulatory deep learning prediction cannot assert "
                "'VALIDATED_MECHANISM' without confirmed orthogonal empirical validation.",
            )
        return True, "Valid epistemic boundary."

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "profile_id": self.profile_id,
            "target_factor": self.target_factor,
            "locus": self.locus,
            "cell_type": self.cell_type,
            "modality": str(self.modality.value if hasattr(self.modality, "value") else self.modality),
            "count_head": self.count_head.to_dict(),
            "profile_head": self.profile_head.to_dict(),
            "epistemic_level": str(
                self.epistemic_level.value if hasattr(self.epistemic_level, "value") else self.epistemic_level
            ),
            "orthogonal_validation_required": self.orthogonal_validation_required,
            "orthogonal_validation_confirmed": self.orthogonal_validation_confirmed,
            "source_model": self.source_model,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegulatoryProfileContract:
        """Instantiate RegulatoryProfileContract from dictionary."""
        mod_val = data.get("modality", SignalModality.DE_NOVO_SEQUENCE_DIRECT)
        try:
            mod_enum = SignalModality(str(mod_val).lower())
        except ValueError:
            mod_enum = SignalModality.DE_NOVO_SEQUENCE_DIRECT

        epi_val = data.get("epistemic_level", EpistemicLevel.PREDICTIVE_GUIDANCE)
        try:
            epi_enum = EpistemicLevel(str(epi_val).lower())
        except ValueError:
            epi_enum = EpistemicLevel.PREDICTIVE_GUIDANCE

        count_data = data.get("count_head", {})
        count_head = (
            count_data
            if isinstance(count_data, CountHeadContract)
            else CountHeadContract.from_dict(count_data if isinstance(count_data, dict) else {})
        )

        profile_data = data.get("profile_head", {})
        profile_head = (
            profile_data
            if isinstance(profile_data, ProfileHeadContract)
            else ProfileHeadContract.from_dict(profile_data if isinstance(profile_data, dict) else {})
        )

        return cls(
            profile_id=str(data.get("profile_id", data.get("name", "regulatory_profile_01"))),
            target_factor=str(data.get("target_factor", "UNKNOWN")),
            locus=str(data.get("locus", "chr1:1-1000")),
            cell_type=str(data.get("cell_type", "K562")),
            modality=mod_enum,
            count_head=count_head,
            profile_head=profile_head,
            epistemic_level=epi_enum,
            orthogonal_validation_required=bool(data.get("orthogonal_validation_required", True)),
            orthogonal_validation_confirmed=bool(data.get("orthogonal_validation_confirmed", False)),
            source_model=str(data.get("source_model", "BPNet")),
        )


# AlphaGenome Atlas and Variant Impact Types
class AviModality(str, Enum):
    """The 18 biological feature attribution modalities defined in AlphaGenome Atlas."""

    SPLICING = "Splicing"
    ALPHAMISSENSE = "AlphaMissense"
    CHIP_TF = "ChIP-TF"
    DNASE_SEQ = "DNASE-seq"
    CACTUS_241_WAY = "Cactus"
    RNA_SEQ = "RNA-seq"
    HISTONE_CHIP = "Histone-ChIP"
    SPLICE_JUNCTIONS = "Splice-Junctions"
    SPLICE_SITE_USAGE = "Splice-Site-Usage"
    SPLICE_SITES = "Splice-Sites"
    CAGE = "CAGE"
    PRO_SEQ = "PRO-seq"
    RAMPAGE = "RAMPAGE"
    MICRO_C = "Micro-C"
    HI_C = "Hi-C"
    ATAC_SEQ = "ATAC-seq"
    MOTIF_DISRUPTION = "Motif-Disruption"
    EVOLUTIONARY_CONSERVATION = "Evolutionary-Conservation"
    FIVE_HMC = "5hmC"

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


@dataclass
class AviScore:
    """AlphaGenome Variant Impact (AVI) score representation."""

    phred: float
    raw: float
    quantile: float
    top_percentile: float
    top_modality: str
    top_feature_importance: float = 0.0
    feature_importances: dict[str, float] = field(default_factory=dict)

    @property
    def is_high_impact(self) -> bool:
        """Check if variant falls into high impact tier (Phred >= 20, top 1%)."""
        return self.phred >= 20.0

    @property
    def is_ultra_rare_impact(self) -> bool:
        """Check if variant falls into ultra-high impact tier (Phred >= 40, top 0.01%)."""
        return self.phred >= 40.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "phred": self.phred,
            "raw": self.raw,
            "quantile": self.quantile,
            "top_percentile": self.top_percentile,
            "top_modality": self.top_modality,
            "top_feature_importance": self.top_feature_importance,
            "feature_importances": self.feature_importances,
            "is_high_impact": self.is_high_impact,
            "is_ultra_rare_impact": self.is_ultra_rare_impact,
        }


@dataclass
class RegulatoryMotifAnnotation:
    """Regulatory DNA motif disruption or binding annotation."""

    motif_id: str
    motif_name: str
    chromosome: str
    position: int
    strand: str = "+"
    affinity_change: float = 0.0
    transcription_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "motif_id": self.motif_id,
            "motif_name": self.motif_name,
            "chromosome": self.chromosome,
            "position": self.position,
            "strand": self.strand,
            "affinity_change": self.affinity_change,
            "transcription_factors": self.transcription_factors,
        }


class ClinVarSignificance(str, Enum):
    """Clinical significance classification according to ClinVar / ACMG standards."""

    PATHOGENIC = "Pathogenic"
    LIKELY_PATHOGENIC = "Likely pathogenic"
    UNCERTAIN_SIGNIFICANCE = "Uncertain significance"  # VUS
    LIKELY_BENIGN = "Likely benign"
    BENIGN = "Benign"
    CONFLICTING = "Conflicting classifications of pathogenicity"
    NOT_PROVIDED = "not provided"

    def __str__(self) -> str:
        """Return string value."""
        return self.value

    @property
    def is_vus(self) -> bool:
        """Check if classification corresponds to a Variant of Uncertain Significance."""
        return self == ClinVarSignificance.UNCERTAIN_SIGNIFICANCE or self == ClinVarSignificance.CONFLICTING


@dataclass
class TissueRegulatoryEffect:
    """Tissue-specific regulatory alteration predicted by genomic foundation models."""

    tissue_ontology_id: str  # e.g., UBERON:0000955 (Brain cortex) or CL:0000129 (Microglial cell)
    tissue_name: str
    dnase_delta: float = 0.0
    rna_fold_change: float = 0.0
    h3k27ac_delta: float = 0.0
    promoter_enhancer_contact_delta: float = 0.0
    disrupted_transcription_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tissue_ontology_id": self.tissue_ontology_id,
            "tissue_name": self.tissue_name,
            "dnase_delta": self.dnase_delta,
            "rna_fold_change": self.rna_fold_change,
            "h3k27ac_delta": self.h3k27ac_delta,
            "promoter_enhancer_contact_delta": self.promoter_enhancer_contact_delta,
            "disrupted_transcription_factors": self.disrupted_transcription_factors,
        }


@dataclass
class NonCodingRegulatoryContract:
    """Formal IO Contract for non-coding regulatory variant interpretation (ClinVar + AlphaGenome)."""

    target_locus: str
    target_tissue: str  # Primary affected tissue (e.g., UBERON:0000955)
    control_tissue: str  # Control / unaffected tissue (e.g., UBERON:0002107)
    clinvar_status: ClinVarSignificance = ClinVarSignificance.UNCERTAIN_SIGNIFICANCE
    min_avi_phred_threshold: float = 20.0
    required_tf_conservation: list[str] = field(default_factory=list)
    max_control_tissue_impact: float = 5.0  # Asserts specificity: control tissue must not be disrupted

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "target_locus": self.target_locus,
            "target_tissue": self.target_tissue,
            "control_tissue": self.control_tissue,
            "clinvar_status": str(self.clinvar_status),
            "min_avi_phred_threshold": self.min_avi_phred_threshold,
            "required_tf_conservation": self.required_tf_conservation,
            "max_control_tissue_impact": self.max_control_tissue_impact,
        }


@dataclass
class VariantImpact:
    """Genomic variant with AlphaGenome Atlas impact annotations and ClinVar resolution."""

    variant_str: str  # 1-based format chr:pos:ref>alt
    chromosome: str
    position: int
    ref: str
    alt: str
    avi_score: AviScore | None = None
    regulatory_motifs: list[RegulatoryMotifAnnotation] = field(default_factory=list)
    tissue_effects: list[TissueRegulatoryEffect] = field(default_factory=list)
    clinvar_significance: ClinVarSignificance = ClinVarSignificance.NOT_PROVIDED
    atlas_url: str | None = None

    def __post_init__(self) -> None:
        """Construct atlas URL if missing."""
        if not self.atlas_url and self.variant_str:
            self.atlas_url = f"https://deepmind.google.com/science/alphagenome/atlas/variant/{self.variant_str}"

    @property
    def resolves_non_coding_vus(self) -> bool:
        """Determines if a ClinVar VUS can be resolved into a regulatory damaging candidate."""
        return bool(self.clinvar_significance.is_vus and self.avi_score and self.avi_score.is_high_impact)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "variant": self.variant_str,
            "chromosome": self.chromosome,
            "position": self.position,
            "ref": self.ref,
            "alt": self.alt,
            "avi_score": self.avi_score.to_dict() if self.avi_score else None,
            "regulatory_motifs": [m.to_dict() for m in self.regulatory_motifs],
            "tissue_effects": [t.to_dict() for t in self.tissue_effects],
            "clinvar_significance": str(self.clinvar_significance),
            "resolves_non_coding_vus": self.resolves_non_coding_vus,
            "atlas_url": self.atlas_url,
        }


# DepMap and Causal Transition Graph Types
class CoDependencyTier(str, Enum):
    """Co-dependency strength tiers for CRISPR screens."""

    HIGH = "HIGH"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    NONE = "NONE"

    def __str__(self) -> str:
        """Return string value."""
        return self.value


class CausalLevel(str, Enum):
    """Biological abstraction levels in causal transition graph."""

    PHENOTYPIC = "PHENOTYPIC"
    CELLULAR = "CELLULAR"
    MOLECULAR = "MOLECULAR"
    ATOMIC = "ATOMIC"

    def __str__(self) -> str:
        """Return string value."""
        return self.value


@dataclass
class DepMapCoDependency:
    """CRISPR DepMap functional co-dependency between two genes."""

    gene_a: str
    gene_b: str
    correlation_score: float
    p_value: float
    codependency_tier: CoDependencyTier = CoDependencyTier.NONE
    screen_type: str = "CRISPR_DepMap_Public"

    def __post_init__(self) -> None:
        """Infer tier from correlation score if not set."""
        if self.codependency_tier == CoDependencyTier.NONE and self.correlation_score > 0.0:
            if self.correlation_score >= 0.5:
                self.codependency_tier = CoDependencyTier.HIGH
            elif self.correlation_score >= 0.3:
                self.codependency_tier = CoDependencyTier.MODERATE
            elif self.correlation_score >= 0.1:
                self.codependency_tier = CoDependencyTier.WEAK

    @property
    def is_significant(self) -> bool:
        """Check if correlation is statistically significant (p < 0.05)."""
        return self.p_value < 0.05 and self.correlation_score > 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "gene_a": self.gene_a,
            "gene_b": self.gene_b,
            "correlation_score": self.correlation_score,
            "p_value": self.p_value,
            "codependency_tier": str(self.codependency_tier),
            "screen_type": self.screen_type,
            "is_significant": self.is_significant,
        }


@dataclass
class CausalTransitionNode:
    """Formal representation of a biological causal transition node."""

    node_id: str
    level: CausalLevel
    entity_name: str
    biological_state: str
    confidence: float = 1.0
    evidence_sources: list[str] = field(default_factory=list)
    incoming_edges: list[str] = field(default_factory=list)
    outgoing_edges: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "level": str(self.level),
            "entity_name": self.entity_name,
            "biological_state": self.biological_state,
            "confidence": self.confidence,
            "evidence_sources": self.evidence_sources,
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges,
        }


class CandidateStatus(str, Enum):
    """Lifecycle status of a generated biological design candidate (inspired by RFOptimization)."""

    VALIDATED = "validated"
    NEAR_MISS = "near_miss"
    REJECTED = "rejected"
    OPTIMIZED = "optimized"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


class ConsensusModel(str, Enum):
    """Structural and sequence foundation models for multi-model consensus validation."""

    AF3 = "alphafold3"
    RF3 = "rosettafold3"
    BOLTZ = "boltz1"
    CHAI_1 = "chai1"
    PROTENIX = "protenix"
    PROTEIN_MPNN = "protein_mpnn"
    LIGAND_MPNN = "ligand_mpnn"
    OMNII_1 = "omnii1"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


@dataclass
class MultiModelConsensus:
    """Cross-model consensus validation metrics (Baker Lab RFO & Runs N' Poses consensus).

    Evaluates structural predictions across independent models (AF3, RF3, Boltz, Chai-1, Protenix)
    to eliminate single-predictor over-fitting.
    """

    af3_iptm: float | None = None
    af3_ipae: float | None = None
    af3_version: str = "3.0.5"
    af3_fast_jackhmmer_msa: bool = True
    rf3_confidence: float | None = None
    boltz_confidence: float | None = None
    chai1_confidence: float | None = None
    protenix_confidence: float | None = None
    plddt_mean: float | None = None

    def passes_consensus(
        self,
        min_iptm: float = 0.8,
        max_ipae: float = 2.5,
        min_confidence: float = 0.8,
    ) -> bool:
        """Check if candidate satisfies the multi-model consensus thresholds."""
        if self.af3_iptm is not None and self.af3_iptm < min_iptm:
            return False
        if self.af3_ipae is not None and self.af3_ipae > max_ipae:
            return False
        if self.rf3_confidence is not None and self.rf3_confidence < min_confidence:
            return False
        if self.boltz_confidence is not None and self.boltz_confidence < min_confidence:
            return False
        if self.chai1_confidence is not None and self.chai1_confidence < min_confidence:
            return False
        if self.protenix_confidence is not None:
            return self.protenix_confidence >= min_confidence
        return True

    def is_near_miss(
        self,
        iptm_threshold: float = 0.8,
        ipae_threshold: float = 2.5,
        margin: float = 0.15,
    ) -> bool:
        """Determine if candidate is near the decision boundary and eligible for rescue."""
        if self.passes_consensus(min_iptm=iptm_threshold, max_ipae=ipae_threshold):
            return False

        # Check if borderline near pass threshold
        borderline_iptm = self.af3_iptm is not None and (iptm_threshold - margin) <= self.af3_iptm < iptm_threshold
        borderline_ipae = self.af3_ipae is not None and ipae_threshold < self.af3_ipae <= (
            ipae_threshold + margin * 2.0
        )
        return borderline_iptm or borderline_ipae

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "af3_iptm": self.af3_iptm,
            "af3_ipae": self.af3_ipae,
            "af3_version": self.af3_version,
            "af3_fast_jackhmmer_msa": self.af3_fast_jackhmmer_msa,
            "rf3_confidence": self.rf3_confidence,
            "boltz_confidence": self.boltz_confidence,
            "chai1_confidence": self.chai1_confidence,
            "protenix_confidence": self.protenix_confidence,
            "plddt_mean": self.plddt_mean,
            "passes_consensus": self.passes_consensus(),
            "is_near_miss": self.is_near_miss(),
        }


class RestraintType(str, Enum):
    """Experimental structural restraint modalities for measurement-guided ensembles."""

    NMR_NOE = "nmr_noe"
    CRYO_EM_MAP = "cryo_em_map"
    XL_MS = "xl_ms"
    SAXS_ENVELOPE = "saxs_envelope"
    EPR_DEER = "epr_deer"

    def __str__(self) -> str:
        return self.value


@dataclass
class ExperimentalRestraintsContract:
    """Steers AI structural diffusion toward measurement-consistent conformational ensembles.

    Based on 'Experiment-guided AlphaFold3 resolves measurement-consistent protein ensembles' (2025/2026).
    """

    restraint_type: RestraintType = RestraintType.NMR_NOE
    restraint_file: str | None = None
    tolerance_angstrom: float = 3.0
    weight: float = 1.0
    satisfaction_ratio: float | None = None
    min_satisfaction_threshold: float = 0.8
    target_chain: str | None = None

    def is_satisfied(self) -> bool:
        """Check if empirical experimental restraints are satisfied within the tolerance threshold."""
        if self.satisfaction_ratio is None:
            return True
        return self.satisfaction_ratio >= self.min_satisfaction_threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "restraint_type": str(self.restraint_type),
            "restraint_file": self.restraint_file,
            "tolerance_angstrom": self.tolerance_angstrom,
            "weight": self.weight,
            "satisfaction_ratio": self.satisfaction_ratio,
            "min_satisfaction_threshold": self.min_satisfaction_threshold,
            "target_chain": self.target_chain,
            "is_satisfied": self.is_satisfied(),
        }


@dataclass
class RunsNPosesMetric:
    """Benchmark metrics for protein-ligand co-folding generalization (Runs N' Poses benchmark 2026)."""

    pose_rmsd: float | None = None
    clash_score: float | None = None
    contact_recovery: float | None = None
    force_field_energy_kcal_mol: float | None = None

    def passes_pose_gate(self, max_rmsd: float = 2.0, max_clash: float = 10.0) -> bool:
        """Evaluate whether co-folding pose generalizes without steric clashes or conformational distortion."""
        if self.pose_rmsd is not None and self.pose_rmsd > max_rmsd:
            return False
        if self.clash_score is not None:
            return self.clash_score <= max_clash
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "pose_rmsd": self.pose_rmsd,
            "clash_score": self.clash_score,
            "contact_recovery": self.contact_recovery,
            "force_field_energy_kcal_mol": self.force_field_energy_kcal_mol,
            "passes_pose_gate": self.passes_pose_gate(),
        }


@dataclass
class LigandConditionedPocketContract:
    """Models ligand-induced cryptic pocket opening vs. collapsed apo states in AlphaFold3 / Boltz co-folding."""

    target_receptor: str
    probe_ligand_smiles: str | None = None
    pocket_mode: str = "differential"  # 'apo_uninduced', 'holo_induced', 'differential'
    cryptic_delta_score: float | None = None
    min_cryptic_delta_threshold: float = 0.35

    def is_cryptic_induced(self) -> bool:
        """Check if pocket opening is significantly favored in the presence of ligand."""
        if self.cryptic_delta_score is None:
            return False
        return self.cryptic_delta_score >= self.min_cryptic_delta_threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_receptor": self.target_receptor,
            "probe_ligand_smiles": self.probe_ligand_smiles,
            "pocket_mode": self.pocket_mode,
            "cryptic_delta_score": self.cryptic_delta_score,
            "min_cryptic_delta_threshold": self.min_cryptic_delta_threshold,
            "is_cryptic_induced": self.is_cryptic_induced(),
        }


class EnsembleGenerator(str, Enum):
    """Generative structural ensemble models (grounded in BioEmu2 / Microsoft Research AI for Science 2026)."""

    BIOEMU_2 = "bioemu2"
    ALPHAFOLD_3 = "alphafold3"
    CHAI_1 = "chai1"
    BOLTZ_1 = "boltz1"
    MOLECULAR_DYNAMICS = "molecular_dynamics"

    def __str__(self) -> str:
        return self.value


class SolvationModel(str, Enum):
    """Solvation treatment for thermodynamic conformational ensembles."""

    EXPLICIT_EQUIVALENT = "explicit_equivalent"
    IMPLICIT_GB = "implicit_gb"
    VACUUM = "vacuum"

    def __str__(self) -> str:
        return self.value


@dataclass
class BoltzmannEnsembleContract:
    """Formal GFL IO Contract for Thermodynamic Boltzmann Conformational Ensembles.

    Inspired by Microsoft Research AI for Science's BioEmu2 (MIT license, 2026):
    - Emulates equilibrium conformational dynamics generating thousands of independent,
      thermodynamically consistent structures per hour on a single GPU.
    - Yields relative free energy accuracy (~1 kcal/mol), resolving cryptic pockets,
      metastable functional states, and transient cavity exposures.
    """

    target: str  # Protein name, UniProt ID, or sequence identifier (e.g., 'MAPT_HUMAN', 'TDP43')
    sample_size: int = 1000  # Number of independent conformational samples
    generator: EnsembleGenerator = EnsembleGenerator.BIOEMU_2
    temperature_kelvin: float = 310.15  # Physiological temperature (37 °C)
    solvation: SolvationModel = SolvationModel.EXPLICIT_EQUIVALENT
    ensemble_id: str | None = None
    max_energy_cutoff_kcal_mol: float = 15.0  # Cutoff above ground state to discard non-physical conformers
    engine_version: str | None = None
    fast_jackhmmer_msa: bool = True

    def compute_boltzmann_weight(self, delta_g_kcal_mol: float) -> float:
        """Calculate Boltzmann probability weight P_i proportional to exp(-Delta G / (k_B * T)).

        k_B = 0.001987204 kcal / (mol * K).
        """
        import math

        k_b = 0.00198720425864083
        kt = k_b * max(1.0, self.temperature_kelvin)
        exponent = -max(-50.0, min(50.0, delta_g_kcal_mol / kt))
        return float(math.exp(exponent))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "target": self.target,
            "sample_size": self.sample_size,
            "generator": str(self.generator),
            "temperature_kelvin": self.temperature_kelvin,
            "solvation": str(self.solvation),
            "max_energy_cutoff_kcal_mol": self.max_energy_cutoff_kcal_mol,
            "fast_jackhmmer_msa": self.fast_jackhmmer_msa,
        }
        if self.engine_version:
            res["engine_version"] = self.engine_version
        if self.ensemble_id:
            res["ensemble_id"] = self.ensemble_id
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BoltzmannEnsembleContract:
        """Instantiate BoltzmannEnsembleContract from dictionary."""
        gen_val = data.get("generator", EnsembleGenerator.BIOEMU_2)
        try:
            gen_enum = EnsembleGenerator(str(gen_val).lower())
        except ValueError:
            gen_enum = EnsembleGenerator.BIOEMU_2

        solv_val = data.get("solvation", SolvationModel.EXPLICIT_EQUIVALENT)
        try:
            solv_enum = SolvationModel(str(solv_val).lower())
        except ValueError:
            solv_enum = SolvationModel.EXPLICIT_EQUIVALENT

        return cls(
            target=str(data.get("target", "TARGET_PROTEIN")),
            sample_size=int(data.get("sample_size", 1000)),
            generator=gen_enum,
            temperature_kelvin=float(data.get("temperature_kelvin", 310.15)),
            solvation=solv_enum,
            ensemble_id=str(data.get("ensemble_id", data.get("name", ""))) or None,
            max_energy_cutoff_kcal_mol=float(data.get("max_energy_cutoff_kcal_mol", 15.0)),
            engine_version=str(data["engine_version"]) if data.get("engine_version") else None,
            fast_jackhmmer_msa=bool(data.get("fast_jackhmmer_msa", True)),
        )


@dataclass
class CrypticPocketContract:
    """Formal GFL IO Contract for Cryptic Pocket Conformational Selection and Dynamic Cavity Queries.

    Models transiently accessible binding pockets that remain collapsed in the apo static ground state
    but open with significant Boltzmann weight (P >= threshold) in the thermodynamic ensemble.
    """

    pocket_id: str
    target_ensemble: str  # Identifier of the BoltzmannEnsembleContract
    residues: list[int]  # 1-based residue indices defining the cryptic pocket boundary
    probe_radius_angstrom: float = 1.4  # Water probe equivalent
    min_boltzmann_weight: float = 0.05  # Minimum thermodynamic occupancy (e.g. 5% population)
    max_delta_g_relative_kcal_mol: float = 2.5  # Energy penalty for pocket opening relative to ground state
    is_transient: bool = True
    target_pathogen_domain: str | None = None  # e.g., 'tau_phf6_hexapeptide', 'tdp43_rrm_loop'

    def evaluates_druggability(self, observed_boltzmann_weight: float, observed_delta_g: float) -> bool:
        """Check if transient pocket meets thermodynamic druggability criteria."""
        return (
            observed_boltzmann_weight >= self.min_boltzmann_weight
            and observed_delta_g <= self.max_delta_g_relative_kcal_mol
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "pocket_id": self.pocket_id,
            "target_ensemble": self.target_ensemble,
            "residues": list(self.residues),
            "probe_radius_angstrom": self.probe_radius_angstrom,
            "min_boltzmann_weight": self.min_boltzmann_weight,
            "max_delta_g_relative_kcal_mol": self.max_delta_g_relative_kcal_mol,
            "is_transient": self.is_transient,
        }
        if self.target_pathogen_domain:
            res["target_pathogen_domain"] = self.target_pathogen_domain
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CrypticPocketContract:
        """Instantiate CrypticPocketContract from dictionary."""
        residues_raw = data.get("residues", [])
        return cls(
            pocket_id=str(data.get("pocket_id", data.get("name", "cryptic_pocket_01"))),
            target_ensemble=str(data.get("target_ensemble", data.get("from", "default_ensemble"))),
            residues=[int(r) for r in residues_raw],
            probe_radius_angstrom=float(data.get("probe_radius_angstrom", 1.4)),
            min_boltzmann_weight=float(data.get("min_boltzmann_weight", 0.05)),
            max_delta_g_relative_kcal_mol=float(data.get("max_delta_g_relative_kcal_mol", 2.5)),
            is_transient=bool(data.get("is_transient", True)),
            target_pathogen_domain=str(data["target_pathogen_domain"]) if "target_pathogen_domain" in data else None,
        )


@dataclass
class ThermodynamicBindingContract:
    """Formal GFL IO Contract for VHH/Nanobody and Small-Molecule Conformational Selection.

    Formulates binding equilibrium not as rigid lock-and-key docking, but as allosteric stabilization
    of active/desired conformational states (e.g. GPCR TM6 outward displacement >= 10.0 A)
    with relative binding free energy Delta Delta G (kcal/mol).
    """

    binder_id: str
    target_ensemble: str
    stabilized_state_condition: str  # e.g., 'tm6_displacement >= 10.0'
    min_target_fraction: float = 0.80  # Desired population shift into active state
    max_delta_delta_g_kcal_mol: float = -2.0  # Favorable relative stabilization energy
    binding_pocket_id: str | None = None
    temperature_kelvin: float = 310.15

    def satisfies_allosteric_stabilization(
        self, observed_active_fraction: float, observed_delta_delta_g: float
    ) -> bool:
        """Verify whether binder successfully shifts conformational equilibrium to active state."""
        return (
            observed_active_fraction >= self.min_target_fraction
            and observed_delta_delta_g <= self.max_delta_delta_g_kcal_mol
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "binder_id": self.binder_id,
            "target_ensemble": self.target_ensemble,
            "stabilized_state_condition": self.stabilized_state_condition,
            "min_target_fraction": self.min_target_fraction,
            "max_delta_delta_g_kcal_mol": self.max_delta_delta_g_kcal_mol,
            "temperature_kelvin": self.temperature_kelvin,
        }
        if self.binding_pocket_id:
            res["binding_pocket_id"] = self.binding_pocket_id
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThermodynamicBindingContract:
        """Instantiate ThermodynamicBindingContract from dictionary."""
        return cls(
            binder_id=str(data.get("binder_id", data.get("name", "vhh_stabilizer_01"))),
            target_ensemble=str(data.get("target_ensemble", "default_ensemble")),
            stabilized_state_condition=str(data.get("stabilized_state_condition", "active_conformation == True")),
            min_target_fraction=float(data.get("min_target_fraction", 0.80)),
            max_delta_delta_g_kcal_mol=float(data.get("max_delta_delta_g_kcal_mol", -2.0)),
            binding_pocket_id=str(data["binding_pocket_id"]) if "binding_pocket_id" in data else None,
            temperature_kelvin=float(data.get("temperature_kelvin", 310.15)),
        )


class PhageCapsidArchitecture(str, Enum):
    """Bacteriophage virion morphology and genomic delivery chassis."""

    MYOVIRIDAE_T4 = "myoviridae_t4"  # Contractile tail, large genome (e.g. T4-like)
    SIPHOVIRIDAE_LAMBDA = "siphoviridae_lambda"  # Long non-contractile tail (e.g. Lambda)
    PODOVIRIDAE_T7 = "podoviridae_t7"  # Short non-contractile tail (e.g. T7)
    TEQUATROVIRUS = "tequatrovirus"
    CUSTOM_CHASSIS = "custom_chassis"

    def __str__(self) -> str:
        return self.value


@dataclass
class BiodefenseSafetyGate:
    """Strict biodefense and clinical biosafety verification for synthetic bacteriophages.

    Enforces compassion-use clinical invariants:
    - Zero horizontal gene transfer of antimicrobial resistance (AMR).
    - Zero bacterial toxin or virulence factor homology.
    - Zero off-target lysis of beneficial human commensal microbiota.
    """

    max_immunogenicity_score: float = 0.15
    prohibit_amr_transfer_genes: bool = True
    prohibit_toxin_homology: bool = True
    max_off_target_microbiome_lysis: float = 0.01  # <= 1% commensal perturbation
    verified_clearance: bool = True

    def passes_safety_gate(
        self,
        immunogenicity: float,
        has_amr_genes: bool,
        has_toxin_homology: bool,
        off_target_lysis: float,
    ) -> bool:
        """Evaluate synthetic phage candidate against biodefense safety constraints."""
        if immunogenicity > self.max_immunogenicity_score:
            return False
        if self.prohibit_amr_transfer_genes and has_amr_genes:
            return False
        if self.prohibit_toxin_homology and has_toxin_homology:
            return False
        return off_target_lysis <= self.max_off_target_microbiome_lysis

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "max_immunogenicity_score": self.max_immunogenicity_score,
            "prohibit_amr_transfer_genes": self.prohibit_amr_transfer_genes,
            "prohibit_toxin_homology": self.prohibit_toxin_homology,
            "max_off_target_microbiome_lysis": self.max_off_target_microbiome_lysis,
            "verified_clearance": self.verified_clearance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BiodefenseSafetyGate:
        """Instantiate BiodefenseSafetyGate from dictionary."""
        return cls(
            max_immunogenicity_score=float(data.get("max_immunogenicity_score", 0.15)),
            prohibit_amr_transfer_genes=bool(data.get("prohibit_amr_transfer_genes", True)),
            prohibit_toxin_homology=bool(data.get("prohibit_toxin_homology", True)),
            max_off_target_microbiome_lysis=float(data.get("max_off_target_microbiome_lysis", 0.01)),
            verified_clearance=bool(data.get("verified_clearance", True)),
        )


@dataclass
class BacteriophageTherapyContract:
    """Formal GFL IO Contract for AI-Designed Synthetic Bacteriophage Therapy.

    Grounded in Radical Numerics' Omnii-1 multimodal genome foundation model (2026),
    enabling compassionate human administration against antimicrobial resistant (AMR) pathogens
    (Pseudomonas aeruginosa, Acinetobacter baumannii, MRSA):
    - Unifies genomic DNA architecture, tail fiber receptor binding, and 5hmC epigenetic evasion.
    - Enforces biodefense safety gates against toxin/AMR transduction.
    """

    therapy_id: str
    target_pathogen: str  # e.g., "Pseudomonas_aeruginosa_AMR_strain_01"
    model: str = "omnii-1"
    modalities: list[str] = field(
        default_factory=lambda: [
            "DNA_GENOME",
            "COAT_PROTEIN_STRUCTURE",
            "RECEPTOR_BINDING_FIBER",
            "EPIGENOMIC_5HMC_EVASION",
        ]
    )
    capsid_architecture: PhageCapsidArchitecture = PhageCapsidArchitecture.MYOVIRIDAE_T4
    host_range_expansion: bool = True
    receptor_binding_fiber_ref: str | None = None
    biodefense_gate: BiodefenseSafetyGate = field(default_factory=BiodefenseSafetyGate)
    compassionate_use_approved: bool = True
    target_cfu_reduction_log10: float = 6.0  # Log-kill efficacy target

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "therapy_id": self.therapy_id,
            "target_pathogen": self.target_pathogen,
            "model": self.model,
            "modalities": list(self.modalities),
            "capsid_architecture": str(self.capsid_architecture),
            "host_range_expansion": self.host_range_expansion,
            "receptor_binding_fiber_ref": self.receptor_binding_fiber_ref,
            "biodefense_gate": self.biodefense_gate.to_dict(),
            "compassionate_use_approved": self.compassionate_use_approved,
            "target_cfu_reduction_log10": self.target_cfu_reduction_log10,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BacteriophageTherapyContract:
        """Instantiate BacteriophageTherapyContract from dictionary."""
        arch_val = data.get("capsid_architecture", PhageCapsidArchitecture.MYOVIRIDAE_T4)
        try:
            arch_enum = PhageCapsidArchitecture(str(arch_val).lower())
        except ValueError:
            arch_enum = PhageCapsidArchitecture.MYOVIRIDAE_T4

        gate_data = data.get("biodefense_gate", {})
        gate = (
            gate_data
            if isinstance(gate_data, BiodefenseSafetyGate)
            else BiodefenseSafetyGate.from_dict(gate_data if isinstance(gate_data, dict) else {})
        )

        return cls(
            therapy_id=str(data.get("therapy_id", data.get("name", "phage_therapy_01"))),
            target_pathogen=str(data.get("target_pathogen", "UNKNOWN_PATHOGEN")),
            model=str(data.get("model", "omnii-1")),
            modalities=list(data.get("modalities", ["DNA_GENOME", "COAT_PROTEIN_STRUCTURE"])),
            capsid_architecture=arch_enum,
            host_range_expansion=bool(data.get("host_range_expansion", True)),
            receptor_binding_fiber_ref=str(data["receptor_binding_fiber_ref"])
            if "receptor_binding_fiber_ref" in data
            else None,
            biodefense_gate=gate,
            compassionate_use_approved=bool(data.get("compassionate_use_approved", True)),
            target_cfu_reduction_log10=float(data.get("target_cfu_reduction_log10", 6.0)),
        )


class PerturbationType(str, Enum):
    """Experimental or in silico biological perturbation modality."""

    CRISPR_KNOCKOUT = "crispr_knockout"
    CRISPR_INHIBITION = "crispr_inhibition"
    CRISPR_ACTIVATION = "crispr_activation"
    SMALL_MOLECULE_INHIBITION = "small_molecule_inhibition"
    BASE_EDITING = "base_editing"
    PRIME_EDITING = "prime_editing"
    OVEREXPRESSION = "overexpression"

    def __str__(self) -> str:
        return self.value


class CellAtlasReference(str, Enum):
    """Canonical open cellular and developmental atlas repositories (Virtual Biology Initiative)."""

    TABULA_SAPIENS = "tabula_sapiens"
    CELLXGENE = "cellxgene"
    ZEBRAHUB = "zebrahub"
    HUMAN_CELL_ATLAS = "human_cell_atlas"
    CUSTOM_ATLAS = "custom_atlas"
    SHI_BRAIN_PERTURB_SEQ = "shi_brain_perturb_seq"
    PERTURBAI_BRAIN_ATLAS = "perturbai_brain_atlas"

    def __str__(self) -> str:
        return self.value


@dataclass
class PerturbationReadout:
    """Quantitative single-cell and phenotypic endpoints for in silico perturbation predictions."""

    max_transcriptome_cosine_distance: float = 0.15  # Transcriptomic divergence threshold
    min_survival_probability: float = 0.85  # Predicted cell viability fraction
    mitochondrial_potential_retention: float = 0.90  # Metabolic and organellar integrity
    off_target_pathway_disruption: float = 0.05  # Maximum permissible uncalibrated collateral disruption

    def satisfies_phenotype_gate(
        self,
        observed_cosine_distance: float,
        observed_survival: float,
        observed_mito_retention: float,
        observed_off_target: float,
    ) -> bool:
        """Evaluate if in silico perturbed cell state satisfies therapeutic criteria without toxic collapse."""
        return (
            observed_cosine_distance <= self.max_transcriptome_cosine_distance
            and observed_survival >= self.min_survival_probability
            and observed_mito_retention >= self.mitochondrial_potential_retention
            and observed_off_target <= self.off_target_pathway_disruption
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "max_transcriptome_cosine_distance": self.max_transcriptome_cosine_distance,
            "min_survival_probability": self.min_survival_probability,
            "mitochondrial_potential_retention": self.mitochondrial_potential_retention,
            "off_target_pathway_disruption": self.off_target_pathway_disruption,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerturbationReadout:
        """Instantiate PerturbationReadout from dictionary."""
        return cls(
            max_transcriptome_cosine_distance=float(data.get("max_transcriptome_cosine_distance", 0.15)),
            min_survival_probability=float(data.get("min_survival_probability", 0.85)),
            mitochondrial_potential_retention=float(data.get("mitochondrial_potential_retention", 0.90)),
            off_target_pathway_disruption=float(data.get("off_target_pathway_disruption", 0.05)),
        )


@dataclass
class VirtualCellPerturbationContract:
    """Formal GFL IO Contract for Whole-Cell In Silico Perturbation and Virtual Biology.

    Grounded in the $1.8B Virtual Biology Initiative (CZ Biohub, DOE, NIH, Google DeepMind,
    Isomorphic Labs, Meta, 2026; Tabula Sapiens, CELLxGENE, Zebrahub):
    - Replaces isolated single-protein models with digital cellular experiments predicting
      system-level responses to drug or genetic interventions before touching the wet lab.
    - Anchors predictions to open cell atlas foundations and verifies viability/phenotypic retention.
    """

    simulation_id: str
    cell_type: str  # e.g., "human_cortical_neuron", "striatal_msn", "hepatocyte"
    target_gene_or_compound: str  # e.g., "MAPT", "SNCA", "Gcase_activator"
    perturbation_type: PerturbationType = PerturbationType.CRISPR_INHIBITION
    atlas_ref: CellAtlasReference = CellAtlasReference.TABULA_SAPIENS
    dose_or_fold_change: float = 0.20  # e.g., 0.20 = 80% knockdown
    readout: PerturbationReadout = field(default_factory=PerturbationReadout)
    engine: str = "virtual-cell-foundation-1"
    wet_lab_clearance: bool = True
    tissue_context: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "simulation_id": self.simulation_id,
            "cell_type": self.cell_type,
            "target_gene_or_compound": self.target_gene_or_compound,
            "perturbation_type": str(self.perturbation_type),
            "atlas_ref": str(self.atlas_ref),
            "dose_or_fold_change": self.dose_or_fold_change,
            "readout": self.readout.to_dict(),
            "engine": self.engine,
            "wet_lab_clearance": self.wet_lab_clearance,
        }
        if self.tissue_context:
            res["tissue_context"] = self.tissue_context
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VirtualCellPerturbationContract:
        """Instantiate VirtualCellPerturbationContract from dictionary."""
        pt_val = data.get("perturbation_type", PerturbationType.CRISPR_INHIBITION)
        try:
            pt_enum = PerturbationType(str(pt_val).lower())
        except ValueError:
            pt_enum = PerturbationType.CRISPR_INHIBITION

        atlas_val = data.get("atlas_ref", CellAtlasReference.TABULA_SAPIENS)
        try:
            atlas_enum = CellAtlasReference(str(atlas_val).lower())
        except ValueError:
            atlas_enum = CellAtlasReference.TABULA_SAPIENS

        readout_data = data.get("readout", {})
        readout = (
            readout_data
            if isinstance(readout_data, PerturbationReadout)
            else PerturbationReadout.from_dict(readout_data if isinstance(readout_data, dict) else {})
        )

        return cls(
            simulation_id=str(data.get("simulation_id", data.get("name", "virtual_cell_sim_01"))),
            cell_type=str(data.get("cell_type", "human_cell")),
            target_gene_or_compound=str(data.get("target_gene_or_compound", "TARGET_GENE")),
            perturbation_type=pt_enum,
            atlas_ref=atlas_enum,
            dose_or_fold_change=float(data.get("dose_or_fold_change", 0.20)),
            readout=readout,
            engine=str(data.get("engine", "virtual-cell-foundation-1")),
            wet_lab_clearance=bool(data.get("wet_lab_clearance", True)),
            tissue_context=str(data["tissue_context"]) if "tissue_context" in data else None,
        )


# ============================================================================
# Distributed Biological Reasoning & Perturbation Screen Contracts (OpenAI / Scripps / PerturbAI)
# ============================================================================


class AtlasModality(str, Enum):
    """Experimental modality of high-throughput perturbation screen."""

    IN_VIVO_PERTURB_SEQ = "in_vivo_perturb_seq"
    SINGLE_CELL_CRISPR = "single_cell_crispr"
    PERTURB_CITE_SEQ = "perturb_cite_seq"
    OPTICAL_POOLED_SCREEN = "optical_pooled_screen"

    def __str__(self) -> str:
        return self.value


class SwarmGranularity(str, Enum):
    """Allocation granularity of autonomous AI reasoning agents across biological perturbations."""

    PER_PERTURBATION = "per_perturbation"
    PER_CELL_TYPE = "per_cell_type"
    HIERARCHICAL_CLUSTER = "hierarchical_cluster"

    def __str__(self) -> str:
        return self.value


class PhenotypicRelationshipType(str, Enum):
    """Epistemic relationship between perturbation outcomes in reasoning atlas."""

    SYNERGISTIC = "synergistic"
    OPPOSING = "opposing"
    NEUTRAL = "neutral"
    DIVERGENT = "divergent"

    def __str__(self) -> str:
        return self.value


@dataclass
class SwarmReasoningPolicy:
    """Policy governing distributed agent allocation and literature grounding (Sun et al., 2026)."""

    agent_granularity: SwarmGranularity = SwarmGranularity.PER_PERTURBATION
    literature_grounding: bool = True
    min_expert_preference_score: float = 0.75
    synthesis_aggregator: str = "reasoning_atlas"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agent_granularity": str(self.agent_granularity),
            "literature_grounding": self.literature_grounding,
            "min_expert_preference_score": self.min_expert_preference_score,
            "synthesis_aggregator": self.synthesis_aggregator,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SwarmReasoningPolicy:
        """Instantiate SwarmReasoningPolicy from dictionary."""
        gran = data.get("agent_granularity", SwarmGranularity.PER_PERTURBATION)
        try:
            gran_enum = SwarmGranularity(str(gran).lower())
        except ValueError:
            gran_enum = SwarmGranularity.PER_PERTURBATION

        return cls(
            agent_granularity=gran_enum,
            literature_grounding=bool(data.get("literature_grounding", True)),
            min_expert_preference_score=float(data.get("min_expert_preference_score", 0.75)),
            synthesis_aggregator=str(data.get("synthesis_aggregator", "reasoning_atlas")),
        )


@dataclass
class ParalogDivergenceContract:
    """Formal contract evaluating phenotypic and transcriptional divergence between paralogous genes."""

    evaluate_paralog_opposition: bool = True
    pair: list[str] = field(default_factory=list)
    pairs: list[list[str]] = field(default_factory=list)
    min_transcriptional_divergence: float = 0.30

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "evaluate_paralog_opposition": self.evaluate_paralog_opposition,
            "min_transcriptional_divergence": self.min_transcriptional_divergence,
        }
        if self.pair:
            res["pair"] = list(self.pair)
        if self.pairs:
            res["pairs"] = [list(p) for p in self.pairs]
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParalogDivergenceContract:
        """Instantiate ParalogDivergenceContract from dictionary."""
        raw_pair = data.get("pair", [])
        pair = [str(g) for g in raw_pair] if isinstance(raw_pair, list) else []

        raw_pairs = data.get("pairs", [])
        pairs = []
        if isinstance(raw_pairs, list):
            for p in raw_pairs:
                if isinstance(p, list):
                    pairs.append([str(g) for g in p])

        if not pairs and pair:
            pairs = [pair]

        return cls(
            evaluate_paralog_opposition=bool(data.get("evaluate_paralog_opposition", True)),
            pair=pair,
            pairs=pairs,
            min_transcriptional_divergence=float(data.get("min_transcriptional_divergence", 0.30)),
        )


@dataclass
class PerturbationAtlasTarget:
    """Single genetic perturbation target within high-throughput screening atlas."""

    gene: str
    pathway_focus: str | None = None
    target_cell_types: list[str] = field(default_factory=list)
    expected_phenotype: str | None = None
    causal_transition_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "gene": self.gene,
            "target_cell_types": list(self.target_cell_types),
            "causal_transition_refs": list(self.causal_transition_refs),
        }
        if self.pathway_focus:
            res["pathway_focus"] = self.pathway_focus
        if self.expected_phenotype:
            res["expected_phenotype"] = self.expected_phenotype
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerturbationAtlasTarget:
        """Instantiate PerturbationAtlasTarget from dictionary."""
        raw_types = data.get("target_cell_types", [])
        cell_types = [str(ct) for ct in raw_types] if isinstance(raw_types, list) else []

        raw_refs = data.get("causal_transition_refs", [])
        refs = [str(r) for r in raw_refs] if isinstance(raw_refs, list) else []

        return cls(
            gene=str(data.get("gene", "")),
            pathway_focus=data.get("pathway_focus"),
            target_cell_types=cell_types,
            expected_phenotype=data.get("expected_phenotype"),
            causal_transition_refs=refs,
        )


@dataclass
class ReasoningAtlasEdge:
    """Causal and phenotypic relationship edge between perturbations in Reasoning Atlas."""

    source_gene: str
    target_gene: str
    relationship_type: PhenotypicRelationshipType
    confidence: float = 1.0
    literature_support: list[str] = field(default_factory=list)
    transcriptional_cosine_similarity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_gene": self.source_gene,
            "target_gene": self.target_gene,
            "relationship_type": str(self.relationship_type),
            "confidence": self.confidence,
            "literature_support": list(self.literature_support),
            "transcriptional_cosine_similarity": self.transcriptional_cosine_similarity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReasoningAtlasEdge:
        """Instantiate ReasoningAtlasEdge from dictionary."""
        rel = data.get("relationship_type", PhenotypicRelationshipType.NEUTRAL)
        try:
            rel_enum = PhenotypicRelationshipType(str(rel).lower())
        except ValueError:
            rel_enum = PhenotypicRelationshipType.NEUTRAL

        raw_lit = data.get("literature_support", [])
        lit = [str(x) for x in raw_lit] if isinstance(raw_lit, list) else []

        return cls(
            source_gene=str(data.get("source_gene", "")),
            target_gene=str(data.get("target_gene", "")),
            relationship_type=rel_enum,
            confidence=float(data.get("confidence", 1.0)),
            literature_support=lit,
            transcriptional_cosine_similarity=float(data.get("transcriptional_cosine_similarity", 0.0)),
        )


@dataclass
class ReasoningAtlasGraph:
    """Epistemic causality graph output generated by ReasoningAtlasCompiler."""

    atlas_name: str
    organism: str
    nodes: list[str] = field(default_factory=list)
    edges: list[ReasoningAtlasEdge] = field(default_factory=list)
    paralog_divergences: list[dict[str, Any]] = field(default_factory=list)
    causal_transitions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "atlas_name": self.atlas_name,
            "organism": self.organism,
            "nodes": list(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
            "paralog_divergences": self.paralog_divergences,
            "causal_transitions": self.causal_transitions,
            "metadata": self.metadata,
        }


@dataclass
class PerturbationAtlasContract:
    """Formal GFL IO Contract for High-Throughput In Vivo CRISPR Perturbation Screens.

    Grounded in Sun et al., 2026 (OpenAI, Scripps Research, PerturbAI) and Shi et al., 2026
    (Whole-Brain In Vivo Perturb-seq Atlas, 7.7M cells, 1,947 disease genes):
    - Deploys distributed biological reasoning swarms (1 agent per perturbation).
    - Detects paralog phenotypic dissonance (e.g., Grin2a vs Grin2b opposition).
    - Unifies cellular perturbation outcomes with causal disease transition graphs and virtual_cell simulations.
    """

    name: str
    organism: str = "Mus musculus"
    dataset_ref: str = "doi:10.64898/2026.10.15.759436v1"
    cell_atlas_size: int = 7700000
    modality: AtlasModality = AtlasModality.IN_VIVO_PERTURB_SEQ
    perturbation_targets: list[PerturbationAtlasTarget] = field(default_factory=list)
    swarm_policy: SwarmReasoningPolicy = field(default_factory=SwarmReasoningPolicy)
    divergence_check: ParalogDivergenceContract | None = None
    mcp_endpoint: str | None = None
    virtual_cell_link: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "name": self.name,
            "organism": self.organism,
            "dataset_ref": self.dataset_ref,
            "cell_atlas_size": self.cell_atlas_size,
            "modality": str(self.modality),
            "perturbation_targets": [t.to_dict() for t in self.perturbation_targets],
            "swarm_policy": self.swarm_policy.to_dict(),
        }
        if self.divergence_check:
            res["divergence_check"] = self.divergence_check.to_dict()
        if self.mcp_endpoint:
            res["mcp_endpoint"] = self.mcp_endpoint
        if self.virtual_cell_link:
            res["virtual_cell_link"] = self.virtual_cell_link
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PerturbationAtlasContract:
        """Instantiate PerturbationAtlasContract from dictionary."""
        mod_raw = data.get("modality", AtlasModality.IN_VIVO_PERTURB_SEQ)
        try:
            mod_enum = AtlasModality(str(mod_raw).lower())
        except ValueError:
            mod_enum = AtlasModality.IN_VIVO_PERTURB_SEQ

        raw_targets = data.get("perturbation_targets", [])
        targets = []
        if isinstance(raw_targets, list):
            for t in raw_targets:
                if isinstance(t, PerturbationAtlasTarget):
                    targets.append(t)
                elif isinstance(t, dict):
                    targets.append(PerturbationAtlasTarget.from_dict(t))

        raw_policy = data.get("swarm_policy", {})
        policy = (
            raw_policy
            if isinstance(raw_policy, SwarmReasoningPolicy)
            else SwarmReasoningPolicy.from_dict(raw_policy if isinstance(raw_policy, dict) else {})
        )

        div_raw = data.get("divergence_check", data.get("paralog_divergence"))
        divergence = None
        if div_raw:
            divergence = (
                div_raw
                if isinstance(div_raw, ParalogDivergenceContract)
                else ParalogDivergenceContract.from_dict(div_raw if isinstance(div_raw, dict) else {})
            )

        return cls(
            name=str(data.get("name", "whole_brain_crispr_screen")),
            organism=str(data.get("organism", "Mus musculus")),
            dataset_ref=str(data.get("dataset_ref", "doi:10.64898/2026.10.15.759436v1")),
            cell_atlas_size=int(data.get("cell_atlas_size", 7700000)),
            modality=mod_enum,
            perturbation_targets=targets,
            swarm_policy=policy,
            divergence_check=divergence,
            mcp_endpoint=data.get("mcp_endpoint"),
            virtual_cell_link=data.get("virtual_cell_link"),
        )


# ============================================================================
# SynthID Bio & Multimodal Biological Watermarking Contracts (Nature 2026; DeepMind)
# ============================================================================


class WatermarkModality(str, Enum):
    """Biological sequence or structural modality target for watermarking."""

    PROTEIN = "protein"
    MRNA = "mrna"
    CODING_DNA = "coding_dna"
    GENOMIC_DNA = "genomic_dna"
    MULTIMODAL = "multimodal"

    def __str__(self) -> str:
        return self.value


class WatermarkAlgorithm(str, Enum):
    """Cryptographic and statistical watermarking algorithms for biological sequences."""

    SYNTHID_GVALUE = "synthid_gvalue"
    SYNONYMOUS_CODON_HMAC = "synonymous_codon_hmac"
    KMER_PSEUDORANDOM = "kmer_pseudorandom"

    def __str__(self) -> str:
        return self.value


@dataclass
class WatermarkProvenance:
    """Institutional, provenance, and biosecurity metadata embedded in biological watermark."""

    institution: str = "Fundacion de Neurociencias"
    lab_id: str = "INVESTIGO_NEUROIA"
    generator_engine: str = "GeneForge-Rosalind"
    biosecurity_clearance: str = "passed_pathogen_screening"
    timestamp: str = ""
    signature_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "institution": self.institution,
            "lab_id": self.lab_id,
            "generator_engine": self.generator_engine,
            "biosecurity_clearance": self.biosecurity_clearance,
            "timestamp": self.timestamp,
            "signature_hash": self.signature_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WatermarkProvenance:
        return cls(
            institution=str(data.get("institution", "Fundacion de Neurociencias")),
            lab_id=str(data.get("lab_id", "INVESTIGO_NEUROIA")),
            generator_engine=str(data.get("generator_engine", "GeneForge-Rosalind")),
            biosecurity_clearance=str(data.get("biosecurity_clearance", "passed_pathogen_screening")),
            timestamp=str(data.get("timestamp", "")),
            signature_hash=str(data.get("signature_hash", "")),
        )


@dataclass
class WatermarkViabilityGuardrails:
    """Biophysical and biochemical constraints ensuring watermarking preserves biological function."""

    max_delta_delta_g: float = 0.50  # kcal/mol
    min_cai_score: float = 0.80  # Codon Adaptation Index
    preserve_amino_acid_sequence: bool = True  # 100% synonymous in coding DNA/mRNA
    avoid_splice_motifs: bool = True  # Avoid introducing cryptic splice donors/acceptors
    forbidden_motifs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_delta_delta_g": self.max_delta_delta_g,
            "min_cai_score": self.min_cai_score,
            "preserve_amino_acid_sequence": self.preserve_amino_acid_sequence,
            "avoid_splice_motifs": self.avoid_splice_motifs,
            "forbidden_motifs": list(self.forbidden_motifs),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WatermarkViabilityGuardrails:
        return cls(
            max_delta_delta_g=float(data.get("max_delta_delta_g", 0.50)),
            min_cai_score=float(data.get("min_cai_score", 0.80)),
            preserve_amino_acid_sequence=bool(data.get("preserve_amino_acid_sequence", True)),
            avoid_splice_motifs=bool(data.get("avoid_splice_motifs", True)),
            forbidden_motifs=list(data.get("forbidden_motifs", [])),
        )


@dataclass
class WatermarkDetectionPolicy:
    """Detection statistical thresholds and parameters for provenance verification."""

    min_z_score: float = 4.50
    green_list_fraction: float = 0.50
    context_kmer_size: int = 3
    significance_threshold_pvalue: float = 1e-5

    def to_dict(self) -> dict[str, Any]:
        return {
            "min_z_score": self.min_z_score,
            "green_list_fraction": self.green_list_fraction,
            "context_kmer_size": self.context_kmer_size,
            "significance_threshold_pvalue": self.significance_threshold_pvalue,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WatermarkDetectionPolicy:
        return cls(
            min_z_score=float(data.get("min_z_score", 4.50)),
            green_list_fraction=float(data.get("green_list_fraction", 0.50)),
            context_kmer_size=int(data.get("context_kmer_size", 3)),
            significance_threshold_pvalue=float(data.get("significance_threshold_pvalue", 1e-5)),
        )


@dataclass
class WatermarkVerificationResult:
    """Empirical detection result proving presence or absence of AI provenance watermark."""

    is_watermarked: bool
    g_value: float
    z_score: float
    p_value: float
    modality: WatermarkModality | str
    confidence_level: str
    extracted_provenance: dict[str, Any] = field(default_factory=dict)
    cai_score: float | None = None
    amino_acid_identity_preserved: bool | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_watermarked": self.is_watermarked,
            "g_value": self.g_value,
            "z_score": self.z_score,
            "p_value": self.p_value,
            "modality": str(self.modality),
            "confidence_level": self.confidence_level,
            "extracted_provenance": dict(self.extracted_provenance),
            "cai_score": self.cai_score,
            "amino_acid_identity_preserved": self.amino_acid_identity_preserved,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WatermarkVerificationResult:
        mod_raw = data.get("modality", WatermarkModality.PROTEIN)
        mod = mod_raw if isinstance(mod_raw, WatermarkModality) else WatermarkModality(str(mod_raw))
        return cls(
            is_watermarked=bool(data.get("is_watermarked", False)),
            g_value=float(data.get("g_value", 0.50)),
            z_score=float(data.get("z_score", 0.0)),
            p_value=float(data.get("p_value", 1.0)),
            modality=mod,
            confidence_level=str(data.get("confidence_level", "NATURAL_OR_UNWATERMARKED")),
            extracted_provenance=dict(data.get("extracted_provenance", {})),
            cai_score=float(data["cai_score"]) if data.get("cai_score") is not None else None,
            amino_acid_identity_preserved=(
                bool(data["amino_acid_identity_preserved"])
                if data.get("amino_acid_identity_preserved") is not None
                else None
            ),
            notes=str(data.get("notes", "")),
        )


@dataclass
class BiosecurityWatermarkContract:
    """Formal GFL contract for SynthID Bio and multimodal biological watermarking."""

    name: str
    target_modality: WatermarkModality = WatermarkModality.PROTEIN
    algorithm: WatermarkAlgorithm = WatermarkAlgorithm.SYNTHID_GVALUE
    provenance: WatermarkProvenance = field(default_factory=WatermarkProvenance)
    viability_guardrails: WatermarkViabilityGuardrails = field(default_factory=WatermarkViabilityGuardrails)
    detection_policy: WatermarkDetectionPolicy = field(default_factory=WatermarkDetectionPolicy)
    security_key_ref: str | None = None
    sequence_payload: str | None = None
    verified_result: WatermarkVerificationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_modality": str(self.target_modality),
            "algorithm": str(self.algorithm),
            "provenance": self.provenance.to_dict(),
            "viability_guardrails": self.viability_guardrails.to_dict(),
            "detection_policy": self.detection_policy.to_dict(),
            "security_key_ref": self.security_key_ref,
            "sequence_payload": self.sequence_payload,
            "verified_result": self.verified_result.to_dict() if self.verified_result else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BiosecurityWatermarkContract:
        mod_raw = data.get("target_modality", data.get("modality", WatermarkModality.PROTEIN))
        mod_enum = mod_raw if isinstance(mod_raw, WatermarkModality) else WatermarkModality(str(mod_raw).lower())

        alg_raw = data.get("algorithm", data.get("watermark_algorithm", WatermarkAlgorithm.SYNTHID_GVALUE))
        alg_enum = alg_raw if isinstance(alg_raw, WatermarkAlgorithm) else WatermarkAlgorithm(str(alg_raw).lower())

        raw_prov = data.get("provenance", {})
        prov = (
            raw_prov
            if isinstance(raw_prov, WatermarkProvenance)
            else WatermarkProvenance.from_dict(raw_prov if isinstance(raw_prov, dict) else {})
        )

        raw_guard = data.get("viability_guardrails", data.get("guardrails", {}))
        guard = (
            raw_guard
            if isinstance(raw_guard, WatermarkViabilityGuardrails)
            else WatermarkViabilityGuardrails.from_dict(raw_guard if isinstance(raw_guard, dict) else {})
        )

        raw_pol = data.get("detection_policy", data.get("policy", {}))
        pol = (
            raw_pol
            if isinstance(raw_pol, WatermarkDetectionPolicy)
            else WatermarkDetectionPolicy.from_dict(raw_pol if isinstance(raw_pol, dict) else {})
        )

        raw_res = data.get("verified_result")
        res = None
        if raw_res:
            res = (
                raw_res
                if isinstance(raw_res, WatermarkVerificationResult)
                else WatermarkVerificationResult.from_dict(raw_res if isinstance(raw_res, dict) else {})
            )

        return cls(
            name=str(data.get("name", "biosecurity_watermark")),
            target_modality=mod_enum,
            algorithm=alg_enum,
            provenance=prov,
            viability_guardrails=guard,
            detection_policy=pol,
            security_key_ref=data.get("security_key_ref"),
            sequence_payload=data.get("sequence_payload"),
            verified_result=res,
            metadata=dict(data.get("metadata", {})),
        )


class CarbonXTaskType(str, Enum):
    """Supported reasoning and generative task types for Carbon-X."""

    VARIANT_EFFECT_REASONING = "variant_effect_reasoning"
    LOCUS_ANNOTATION = "locus_annotation"
    PROMOTER_GENERATION = "promoter_generation"
    PATHWAY_IMPACT = "pathway_impact"
    CHAT_WITH_DNA = "chat_with_dna"


class CarbonXModelSize(str, Enum):
    """Carbon-X model checkpoints."""

    CARBONX_14B = "carbonx-14b"
    CARBONX_BASE = "carbonx-base"


@dataclass
class CarbonXTargetLocus:
    """Genomic locus coordinate specification."""

    chrom: str = "chr1"
    start: int = 0
    end: int = 0
    strand: str = "+"
    assembly: str = "GRCh38"
    gene_symbol: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chrom": self.chrom,
            "start": self.start,
            "end": self.end,
            "strand": self.strand,
            "assembly": self.assembly,
            "gene_symbol": self.gene_symbol,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CarbonXTargetLocus:
        return cls(
            chrom=str(data.get("chrom", data.get("chr", "chr1"))),
            start=int(data.get("start", 0)),
            end=int(data.get("end", 0)),
            strand=str(data.get("strand", "+")),
            assembly=str(data.get("assembly", "GRCh38")),
            gene_symbol=str(data["gene_symbol"]) if "gene_symbol" in data and data["gene_symbol"] is not None else None,
        )


@dataclass
class CarbonXQuery:
    """Prompt and query configuration for Carbon-X."""

    prompt: str
    task_type: CarbonXTaskType = CarbonXTaskType.VARIANT_EFFECT_REASONING
    sequence: str | None = None
    locus: CarbonXTargetLocus | None = None
    variant_delta: dict[str, Any] | None = None
    max_new_tokens: int = 1024
    temperature: float = 0.2
    system_prompt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "task_type": self.task_type.value if hasattr(self.task_type, "value") else str(self.task_type),
            "sequence": self.sequence,
            "locus": self.locus.to_dict() if self.locus else None,
            "variant_delta": self.variant_delta,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CarbonXQuery:
        task_raw = data.get("task_type", CarbonXTaskType.VARIANT_EFFECT_REASONING)
        if isinstance(task_raw, CarbonXTaskType):
            task_enum = task_raw
        else:
            s_task = str(task_raw).lower()
            if "." in s_task:
                s_task = s_task.split(".")[-1]
            task_enum = CarbonXTaskType(s_task)

        locus_raw = data.get("locus")
        locus = None
        if locus_raw:
            locus = locus_raw if isinstance(locus_raw, CarbonXTargetLocus) else CarbonXTargetLocus.from_dict(locus_raw)

        return cls(
            prompt=str(data.get("prompt", "")),
            task_type=task_enum,
            sequence=data.get("sequence"),
            locus=locus,
            variant_delta=data.get("variant_delta"),
            max_new_tokens=int(data.get("max_new_tokens", 1024)),
            temperature=float(data.get("temperature", 0.2)),
            system_prompt=data.get("system_prompt"),
        )


@dataclass
class CarbonXReasoningResult:
    """Structured scientific explanation and predictions generated by Carbon-X."""

    explanation: str
    predicted_effects: list[str] = field(default_factory=list)
    functional_consequences: list[str] = field(default_factory=list)
    confidence_score: float = 0.85
    token_count_dna: int = 0
    token_count_text: int = 0
    evidence_status: str = "carbonx_inference"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "explanation": self.explanation,
            "predicted_effects": list(self.predicted_effects),
            "functional_consequences": list(self.functional_consequences),
            "confidence_score": self.confidence_score,
            "token_count_dna": self.token_count_dna,
            "token_count_text": self.token_count_text,
            "evidence_status": self.evidence_status,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CarbonXReasoningResult:
        return cls(
            explanation=str(data.get("explanation", "")),
            predicted_effects=list(data.get("predicted_effects", [])),
            functional_consequences=list(data.get("functional_consequences", [])),
            confidence_score=float(data.get("confidence_score", 0.85)),
            token_count_dna=int(data.get("token_count_dna", 0)),
            token_count_text=int(data.get("token_count_text", 0)),
            evidence_status=str(data.get("evidence_status", "carbonx_inference")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class GenomicLLMContract:
    """Formal GFL contract for Carbon-X and genomic foundation language models."""

    name: str
    model: CarbonXModelSize = CarbonXModelSize.CARBONX_14B
    task_type: CarbonXTaskType = CarbonXTaskType.VARIANT_EFFECT_REASONING
    query: CarbonXQuery | None = None
    target_locus: CarbonXTargetLocus | None = None
    sequence_payload: str | None = None
    max_context_tokens: int = 40960
    temperature: float = 0.2
    verified_result: CarbonXReasoningResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model.value if hasattr(self.model, "value") else str(self.model),
            "task_type": self.task_type.value if hasattr(self.task_type, "value") else str(self.task_type),
            "query": self.query.to_dict() if self.query else None,
            "target_locus": self.target_locus.to_dict() if self.target_locus else None,
            "sequence_payload": self.sequence_payload,
            "max_context_tokens": self.max_context_tokens,
            "temperature": self.temperature,
            "verified_result": self.verified_result.to_dict() if self.verified_result else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GenomicLLMContract:
        mod_raw = data.get("model", CarbonXModelSize.CARBONX_14B)
        if isinstance(mod_raw, CarbonXModelSize):
            mod_enum = mod_raw
        else:
            s_mod = str(mod_raw).lower()
            if "." in s_mod:
                s_mod = s_mod.split(".")[-1]
            mod_enum = CarbonXModelSize(s_mod)

        task_raw = data.get("task_type", CarbonXTaskType.VARIANT_EFFECT_REASONING)
        if isinstance(task_raw, CarbonXTaskType):
            task_enum = task_raw
        else:
            s_task = str(task_raw).lower()
            if "." in s_task:
                s_task = s_task.split(".")[-1]
            task_enum = CarbonXTaskType(s_task)

        query_raw = data.get("query")
        query = None
        if query_raw:
            query = query_raw if isinstance(query_raw, CarbonXQuery) else CarbonXQuery.from_dict(query_raw)

        locus_raw = data.get("target_locus", data.get("locus"))
        locus = None
        if locus_raw:
            locus = locus_raw if isinstance(locus_raw, CarbonXTargetLocus) else CarbonXTargetLocus.from_dict(locus_raw)

        res_raw = data.get("verified_result", data.get("reasoning_result"))
        res = None
        if res_raw:
            res = res_raw if isinstance(res_raw, CarbonXReasoningResult) else CarbonXReasoningResult.from_dict(res_raw)

        return cls(
            name=str(data.get("name", "genomic_llm_analysis")),
            model=mod_enum,
            task_type=task_enum,
            query=query,
            target_locus=locus,
            sequence_payload=data.get("sequence_payload", data.get("sequence")),
            max_context_tokens=int(data.get("max_context_tokens", 40960)),
            temperature=float(data.get("temperature", 0.2)),
            verified_result=res,
            metadata=dict(data.get("metadata", {})),
        )


class ProTokModality(str, Enum):
    """Biological modalities unified by the ProTok discrete vocabulary."""

    SEQUENCE = "sequence"
    STRUCTURE = "structure"
    FUNCTION = "function"
    TRIMODAL = "trimodal"


class ProTokConditioningMode(str, Enum):
    """Conditioning directionalities supported by ProTok Codebook Group Dropout."""

    UNCONDITIONAL = "unconditional"
    SEQUENCE_TO_STRUCTURE = "sequence_to_structure"
    STRUCTURE_TO_FUNCTION = "structure_to_function"
    FUNCTION_TO_ALL = "function_to_all"
    SEQUENCE_TO_FUNCTION = "sequence_to_function"


@dataclass
class ProTokResidueToken:
    """Unified composite token representing a single residue across sequence, structure, and function."""

    pos: int
    amino_acid: str = "A"
    structure_code: int = 0  # Geometric codebook index (0..511)
    function_code: int = 0  # Functional codebook index (0..255)
    dihedral_phi: float | None = None
    dihedral_psi: float | None = None
    ec_classification: str | None = None
    go_term: str | None = None
    composite_token_id: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "pos": self.pos,
            "amino_acid": self.amino_acid,
            "structure_code": self.structure_code,
            "function_code": self.function_code,
            "dihedral_phi": self.dihedral_phi,
            "dihedral_psi": self.dihedral_psi,
            "ec_classification": self.ec_classification,
            "go_term": self.go_term,
            "composite_token_id": self.composite_token_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProTokResidueToken:
        return cls(
            pos=int(data.get("pos", 1)),
            amino_acid=str(data.get("amino_acid", "A")),
            structure_code=int(data.get("structure_code", 0)),
            function_code=int(data.get("function_code", 0)),
            dihedral_phi=float(data["dihedral_phi"])
            if "dihedral_phi" in data and data["dihedral_phi"] is not None
            else None,
            dihedral_psi=float(data["dihedral_psi"])
            if "dihedral_psi" in data and data["dihedral_psi"] is not None
            else None,
            ec_classification=str(data["ec_classification"])
            if "ec_classification" in data and data["ec_classification"] is not None
            else None,
            go_term=str(data["go_term"]) if "go_term" in data and data["go_term"] is not None else None,
            composite_token_id=int(data.get("composite_token_id", 0)),
        )


@dataclass
class ProTokDropoutPolicy:
    """Codebook Group Dropout parameters allowing inference from any modality subset."""

    allow_missing_sequence: bool = False
    allow_missing_structure: bool = False
    allow_missing_function: bool = True
    dropout_rate: float = 0.15

    def to_dict(self) -> dict[str, Any]:
        return {
            "allow_missing_sequence": self.allow_missing_sequence,
            "allow_missing_structure": self.allow_missing_structure,
            "allow_missing_function": self.allow_missing_function,
            "dropout_rate": self.dropout_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProTokDropoutPolicy:
        return cls(
            allow_missing_sequence=bool(data.get("allow_missing_sequence", False)),
            allow_missing_structure=bool(data.get("allow_missing_structure", False)),
            allow_missing_function=bool(data.get("allow_missing_function", True)),
            dropout_rate=float(data.get("dropout_rate", 0.15)),
        )


@dataclass
class ProTokVerificationResult:
    """Biophysical and downstream performance evaluation metrics for ProTok."""

    reconstructed_lddt: float = 0.939  # Baseline CATH 4.2 lDDT
    ec_top1_precision: float = 0.695  # Baseline EC level 1 top-1 retrieval precision
    recovered_modalities: list[str] = field(default_factory=list)
    designability_score: float = 0.52  # Baseline backbone designability
    token_count: int = 0
    evidence_status: str = "protok_reconstruction_verified"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reconstructed_lddt": self.reconstructed_lddt,
            "ec_top1_precision": self.ec_top1_precision,
            "recovered_modalities": list(self.recovered_modalities),
            "designability_score": self.designability_score,
            "token_count": self.token_count,
            "evidence_status": self.evidence_status,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProTokVerificationResult:
        return cls(
            reconstructed_lddt=float(data.get("reconstructed_lddt", 0.939)),
            ec_top1_precision=float(data.get("ec_top1_precision", 0.695)),
            recovered_modalities=list(data.get("recovered_modalities", [])),
            designability_score=float(data.get("designability_score", 0.52)),
            token_count=int(data.get("token_count", 0)),
            evidence_status=str(data.get("evidence_status", "protok_reconstruction_verified")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ProTokContract:
    """Formal GFL contract for ProTok unified multimodal residue token stream."""

    name: str
    target_protein: str | None = None
    conditioning_mode: ProTokConditioningMode = ProTokConditioningMode.STRUCTURE_TO_FUNCTION
    target_modality: ProTokModality = ProTokModality.TRIMODAL
    dropout_policy: ProTokDropoutPolicy = field(default_factory=ProTokDropoutPolicy)
    residue_stream: list[ProTokResidueToken] = field(default_factory=list)
    sequence_payload: str | None = None
    target_ec_classification: str | None = None
    target_go_terms: list[str] = field(default_factory=list)
    expected_lddt_min: float = 0.90
    verified_result: ProTokVerificationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_protein": self.target_protein,
            "conditioning_mode": self.conditioning_mode.value
            if hasattr(self.conditioning_mode, "value")
            else str(self.conditioning_mode),
            "target_modality": self.target_modality.value
            if hasattr(self.target_modality, "value")
            else str(self.target_modality),
            "dropout_policy": self.dropout_policy.to_dict(),
            "residue_stream": [t.to_dict() for t in self.residue_stream],
            "sequence_payload": self.sequence_payload,
            "target_ec_classification": self.target_ec_classification,
            "target_go_terms": list(self.target_go_terms),
            "expected_lddt_min": self.expected_lddt_min,
            "verified_result": self.verified_result.to_dict() if self.verified_result else None,
            "metadata": dict(self.metadata),
        }

    def to_ontrack_payload(self) -> dict[str, Any]:
        """Export serialized contract payload for GeneForge OnTrack execution (ADR-ARCH-001)."""
        return {
            "contract_type": "protok_multimodal_stream",
            "name": self.name,
            "target_protein": self.target_protein,
            "conditioning_mode": self.conditioning_mode.value
            if hasattr(self.conditioning_mode, "value")
            else str(self.conditioning_mode),
            "target_modality": self.target_modality.value
            if hasattr(self.target_modality, "value")
            else str(self.target_modality),
            "dropout_policy": self.dropout_policy.to_dict(),
            "sequence_payload": self.sequence_payload,
            "target_ec_classification": self.target_ec_classification,
            "target_go_terms": list(self.target_go_terms),
            "expected_lddt_min": self.expected_lddt_min,
            "token_ids": [t.composite_token_id for t in self.residue_stream if t.composite_token_id is not None],
            "raw_stream": [t.to_dict() for t in self.residue_stream],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProTokContract:
        cond_raw = data.get("conditioning_mode", ProTokConditioningMode.STRUCTURE_TO_FUNCTION)
        if isinstance(cond_raw, ProTokConditioningMode):
            cond_enum = cond_raw
        else:
            s_cond = str(cond_raw).lower()
            if "." in s_cond:
                s_cond = s_cond.split(".")[-1]
            cond_enum = ProTokConditioningMode(s_cond)

        mod_raw = data.get("target_modality", ProTokModality.TRIMODAL)
        if isinstance(mod_raw, ProTokModality):
            mod_enum = mod_raw
        else:
            s_mod = str(mod_raw).lower()
            if "." in s_mod:
                s_mod = s_mod.split(".")[-1]
            mod_enum = ProTokModality(s_mod)

        dp_raw = data.get("dropout_policy", {})
        dp = (
            dp_raw
            if isinstance(dp_raw, ProTokDropoutPolicy)
            else ProTokDropoutPolicy.from_dict(dp_raw if isinstance(dp_raw, dict) else {})
        )

        stream_raw = data.get("residue_stream", [])
        stream = [t if isinstance(t, ProTokResidueToken) else ProTokResidueToken.from_dict(t) for t in stream_raw]

        res_raw = data.get("verified_result")
        res = (
            res_raw
            if isinstance(res_raw, ProTokVerificationResult)
            else ProTokVerificationResult.from_dict(res_raw)
            if isinstance(res_raw, dict)
            else None
        )

        return cls(
            name=str(data.get("name", "protok_analysis")),
            target_protein=str(data["target_protein"])
            if "target_protein" in data and data["target_protein"] is not None
            else None,
            conditioning_mode=cond_enum,
            target_modality=mod_enum,
            dropout_policy=dp,
            residue_stream=stream,
            sequence_payload=data.get("sequence_payload", data.get("sequence")),
            target_ec_classification=data.get("target_ec_classification"),
            target_go_terms=list(data.get("target_go_terms", [])),
            expected_lddt_min=float(data.get("expected_lddt_min", 0.90)),
            verified_result=res,
            metadata=dict(data.get("metadata", {})),
        )


class ForceFieldFamily(str, Enum):
    """Molecular mechanics all-atom force field families."""

    AMBER_FF14SB = "amber_ff14sb"
    AMBER_FF19SB = "amber_ff19sb"
    CHARMM36M = "charmm36m"
    OPLS_AA = "opls_aa"

    def __str__(self) -> str:
        return self.value


class SimulationEngine(str, Enum):
    """Computational molecular dynamics and mechanics engines."""

    GROMACS = "gromacs"
    AMBER = "amber"
    OPENMM = "openmm"
    NAMD = "namd"

    def __str__(self) -> str:
        return self.value


class WaterModel(str, Enum):
    """Explicit solvent water models for biomolecular simulation."""

    OPC = "opc"  # 4-point optimal point charge water (recommended for ff19SB)
    OPC3 = "opc3"  # 3-point optimal point charge water
    TIP3P = "tip3p"  # Standard 3-point water
    TIP4P_EW = "tip4p_ew"
    TIP4P_D = "tip4p_d"  # Dispersion-corrected water for IDPs

    def __str__(self) -> str:
        return self.value


@dataclass
class InterEngineEnergyTolerance:
    """Rigorous inter-engine potential energy and force consistency standards.

    Grounded in Miletić, Wieczór, Simmerling et al. (JCTC / ChemRxiv 2024/2026):
    - Validates static potential energy equivalence across independent MD engines (e.g. GROMACS vs Amber).
    - Checks amino-acid-specific CMAP corrections, improper dihedral atom ordering,
      and 1-4 electrostatic (0.8333) and van der Waals (0.5) scaling factors.
    """

    max_potential_energy_delta_kj_mol: float = 1e-6  # Ground truth static interaction energy tolerance
    max_force_delta_kj_mol_nm: float = 1e-4  # Ground truth atomic force tolerance
    audit_improper_dihedral_ordering: bool = True  # Strict atom sequence check to prevent chiral inversion
    audit_cmap_residue_spec: bool = True  # 2D phi/psi grid specific to each of the 20 amino acids
    electrostatic_14_scale: float = 0.8333333  # Amber standard 1/1.2 electrostatic 1-4 scaling
    vdw_14_scale: float = 0.5000000  # Amber standard 1/2.0 van der Waals 1-4 scaling

    def satisfies_inter_engine_portability(
        self,
        observed_energy_delta: float,
        observed_force_delta: float,
        improper_ordering_valid: bool = True,
        cmap_spec_valid: bool = True,
    ) -> bool:
        """Evaluate if cross-engine topology translation preserves bitwise energetic equivalence."""
        if observed_energy_delta > self.max_potential_energy_delta_kj_mol:
            return False
        if observed_force_delta > self.max_force_delta_kj_mol_nm:
            return False
        if self.audit_improper_dihedral_ordering and not improper_ordering_valid:
            return False
        return not (self.audit_cmap_residue_spec and not cmap_spec_valid)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "max_potential_energy_delta_kj_mol": self.max_potential_energy_delta_kj_mol,
            "max_force_delta_kj_mol_nm": self.max_force_delta_kj_mol_nm,
            "audit_improper_dihedral_ordering": self.audit_improper_dihedral_ordering,
            "audit_cmap_residue_spec": self.audit_cmap_residue_spec,
            "electrostatic_14_scale": self.electrostatic_14_scale,
            "vdw_14_scale": self.vdw_14_scale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterEngineEnergyTolerance:
        """Instantiate InterEngineEnergyTolerance from dictionary."""
        return cls(
            max_potential_energy_delta_kj_mol=float(data.get("max_potential_energy_delta_kj_mol", 1e-6)),
            max_force_delta_kj_mol_nm=float(data.get("max_force_delta_kj_mol_nm", 1e-4)),
            audit_improper_dihedral_ordering=bool(data.get("audit_improper_dihedral_ordering", True)),
            audit_cmap_residue_spec=bool(data.get("audit_cmap_residue_spec", True)),
            electrostatic_14_scale=float(data.get("electrostatic_14_scale", 0.8333333)),
            vdw_14_scale=float(data.get("vdw_14_scale", 0.5)),
        )


@dataclass
class ForceFieldEngineContract:
    """Formal GFL IO Contract for Force Field Engine Portability and CMAP/Improper Validation.

    Guarantees that a molecular topology parameterized in Amber (prmtop/inpcrd) or GROMACS (top/gro)
    yields identical potential energy landscapes and forces without engine-dependent parameter drift.
    """

    contract_id: str
    force_field: ForceFieldFamily = ForceFieldFamily.AMBER_FF19SB
    primary_engine: SimulationEngine = SimulationEngine.GROMACS
    reference_engine: SimulationEngine = SimulationEngine.AMBER
    water_model: WaterModel = WaterModel.OPC
    energy_tolerance: InterEngineEnergyTolerance = field(default_factory=InterEngineEnergyTolerance)
    verified_portability: bool = True
    target_structure_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "contract_id": self.contract_id,
            "force_field": str(self.force_field),
            "primary_engine": str(self.primary_engine),
            "reference_engine": str(self.reference_engine),
            "water_model": str(self.water_model),
            "energy_tolerance": self.energy_tolerance.to_dict(),
            "verified_portability": self.verified_portability,
        }
        if self.target_structure_ref:
            res["target_structure_ref"] = self.target_structure_ref
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ForceFieldEngineContract:
        """Instantiate ForceFieldEngineContract from dictionary."""
        ff_val = data.get("force_field", ForceFieldFamily.AMBER_FF19SB)
        try:
            ff_enum = ForceFieldFamily(str(ff_val).lower())
        except ValueError:
            ff_enum = ForceFieldFamily.AMBER_FF19SB

        pe_val = data.get("primary_engine", SimulationEngine.GROMACS)
        try:
            pe_enum = SimulationEngine(str(pe_val).lower())
        except ValueError:
            pe_enum = SimulationEngine.GROMACS

        re_val = data.get("reference_engine", SimulationEngine.AMBER)
        try:
            re_enum = SimulationEngine(str(re_val).lower())
        except ValueError:
            re_enum = SimulationEngine.AMBER

        wm_val = data.get("water_model", WaterModel.OPC)
        try:
            wm_enum = WaterModel(str(wm_val).lower())
        except ValueError:
            wm_enum = WaterModel.OPC

        tol_data = data.get("energy_tolerance", {})
        tol = (
            tol_data
            if isinstance(tol_data, InterEngineEnergyTolerance)
            else InterEngineEnergyTolerance.from_dict(tol_data if isinstance(tol_data, dict) else {})
        )

        return cls(
            contract_id=str(data.get("contract_id", data.get("name", "ff_portability_01"))),
            force_field=ff_enum,
            primary_engine=pe_enum,
            reference_engine=re_enum,
            water_model=wm_enum,
            energy_tolerance=tol,
            verified_portability=bool(data.get("verified_portability", True)),
            target_structure_ref=str(data["target_structure_ref"]) if "target_structure_ref" in data else None,
        )


class HelixConformation(str, Enum):
    """Canonical nucleic acid double helix conformations."""

    B_DNA = "b_dna"  # Canonical Watson-Crick right-handed B-DNA (10-10.5 bp/turn, pitch 3.4 nm, rise 0.34 nm)
    A_DNA = "a_dna"  # Compact right-handed A-form (11 bp/turn, dehydrated or RNA-DNA hybrid)
    Z_DNA = "z_dna"  # Left-handed zig-zag Z-form (12 bp/turn, alternating purine-pyrimidine tracts)

    def __str__(self) -> str:
        return self.value


class ViewerTrackType(str, Enum):
    """Modular genomic visualization and multi-omic overlay tracks."""

    EXONS = "exons"  # Exon/intron boundaries, splice donor (GT) and acceptor (AG) junctions
    READING_FRAMES = "reading_frames"  # Codon triplet groupings, 3-frame translation, frameshift alerts
    CLINVAR_VARIANTS = "clinvar_variants"  # Pathogenic, likely pathogenic, and VUS variant pins
    EPIGENETICS_5HMC = "epigenetics_5hmc"  # 5hmC and 5mC methylation marks and modification probabilities
    CRISPR_PAM_SITES = "crispr_pam_sites"  # SpCas9 NGG, Cas12a TTTV PAM recognition and guide RNA target windows
    SOMATIC_REPEAT_EXPANSION = (
        "somatic_repeat_expansion"  # Tandem microsatellite repeat count and instability threshold
    )

    def __str__(self) -> str:
        return self.value


class VariantPathogenicity(str, Enum):
    """ACMG/AMP clinical pathogenicity classifications."""

    PATHOGENIC = "pathogenic"
    LIKELY_PATHOGENIC = "likely_pathogenic"
    UNCERTAIN_SIGNIFICANCE = "uncertain_significance"
    LIKELY_BENIGN = "likely_benign"
    BENIGN = "benign"

    def __str__(self) -> str:
        return self.value


@dataclass
class ViewerVariantAnnotation:
    """Clinical or population variant mapped to exact genomic/transcript coordinates."""

    coordinate: int
    ref_allele: str
    alt_allele: str
    variant_id: str
    pathogenicity: VariantPathogenicity = VariantPathogenicity.PATHOGENIC
    molecular_consequence: str = "missense"  # missense, nonsense, frameshift, splice_donor, inframe_deletion
    clinical_significance: str = "Pathogenic"
    condition: str = "Muscular Dystrophy"
    hgvs_c: str | None = None
    hgvs_p: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "coordinate": self.coordinate,
            "ref_allele": self.ref_allele,
            "alt_allele": self.alt_allele,
            "variant_id": self.variant_id,
            "pathogenicity": str(self.pathogenicity),
            "molecular_consequence": self.molecular_consequence,
            "clinical_significance": self.clinical_significance,
            "condition": self.condition,
        }
        if self.hgvs_c:
            res["hgvs_c"] = self.hgvs_c
        if self.hgvs_p:
            res["hgvs_p"] = self.hgvs_p
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ViewerVariantAnnotation:
        """Instantiate ViewerVariantAnnotation from dictionary."""
        patho_val = data.get("pathogenicity", VariantPathogenicity.PATHOGENIC)
        try:
            patho_enum = VariantPathogenicity(str(patho_val).lower())
        except ValueError:
            patho_enum = VariantPathogenicity.PATHOGENIC

        return cls(
            coordinate=int(data.get("coordinate", 1)),
            ref_allele=str(data.get("ref_allele", "A")),
            alt_allele=str(data.get("alt_allele", "T")),
            variant_id=str(data.get("variant_id", "VAR_001")),
            pathogenicity=patho_enum,
            molecular_consequence=str(data.get("molecular_consequence", "missense")),
            clinical_significance=str(data.get("clinical_significance", "Pathogenic")),
            condition=str(data.get("condition", "Muscular Dystrophy")),
            hgvs_c=str(data["hgvs_c"]) if "hgvs_c" in data else None,
            hgvs_p=str(data["hgvs_p"]) if "hgvs_p" in data else None,
        )


@dataclass
class ViewerExonAnnotation:
    """Exon structure and splice junction coordinate boundaries."""

    exon_number: int
    start_coord: int
    end_coord: int
    phase: int = 0
    splice_donor: str = "GT"
    splice_acceptor: str = "AG"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "exon_number": self.exon_number,
            "start_coord": self.start_coord,
            "end_coord": self.end_coord,
            "phase": self.phase,
            "splice_donor": self.splice_donor,
            "splice_acceptor": self.splice_acceptor,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ViewerExonAnnotation:
        """Instantiate ViewerExonAnnotation from dictionary."""
        return cls(
            exon_number=int(data.get("exon_number", 1)),
            start_coord=int(data.get("start_coord", 1)),
            end_coord=int(data.get("end_coord", 100)),
            phase=int(data.get("phase", 0)),
            splice_donor=str(data.get("splice_donor", "GT")),
            splice_acceptor=str(data.get("splice_acceptor", "AG")),
        )


@dataclass
class ViewerEpigeneticMark:
    """Cytosine base modifications (5mC / 5hmC) and chromatin accessibility."""

    coordinate: int
    modification_type: str = "5hmC"
    modification_probability: float = 0.95

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "coordinate": self.coordinate,
            "modification_type": self.modification_type,
            "modification_probability": self.modification_probability,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ViewerEpigeneticMark:
        """Instantiate ViewerEpigeneticMark from dictionary."""
        return cls(
            coordinate=int(data.get("coordinate", 1)),
            modification_type=str(data.get("modification_type", "5hmC")),
            modification_probability=float(data.get("modification_probability", 0.95)),
        )


@dataclass
class ViewerCrisprPamSite:
    """Targetable CRISPR Cas endonuclease recognition motif."""

    pam_sequence: str = "NGG"
    start_coord: int = 1
    strand: str = "+"
    target_grna_20nt: str = ""
    cleavage_offset: int = -3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pam_sequence": self.pam_sequence,
            "start_coord": self.start_coord,
            "strand": self.strand,
            "target_grna_20nt": self.target_grna_20nt,
            "cleavage_offset": self.cleavage_offset,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ViewerCrisprPamSite:
        """Instantiate ViewerCrisprPamSite from dictionary."""
        return cls(
            pam_sequence=str(data.get("pam_sequence", "NGG")),
            start_coord=int(data.get("start_coord", 1)),
            strand=str(data.get("strand", "+")),
            target_grna_20nt=str(data.get("target_grna_20nt", "")),
            cleavage_offset=int(data.get("cleavage_offset", -3)),
        )


@dataclass
class DNAViewerContract:
    """Formal GFL IO Contract for Multi-Dimensional Dynamic DNA Helix Visualization.

    Inspired by the interactive B-DNA double helix scanner design (Sohaib Hassan 2026)
    and extended with full multi-omic dimensions: exons/introns, reading frames & translation,
    ClinVar pathogenic variant pins, 5mC/5hmC epigenetic marks, and CRISPR-Cas PAM windows.
    """

    viewer_id: str
    target_gene: str = "DMD"
    sequence_source: str | None = None
    raw_sequence: str | None = None
    genomic_range: str | None = "chrX:31119222-31139222"
    reference_build: str = "GRCh38"
    helix_type: HelixConformation = HelixConformation.B_DNA
    active_coordinate: int = 1
    tracks: list[ViewerTrackType] = field(
        default_factory=lambda: [
            ViewerTrackType.EXONS,
            ViewerTrackType.READING_FRAMES,
            ViewerTrackType.CLINVAR_VARIANTS,
        ]
    )
    variants: list[ViewerVariantAnnotation] = field(default_factory=list)
    exons: list[ViewerExonAnnotation] = field(default_factory=list)
    epigenetic_marks: list[ViewerEpigeneticMark] = field(default_factory=list)
    crispr_sites: list[ViewerCrisprPamSite] = field(default_factory=list)
    interactive: bool = True
    export_format: str = "html"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        res: dict[str, Any] = {
            "viewer_id": self.viewer_id,
            "target_gene": self.target_gene,
            "reference_build": self.reference_build,
            "helix_type": str(self.helix_type),
            "active_coordinate": self.active_coordinate,
            "tracks": [str(t) for t in self.tracks],
            "interactive": self.interactive,
            "export_format": self.export_format,
        }
        if self.sequence_source:
            res["sequence_source"] = self.sequence_source
        if self.raw_sequence:
            res["raw_sequence"] = self.raw_sequence
        if self.genomic_range:
            res["genomic_range"] = self.genomic_range
        if self.variants:
            res["variants"] = [v.to_dict() for v in self.variants]
        if self.exons:
            res["exons"] = [e.to_dict() for e in self.exons]
        if self.epigenetic_marks:
            res["epigenetic_marks"] = [m.to_dict() for m in self.epigenetic_marks]
        if self.crispr_sites:
            res["crispr_sites"] = [c.to_dict() for c in self.crispr_sites]
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNAViewerContract:
        """Instantiate DNAViewerContract from dictionary."""
        ht_val = data.get("helix_type", HelixConformation.B_DNA)
        try:
            ht_enum = HelixConformation(str(ht_val).lower())
        except ValueError:
            ht_enum = HelixConformation.B_DNA

        tracks_list: list[ViewerTrackType] = []
        raw_tracks = data.get("tracks", ["exons", "reading_frames", "clinvar_variants"])
        if isinstance(raw_tracks, list):
            for t in raw_tracks:
                try:
                    tracks_list.append(ViewerTrackType(str(t).lower()))
                except ValueError:
                    pass
        if not tracks_list:
            tracks_list = [
                ViewerTrackType.EXONS,
                ViewerTrackType.READING_FRAMES,
                ViewerTrackType.CLINVAR_VARIANTS,
            ]

        variants: list[ViewerVariantAnnotation] = []
        for v in data.get("variants", []):
            if isinstance(v, ViewerVariantAnnotation):
                variants.append(v)
            elif isinstance(v, dict):
                variants.append(ViewerVariantAnnotation.from_dict(v))

        exons: list[ViewerExonAnnotation] = []
        for e in data.get("exons", []):
            if isinstance(e, ViewerExonAnnotation):
                exons.append(e)
            elif isinstance(e, dict):
                exons.append(ViewerExonAnnotation.from_dict(e))

        epigenetic_marks: list[ViewerEpigeneticMark] = []
        for m in data.get("epigenetic_marks", []):
            if isinstance(m, ViewerEpigeneticMark):
                epigenetic_marks.append(m)
            elif isinstance(m, dict):
                epigenetic_marks.append(ViewerEpigeneticMark.from_dict(m))

        crispr_sites: list[ViewerCrisprPamSite] = []
        for c in data.get("crispr_sites", []):
            if isinstance(c, ViewerCrisprPamSite):
                crispr_sites.append(c)
            elif isinstance(c, dict):
                crispr_sites.append(ViewerCrisprPamSite.from_dict(c))

        return cls(
            viewer_id=str(data.get("viewer_id", data.get("name", "dmd_helix_viewer"))),
            target_gene=str(data.get("target_gene", "DMD")),
            sequence_source=str(data["sequence_source"]) if "sequence_source" in data else None,
            raw_sequence=str(data["raw_sequence"]) if "raw_sequence" in data else None,
            genomic_range=str(data["genomic_range"]) if "genomic_range" in data else "chrX:31119222-31139222",
            reference_build=str(data.get("reference_build", "GRCh38")),
            helix_type=ht_enum,
            active_coordinate=int(data.get("active_coordinate", 1)),
            tracks=tracks_list,
            variants=variants,
            exons=exons,
            epigenetic_marks=epigenetic_marks,
            crispr_sites=crispr_sites,
            interactive=bool(data.get("interactive", True)),
            export_format=str(data.get("export_format", "html")),
        )


@dataclass
class PhysicsRefinementPolicy:
    """Physics-based force field energy minimization and steric clash relief for co-folding predictions."""

    engine: str = "openmm"  # 'openmm', 'rosetta', 'amber'
    force_field: str = "amber14sb"
    max_iterations: int = 500
    tolerance_kj_mol: float = 10.0
    restrain_backbone: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "force_field": self.force_field,
            "max_iterations": self.max_iterations,
            "tolerance_kj_mol": self.tolerance_kj_mol,
            "restrain_backbone": self.restrain_backbone,
        }


@dataclass
class RescuePolicy:
    """Policy for rescuing borderline near-miss candidates via alternating gradient-guided search."""

    max_cycles: int = 3
    near_miss_margin: float = 0.15
    iptm_threshold: float = 0.8
    ipae_threshold: float = 2.5
    consensus_models: list[ConsensusModel] = field(
        default_factory=lambda: [ConsensusModel.AF3, ConsensusModel.RF3, ConsensusModel.BOLTZ]
    )
    strategy: str = "gradient_guided_mcmc"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "max_cycles": self.max_cycles,
            "near_miss_margin": self.near_miss_margin,
            "iptm_threshold": self.iptm_threshold,
            "ipae_threshold": self.ipae_threshold,
            "consensus_models": [str(m) for m in self.consensus_models],
            "strategy": self.strategy,
        }


class BiosyntheticDomainType(str, Enum):
    """Enzymatic domain types in modular megasynthases (PKS, NRPS, and hybrid BGCs)."""

    # Polyketide Synthase (PKS) domains
    KS = "KS"  # Ketosynthase (condensation)
    AT = "AT"  # Acyltransferase (substrate loading/selection)
    KR = "KR"  # Ketoreductase (beta-keto reduction)
    DH = "DH"  # Dehydratase (hydroxyl dehydration to double bond)
    ER = "ER"  # Enoylreductase (double bond reduction to single bond)
    ACP = "ACP"  # Acyl carrier protein (phosphopantetheine arm tether)
    TE = "TE"  # Thioesterase (chain termination/release/cyclization)

    # Non-Ribosomal Peptide Synthetase (NRPS) domains
    CONDENSATION = "CONDENSATION"  # C domain: amide bond formation
    ADENYLATION = "ADENYLATION"  # A domain: amino/carboxylic acid activation
    THIOLATION = "THIOLATION"  # T / PCP domain: peptidyl carrier protein
    EPIMERIZATION = "EPIMERIZATION"  # E domain: D/L chiral inversion
    CYCLIZATION = "CYCLIZATION"  # Cy domain: heterocyclic ring formation

    # Tailoring / Specialized domains
    METHYLTRANSFERASE = "METHYLTRANSFERASE"  # MT (C-MT, O-MT, N-MT)
    OXYGENASE = "OXYGENASE"
    HALOGENASE = "HALOGENASE"
    CUSTOM = "CUSTOM"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


@dataclass
class MegasynthaseDomain:
    """Individual enzymatic domain within a modular megasynthase."""

    domain_id: str
    domain_type: BiosyntheticDomainType
    start_pos: int
    end_pos: int
    substrate_specificity: str | None = None
    stereochemistry: str | None = None
    sequence_slice: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "domain_id": self.domain_id,
            "domain_type": str(self.domain_type),
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "substrate_specificity": self.substrate_specificity,
            "stereochemistry": self.stereochemistry,
            "sequence_slice": self.sequence_slice,
            "metadata": self.metadata,
        }


@dataclass
class MegasynthaseModule:
    """Modular unit in an enzymatic assembly line performing an elongation or loading cycle."""

    module_index: int
    domains: list[MegasynthaseDomain]
    elongation_substrate: str | None = None
    is_loading: bool = False
    is_termination: bool = False

    def has_domain(self, domain_type: BiosyntheticDomainType) -> bool:
        """Check if module contains a domain of specified type."""
        return any(d.domain_type == domain_type for d in self.domains)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module_index": self.module_index,
            "domains": [d.to_dict() for d in self.domains],
            "elongation_substrate": self.elongation_substrate,
            "is_loading": self.is_loading,
            "is_termination": self.is_termination,
        }


@dataclass
class BGCAssemblyContract:
    """Formal specification and validation contract for Biosynthetic Gene Clusters and Megasynthases."""

    cluster_id: str
    cluster_type: str  # e.g., "PKS_TYPE_I", "NRPS", "PKS_NRPS_HYBRID"
    target_chemical_product: str  # Target molecule (e.g., "delta-valerolactam")
    modules: list[MegasynthaseModule]
    cross_domain_compatibility_score: float = 1.0
    validation_status: str = "PENDING"
    notes: str | None = None

    def total_domains(self) -> int:
        """Return total domain count across all modules."""
        return sum(len(m.domains) for m in self.modules)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "cluster_id": self.cluster_id,
            "cluster_type": self.cluster_type,
            "target_chemical_product": self.target_chemical_product,
            "modules": [m.to_dict() for m in self.modules],
            "total_domains": self.total_domains(),
            "cross_domain_compatibility_score": self.cross_domain_compatibility_score,
            "validation_status": self.validation_status,
            "notes": self.notes,
        }


class DecisionStrategy(str, Enum):
    """Decision strategies for discrete option selection and pre-screening (System 1)."""

    PERMUTATION_INVARIANT_LOGITS = "permutation_invariant_logits"  # AnyJev style cyclic option permutation
    CALIBRATED_TEMPERATURE = "calibrated_temperature"  # Temperature-scaled confidence calibration
    EXACT_MATCH_PRIOR = "exact_match_prior"  # Deterministic schema prior match
    ENSEMBLE_MARGINALIZED = "ensemble_marginalized"  # Marginalized over permutation distribution
    SYSTEM_1_CALIBRATED = "system_1_calibrated"  # BioDecision-4B Tev1 calibrated single-forward-pass
    SYSTEM_1_FAST = "system_1_fast"  # Sub-50ms deterministic fast gating
    BIODECISION_SINGLE_FORWARD = "biodecision_single_forward"  # Dedicated single forward pass recipe

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


class DecisionMode(str, Enum):
    """Operating mode for discrete decision evaluation."""

    CHOICE = "choice"  # Multi-class single selection from allowed space
    BINARY = "binary"  # Binary gating (e.g. YES / NO, PASS / FAIL)
    SCORE = "score"  # Continuous calibrated alignment score in [0.0, 1.0]

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


@dataclass
class DecisionOption:
    """An option candidate evaluated during discrete decision selection."""

    option_id: str
    label: str
    raw_score: float = 0.0
    calibrated_probability: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "option_id": self.option_id,
            "label": self.label,
            "raw_score": self.raw_score,
            "calibrated_probability": self.calibrated_probability,
            "metadata": self.metadata,
        }


@dataclass
class DecisionOutcome:
    """Result of a fast discrete decision evaluation (System 1)."""

    selected_option_id: str
    confidence: float
    is_ambiguous: bool
    options_evaluated: list[DecisionOption]
    calibration_method: str = "temperature_scaling"
    latency_ms: float = 0.0
    ece: float | None = None
    mode: str = "choice"

    def passes_threshold(self, threshold: float = 0.85) -> bool:
        """Check if outcome satisfies confidence threshold without ambiguity."""
        return self.confidence >= threshold and not self.is_ambiguous

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "selected_option_id": self.selected_option_id,
            "confidence": self.confidence,
            "is_ambiguous": self.is_ambiguous,
            "options_evaluated": [opt.to_dict() for opt in self.options_evaluated],
            "calibration_method": self.calibration_method,
            "latency_ms": self.latency_ms,
            "ece": self.ece,
            "mode": self.mode,
        }


@dataclass
class DecisionContract:
    """Formal IO contract for pre-screening routing and discrete option arbitration."""

    task_id: str
    allowed_options: list[str] = field(default_factory=list)
    allowed_space: list[str] = field(default_factory=list)
    confidence_threshold: float = 0.85
    threshold: float = 0.85
    fallback_strategy: str = "ESCALATE_TO_SYSTEM2"
    strategy: DecisionStrategy = DecisionStrategy.SYSTEM_1_CALIBRATED
    engine: str = "biodecision-4b"
    latency_budget_ms: float = 50.0
    calibration_error_max: float = 0.08
    mode: DecisionMode = DecisionMode.CHOICE
    target_tissue: str | None = None
    cfdna_methylation_profile: str | None = None

    def __post_init__(self) -> None:
        """Synchronize allowed_options and allowed_space, and confidence threshold."""
        if not self.allowed_space and self.allowed_options:
            self.allowed_space = list(self.allowed_options)
        elif not self.allowed_options and self.allowed_space:
            self.allowed_options = list(self.allowed_space)

        if self.threshold != 0.85 and self.confidence_threshold == 0.85:
            self.confidence_threshold = self.threshold
        elif self.confidence_threshold != 0.85 and self.threshold == 0.85:
            self.threshold = self.confidence_threshold

    def is_within_budget(self, measured_latency_ms: float) -> bool:
        """Check if inference latency is within the allocated budget."""
        return measured_latency_ms <= self.latency_budget_ms

    def passes_calibration(self, measured_ece: float) -> bool:
        """Check if empirical calibration error is within the allowed bound."""
        return measured_ece <= self.calibration_error_max

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "allowed_options": self.allowed_options,
            "allowed_space": self.allowed_space,
            "confidence_threshold": self.confidence_threshold,
            "threshold": self.threshold,
            "fallback_strategy": self.fallback_strategy,
            "strategy": str(self.strategy),
            "engine": self.engine,
            "latency_budget_ms": self.latency_budget_ms,
            "calibration_error_max": self.calibration_error_max,
            "mode": str(self.mode),
            "target_tissue": self.target_tissue,
            "cfdna_methylation_profile": self.cfdna_methylation_profile,
        }


# Deterministic Discovery & Retroelement Architecture Types
# (Addressing the stochasticity and reproducibility trap in LLM agent discoveries)
class RetroelementType(str, Enum):
    """Classification of mobile genetic elements, retrons, and reverse transcriptases."""

    ARRAY_ASSOCIATED_RT = "ARRAY_ASSOCIATED_RT"  # ART: Array-associated Reverse Transcriptase
    RETRON = "RETRON"  # Bacterial retrons (msr-msd + RT)
    GROUP_II_INTRON = "GROUP_II_INTRON"  # Self-splicing ribozyme with RT
    DIVERSITY_GENERATING_RETROELEMENT = "DGR"  # Targeted mutagenic RT systems
    CRISPR_ASSOCIATED_RT = "CRISPR_ASSOCIATED_RT"  # Cas1-RT / Type III RT fusions
    VIRAL_RT = "VIRAL_RT"  # Retroviral reverse transcriptase

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


@dataclass
class ExhaustiveCoverageContract:
    """Contract enforcing full, non-fragmented base-level sequence scanning.

    Guarantees that an autonomous agent or screening tool does not suffer from
    stochastic context-window drift or partial sequence inspection.
    """

    window_size_bp: int = 1000
    stride_bp: int = 200
    min_coverage_pct: float = 100.0
    scan_both_strands: bool = True
    sequence_checksum: str = ""  # SHA-256 hash of the target sequence being screened

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "window_size_bp": self.window_size_bp,
            "stride_bp": self.stride_bp,
            "min_coverage_pct": self.min_coverage_pct,
            "scan_both_strands": self.scan_both_strands,
            "sequence_checksum": self.sequence_checksum,
        }


@dataclass
class DeterministicReplayContract:
    """Formal reproducibility contract binding candidate discoveries to deterministic proof.

    Guarantees that any biological discovery reported by an agent (e.g. Anthropic Mythos ART)
    is deterministically replayable across N independent runs without stochastic loss.
    """

    seed: int
    candidate_id: str
    target_checksum: str  # SHA-256 of the sequence/dataset
    coordinates: str  # Format: "start-end" or "chr:start-end"
    catalytic_motifs_verified: list[str] = field(default_factory=list)  # e.g., ["YADD", "YMDD"]
    required_reproducibility_rate: float = 1.0  # 1.0 = 100% deterministic re-discovery
    verification_hash: str = ""

    def __post_init__(self) -> None:
        """Compute verification hash if missing."""
        if not self.verification_hash and self.candidate_id and self.target_checksum:
            import hashlib

            data = f"{self.seed}:{self.candidate_id}:{self.target_checksum}:{self.coordinates}".encode()
            self.verification_hash = hashlib.sha256(data).hexdigest()

    @property
    def is_deterministic(self) -> bool:
        """Checks if the discovery meets the deterministic replay standard."""
        return self.required_reproducibility_rate >= 1.0 and bool(self.verification_hash)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "seed": self.seed,
            "candidate_id": self.candidate_id,
            "target_checksum": self.target_checksum,
            "coordinates": self.coordinates,
            "catalytic_motifs_verified": self.catalytic_motifs_verified,
            "required_reproducibility_rate": self.required_reproducibility_rate,
            "verification_hash": self.verification_hash,
            "is_deterministic": self.is_deterministic,
        }


@dataclass
class RetroelementArchitecture:
    """Formal biological specification for Reverse Transcriptases and repeat-associated retroelements."""

    element_id: str
    element_type: RetroelementType
    rt_domain_range: tuple[int, int]  # Amino acid coordinate range of the RT domain
    catalytic_triad: str  # Catalytic triad motif, typically YADD, YMDD, or LGDD
    associated_repeat_array: str = ""  # Nucleotide repeat pattern (e.g., direct repeat array)
    flanking_genes: list[str] = field(default_factory=list)
    replay_proof: DeterministicReplayContract | None = None

    @property
    def has_canonical_catalytic_triad(self) -> bool:
        """Verify presence of canonical reverse transcriptase active site."""
        return self.catalytic_triad in ["YADD", "YMDD", "RYADD", "RYVDD", "LGDD"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "element_id": self.element_id,
            "element_type": str(self.element_type),
            "rt_domain_range": list(self.rt_domain_range),
            "catalytic_triad": self.catalytic_triad,
            "associated_repeat_array": self.associated_repeat_array,
            "flanking_genes": self.flanking_genes,
            "has_canonical_catalytic_triad": self.has_canonical_catalytic_triad,
            "replay_proof": self.replay_proof.to_dict() if self.replay_proof else None,
        }


# De Novo Catalytic & Enzyme Design Layer (AlphaProtein Novo Synergy)
# Pure syntactic representation & structural observation containers (ADR-ARCH-001)
class CatalyticResidueRole(str, Enum):
    """Functional role of a catalytic active-site residue."""

    NUCLEOPHILE = "NUCLEOPHILE"
    GENERAL_ACID = "GENERAL_ACID"
    GENERAL_BASE = "GENERAL_BASE"
    TRANSITION_STATE_STABILIZER = "TRANSITION_STATE_STABILIZER"
    OXYANION_HOLE = "OXYANION_HOLE"
    ELECTROPHILE = "ELECTROPHILE"
    COFACTOR_COORDINATOR = "COFACTOR_COORDINATOR"

    def __str__(self) -> str:
        """Return the enum string value."""
        return self.value


@dataclass
class CatalyticResidue:
    """Specification of an active-site catalytic residue."""

    residue_name: str  # 3-letter code: 'SER', 'HIS', 'ASP', 'CYS', 'GLU', 'LYS'
    role: CatalyticResidueRole
    position: int | None = None  # None for de novo unassigned scaffolds
    chain: str = "A"
    target_atom: str = "CA"  # Key interaction atom: 'OG', 'NE2', 'OD1', 'SG'
    ideal_coordinates: tuple[float, float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "residue_name": self.residue_name,
            "role": str(self.role),
            "position": self.position,
            "chain": self.chain,
            "target_atom": self.target_atom,
            "ideal_coordinates": list(self.ideal_coordinates) if self.ideal_coordinates else None,
        }


@dataclass
class SubstrateLigandContainer:
    """Syntactic container representing a bound ligand or transition-state substrate."""

    substrate_name: str
    smiles: str
    charge: int = 0
    transition_state_analog: bool = False
    reactive_atom_indices: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "substrate_name": self.substrate_name,
            "smiles": self.smiles,
            "charge": self.charge,
            "transition_state_analog": self.transition_state_analog,
            "reactive_atom_indices": self.reactive_atom_indices,
        }


@dataclass
class CatalyticMotif:
    """Multi-residue catalytic geometry declaration (e.g. Ser-His-Asp catalytic triad)."""

    motif_id: str
    residues: list[CatalyticResidue]
    max_active_site_rmsd: float = 1.0  # Angstrom tolerance for de novo scaffold matching
    spatial_distance_constraints: dict[str, tuple[float, float]] = field(default_factory=dict)
    # e.g. {"SER:OG-HIS:NE2": (2.6, 3.2), "HIS:ND1-ASP:OD1": (2.5, 3.1)}

    @property
    def residue_count(self) -> int:
        """Count of catalytic residues in the motif."""
        return len(self.residues)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "motif_id": self.motif_id,
            "residues": [r.to_dict() for r in self.residues],
            "max_active_site_rmsd": self.max_active_site_rmsd,
            "spatial_distance_constraints": self.spatial_distance_constraints,
            "residue_count": self.residue_count,
        }


@dataclass
class EnzymeDesignContract:
    """Formal GFL IO Contract for de novo enzyme design candidates and catalytic scaffolding."""

    enzyme_family: str  # e.g., 'SERINE_PROTEASE', 'ESTERASE', 'RETRO_ALDOLASE'
    catalytic_motif: CatalyticMotif
    substrate: SubstrateLigandContainer | None = None
    target_transition_state_distance: float = 3.5  # Maximum Angstrom distance to substrate
    max_scaffold_pocket_clash: float = 0.0  # Steric clash tolerance

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "enzyme_family": self.enzyme_family,
            "catalytic_motif": self.catalytic_motif.to_dict(),
            "substrate": self.substrate.to_dict() if self.substrate else None,
            "target_transition_state_distance": self.target_transition_state_distance,
            "max_scaffold_pocket_clash": self.max_scaffold_pocket_clash,
        }


# DNA Typewriter & Developmental Lineage Tracing Layer
# Grounded in Science 2026 (Yu et al., DOI: 10.1126/science.ael0508)
class CassetteArchitecture(str, Enum):
    """Architecture of recording cassette for continuous cellular lineage tracing."""

    TANDEM_PEGRNA_INSERTIONAL = "tandem_pegRNA_insertional"
    BASE_EDITOR_ACCUMULATION = "base_editor_accumulation"
    CRISPR_HOMING_BARCODE = "crispr_homing_barcode"
    PRIME_EDITING_TAPE = "prime_editing_tape"

    def __str__(self) -> str:
        """Return the enum value."""
        return self.value


class ReadoutModality(str, Enum):
    """Modality for reading out recorded cellular tape barcodes."""

    TARGETED_AMPLICON_DNA_SEQ = "targeted_amplicon_dna_seq"
    SINGLE_CELL_RNA_SEQ_EXPRESSION = "single_cell_rna_seq_expression"
    MULTIPLEX_AMPLICON_SEQ = "multiplex_amplicon_seq"
    LONG_READ_PACBIO = "long_read_pacbio"
    LONG_READ_ONT = "long_read_ont"

    def __str__(self) -> str:
        """Return the enum value."""
        return self.value


@dataclass
class TapeRecorderContract:
    """Formal IO contract for DNA Typewriter sequential recording cassette.

    Captures non-destructive, sequential insertion markings stored in cells' own DNA
    to reconstruct cellular developmental family trees from zygote to organogenesis.
    """

    recorder_id: str
    cassette_architecture: CassetteArchitecture = CassetteArchitecture.TANDEM_PEGRNA_INSERTIONAL
    tape_capacity_sites: int = 50
    recording_interval_hours: float = 6.0
    edit_signature_alphabet: list[str] = field(default_factory=list)
    target_organism: str | None = "mus_musculus"
    developmental_window: str | None = "13.5_days"
    readout_modality: str | ReadoutModality | None = ReadoutModality.TARGETED_AMPLICON_DNA_SEQ

    @property
    def total_recording_capacity_hours(self) -> float:
        """Theoretical maximum continuous recording window before tape saturation."""
        return self.tape_capacity_sites * self.recording_interval_hours

    def can_accommodate_duration_hours(self, duration_hours: float) -> bool:
        """Verify whether duration fits within cassette site capacity."""
        return duration_hours <= self.total_recording_capacity_hours

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "recorder_id": self.recorder_id,
            "cassette_architecture": str(self.cassette_architecture),
            "tape_capacity_sites": self.tape_capacity_sites,
            "recording_interval_hours": self.recording_interval_hours,
            "edit_signature_alphabet": list(self.edit_signature_alphabet),
            "target_organism": self.target_organism,
            "developmental_window": self.developmental_window,
            "readout_modality": str(self.readout_modality) if self.readout_modality else None,
            "total_recording_capacity_hours": self.total_recording_capacity_hours,
        }


@dataclass
class LineageNode:
    """Node in an embryonic cellular lineage tree reconstructed from tape barcodes."""

    cell_id: str
    generation: int
    tape_state: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    cell_type_annotation: str | None = None
    time_point_hours: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "cell_id": self.cell_id,
            "generation": self.generation,
            "tape_state": list(self.tape_state),
            "children": list(self.children),
            "cell_type_annotation": self.cell_type_annotation,
            "time_point_hours": self.time_point_hours,
        }


@dataclass
class ProgramEvolutionContract:
    """Declarative specification for an AlphaEvolve program evolution optimization run.

    AlphaEvolve evolves code representations (executable protocols, scoring functions,
    or design heuristics) via LLM mutation engines guided by deterministic fitness evaluations.
    """

    seed_program: str
    fitness_metric: str
    mutation_engine: str = "gemini-1.5-pro"
    population_size: int = 20
    generations: int = 15
    elitism_rate: float = 0.20
    mutation_operators: list[str] = field(
        default_factory=lambda: [
            "diff_prompt",
            "semantic_refactor",
            "hyperparameter_tune",
            "algorithmic_crossover",
        ]
    )
    timeout_per_eval_seconds: float = 60.0
    deterministic_eval_harness: str | None = None
    target_fitness_threshold: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "seed_program": self.seed_program,
            "fitness_metric": self.fitness_metric,
            "mutation_engine": self.mutation_engine,
            "population_size": self.population_size,
            "generations": self.generations,
            "elitism_rate": self.elitism_rate,
            "mutation_operators": list(self.mutation_operators),
            "timeout_per_eval_seconds": self.timeout_per_eval_seconds,
            "deterministic_eval_harness": self.deterministic_eval_harness,
            "target_fitness_threshold": self.target_fitness_threshold,
        }


class FragmentomicsModality(str, Enum):
    """Modality for cell-free DNA fragmentomics and epigenetic deconvolution."""

    METHYLATION_DENSITY = "methylation_density"
    FRAGMENT_LENGTH_DISTRIBUTION = "fragment_length_distribution"
    END_MOTIF_FREQUENCY = "end_motif_frequency"
    WINDOW_PROTECTION_SCORE = "window_protection_score"
    HIERARCHICAL_STACKED_ATTENTION = "hierarchical_stacked_attention"
    HYDROXYMETHYLATION_5HMC = "5hmC_hydroxymethylation"

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


@dataclass
class EpigeneticDeconvolutionContract:
    """Formal IO Contract for whole-epigenome foundation model deconvolution.

    Captures joint DNA sequence and CpG methylation patterns from liquid biopsy plasma cfDNA,
    mapping fragment-level, region-level, and sample-level signals to cell-type-of-origin
    deconvolution (e.g. Pleiades 90M / 600M / 7B architecture).
    """

    deconvolution_id: str
    target_tissue: str  # e.g., "central_nervous_system", "cortex", "hippocampus", "pancreas"
    cfdna_methylation_profile: str  # identifier or path to plasma sample run
    engine: str = "pleiades-biodecision"
    modality: FragmentomicsModality = FragmentomicsModality.HIERARCHICAL_STACKED_ATTENTION
    confidence_threshold: float = 0.90
    min_fragment_coverage: int = 100000
    sub_cell_types: list[str] = field(default_factory=list)  # e.g. ["astrocytes", "neurons", "microglia"]
    calibration_method: str = "temperature_scaling"
    max_ece: float = 0.05

    def passes_gate(self, inferred_confidence: float, sample_fragments: int) -> bool:
        """Check if inferred confidence and depth satisfy deconvolution criteria."""
        return inferred_confidence >= self.confidence_threshold and sample_fragments >= self.min_fragment_coverage

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "deconvolution_id": self.deconvolution_id,
            "target_tissue": self.target_tissue,
            "cfdna_methylation_profile": self.cfdna_methylation_profile,
            "engine": self.engine,
            "modality": str(self.modality),
            "confidence_threshold": self.confidence_threshold,
            "min_fragment_coverage": self.min_fragment_coverage,
            "sub_cell_types": list(self.sub_cell_types),
            "calibration_method": self.calibration_method,
            "max_ece": self.max_ece,
        }


@dataclass
class NaturalLanguageConditioningContract:
    """Multi-scale natural language prompt conditioning for de novo protein design.

    Grounded in Prompteina (Baker Lab / IPD & Ai2, 2026), capturing macro-topology,
    residue-specific target interactions, negative design gates, and diffusion guidance scale.
    """

    prompt: str = ""
    macro_topology: str = ""  # e.g., "three-helix bundle", "TIM barrel", "beta-propeller"
    interaction_site: str = ""  # e.g., "binds apical hydrophobic cavity of GM2A"
    negative_design: str = ""  # e.g., "avoid lipid transfer gateway Lys88-Asp91"
    symmetry: str = "C1"
    sequence_composition: str = ""
    guidance_scale: float = 7.5  # Text classifier-free guidance weight
    num_inference_steps: int = 50

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "prompt": self.prompt,
            "macro_topology": self.macro_topology,
            "interaction_site": self.interaction_site,
            "negative_design": self.negative_design,
            "symmetry": self.symmetry,
            "sequence_composition": self.sequence_composition,
            "guidance_scale": self.guidance_scale,
            "num_inference_steps": self.num_inference_steps,
        }


@dataclass
class TextConditionedDesignContract:
    """Formal GFL IO Contract for Prompteina text-conditioned all-atom binder and structure design."""

    design_id: str
    target_pdb: str
    prompt_conditioning: NaturalLanguageConditioningContract
    entity: str = "ProteinSequence"
    model: str = "prompteina"
    count: int = 100
    target_protein_name: str | None = None  # e.g. "GM2A"
    min_affinity_nm: float = 1000.0  # Sub-micromolar target hit threshold
    max_interface_rmsd: float = 2.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "design_id": self.design_id,
            "target_pdb": self.target_pdb,
            "prompt_conditioning": self.prompt_conditioning.to_dict(),
            "entity": self.entity,
            "model": self.model,
            "count": self.count,
            "target_protein_name": self.target_protein_name,
            "min_affinity_nm": self.min_affinity_nm,
            "max_interface_rmsd": self.max_interface_rmsd,
        }


class ViralInteractomeType(str, Enum):
    """Type of viral-host or intra-viral multimeric complex."""

    HOMODIMER = "homodimer"
    HETERODIMER = "heterodimer"
    HIGHER_ORDER_OLIGOMER = "higher_order_oligomer"
    HOST_PATHOGEN_INTERACTION = "host_pathogen_interaction"

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


@dataclass
class AlphaGenomeLocusLink:
    """Genomic locus cross-reference for host receptor or viral escape variants.

    Constructs and verifies coordinate links formatted for the AlphaGenome Atlas
    (e.g., 1-based chr:pos:ref>alt, target biosample, and functional modalities).
    """

    variant: str  # 1-based "chr:pos:ref>alt"
    gene: str | None = None  # e.g., "ACE2", "NRP1"
    biosample: str = "Lung"
    modalities: list[str] = field(default_factory=lambda: ["RNA_SEQ", "DNASE"])

    def to_atlas_query(self) -> str:
        """Format variant query according to AlphaGenome Atlas specification."""
        return self.variant

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "variant": self.variant,
            "gene": self.gene,
            "biosample": self.biosample,
            "modalities": list(self.modalities),
        }


@dataclass
class ViralInteractomeComplexContract:
    """Formal GFL IO Contract for viral-host protein complexes.

    Grounded in AlphaFold Database Pandemic Preparedness Portal (DeepMind, EMBL-EBI, NVIDIA,
    CEPI, SIB, MRC Glasgow 2026), systematically exploring viral proteome interactomes
    (~1.7M predicted dimers, 8,028 high-confidence complexes across 2,812 proteomes).
    """

    complex_id: str
    subunits: list[str]  # UniProt accession IDs or subunit symbols
    interactome_type: ViralInteractomeType = ViralInteractomeType.HETERODIMER
    portal: str = "alphafold_pandemic_preparedness"
    viral_family: str | None = None  # e.g., "coronaviridae", "flaviviridae", "filoviridae"
    proteome_id: str | None = None  # e.g., "UP000464024"
    iplddt_threshold: float = 75.0
    iptm_threshold: float = 0.70
    is_high_confidence_portal_hit: bool = True
    host_locus_link: AlphaGenomeLocusLink | None = None

    def passes_confidence_gate(self, iplddt: float, iptm: float) -> bool:
        """Check if complex prediction meets the high-confidence threshold."""
        return iplddt >= self.iplddt_threshold and iptm >= self.iptm_threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "complex_id": self.complex_id,
            "subunits": list(self.subunits),
            "interactome_type": str(self.interactome_type),
            "portal": self.portal,
            "viral_family": self.viral_family,
            "proteome_id": self.proteome_id,
            "iplddt_threshold": self.iplddt_threshold,
            "iptm_threshold": self.iptm_threshold,
            "is_high_confidence_portal_hit": self.is_high_confidence_portal_hit,
            "host_locus_link": self.host_locus_link.to_dict() if self.host_locus_link else None,
        }


class DNABreathingModel(str, Enum):
    """Mesoscopic and statistical mechanics models for DNA breathing and base-pair opening."""

    PBD_MESOSCOPIC = "pbd_mesoscopic"
    EPBD_STOCHASTIC = "epbd_stochastic"
    THERMODYNAMIC_MELTING = "thermodynamic_melting"

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


class TFBindingCouplingMode(str, Enum):
    """Transcription factor binding coupling mode relative to DNA breathing dynamics.

    Grounded in Chiu et al. (Bioinformatics Advances, 2026 / Rohs Lab):
    - RIGID_SHAPE_DOMINATED: TF relies on equilibrium double-helix shape (MGW, Roll);
      transient base opening disrupts hydrogen bonds (e.g. Homeodomains, bHLH).
    - BREATHING_ASSISTED: TF binding is enhanced by transient local opening/bubbles,
      intercalation, or severe DNA bending (e.g. TBP, pioneer factors, Cas9 unwinding).
    - BIFUNCTIONAL_BALANCED: Requires equilibrium shape for core contact and local
      thermal opening flexibility at flanking regions.
    """

    RIGID_SHAPE_DOMINATED = "rigid_shape_dominated"
    BREATHING_ASSISTED = "breathing_assisted"
    BIFUNCTIONAL_BALANCED = "bifunctional_balanced"

    def __str__(self) -> str:
        """Return enum value."""
        return self.value


@dataclass
class DNABreathingProfile:
    """Quantitative physical profile of DNA breathing and static shape.

    Grounded in Peyrard-Bishop-Dauxois (PBD) mesoscopic dynamics and DNAshape
    (Chiu, Tang, Butt, Lai, Qian, Alexandrov, Duan, He, Rohs; Bioinformatics Advances 2026).
    """

    sequence: str
    temperature_kelvin: float = 310.15  # 37°C physiological
    displacement_threshold_angstrom: float = 1.5
    mean_displacements: list[float] = field(default_factory=list)  # <y_n> in Angstroms
    opening_probabilities: list[float] = field(default_factory=list)  # P(y_n > threshold)
    local_melting_energies: list[float] = field(default_factory=list)  # Delta G_open in kcal/mol
    bubble_prone_regions: list[tuple[int, int]] = field(default_factory=list)  # (start, end) 0-indexed
    static_shape_mgw: list[float] = field(default_factory=list)  # Minor Groove Width (Angstroms)
    static_shape_roll: list[float] = field(default_factory=list)  # Roll (degrees)
    static_shape_helt: list[float] = field(default_factory=list)  # Helical Twist (degrees)
    static_shape_prot: list[float] = field(default_factory=list)  # Propeller Twist (degrees)
    evidence_status: str = "analytical_mesoscopic"
    source_citation: str = (
        "Chiu TP, Tang WY, Butt W, Lai B, Qian S, Alexandrov BS, Duan J, He X, Rohs R. "
        "DNA breathing and shape encode distinct mechanisms of transcription factor binding. "
        "Bioinformatics Advances, 2026."
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sequence": self.sequence,
            "temperature_kelvin": self.temperature_kelvin,
            "displacement_threshold_angstrom": self.displacement_threshold_angstrom,
            "mean_displacements": list(self.mean_displacements),
            "opening_probabilities": list(self.opening_probabilities),
            "local_melting_energies": list(self.local_melting_energies),
            "bubble_prone_regions": [list(r) for r in self.bubble_prone_regions],
            "static_shape_mgw": list(self.static_shape_mgw),
            "static_shape_roll": list(self.static_shape_roll),
            "static_shape_helt": list(self.static_shape_helt),
            "static_shape_prot": list(self.static_shape_prot),
            "evidence_status": self.evidence_status,
            "source_citation": self.source_citation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNABreathingProfile:
        """Create DNABreathingProfile from dictionary representation."""
        return cls(
            sequence=str(data.get("sequence", "")),
            temperature_kelvin=float(data.get("temperature_kelvin", 310.15)),
            displacement_threshold_angstrom=float(data.get("displacement_threshold_angstrom", 1.5)),
            mean_displacements=[float(x) for x in data.get("mean_displacements", [])],
            opening_probabilities=[float(x) for x in data.get("opening_probabilities", [])],
            local_melting_energies=[float(x) for x in data.get("local_melting_energies", [])],
            bubble_prone_regions=[(int(r[0]), int(r[1])) for r in data.get("bubble_prone_regions", [])],
            static_shape_mgw=[float(x) for x in data.get("static_shape_mgw", [])],
            static_shape_roll=[float(x) for x in data.get("static_shape_roll", [])],
            static_shape_helt=[float(x) for x in data.get("static_shape_helt", [])],
            static_shape_prot=[float(x) for x in data.get("static_shape_prot", [])],
            evidence_status=str(data.get("evidence_status", "analytical_mesoscopic")),
            source_citation=str(data.get("source_citation", "")),
        )


@dataclass
class TFBreathingCouplingContract:
    """Coupling specification between transcription factor binding affinity and DNA physical dynamics."""

    tf_name: str
    coupling_mode: TFBindingCouplingMode = TFBindingCouplingMode.BIFUNCTIONAL_BALANCED
    shape_weight: float = 0.5
    breathing_weight: float = 0.5
    target_motif: str | None = None
    binding_affinity_delta_kcal: float | None = None  # Delta Delta G predicted

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tf_name": self.tf_name,
            "coupling_mode": str(self.coupling_mode),
            "shape_weight": self.shape_weight,
            "breathing_weight": self.breathing_weight,
            "target_motif": self.target_motif,
            "binding_affinity_delta_kcal": self.binding_affinity_delta_kcal,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TFBreathingCouplingContract:
        """Create TFBreathingCouplingContract from dictionary representation."""
        raw_mode = data.get("coupling_mode", TFBindingCouplingMode.BIFUNCTIONAL_BALANCED)
        mode = TFBindingCouplingMode(raw_mode) if not isinstance(raw_mode, TFBindingCouplingMode) else raw_mode
        return cls(
            tf_name=str(data.get("tf_name", "unspecified_tf")),
            coupling_mode=mode,
            shape_weight=float(data.get("shape_weight", 0.5)),
            breathing_weight=float(data.get("breathing_weight", 0.5)),
            target_motif=data.get("target_motif"),
            binding_affinity_delta_kcal=float(data["binding_affinity_delta_kcal"])
            if data.get("binding_affinity_delta_kcal") is not None
            else None,
        )


@dataclass
class DNADynamicsContract:
    """Formal GFL IO Contract for DNA Breathing and Mesoscopic Physical Code."""

    contract_id: str
    sequence: str
    temperature_kelvin: float = 310.15
    model: DNABreathingModel = DNABreathingModel.PBD_MESOSCOPIC
    displacement_threshold_angstrom: float = 1.5
    include_static_shape: bool = True
    target_tf_coupling: TFBreathingCouplingContract | None = None
    variant_delta: dict[str, Any] | None = None  # e.g. {"ref": "C", "alt": "T", "pos": 15}
    verified_profile: DNABreathingProfile | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "sequence": self.sequence,
            "temperature_kelvin": self.temperature_kelvin,
            "model": str(self.model),
            "displacement_threshold_angstrom": self.displacement_threshold_angstrom,
            "include_static_shape": self.include_static_shape,
            "target_tf_coupling": self.target_tf_coupling.to_dict() if self.target_tf_coupling else None,
            "variant_delta": dict(self.variant_delta) if self.variant_delta else None,
            "verified_profile": self.verified_profile.to_dict() if self.verified_profile else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNADynamicsContract:
        """Create DNADynamicsContract from dictionary representation."""
        raw_model = data.get("model", DNABreathingModel.PBD_MESOSCOPIC)
        model = DNABreathingModel(raw_model) if not isinstance(raw_model, DNABreathingModel) else raw_model
        tf_data = data.get("target_tf_coupling")
        tf_coupling = TFBreathingCouplingContract.from_dict(tf_data) if isinstance(tf_data, dict) else tf_data
        prof_data = data.get("verified_profile")
        prof = DNABreathingProfile.from_dict(prof_data) if isinstance(prof_data, dict) else prof_data

        return cls(
            contract_id=str(data.get("contract_id", data.get("name", "dna_dynamics_contract"))),
            sequence=str(data.get("sequence", data.get("dna_sequence", ""))),
            temperature_kelvin=float(data.get("temperature_kelvin", 310.15)),
            model=model,
            displacement_threshold_angstrom=float(data.get("displacement_threshold_angstrom", 1.5)),
            include_static_shape=bool(data.get("include_static_shape", True)),
            target_tf_coupling=tf_coupling,
            variant_delta=data.get("variant_delta"),
            verified_profile=prof,
            metadata=dict(data.get("metadata", {})),
        )


# ============================================================================
# Single-Cell Immune Regulation & Cell-State Dynamics Layer
# Grounded in TenK10K Phase 1 (Cuomo et al., Nature 2026, DOI: 10.1038/s41586-026-10721-2)
# ============================================================================


class TenK10KImmuneCellType(str, Enum):
    """Canonical PBMC immune cell types profiled in TenK10K mapped to Cell Ontology (CL)."""

    # CD4+ T cell lineages
    CD4_NAIVE = "CL:0000895"
    CD4_CENTRAL_MEMORY = "CL:0000897"
    CD4_EFFECTOR_MEMORY = "CL:0000905"
    CD4_TEMRA = "CL:0001084"
    CD4_TREG = "CL:0000815"
    CD4_FOLLICULAR_HELPER = "CL:0002038"

    # CD8+ T cell lineages
    CD8_NAIVE = "CL:0000900"
    CD8_CENTRAL_MEMORY = "CL:0000907"
    CD8_EFFECTOR_MEMORY = "CL:0000910"
    CD8_TEMRA = "CL:0001085"
    CD8_CYTOTOXIC = "CL:0000911"
    CD8_EXHAUSTED = "CL:0002047"
    GAMMA_DELTA_T = "CL:0000798"
    MAIT_CELL = "CL:0000940"

    # B cell lineages
    B_NAIVE = "CL:0000788"
    B_SWITCHED_MEMORY = "CL:0000972"
    B_UNSWITCHED_MEMORY = "CL:0000970"
    PLASMA_CELL = "CL:0000786"

    # Natural Killer (NK) cell lineages
    NK_CD56_DIM = "CL:0000938"
    NK_CD56_BRIGHT = "CL:0000939"

    # Monocyte lineages
    MONOCYTE_CLASSICAL = "CL:0000860"
    MONOCYTE_NON_CLASSICAL = "CL:0000875"
    MONOCYTE_INTERMEDIATE = "CL:0002396"

    # Dendritic cell lineages
    DC_CONVENTIONAL_1 = "CL:0000990"
    DC_CONVENTIONAL_2 = "CL:0002399"
    DC_PLASMACYTOID = "CL:0000784"

    # Innate Lymphoid & Platelet lineages
    ILC_UNCOMMITTED = "CL:0001065"
    PLATELET = "CL:0000233"

    def __str__(self) -> str:
        """Return the CL CURIE string value."""
        return self.value


class RegulatoryQTLType(str, Enum):
    """Modes of single-cell expression and cell-state regulation."""

    COMMON_CIS_EQTL = "common_cis_eqtl"
    RARE_VARIANT_COLLAPSE = "rare_variant_collapse"
    SECONDARY_INDEPENDENT_SIGNAL = "secondary_independent_signal"
    CELL_STATE_INTERACTION = "cell_state_interaction"
    CELL_ABUNDANCE_QTL = "cell_abundance_qtl"
    TANDEM_REPEAT_EQTL = "tandem_repeat_eqtl"
    CHROMATIN_ACCESSIBILITY_CAQTL = "chromatin_accessibility_caqtl"

    def __str__(self) -> str:
        """Return the enum string value."""
        return self.value


class CellStateAxis(str, Enum):
    """Dynamic cellular activation/functional axes."""

    CYTOTOXICITY = "cytotoxicity"
    INTERFERON_STIMULATION = "interferon_stimulation"
    EXHAUSTION = "exhaustion"
    PROLIFERATION = "proliferation"
    INFLAMMATORY_SIGNALING = "inflammatory_signaling"
    DIFFERENTIATION = "differentiation"
    CUSTOM = "custom"

    def __str__(self) -> str:
        """Return the enum string value."""
        return self.value


@dataclass
class CellStateInteractionContract:
    """Contract for dynamic eQTLs modulated along a continuous cellular state axis."""

    state_axis: CellStateAxis | str = CellStateAxis.CYTOTOXICITY
    beta_baseline: float = 0.0
    gamma_interaction: float = 0.0
    state_range: tuple[float, float] = (0.0, 1.0)
    p_value_interaction: float = 1e-6
    fdr: float = 0.05

    def effective_beta(self, state_value: float) -> float:
        """Compute beta_eff = beta_0 + gamma * state_value."""
        clamped_state = max(self.state_range[0], min(self.state_range[1], state_value))
        return self.beta_baseline + self.gamma_interaction * clamped_state

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "state_axis": str(self.state_axis),
            "beta_baseline": self.beta_baseline,
            "gamma_interaction": self.gamma_interaction,
            "state_range": list(self.state_range),
            "p_value_interaction": self.p_value_interaction,
            "fdr": self.fdr,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CellStateInteractionContract:
        """Create from dictionary representation."""
        axis_raw = data.get("state_axis", CellStateAxis.CYTOTOXICITY)
        axis = CellStateAxis(axis_raw) if axis_raw in CellStateAxis._value2member_map_ else axis_raw
        raw_range = data.get("state_range", (0.0, 1.0))
        state_range = (float(raw_range[0]), float(raw_range[1])) if len(raw_range) >= 2 else (0.0, 1.0)

        return cls(
            state_axis=axis,
            beta_baseline=float(data.get("beta_baseline", 0.0)),
            gamma_interaction=float(data.get("gamma_interaction", 0.0)),
            state_range=state_range,
            p_value_interaction=float(data.get("p_value_interaction", 1e-6)),
            fdr=float(data.get("fdr", 0.05)),
        )


@dataclass
class CellAbundanceQTLContract:
    """Contract for genetic variants modulating proportional cell type abundance (caQTLs)."""

    target_cell_type: str = "CL:0000860"  # e.g. Monocytes classical
    effect_size_delta: float = 0.0  # Proportional fraction delta [-1.0, 1.0]
    baseline_fraction: float = 0.10
    driver_gene: str = "LYZ"
    differentiation_mechanism: str = "lineage_fate_bias"
    p_value: float = 1e-8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "target_cell_type": self.target_cell_type,
            "effect_size_delta": self.effect_size_delta,
            "baseline_fraction": self.baseline_fraction,
            "driver_gene": self.driver_gene,
            "differentiation_mechanism": self.differentiation_mechanism,
            "p_value": self.p_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CellAbundanceQTLContract:
        """Create from dictionary representation."""
        return cls(
            target_cell_type=str(data.get("target_cell_type", "CL:0000860")),
            effect_size_delta=float(data.get("effect_size_delta", 0.0)),
            baseline_fraction=float(data.get("baseline_fraction", 0.10)),
            driver_gene=str(data.get("driver_gene", "LYZ")),
            differentiation_mechanism=str(data.get("differentiation_mechanism", "lineage_fate_bias")),
            p_value=float(data.get("p_value", 1e-8)),
        )


@dataclass
class ColocalizationGateContract:
    """Bayesian colocalization contract between GWAS complex traits and single-cell eQTLs."""

    gwas_trait_id: str = ""
    gwas_trait_name: str = ""
    candidate_gene: str = ""
    posterior_prob_h4: float = 0.85  # PP4: shared causal variant
    pp4_threshold: float = 0.80
    credible_set_size: int = 1
    lead_variant_rsid: str = ""

    @property
    def is_colocalized(self) -> bool:
        """Return True if posterior probability H4 exceeds gating threshold."""
        return self.posterior_prob_h4 >= self.pp4_threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "gwas_trait_id": self.gwas_trait_id,
            "gwas_trait_name": self.gwas_trait_name,
            "candidate_gene": self.candidate_gene,
            "posterior_prob_h4": self.posterior_prob_h4,
            "pp4_threshold": self.pp4_threshold,
            "credible_set_size": self.credible_set_size,
            "lead_variant_rsid": self.lead_variant_rsid,
            "is_colocalized": self.is_colocalized,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ColocalizationGateContract:
        """Create from dictionary representation."""
        return cls(
            gwas_trait_id=str(data.get("gwas_trait_id", "")),
            gwas_trait_name=str(data.get("gwas_trait_name", "")),
            candidate_gene=str(data.get("candidate_gene", "")),
            posterior_prob_h4=float(data.get("posterior_prob_h4", 0.85)),
            pp4_threshold=float(data.get("pp4_threshold", 0.80)),
            credible_set_size=int(data.get("credible_set_size", 1)),
            lead_variant_rsid=str(data.get("lead_variant_rsid", "")),
        )


@dataclass
class TandemRepeatContract:
    """Tandem repeat / VNTR variation shaping single-cell expression."""

    repeat_unit_motif: str = "CAG"
    reference_copy_number: int = 10
    alternate_copy_number: int = 15
    delta_copies: int = 5
    expansion_risk_category: str = "normal"  # "normal", "pre_mutation", "full_expansion"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "repeat_unit_motif": self.repeat_unit_motif,
            "reference_copy_number": self.reference_copy_number,
            "alternate_copy_number": self.alternate_copy_number,
            "delta_copies": self.delta_copies,
            "expansion_risk_category": self.expansion_risk_category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TandemRepeatContract:
        """Create from dictionary representation."""
        ref_n = int(data.get("reference_copy_number", 10))
        alt_n = int(data.get("alternate_copy_number", ref_n))
        delta = int(data.get("delta_copies", alt_n - ref_n))

        return cls(
            repeat_unit_motif=str(data.get("repeat_unit_motif", "CAG")),
            reference_copy_number=ref_n,
            alternate_copy_number=alt_n,
            delta_copies=delta,
            expansion_risk_category=str(data.get("expansion_risk_category", "normal")),
        )


@dataclass
class SingleCellRegulatoryContract:
    """Formal GFL contract for cell-type-specific and cell-state-dynamic immune regulation.

    Grounded in the TenK10K Phase 1 landmark dataset (Cuomo, Spenceley, Tanudisastro et al.,
    Powell & MacArthur, Nature 2026, DOI: 10.1038/s41586-026-10721-2).
    """

    contract_id: str
    target_gene: str
    variant: str
    variant_type: str = "snv"  # "snv", "indel", "tandem_repeat", "structural_variant"
    cell_type: TenK10KImmuneCellType | str = TenK10KImmuneCellType.NK_CD56_DIM
    qtl_type: RegulatoryQTLType = RegulatoryQTLType.COMMON_CIS_EQTL
    is_cell_type_specific: bool = False
    is_distal_enhancer: bool = False
    distance_to_tss_bp: int = 0
    beta_marginal: float = 0.0
    standard_error: float = 0.02
    p_value_empirical: float = 1e-7
    state_interaction: CellStateInteractionContract | None = None
    abundance_qtl: CellAbundanceQTLContract | None = None
    colocalization_gate: ColocalizationGateContract | None = None
    tandem_repeat: TandemRepeatContract | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "target_gene": self.target_gene,
            "variant": self.variant,
            "variant_type": self.variant_type,
            "cell_type": str(self.cell_type),
            "qtl_type": str(self.qtl_type),
            "is_cell_type_specific": self.is_cell_type_specific,
            "is_distal_enhancer": self.is_distal_enhancer,
            "distance_to_tss_bp": self.distance_to_tss_bp,
            "beta_marginal": self.beta_marginal,
            "standard_error": self.standard_error,
            "p_value_empirical": self.p_value_empirical,
            "state_interaction": self.state_interaction.to_dict() if self.state_interaction else None,
            "abundance_qtl": self.abundance_qtl.to_dict() if self.abundance_qtl else None,
            "colocalization_gate": self.colocalization_gate.to_dict() if self.colocalization_gate else None,
            "tandem_repeat": self.tandem_repeat.to_dict() if self.tandem_repeat else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SingleCellRegulatoryContract:
        """Create SingleCellRegulatoryContract from dictionary representation."""
        raw_ct = data.get("cell_type", TenK10KImmuneCellType.NK_CD56_DIM)
        cell_type = TenK10KImmuneCellType(raw_ct) if raw_ct in TenK10KImmuneCellType._value2member_map_ else raw_ct

        raw_qtl = data.get("qtl_type", RegulatoryQTLType.COMMON_CIS_EQTL)
        qtl_type = (
            RegulatoryQTLType(raw_qtl)
            if raw_qtl in RegulatoryQTLType._value2member_map_
            else RegulatoryQTLType.COMMON_CIS_EQTL
        )

        si_data = data.get("state_interaction")
        state_interaction = CellStateInteractionContract.from_dict(si_data) if isinstance(si_data, dict) else si_data

        ab_data = data.get("abundance_qtl")
        abundance_qtl = CellAbundanceQTLContract.from_dict(ab_data) if isinstance(ab_data, dict) else ab_data

        coloc_data = data.get("colocalization_gate")
        colocalization_gate = (
            ColocalizationGateContract.from_dict(coloc_data) if isinstance(coloc_data, dict) else coloc_data
        )

        tr_data = data.get("tandem_repeat")
        tandem_repeat = TandemRepeatContract.from_dict(tr_data) if isinstance(tr_data, dict) else tr_data

        return cls(
            contract_id=str(data.get("contract_id", data.get("name", "sc_regulatory_contract"))),
            target_gene=str(data.get("target_gene", "")),
            variant=str(data.get("variant", "")),
            variant_type=str(data.get("variant_type", "snv")),
            cell_type=cell_type,
            qtl_type=qtl_type,
            is_cell_type_specific=bool(data.get("is_cell_type_specific", False)),
            is_distal_enhancer=bool(data.get("is_distal_enhancer", False)),
            distance_to_tss_bp=int(data.get("distance_to_tss_bp", 0)),
            beta_marginal=float(data.get("beta_marginal", 0.0)),
            standard_error=float(data.get("standard_error", 0.02)),
            p_value_empirical=float(data.get("p_value_empirical", 1e-7)),
            state_interaction=state_interaction,
            abundance_qtl=abundance_qtl,
            colocalization_gate=colocalization_gate,
            tandem_repeat=tandem_repeat,
            metadata=dict(data.get("metadata", {})),
        )


# ============================================================================
# Verifiable DNA Computation & RLVR Verification Layer (FineDNA Synergy)
# Grounded in FineDNA (Mid-training, SFT, and RLVR for genomic foundation models)
# ============================================================================


class DNAComputationType(str, Enum):
    """Formal DNA computational primitives inspired by FineDNA multi-stage tasks."""

    TRANSLATION = "translation"
    TRANSCRIPTION = "transcription"
    REVERSE_COMPLEMENT = "reverse_complement"
    ORF_DETECTION = "orf_detection"
    RESTRICTION_DIGEST = "restriction_digest"
    GC_SKEW_WINDOW = "gc_skew_window"
    CODON_OPTIMIZATION = "codon_optimization"
    KMER_FREQUENCY = "kmer_frequency"
    IUPAC_DEGENERATE_MATCH = "iupac_degenerate_match"

    def __str__(self) -> str:
        """Return the string value."""
        return self.value


class SequenceLocalizationMode(str, Enum):
    """Localization strategy for mapping DNA strands within large genomic sequences."""

    EXACT_MATCH = "exact_match"
    HAMMING_DISTANCE = "hamming_distance"
    LEVENSHTEIN_DISTANCE = "levenshtein_distance"
    IUPAC_PATTERN = "iupac_pattern"
    HOMOLOGY_FUZZY = "homology_fuzzy"

    def __str__(self) -> str:
        """Return the string value."""
        return self.value


class CoordinateSystem(str, Enum):
    """Coordinate convention for genomic interval representation."""

    ONE_BASED_CLOSED = "1_based_closed"  # Genomic convention: [start, end]
    ZERO_BASED_HALF_OPEN = "0_based_half_open"  # BED / Python convention: [start, end)

    def __str__(self) -> str:
        """Return the string value."""
        return self.value


class StrandOrientation(str, Enum):
    """Strand search orientation for DNA sequence localization."""

    FORWARD = "forward"
    REVERSE_COMPLEMENT = "reverse_complement"
    DUAL_STRAND = "dual_strand"

    def __str__(self) -> str:
        """Return the string value."""
        return self.value


class RLVRTaskDomain(str, Enum):
    """Domain of verifiable genomic reasoning for RLVR reward contracts."""

    SEQUENCE_LOCALIZATION = "sequence_localization"
    DNA_COMPUTATION = "dna_computation"
    VARIANT_EFFECT_GROUNDING = "variant_effect_grounding"
    FRAME_PRESERVATION = "frame_preservation"
    MOTIF_DISCOVERY = "motif_discovery"

    def __str__(self) -> str:
        """Return the string value."""
        return self.value


@dataclass
class SequenceLocalizationContract:
    """Formal contract for deterministically localizing DNA strands in massive sequences.

    Grounded in the FineDNA RLVR benchmark for sequence localization,
    formalizing exact start/end intervals, strand orientation, and mismatch tolerances.
    """

    contract_id: str
    query_pattern: str  # Subsequence or IUPAC motif to locate
    target_sequence: str = ""  # Full target sequence or accession reference
    mode: SequenceLocalizationMode = SequenceLocalizationMode.EXACT_MATCH
    coordinate_system: CoordinateSystem = CoordinateSystem.ONE_BASED_CLOSED
    strand_orientation: StrandOrientation = StrandOrientation.DUAL_STRAND
    max_mismatches: int = 0
    expected_coordinates: list[tuple[int, int, str]] = field(default_factory=list)  # (start, end, strand)
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def reverse_complement(seq: str) -> str:
        """Compute reverse complement supporting canonical and degenerate IUPAC nucleotide codes."""
        complement_map = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C",
            "U": "A",
            "a": "t",
            "t": "a",
            "c": "g",
            "g": "c",
            "u": "a",
            "R": "Y",
            "Y": "R",
            "S": "S",
            "W": "W",
            "K": "M",
            "M": "K",
            "B": "V",
            "D": "H",
            "H": "D",
            "V": "B",
            "N": "N",
            "r": "y",
            "y": "r",
            "s": "s",
            "w": "w",
            "k": "m",
            "m": "k",
            "b": "v",
            "d": "h",
            "h": "d",
            "v": "b",
            "n": "n",
        }
        return "".join(complement_map.get(base, base) for base in reversed(seq))

    def find_matches(self, target: str | None = None) -> list[tuple[int, int, str]]:
        """Search target sequence for matches according to contract mode and coordinate system.

        Returns a list of tuples: (start, end, strand)
        """
        import re

        seq = (target if target is not None else self.target_sequence).upper()
        pat = self.query_pattern.upper()
        if not seq or not pat:
            return []

        hits: list[tuple[int, int, str]] = []
        is_one_based = self.coordinate_system == CoordinateSystem.ONE_BASED_CLOSED

        def _iupac_to_regex(p: str) -> str:
            iupac_map = {
                "A": "A",
                "C": "C",
                "G": "G",
                "T": "[TU]",
                "U": "[TU]",
                "R": "[AG]",
                "Y": "[CTU]",
                "S": "[CG]",
                "W": "[ATU]",
                "K": "[GTU]",
                "M": "[AC]",
                "B": "[CGTU]",
                "D": "[AGTU]",
                "H": "[ACTU]",
                "V": "[ACG]",
                "N": "[ACGTU]",
            }
            return "".join(iupac_map.get(c, re.escape(c)) for c in p)

        # Forward strand search
        if self.strand_orientation in [StrandOrientation.FORWARD, StrandOrientation.DUAL_STRAND]:
            if self.mode == SequenceLocalizationMode.IUPAC_PATTERN:
                regex_pat = _iupac_to_regex(pat)
                for m in re.finditer(f"(?={regex_pat})", seq):
                    s = m.start()
                    m_full = re.match(regex_pat, seq[s:])
                    if m_full:
                        e = s + m_full.end()
                        start_coord = s + 1 if is_one_based else s
                        end_coord = e if is_one_based else e
                        hits.append((start_coord, end_coord, "+"))
            elif self.mode == SequenceLocalizationMode.EXACT_MATCH or self.max_mismatches == 0:
                idx = seq.find(pat)
                while idx != -1:
                    s = idx
                    e = s + len(pat)
                    start_coord = s + 1 if is_one_based else s
                    end_coord = e if is_one_based else e
                    hits.append((start_coord, end_coord, "+"))
                    idx = seq.find(pat, idx + 1)
            else:
                plen = len(pat)
                for s in range(len(seq) - plen + 1):
                    window = seq[s : s + plen]
                    mismatches = sum(1 for a, b in zip(window, pat) if a != b)
                    if mismatches <= self.max_mismatches:
                        start_coord = s + 1 if is_one_based else s
                        end_coord = s + plen if is_one_based else s + plen
                        hits.append((start_coord, end_coord, "+"))

        # Reverse complement strand search
        if self.strand_orientation in [StrandOrientation.REVERSE_COMPLEMENT, StrandOrientation.DUAL_STRAND]:
            rc_pat = self.reverse_complement(pat)
            if self.mode == SequenceLocalizationMode.IUPAC_PATTERN:
                regex_rc = _iupac_to_regex(rc_pat)
                for m in re.finditer(f"(?={regex_rc})", seq):
                    s = m.start()
                    m_full = re.match(regex_rc, seq[s:])
                    if m_full:
                        e = s + m_full.end()
                        start_coord = s + 1 if is_one_based else s
                        end_coord = e if is_one_based else e
                        hits.append((start_coord, end_coord, "-"))
            elif self.mode == SequenceLocalizationMode.EXACT_MATCH or self.max_mismatches == 0:
                idx = seq.find(rc_pat)
                while idx != -1:
                    s = idx
                    e = s + len(rc_pat)
                    start_coord = s + 1 if is_one_based else s
                    end_coord = e if is_one_based else e
                    hits.append((start_coord, end_coord, "-"))
                    idx = seq.find(rc_pat, idx + 1)
            else:
                plen = len(rc_pat)
                for s in range(len(seq) - plen + 1):
                    window = seq[s : s + plen]
                    mismatches = sum(1 for a, b in zip(window, rc_pat) if a != b)
                    if mismatches <= self.max_mismatches:
                        start_coord = s + 1 if is_one_based else s
                        end_coord = s + plen if is_one_based else s + plen
                        hits.append((start_coord, end_coord, "-"))

        return hits

    def verify_coordinates(self, candidate_start: int, candidate_end: int, strand: str = "+") -> bool:
        """Verify whether candidate coordinates match expected ground-truth coordinates."""
        targets = self.expected_coordinates if self.expected_coordinates else self.find_matches()
        for exp_s, exp_e, exp_str in targets:
            if candidate_start == exp_s and candidate_end == exp_e and (strand == exp_str or not exp_str):
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "query_pattern": self.query_pattern,
            "target_sequence": self.target_sequence,
            "mode": str(self.mode),
            "coordinate_system": str(self.coordinate_system),
            "strand_orientation": str(self.strand_orientation),
            "max_mismatches": self.max_mismatches,
            "expected_coordinates": [list(item) for item in self.expected_coordinates],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SequenceLocalizationContract:
        """Create from dictionary representation."""
        raw_mode = data.get("mode", SequenceLocalizationMode.EXACT_MATCH)
        mode = (
            SequenceLocalizationMode(raw_mode)
            if raw_mode in SequenceLocalizationMode._value2member_map_
            else SequenceLocalizationMode.EXACT_MATCH
        )

        raw_cs = data.get("coordinate_system", CoordinateSystem.ONE_BASED_CLOSED)
        cs = (
            CoordinateSystem(raw_cs)
            if raw_cs in CoordinateSystem._value2member_map_
            else CoordinateSystem.ONE_BASED_CLOSED
        )

        raw_so = data.get("strand_orientation", StrandOrientation.DUAL_STRAND)
        so = (
            StrandOrientation(raw_so)
            if raw_so in StrandOrientation._value2member_map_
            else StrandOrientation.DUAL_STRAND
        )

        raw_coords = data.get("expected_coordinates", [])
        expected_coordinates = [
            (int(c[0]), int(c[1]), str(c[2]) if len(c) > 2 else "+") for c in raw_coords if len(c) >= 2
        ]

        return cls(
            contract_id=str(data.get("contract_id", data.get("name", "seq_localization_contract"))),
            query_pattern=str(data.get("query_pattern", "")),
            target_sequence=str(data.get("target_sequence", "")),
            mode=mode,
            coordinate_system=cs,
            strand_orientation=so,
            max_mismatches=int(data.get("max_mismatches", 0)),
            expected_coordinates=expected_coordinates,
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class DNAComputationContract:
    """Contract for deterministic DNA transformations and sequence analytics.

    Formalizes the FineDNA SFT / RLVR computational categories:
    translation (6-frame), transcription, reverse complement, ORF detection,
    restriction enzyme digest, and GC skew profiles.
    """

    contract_id: str
    computation_type: DNAComputationType = DNAComputationType.TRANSLATION
    input_dna: str = ""
    genetic_code_table: int = 1  # 1: Standard, 2: Vertebrate Mito, etc.
    reading_frame: int = 1  # 1, 2, 3 (forward) or -1, -2, -3 (reverse)
    expected_output: str = ""
    orf_min_len_nt: int = 75
    restriction_enzyme: str | None = None
    gc_window_size: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)

    STANDARD_CODON_TABLE = {
        "TTT": "F",
        "TTC": "F",
        "TTA": "L",
        "TTG": "L",
        "TCT": "S",
        "TCC": "S",
        "TCA": "S",
        "TCG": "S",
        "TAT": "Y",
        "TAC": "Y",
        "TAA": "*",
        "TAG": "*",
        "TGT": "C",
        "TGC": "C",
        "TGA": "*",
        "TGG": "W",
        "CTT": "L",
        "CTC": "L",
        "CTA": "L",
        "CTG": "L",
        "CCT": "P",
        "CCC": "P",
        "CCA": "P",
        "CCG": "P",
        "CAT": "H",
        "CAC": "H",
        "CAA": "Q",
        "CAG": "Q",
        "CGT": "R",
        "CGC": "R",
        "CGA": "R",
        "CGG": "R",
        "ATT": "I",
        "ATC": "I",
        "ATA": "I",
        "ATG": "M",
        "ACT": "T",
        "ACC": "T",
        "ACA": "T",
        "ACG": "T",
        "AAT": "N",
        "AAC": "N",
        "AAA": "K",
        "AAG": "K",
        "AGT": "S",
        "AGC": "S",
        "AGA": "R",
        "AGG": "R",
        "GTT": "V",
        "GTC": "V",
        "GTA": "V",
        "GTG": "V",
        "GCT": "A",
        "GCC": "A",
        "GCA": "A",
        "GCG": "A",
        "GAT": "D",
        "GAC": "D",
        "GAA": "E",
        "GAG": "E",
        "GGT": "G",
        "GGC": "G",
        "GGA": "G",
        "GGG": "G",
    }

    RESTRICTION_SITES = {
        "EcoRI": "GAATTC",
        "BamHI": "GGATCC",
        "HindIII": "AAGCTT",
        "NotI": "GCGGCCGC",
        "XhoI": "CTCGAG",
        "PstI": "CTGCAG",
        "SmaI": "CCCGGG",
    }

    def execute_computation(self) -> str | list[Any]:
        """Execute deterministic computation on input_dna."""
        dna = self.input_dna.upper().replace(" ", "").replace("\n", "")
        ctype = self.computation_type

        if ctype == DNAComputationType.TRANSCRIPTION:
            return dna.replace("T", "U")

        if ctype == DNAComputationType.REVERSE_COMPLEMENT:
            return SequenceLocalizationContract.reverse_complement(dna)

        if ctype == DNAComputationType.TRANSLATION:
            seq = dna
            frame = self.reading_frame
            if frame < 0:
                seq = SequenceLocalizationContract.reverse_complement(seq)
                offset = abs(frame) - 1
            else:
                offset = max(0, frame - 1)
            pep = []
            for i in range(offset, len(seq) - 2, 3):
                codon = seq[i : i + 3]
                pep.append(self.STANDARD_CODON_TABLE.get(codon, "X"))
            return "".join(pep)

        if ctype == DNAComputationType.GC_SKEW_WINDOW:
            w = self.gc_window_size if self.gc_window_size > 0 else len(dna)
            if len(dna) < w:
                w = len(dna)
            if w <= 0:
                return [0.0]
            skews: list[float] = []
            for i in range(0, len(dna) - w + 1, w):
                sub = dna[i : i + w]
                g = sub.count("G")
                c = sub.count("C")
                skew = (g - c) / (g + c) if (g + c) > 0 else 0.0
                skews.append(round(skew, 4))
            return skews

        if ctype == DNAComputationType.RESTRICTION_DIGEST:
            enzyme = self.restriction_enzyme or "EcoRI"
            site = self.RESTRICTION_SITES.get(enzyme, "GAATTC")
            fragments = []
            start = 0
            idx = dna.find(site)
            while idx != -1:
                cut = idx + 1
                fragments.append(dna[start:cut])
                start = cut
                idx = dna.find(site, start)
            fragments.append(dna[start:])
            return fragments

        if ctype == DNAComputationType.ORF_DETECTION:
            min_len = max(9, self.orf_min_len_nt)
            orfs: list[dict[str, Any]] = []
            for frame in (1, 2, 3):
                offset = frame - 1
                i = offset
                while i < len(dna) - 2:
                    if dna[i : i + 3] == "ATG":
                        start_pos = i + 1
                        for j in range(i + 3, len(dna) - 2, 3):
                            if dna[j : j + 3] in ["TAA", "TAG", "TGA"]:
                                end_pos = j + 3
                                length_nt = end_pos - start_pos + 1
                                if length_nt >= min_len:
                                    orfs.append(
                                        {
                                            "start": start_pos,
                                            "end": end_pos,
                                            "strand": "+",
                                            "frame": frame,
                                            "length_nt": length_nt,
                                            "orf_sequence": dna[start_pos - 1 : end_pos],
                                        }
                                    )
                                i = j
                                break
                    i += 3
            return orfs

        return dna

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "computation_type": str(self.computation_type),
            "input_dna": self.input_dna,
            "genetic_code_table": self.genetic_code_table,
            "reading_frame": self.reading_frame,
            "expected_output": self.expected_output,
            "orf_min_len_nt": self.orf_min_len_nt,
            "restriction_enzyme": self.restriction_enzyme,
            "gc_window_size": self.gc_window_size,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DNAComputationContract:
        """Create from dictionary representation."""
        raw_type = data.get("computation_type", DNAComputationType.TRANSLATION)
        ctype = (
            DNAComputationType(raw_type)
            if raw_type in DNAComputationType._value2member_map_
            else DNAComputationType.TRANSLATION
        )

        return cls(
            contract_id=str(data.get("contract_id", data.get("name", "dna_computation_contract"))),
            computation_type=ctype,
            input_dna=str(data.get("input_dna", data.get("sequence", ""))),
            genetic_code_table=int(data.get("genetic_code_table", 1)),
            reading_frame=int(data.get("reading_frame", 1)),
            expected_output=str(data.get("expected_output", "")),
            orf_min_len_nt=int(data.get("orf_min_len_nt", 75)),
            restriction_enzyme=data.get("restriction_enzyme"),
            gc_window_size=int(data.get("gc_window_size", 100)),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class VerifiableRewardContract:
    """Formal verifiable reward contract for Reinforcement Learning with Verifiable Rewards (RLVR).

    Directly models FineDNA RLVR verifier architectures, providing deterministic
    grading, mathematical/biochemical truth verification, and cryptographic evaluation proofs.
    """

    task_id: str
    domain: RLVRTaskDomain = RLVRTaskDomain.SEQUENCE_LOCALIZATION
    ground_truth_reference: str = ""
    tolerance: float = 0.0
    reward_success: float = 1.0
    reward_failure: float = 0.0
    deterministic_evaluator: str = "gfl_deterministic_reward_oracle"
    localization_contract: SequenceLocalizationContract | None = None
    computation_contract: DNAComputationContract | None = None
    verification_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def evaluate_reward(self, candidate_answer: str) -> tuple[float, bool]:
        """Evaluate candidate answer deterministically against ground truth contract.

        Returns (reward_value, is_verified).
        """
        clean_candidate = candidate_answer.strip().upper()
        clean_truth = self.ground_truth_reference.strip().upper()

        if clean_candidate == clean_truth and clean_truth != "":
            return (self.reward_success, True)

        # If localization contract attached, check coordinates
        if self.localization_contract:
            try:
                parts = clean_candidate.replace(" ", "").split(":")
                coords = parts[0].split("-")
                strand = parts[1] if len(parts) > 1 else "+"
                if len(coords) == 2:
                    c_start, c_end = int(coords[0]), int(coords[1])
                    if self.localization_contract.verify_coordinates(c_start, c_end, strand):
                        return (self.reward_success, True)
            except (ValueError, IndexError):
                pass

        # If computation contract attached, check direct execution
        if self.computation_contract:
            res = self.computation_contract.execute_computation()
            if isinstance(res, str) and clean_candidate == res.strip().upper():
                return (self.reward_success, True)

        return (self.reward_failure, False)

    def generate_verification_proof(self, candidate_answer: str) -> str:
        """Generate deterministic cryptographic proof for verified reward."""
        import hashlib

        payload = f"{self.task_id}:{self.domain}:{candidate_answer.strip()}".encode()
        return hashlib.sha256(payload).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "domain": str(self.domain),
            "ground_truth_reference": self.ground_truth_reference,
            "tolerance": self.tolerance,
            "reward_success": self.reward_success,
            "reward_failure": self.reward_failure,
            "deterministic_evaluator": self.deterministic_evaluator,
            "localization_contract": self.localization_contract.to_dict() if self.localization_contract else None,
            "computation_contract": self.computation_contract.to_dict() if self.computation_contract else None,
            "verification_hash": self.verification_hash,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VerifiableRewardContract:
        """Create from dictionary representation."""
        raw_dom = data.get("domain", RLVRTaskDomain.SEQUENCE_LOCALIZATION)
        domain = (
            RLVRTaskDomain(raw_dom)
            if raw_dom in RLVRTaskDomain._value2member_map_
            else RLVRTaskDomain.SEQUENCE_LOCALIZATION
        )

        loc_data = data.get("localization_contract")
        localization_contract = (
            SequenceLocalizationContract.from_dict(loc_data) if isinstance(loc_data, dict) else loc_data
        )

        comp_data = data.get("computation_contract")
        computation_contract = DNAComputationContract.from_dict(comp_data) if isinstance(comp_data, dict) else comp_data

        return cls(
            task_id=str(data.get("task_id", data.get("name", "rlvr_reward_contract"))),
            domain=domain,
            ground_truth_reference=str(data.get("ground_truth_reference", "")),
            tolerance=float(data.get("tolerance", 0.0)),
            reward_success=float(data.get("reward_success", 1.0)),
            reward_failure=float(data.get("reward_failure", 0.0)),
            deterministic_evaluator=str(data.get("deterministic_evaluator", "gfl_deterministic_reward_oracle")),
            localization_contract=localization_contract,
            computation_contract=computation_contract,
            verification_hash=str(data.get("verification_hash", "")),
            metadata=dict(data.get("metadata", {})),
        )


# ============================================================================
# Autonomous Wet-Lab Execution, Synthesizability & Epistemic Closed-Loop
# Grounded in AutoDNA (Nature 2026; Heidi Ledford; Chen, Wu et al., SJTU)
# DOI: 10.1038/d41586-026-03552-8
# ============================================================================


class SynthesisChemistry(str, Enum):
    """Supported biomolecular synthesis chemistry modes."""

    ENZYMATIC_TDT = "enzymatic_tdt"  # Terminal deoxynucleotidyl transferase (aqueous, green synthesis)
    CHEMICAL_PHOSPHORAMIDITE = "chemical_phosphoramidite"  # Solid-phase chemical phosphoramidite chemistry
    CELL_FREE_CLONING = "cell_free_cloning"  # Isothermal assembly / rolling circle cell-free synthesis


class WetLabInstrumentType(str, Enum):
    """Categorized laboratory instrument types in an autonomous self-driving laboratory."""

    SYNTHESIZER = "synthesizer"
    THERMOCYCLER = "thermocycler"
    LIQUID_HANDLER = "liquid_handler"
    CENTRIFUGE = "centrifuge"
    ELECTROPHORESIS = "electrophoresis"
    SEQUENCER = "sequencer"
    ROBOTIC_ARM = "robotic_arm"
    INCUBATOR = "incubator"


class BiosecurityRiskTier(str, Enum):
    """Risk stratification tiers for autonomous wet-lab synthesis dispatch."""

    BENIGN_RESEARCH = "benign_research"  # Standard non-pathogenic DNA/RNA construct
    MONITORED_GENE = "monitored_gene"  # Housekeeping or regulated gene requiring audit logging
    RESTRICTED_AGENT = "restricted_agent"  # Controlled dual-use pathogen or virulence factor
    PROHIBITED_TOXIN = "prohibited_toxin"  # Regulated select agent toxin (strict dispatch block)


class TelemetryReadoutType(str, Enum):
    """Empirical assay readout modalities for closed-loop telemetry reconciliation."""

    NGS_FASTQ_READS = "ngs_fastq_reads"
    SANGER_CHROMATOGRAM = "sanger_chromatogram"
    STEPWISE_SYNTHESIS_YIELD = "stepwise_synthesis_yield"
    GEL_ELECTROPHORESIS_BAND = "gel_electrophoresis_band"
    MASS_SPECTROMETRY = "mass_spectrometry"


@dataclass
class SynthesizabilityGateContract:
    """Biophysical manufacturability and synthesizability contract for wet-lab fabrication.

    Enforces kinetic, thermodynamic, and sequence complexity constraints:
    - Homopolymer runs (TdT enzymatic slipping threshold <= 4 bp)
    - GC content window [40%, 60%]
    - Hairpin secondary structure delta G (> -8.0 kcal/mol)
    - Linguistic sequence complexity (> 0.45)
    """

    chemistry: SynthesisChemistry = SynthesisChemistry.ENZYMATIC_TDT
    max_homopolymer: int = 4
    min_gc_content: float = 0.40
    max_gc_content: float = 0.60
    min_hairpin_free_energy: float = -8.0
    min_complexity: float = 0.45
    target_length_limit: int = 2000
    passed: bool = True
    calculated_metrics: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "chemistry": str(self.chemistry),
            "max_homopolymer": self.max_homopolymer,
            "min_gc_content": self.min_gc_content,
            "max_gc_content": self.max_gc_content,
            "min_hairpin_free_energy": self.min_hairpin_free_energy,
            "min_complexity": self.min_complexity,
            "target_length_limit": self.target_length_limit,
            "passed": self.passed,
            "calculated_metrics": dict(self.calculated_metrics),
            "issues": list(self.issues),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SynthesizabilityGateContract:
        """Create from dictionary representation."""
        raw_chem = data.get("chemistry", SynthesisChemistry.ENZYMATIC_TDT)
        chemistry = (
            SynthesisChemistry(raw_chem)
            if raw_chem in SynthesisChemistry._value2member_map_
            else SynthesisChemistry.ENZYMATIC_TDT
        )
        return cls(
            chemistry=chemistry,
            max_homopolymer=int(data.get("max_homopolymer", 4)),
            min_gc_content=float(data.get("min_gc_content", 0.40)),
            max_gc_content=float(data.get("max_gc_content", 0.60)),
            min_hairpin_free_energy=float(data.get("min_hairpin_free_energy", -8.0)),
            min_complexity=float(data.get("min_complexity", 0.45)),
            target_length_limit=int(data.get("target_length_limit", 2000)),
            passed=bool(data.get("passed", True)),
            calculated_metrics=dict(data.get("calculated_metrics", {})),
            issues=[str(i) for i in data.get("issues", [])],
        )


@dataclass
class BiosecurityClearanceContract:
    """Pre-dispatch biosecurity screening and cryptographic authorization contract."""

    risk_tier: BiosecurityRiskTier = BiosecurityRiskTier.BENIGN_RESEARCH
    screening_passed: bool = True
    watermark_verified: bool = True
    clearance_hash: str = ""
    authorization_token: str = ""
    operator_id: str = "autodna_planner_agent"
    matched_signatures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "risk_tier": str(self.risk_tier),
            "screening_passed": self.screening_passed,
            "watermark_verified": self.watermark_verified,
            "clearance_hash": self.clearance_hash,
            "authorization_token": self.authorization_token,
            "operator_id": self.operator_id,
            "matched_signatures": list(self.matched_signatures),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BiosecurityClearanceContract:
        """Create from dictionary representation."""
        raw_tier = data.get("risk_tier", BiosecurityRiskTier.BENIGN_RESEARCH)
        risk_tier = (
            BiosecurityRiskTier(raw_tier)
            if raw_tier in BiosecurityRiskTier._value2member_map_
            else BiosecurityRiskTier.BENIGN_RESEARCH
        )
        return cls(
            risk_tier=risk_tier,
            screening_passed=bool(data.get("screening_passed", True)),
            watermark_verified=bool(data.get("watermark_verified", True)),
            clearance_hash=str(data.get("clearance_hash", "")),
            authorization_token=str(data.get("authorization_token", "")),
            operator_id=str(data.get("operator_id", "autodna_planner_agent")),
            matched_signatures=[str(s) for s in data.get("matched_signatures", [])],
        )


@dataclass
class WetLabStepContract:
    """Single instrument execution instruction within an autonomous laboratory workflow."""

    step_id: str
    instrument: WetLabInstrumentType
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    duration_seconds: int = 0
    temperature_celsius: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "instrument": str(self.instrument),
            "operation": self.operation,
            "parameters": dict(self.parameters),
            "duration_seconds": self.duration_seconds,
            "temperature_celsius": self.temperature_celsius,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WetLabStepContract:
        """Create from dictionary representation."""
        raw_inst = data.get("instrument", WetLabInstrumentType.SYNTHESIZER)
        instrument = (
            WetLabInstrumentType(raw_inst)
            if raw_inst in WetLabInstrumentType._value2member_map_
            else WetLabInstrumentType.SYNTHESIZER
        )
        temp = data.get("temperature_celsius")
        return cls(
            step_id=str(data.get("step_id", "step_01")),
            instrument=instrument,
            operation=str(data.get("operation", "")),
            parameters=dict(data.get("parameters", {})),
            duration_seconds=int(data.get("duration_seconds", 0)),
            temperature_celsius=float(temp) if temp is not None else None,
        )


@dataclass
class ExperimentalTelemetryContract:
    """Empirical assay readout container for closed-loop telemetry reconciliation."""

    readout_type: TelemetryReadoutType = TelemetryReadoutType.STEPWISE_SYNTHESIS_YIELD
    observed_yield: float | None = None
    observed_sequence: str = ""
    concordance_rate: float = 1.0
    raw_telemetry_uri: str = ""
    quality_qscore: float = 38.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "readout_type": str(self.readout_type),
            "observed_yield": self.observed_yield,
            "observed_sequence": self.observed_sequence,
            "concordance_rate": self.concordance_rate,
            "raw_telemetry_uri": self.raw_telemetry_uri,
            "quality_qscore": self.quality_qscore,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExperimentalTelemetryContract:
        """Create from dictionary representation."""
        raw_readout = data.get("readout_type", TelemetryReadoutType.STEPWISE_SYNTHESIS_YIELD)
        readout_type = (
            TelemetryReadoutType(raw_readout)
            if raw_readout in TelemetryReadoutType._value2member_map_
            else TelemetryReadoutType.STEPWISE_SYNTHESIS_YIELD
        )
        yield_val = data.get("observed_yield")
        return cls(
            readout_type=readout_type,
            observed_yield=float(yield_val) if yield_val is not None else None,
            observed_sequence=str(data.get("observed_sequence", "")),
            concordance_rate=float(data.get("concordance_rate", 1.0)),
            raw_telemetry_uri=str(data.get("raw_telemetry_uri", "")),
            quality_qscore=float(data.get("quality_qscore", 38.0)),
        )


@dataclass
class AutonomousExecutionContract:
    """Formal GFL Root Contract for Autonomous Wet-Lab Protocol Dispatch & Closed-Loop Execution.

    Grounded in AutoDNA (Nature 2026; Heidi Ledford; Chen, Wu et al., SJTU; DOI: 10.1038/d41586-026-03552-8):
    - Validates biophysical manufacturability and synthesizability gates before robotic actuation.
    - Enforces biosecurity air-gap verification and SHA-256 cryptographic authorization.
    - Compiles declarative multi-instrument sequences into SiLA 2 / AutoDNA JSON IR.
    - Ingests empirical assay telemetry, reconciling physical sequencing reads with in silico claims.
    """

    protocol_id: str
    target_sequence: str
    target_entity: str = ""
    synthesizability: SynthesizabilityGateContract | None = None
    biosecurity: BiosecurityClearanceContract | None = None
    steps: list[WetLabStepContract] = field(default_factory=list)
    telemetry: ExperimentalTelemetryContract | None = None
    evidence_promotion: str = "EMPIRICAL_VERIFIED"
    execution_status: str = "QUEUED"
    export_format: str = "sila2_json"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "protocol_id": self.protocol_id,
            "target_sequence": self.target_sequence,
            "target_entity": self.target_entity,
            "synthesizability": self.synthesizability.to_dict() if self.synthesizability else None,
            "biosecurity": self.biosecurity.to_dict() if self.biosecurity else None,
            "steps": [s.to_dict() for s in self.steps],
            "telemetry": self.telemetry.to_dict() if self.telemetry else None,
            "evidence_promotion": self.evidence_promotion,
            "execution_status": self.execution_status,
            "export_format": self.export_format,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AutonomousExecutionContract:
        """Create from dictionary representation."""
        synth_data = data.get("synthesizability")
        synthesizability = (
            SynthesizabilityGateContract.from_dict(synth_data) if isinstance(synth_data, dict) else synth_data
        )

        bio_data = data.get("biosecurity")
        biosecurity = BiosecurityClearanceContract.from_dict(bio_data) if isinstance(bio_data, dict) else bio_data

        raw_steps = data.get("steps", [])
        steps = [WetLabStepContract.from_dict(s) if isinstance(s, dict) else s for s in raw_steps]

        telem_data = data.get("telemetry")
        telemetry = ExperimentalTelemetryContract.from_dict(telem_data) if isinstance(telem_data, dict) else telem_data

        return cls(
            protocol_id=str(data.get("protocol_id", data.get("name", "autodna_protocol"))),
            target_sequence=str(data.get("target_sequence", "")),
            target_entity=str(data.get("target_entity", "")),
            synthesizability=synthesizability,
            biosecurity=biosecurity,
            steps=steps,
            telemetry=telemetry,
            evidence_promotion=str(data.get("evidence_promotion", "EMPIRICAL_VERIFIED")),
            execution_status=str(data.get("execution_status", "QUEUED")),
            export_format=str(data.get("export_format", "sila2_json")),
            metadata=dict(data.get("metadata", {})),
        )


# ============================================================================
# Cloud-Native Biological Lakehouse & Frozen Annotation Engine (bioc-on-ice)
# Grounded in Bioconductor on Ice (Sean Davis, Cloudflare R2 / Apache Parquet + DuckDB)
# Manifest: https://bioconice.cancerdatasci.org/data/latest/manifest.json
# ============================================================================


class BiocSchemaType(str, Enum):
    """Canonical database schemas in the bioc-on-ice biological lakehouse."""

    ANNOTATION = "annotation"  # Genes, transcripts, exons, identifier mappings
    CLINICAL = "clinical"  # Clinical associations, GWAS catalog, traits
    ONTOLOGY = "ontology"  # Cell Ontology (CL), Gene Ontology (GO), Human Phenotype (HP), DOID
    PROVENANCE = "provenance"  # Release snapshots, file SHA-256 hashes, source versions
    RAW = "raw"  # Direct NCBI gene2ensembl, gene_info, Ensembl GTF dumps
    REFERENCE = "reference"  # Reference genomes, chromosome maps
    RESOURCE = "resource"  # Catalogs and external curated assets


class LakehouseQueryBackend(str, Enum):
    """Execution backend for lakehouse Parquet queries."""

    DUCKDB_HTTPFS = "duckdb_httpfs"  # High-performance zero-download DuckDB pushdown SQL
    ARROW_STREAMING = "arrow_streaming"  # PyArrow streaming dataset scanner
    MANIFEST_INDEX = "manifest_index"  # Fast offline/online manifest metadata index


class ReferenceGenomeBuild(str, Enum):
    """Supported reference genome builds for lakehouse coordinates."""

    GRCH38 = "GRCh38"
    GRCH37 = "GRCh37"
    T2T_CHM13 = "T2T-CHM13"
    GRCM39 = "GRCm39"


@dataclass
class LakehouseTableMetadata:
    """Metadata and cryptographic checksum for a single table in the biological lakehouse."""

    schema: BiocSchemaType
    table: str
    path: str
    row_count: int
    bytes_size: int
    sha256: str = ""
    comment: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "schema": self.schema.value if hasattr(self.schema, "value") else str(self.schema),
            "table": self.table,
            "path": self.path,
            "row_count": self.row_count,
            "bytes_size": self.bytes_size,
            "sha256": self.sha256,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LakehouseTableMetadata:
        """Create from dictionary representation."""
        raw_schema = data.get("schema", BiocSchemaType.ANNOTATION)
        schema = (
            BiocSchemaType(raw_schema) if raw_schema in BiocSchemaType._value2member_map_ else BiocSchemaType.ANNOTATION
        )
        return cls(
            schema=schema,
            table=str(data.get("table", "")),
            path=str(data.get("path", "")),
            row_count=int(data.get("row_count", 0)),
            bytes_size=int(data.get("bytes", data.get("bytes_size", 0))),
            sha256=str(data.get("sha256", "")),
            comment=str(data.get("comment", "")),
        )


@dataclass
class BiocReleaseMetadata:
    """Full snapshot release manifest metadata from bioc-on-ice."""

    manifest_version: int = 1
    release_id: str = "latest"
    published_at: str = ""
    git_sha: str = ""
    base_url: str = "https://data.bioconice.cancerdatasci.org/latest"
    tables: list[LakehouseTableMetadata] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "manifest_version": self.manifest_version,
            "release_id": self.release_id,
            "published_at": self.published_at,
            "git_sha": self.git_sha,
            "base_url": self.base_url,
            "tables": [t.to_dict() for t in self.tables],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BiocReleaseMetadata:
        """Create from dictionary representation."""
        raw_tables = data.get("tables", [])
        tables = [LakehouseTableMetadata.from_dict(t) if isinstance(t, dict) else t for t in raw_tables]
        return cls(
            manifest_version=int(data.get("manifest_version", 1)),
            release_id=str(data.get("release", data.get("release_id", "latest"))),
            published_at=str(data.get("published_at", "")),
            git_sha=str(data.get("git_sha", "")),
            base_url=str(data.get("base_url", "https://data.bioconice.cancerdatasci.org/latest")),
            tables=tables,
        )


@dataclass
class LakehouseQueryContract:
    """Declarative query contract over a bioc-on-ice lakehouse table."""

    schema: BiocSchemaType = BiocSchemaType.ANNOTATION
    table: str = "gene"
    columns: list[str] = field(default_factory=list)
    filter_sql: str = ""
    limit: int = 50
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "schema": self.schema.value if hasattr(self.schema, "value") else str(self.schema),
            "table": self.table,
            "columns": list(self.columns),
            "filter_sql": self.filter_sql,
            "limit": self.limit,
            "parameters": dict(self.parameters),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LakehouseQueryContract:
        """Create from dictionary representation."""
        raw_schema = data.get("schema", BiocSchemaType.ANNOTATION)
        schema = (
            BiocSchemaType(raw_schema) if raw_schema in BiocSchemaType._value2member_map_ else BiocSchemaType.ANNOTATION
        )
        return cls(
            schema=schema,
            table=str(data.get("table", "gene")),
            columns=[str(c) for c in data.get("columns", [])],
            filter_sql=str(data.get("filter_sql", "")),
            limit=int(data.get("limit", 50)),
            parameters=dict(data.get("parameters", {})),
        )


@dataclass
class BiocIceContract:
    """Formal GFL Root Contract for Cloud-Native Biological Lakehouse & Frozen Annotations.

    Grounded in bioc-on-ice (Bioconductor on Ice; Sean Davis; 100GB, 4B rows, 81 tables):
    - Epistemic Pinning: Binds analysis to frozen release snapshots (e.g. '2026-11-08' or 'latest').
    - Pushdown Execution: Zero-download HTTP range queries via DuckDB / Parquet streaming.
    - Lakehouse Validation: Ground truth resolution for genes, transcripts, and ontologies.
    """

    release_id: str = "latest"
    genome_build: ReferenceGenomeBuild = ReferenceGenomeBuild.GRCH38
    base_url: str = "https://data.bioconice.cancerdatasci.org/latest"
    query_backend: LakehouseQueryBackend = LakehouseQueryBackend.MANIFEST_INDEX
    queries: list[LakehouseQueryContract] = field(default_factory=list)
    pinned_tables: list[str] = field(default_factory=list)
    verified_manifest_sha: str = ""
    cache_dir: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "release_id": self.release_id,
            "genome_build": self.genome_build.value if hasattr(self.genome_build, "value") else str(self.genome_build),
            "base_url": self.base_url,
            "query_backend": self.query_backend.value
            if hasattr(self.query_backend, "value")
            else str(self.query_backend),
            "queries": [q.to_dict() for q in self.queries],
            "pinned_tables": list(self.pinned_tables),
            "verified_manifest_sha": self.verified_manifest_sha,
            "cache_dir": self.cache_dir,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BiocIceContract:
        """Create from dictionary representation."""
        raw_build = data.get("genome_build", ReferenceGenomeBuild.GRCH38)
        genome_build = (
            ReferenceGenomeBuild(raw_build)
            if raw_build in ReferenceGenomeBuild._value2member_map_
            else ReferenceGenomeBuild.GRCH38
        )

        raw_backend = data.get("query_backend", LakehouseQueryBackend.MANIFEST_INDEX)
        backend_aliases = {
            "duckdb": LakehouseQueryBackend.DUCKDB_HTTPFS,
            "duckdb_httpfs": LakehouseQueryBackend.DUCKDB_HTTPFS,
            "arrow": LakehouseQueryBackend.ARROW_STREAMING,
            "arrow_streaming": LakehouseQueryBackend.ARROW_STREAMING,
            "polars": LakehouseQueryBackend.ARROW_STREAMING,
            "manifest_index": LakehouseQueryBackend.MANIFEST_INDEX,
            "manifest": LakehouseQueryBackend.MANIFEST_INDEX,
            "index": LakehouseQueryBackend.MANIFEST_INDEX,
        }
        if isinstance(raw_backend, str) and raw_backend.lower() in backend_aliases:
            query_backend = backend_aliases[raw_backend.lower()]
        elif raw_backend in LakehouseQueryBackend._value2member_map_:
            query_backend = LakehouseQueryBackend(raw_backend)
        else:
            query_backend = LakehouseQueryBackend.MANIFEST_INDEX

        raw_queries = data.get("queries", [])
        queries = [LakehouseQueryContract.from_dict(q) if isinstance(q, dict) else q for q in raw_queries]

        raw_pinned = data.get("pinned_tables", [])
        pinned_tables = [str(p) for p in raw_pinned] if isinstance(raw_pinned, list) else []

        return cls(
            release_id=str(data.get("release_id", data.get("release", "latest"))),
            genome_build=genome_build,
            base_url=str(data.get("base_url", "https://data.bioconice.cancerdatasci.org/latest")),
            query_backend=query_backend,
            queries=queries,
            pinned_tables=pinned_tables,
            verified_manifest_sha=str(data.get("verified_manifest_sha", "")),
            cache_dir=str(data["cache_dir"]) if data.get("cache_dir") else None,
            metadata=dict(data.get("metadata", {})),
        )


# Export all public types
__all__ = [
    # Enums
    "DataType",
    "ExperimentType",
    "AnalysisStrategy",
    "AviModality",
    "CoDependencyTier",
    "CausalLevel",
    "CandidateStatus",
    "ConsensusModel",
    "BiosyntheticDomainType",
    "DecisionStrategy",
    "DecisionMode",
    "ClinVarSignificance",
    "RetroelementType",
    "CatalyticResidueRole",
    "FragmentomicsModality",
    "ViralInteractomeType",
    "SignalModality",
    "EpistemicLevel",
    "ProfileResolution",
    "ProfileLossMetric",
    "StrandMode",
    "SomaticDriftModel",
    "EnsembleGenerator",
    "SolvationModel",
    "PhageCapsidArchitecture",
    "PerturbationType",
    "CellAtlasReference",
    "ForceFieldFamily",
    "SimulationEngine",
    "WaterModel",
    "HelixConformation",
    "ViewerTrackType",
    "VariantPathogenicity",
    "DNAComputationType",
    "SequenceLocalizationMode",
    "CoordinateSystem",
    "StrandOrientation",
    "RLVRTaskDomain",
    "SynthesisChemistry",
    "WetLabInstrumentType",
    "BiosecurityRiskTier",
    "TelemetryReadoutType",
    "BiocSchemaType",
    "LakehouseQueryBackend",
    "ReferenceGenomeBuild",
    # Dataclasses
    "IOContract",
    "TensorContract",
    "BlockContract",
    "ExperimentParams",
    "Experiment",
    "Analysis",
    "Design",
    "Optimize",
    "GFLAST",
    "AviScore",
    "RegulatoryMotifAnnotation",
    "TissueRegulatoryEffect",
    "NonCodingRegulatoryContract",
    "VariantImpact",
    "DepMapCoDependency",
    "CausalTransitionNode",
    "MultiModelConsensus",
    "RescuePolicy",
    "RestraintType",
    "ExperimentalRestraintsContract",
    "RunsNPosesMetric",
    "LigandConditionedPocketContract",
    "BoltzmannEnsembleContract",
    "CrypticPocketContract",
    "ThermodynamicBindingContract",
    "BiodefenseSafetyGate",
    "BacteriophageTherapyContract",
    "PerturbationReadout",
    "VirtualCellPerturbationContract",
    "InterEngineEnergyTolerance",
    "ForceFieldEngineContract",
    "ViewerVariantAnnotation",
    "ViewerExonAnnotation",
    "ViewerEpigeneticMark",
    "ViewerCrisprPamSite",
    "DNAViewerContract",
    "AtlasModality",
    "SwarmGranularity",
    "PhenotypicRelationshipType",
    "SwarmReasoningPolicy",
    "ParalogDivergenceContract",
    "PerturbationAtlasTarget",
    "ReasoningAtlasEdge",
    "ReasoningAtlasGraph",
    "PerturbationAtlasContract",
    "WatermarkModality",
    "WatermarkAlgorithm",
    "WatermarkProvenance",
    "WatermarkViabilityGuardrails",
    "WatermarkDetectionPolicy",
    "WatermarkVerificationResult",
    "BiosecurityWatermarkContract",
    "CarbonXTaskType",
    "CarbonXModelSize",
    "CarbonXTargetLocus",
    "CarbonXQuery",
    "CarbonXReasoningResult",
    "GenomicLLMContract",
    "ProTokModality",
    "ProTokConditioningMode",
    "ProTokResidueToken",
    "ProTokDropoutPolicy",
    "ProTokVerificationResult",
    "ProTokContract",
    "PhysicsRefinementPolicy",
    "MegasynthaseDomain",
    "MegasynthaseModule",
    "BGCAssemblyContract",
    "DecisionOption",
    "DecisionOutcome",
    "DecisionContract",
    "ExhaustiveCoverageContract",
    "DeterministicReplayContract",
    "RetroelementArchitecture",
    "CatalyticResidue",
    "SubstrateLigandContainer",
    "CatalyticMotif",
    "EnzymeDesignContract",
    "CassetteArchitecture",
    "ReadoutModality",
    "TapeRecorderContract",
    "LineageNode",
    "ProgramEvolutionContract",
    "EpigeneticDeconvolutionContract",
    "NaturalLanguageConditioningContract",
    "TextConditionedDesignContract",
    "AlphaGenomeLocusLink",
    "ViralInteractomeComplexContract",
    "CountHeadContract",
    "ProfileHeadContract",
    "RegulatoryTrackContract",
    "RegulatoryProfileContract",
    "SomaticDriftSimulationContract",
    "SomaticInstabilityContract",
    "DNABreathingModel",
    "TFBindingCouplingMode",
    "DNABreathingProfile",
    "TFBreathingCouplingContract",
    "DNADynamicsContract",
    "TenK10KImmuneCellType",
    "RegulatoryQTLType",
    "CellStateAxis",
    "CellStateInteractionContract",
    "CellAbundanceQTLContract",
    "ColocalizationGateContract",
    "TandemRepeatContract",
    "SingleCellRegulatoryContract",
    "SequenceLocalizationContract",
    "DNAComputationContract",
    "VerifiableRewardContract",
    "SynthesizabilityGateContract",
    "BiosecurityClearanceContract",
    "WetLabStepContract",
    "ExperimentalTelemetryContract",
    "AutonomousExecutionContract",
    "LakehouseTableMetadata",
    "BiocReleaseMetadata",
    "LakehouseQueryContract",
    "BiocIceContract",
    # Validation types
    "ValidationError",
    "ValidationResult",
    # Inference types
    "InferenceResult",
    # Type aliases
    "GFLValue",
    "GFLDict",
]
