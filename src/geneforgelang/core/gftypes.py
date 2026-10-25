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
        }
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
    # Validation types
    "ValidationError",
    "ValidationResult",
    # Inference types
    "InferenceResult",
    # Type aliases
    "GFLValue",
    "GFLDict",
]
