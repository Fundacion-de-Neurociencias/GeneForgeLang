"""Capability system for GFL validation.

This module defines the capability system that allows the GFL validator
to check if features are supported by the target execution engine.
"""

from typing import Dict, Set, List, Optional
from dataclasses import dataclass
from enum import Enum


class GFLFeature(Enum):
    """GFL features that can be checked for engine support."""
    
    # Core features (always supported)
    EXPERIMENT_BLOCK = "experiment_block"
    ANALYZE_BLOCK = "analyze_block"
    DESIGN_BLOCK = "design_block"
    OPTIMIZE_BLOCK = "optimize_block"
    BRANCH_BLOCK = "branch_block"
    METADATA_BLOCK = "metadata_block"
    
    # Advanced features
    SIMULATE_BLOCK = "simulate_block"
    RULES_BLOCK = "rules_block"
    HYPOTHESIS_BLOCK = "hypothesis_block"
    TIMELINE_BLOCK = "timeline_block"
    REFINE_DATA_BLOCK = "refine_data_block"
    GUIDED_DISCOVERY_BLOCK = "guided_discovery_block"
    
    # Spatial genomic features (new in v1.3.0)
    LOCI_BLOCK = "loci_block"
    SPATIAL_PREDICATES = "spatial_predicates"
    SPATIAL_SIMULATE = "spatial_simulate"
    HIC_INTEGRATION = "hic_integration"
    
    # Advanced reasoning features
    REASONING_ENGINE_V1 = "reasoning_engine_v1"
    WHAT_IF_SIMULATION = "what_if_simulation"
    SPATIAL_REASONING = "spatial_reasoning"
    
    # Data integration features
    SCHEMA_IMPORTS = "schema_imports"
    EXTERNAL_DATA_SOURCES = "external_data_sources"
    CLOUD_INTEGRATION = "cloud_integration"


@dataclass
class CapabilityInfo:
    """Information about a GFL capability."""
    
    feature: GFLFeature
    name: str
    description: str
    version_introduced: str
    dependencies: List[GFLFeature]
    is_experimental: bool = False


class GFLValidationWarning:
    """Warning for capability-related validation issues."""
    
    def __init__(self, message: str, feature: Optional[GFLFeature] = None, 
                 suggestion: Optional[str] = None):
        self.message = message
        self.feature = feature
        self.suggestion = suggestion or self._get_default_suggestion()
    
    def _get_default_suggestion(self) -> str:
        """Get default suggestion based on feature."""
        if self.feature:
            return f"Consider upgrading your GFL engine to support {self.feature.value}"
        return "Consider upgrading your GFL engine to support this feature"
    
    def __str__(self) -> str:
        return f"WARNING: {self.message}"


class GFLValidationResult:
    """Enhanced validation result with capability warnings."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[GFLValidationWarning] = []
        self.info: List[str] = []
    
    def add_warning(self, message: str, feature: Optional[GFLFeature] = None, 
                   suggestion: Optional[str] = None) -> GFLValidationWarning:
        """Add a capability warning."""
        warning = GFLValidationWarning(message, feature, suggestion)
        self.warnings.append(warning)
        return warning
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_warnings_for_feature(self, feature: GFLFeature) -> List[GFLValidationWarning]:
        """Get all warnings for a specific feature."""
        return [w for w in self.warnings if w.feature == feature]


# Capability definitions
CAPABILITY_DEFINITIONS: Dict[GFLFeature, CapabilityInfo] = {
    GFLFeature.EXPERIMENT_BLOCK: CapabilityInfo(
        feature=GFLFeature.EXPERIMENT_BLOCK,
        name="Experiment Block",
        description="Basic experiment execution capability",
        version_introduced="v1.0.0",
        dependencies=[]
    ),
    
    GFLFeature.ANALYZE_BLOCK: CapabilityInfo(
        feature=GFLFeature.ANALYZE_BLOCK,
        name="Analysis Block",
        description="Data analysis and processing capability",
        version_introduced="v1.0.0",
        dependencies=[]
    ),
    
    GFLFeature.SIMULATE_BLOCK: CapabilityInfo(
        feature=GFLFeature.SIMULATE_BLOCK,
        name="Simulation Block",
        description="Basic simulation capability",
        version_introduced="v1.1.0",
        dependencies=[]
    ),
    
    GFLFeature.RULES_BLOCK: CapabilityInfo(
        feature=GFLFeature.RULES_BLOCK,
        name="Rules Block",
        description="Rule-based logic and constraints",
        version_introduced="v1.2.0",
        dependencies=[]
    ),
    
    GFLFeature.LOCI_BLOCK: CapabilityInfo(
        feature=GFLFeature.LOCI_BLOCK,
        name="Loci Block",
        description="Genomic coordinate and region definitions",
        version_introduced="v1.3.0",
        dependencies=[],
        is_experimental=True
    ),
    
    GFLFeature.SPATIAL_PREDICATES: CapabilityInfo(
        feature=GFLFeature.SPATIAL_PREDICATES,
        name="Spatial Predicates",
        description="Spatial genomic predicates (is_within, distance_between, is_in_contact)",
        version_introduced="v1.3.0",
        dependencies=[GFLFeature.LOCI_BLOCK],
        is_experimental=True
    ),
    
    GFLFeature.SPATIAL_SIMULATE: CapabilityInfo(
        feature=GFLFeature.SPATIAL_SIMULATE,
        name="Spatial Simulation",
        description="What-if reasoning with spatial genomic awareness",
        version_introduced="v1.3.0",
        dependencies=[GFLFeature.SIMULATE_BLOCK, GFLFeature.SPATIAL_PREDICATES],
        is_experimental=True
    ),
    
    GFLFeature.REASONING_ENGINE_V1: CapabilityInfo(
        feature=GFLFeature.REASONING_ENGINE_V1,
        name="Reasoning Engine v1",
        description="Advanced reasoning and inference capabilities",
        version_introduced="v1.3.0",
        dependencies=[GFLFeature.RULES_BLOCK],
        is_experimental=True
    ),
    
    GFLFeature.WHAT_IF_SIMULATION: CapabilityInfo(
        feature=GFLFeature.WHAT_IF_SIMULATION,
        name="What-If Simulation",
        description="Hypothetical scenario testing and reasoning",
        version_introduced="v1.3.0",
        dependencies=[GFLFeature.REASONING_ENGINE_V1],
        is_experimental=True
    ),
    
    GFLFeature.HIC_INTEGRATION: CapabilityInfo(
        feature=GFLFeature.HIC_INTEGRATION,
        name="Hi-C Integration",
        description="3D chromatin contact data integration",
        version_introduced="v1.3.0",
        dependencies=[GFLFeature.SPATIAL_PREDICATES],
        is_experimental=True
    )
}


class EngineCapabilityChecker:
    """Checks if engine supports specific GFL capabilities."""
    
    def __init__(self, supported_features: Set[GFLFeature]):
        self.supported_features = supported_features
    
    def supports_feature(self, feature: GFLFeature) -> bool:
        """Check if engine supports a specific feature."""
        return feature in self.supported_features
    
    def check_dependencies(self, feature: GFLFeature) -> List[GFLFeature]:
        """Check if all dependencies for a feature are supported."""
        if feature not in CAPABILITY_DEFINITIONS:
            return []
        
        capability_info = CAPABILITY_DEFINITIONS[feature]
        missing_dependencies = []
        
        for dependency in capability_info.dependencies:
            if not self.supports_feature(dependency):
                missing_dependencies.append(dependency)
        
        return missing_dependencies
    
    def get_capability_info(self, feature: GFLFeature) -> Optional[CapabilityInfo]:
        """Get information about a capability."""
        return CAPABILITY_DEFINITIONS.get(feature)
    
    def get_unsupported_features(self, required_features: Set[GFLFeature]) -> Set[GFLFeature]:
        """Get features that are not supported by the engine."""
        return required_features - self.supported_features


def create_engine_capability_sets() -> Dict[str, Set[GFLFeature]]:
    """Create predefined engine capability sets."""
    
    return {
        # Basic engine - supports core GFL features
        "basic": {
            GFLFeature.EXPERIMENT_BLOCK,
            GFLFeature.ANALYZE_BLOCK,
            GFLFeature.DESIGN_BLOCK,
            GFLFeature.OPTIMIZE_BLOCK,
            GFLFeature.BRANCH_BLOCK,
            GFLFeature.METADATA_BLOCK
        },
        
        # Standard engine - supports most features up to v1.2.0
        "standard": {
            GFLFeature.EXPERIMENT_BLOCK,
            GFLFeature.ANALYZE_BLOCK,
            GFLFeature.DESIGN_BLOCK,
            GFLFeature.OPTIMIZE_BLOCK,
            GFLFeature.BRANCH_BLOCK,
            GFLFeature.METADATA_BLOCK,
            GFLFeature.SIMULATE_BLOCK,
            GFLFeature.RULES_BLOCK,
            GFLFeature.HYPOTHESIS_BLOCK,
            GFLFeature.TIMELINE_BLOCK,
            GFLFeature.REFINE_DATA_BLOCK,
            GFLFeature.GUIDED_DISCOVERY_BLOCK,
            GFLFeature.SCHEMA_IMPORTS
        },
        
        # Advanced engine - supports all features including spatial genomic
        "advanced": {
            GFLFeature.EXPERIMENT_BLOCK,
            GFLFeature.ANALYZE_BLOCK,
            GFLFeature.DESIGN_BLOCK,
            GFLFeature.OPTIMIZE_BLOCK,
            GFLFeature.BRANCH_BLOCK,
            GFLFeature.METADATA_BLOCK,
            GFLFeature.SIMULATE_BLOCK,
            GFLFeature.RULES_BLOCK,
            GFLFeature.HYPOTHESIS_BLOCK,
            GFLFeature.TIMELINE_BLOCK,
            GFLFeature.REFINE_DATA_BLOCK,
            GFLFeature.GUIDED_DISCOVERY_BLOCK,
            GFLFeature.SCHEMA_IMPORTS,
            GFLFeature.LOCI_BLOCK,
            GFLFeature.SPATIAL_PREDICATES,
            GFLFeature.SPATIAL_SIMULATE,
            GFLFeature.REASONING_ENGINE_V1,
            GFLFeature.WHAT_IF_SIMULATION,
            GFLFeature.HIC_INTEGRATION
        },
        
        # Experimental engine - supports cutting-edge features
        "experimental": {
            GFLFeature.EXPERIMENT_BLOCK,
            GFLFeature.ANALYZE_BLOCK,
            GFLFeature.DESIGN_BLOCK,
            GFLFeature.OPTIMIZE_BLOCK,
            GFLFeature.BRANCH_BLOCK,
            GFLFeature.METADATA_BLOCK,
            GFLFeature.SIMULATE_BLOCK,
            GFLFeature.RULES_BLOCK,
            GFLFeature.HYPOTHESIS_BLOCK,
            GFLFeature.TIMELINE_BLOCK,
            GFLFeature.REFINE_DATA_BLOCK,
            GFLFeature.GUIDED_DISCOVERY_BLOCK,
            GFLFeature.SCHEMA_IMPORTS,
            GFLFeature.LOCI_BLOCK,
            GFLFeature.SPATIAL_PREDICATES,
            GFLFeature.SPATIAL_SIMULATE,
            GFLFeature.REASONING_ENGINE_V1,
            GFLFeature.WHAT_IF_SIMULATION,
            GFLFeature.HIC_INTEGRATION,
            GFLFeature.EXTERNAL_DATA_SOURCES,
            GFLFeature.CLOUD_INTEGRATION
        }
    }


def get_engine_capabilities(engine_type: str) -> Set[GFLFeature]:
    """Get capabilities for a specific engine type."""
    capability_sets = create_engine_capability_sets()
    return capability_sets.get(engine_type, capability_sets["basic"])
