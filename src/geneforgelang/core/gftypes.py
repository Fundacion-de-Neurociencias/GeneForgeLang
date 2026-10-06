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

        if "metadata" in data:
            ast.metadata = dict(data["metadata"])

        return ast


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
        if self.clinvar_significance.is_vus and self.avi_score and self.avi_score.is_high_impact:
            return True
        return False

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
    PROTEIN_MPNN = "protein_mpnn"
    LIGAND_MPNN = "ligand_mpnn"

    def __str__(self) -> str:
        """Return the enum value as string."""
        return self.value


@dataclass
class MultiModelConsensus:
    """Cross-model consensus validation metrics (Baker Lab 2026 RFO consensus).

    Evaluates structural predictions across independent models (AF3, RF3, Boltz)
    to eliminate single-predictor over-fitting.
    """

    af3_iptm: float | None = None
    af3_ipae: float | None = None
    rf3_confidence: float | None = None
    boltz_confidence: float | None = None
    plddt_mean: float | None = None

    def passes_consensus(
        self,
        min_iptm: float = 0.8,
        max_ipae: float = 2.5,
        min_confidence: float = 0.8,
    ) -> bool:
        """Check if candidate satisfies the rigorous three-model consensus thresholds."""
        if self.af3_iptm is not None and self.af3_iptm < min_iptm:
            return False
        if self.af3_ipae is not None and self.af3_ipae > max_ipae:
            return False
        if self.rf3_confidence is not None and self.rf3_confidence < min_confidence:
            return False
        if self.boltz_confidence is not None and self.boltz_confidence < min_confidence:
            return False
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
            "plddt_mean": self.plddt_mean,
            "passes_consensus": self.passes_consensus(),
            "is_near_miss": self.is_near_miss(),
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "selected_option_id": self.selected_option_id,
            "confidence": self.confidence,
            "is_ambiguous": self.is_ambiguous,
            "options_evaluated": [opt.to_dict() for opt in self.options_evaluated],
            "calibration_method": self.calibration_method,
            "latency_ms": self.latency_ms,
        }


@dataclass
class DecisionContract:
    """Formal IO contract for pre-screening routing and discrete option arbitration."""

    task_id: str
    allowed_options: list[str]
    confidence_threshold: float = 0.85
    fallback_strategy: str = "ESCALATE_TO_SYSTEM2"
    strategy: DecisionStrategy = DecisionStrategy.PERMUTATION_INVARIANT_LOGITS

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "allowed_options": self.allowed_options,
            "confidence_threshold": self.confidence_threshold,
            "fallback_strategy": self.fallback_strategy,
            "strategy": str(self.strategy),
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
    "ClinVarSignificance",
    "RetroelementType",
    "CatalyticResidueRole",
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
    # Validation types
    "ValidationError",
    "ValidationResult",
    # Inference types
    "InferenceResult",
    # Type aliases
    "GFLValue",
    "GFLDict",
]
