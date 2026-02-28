#!/usr/bin/env python3
"""
GeneForgeLang (GFL) Service

This is a simple FastAPI service that provides the necessary endpoints
for the GeneForge system to interact with the GFL core functionality.
"""

import json
import logging
import os
import sys
from typing import Any, Dict

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import GFL core functionality
from importlib.metadata import entry_points

from gfl.parser import parse_gfl

# Import plugin registry for dynamic plugin discovery
from gfl.plugins.plugin_registry import plugin_registry
from gfl.staging import DataStagingManager

app = FastAPI(
    title="GeneForgeLang Service",
    description="API for parsing, validating, and processing GeneForgeLang code",
    version="1.0.0",
)


class ParseRequest(BaseModel):
    code: str
    typed: bool = True


class ParseResponse(BaseModel):
    success: bool
    message: str = ""
    ast: dict[str, Any] = None


class ValidateRequest(BaseModel):
    ast: dict[str, Any]
    detailed: bool = True


class ValidateResponse(BaseModel):
    success: bool
    message: str = ""
    validation_result: dict[str, Any] = None


class InferRequest(BaseModel):
    ast: dict[str, Any]
    context: dict[str, Any] = {}


class InferResponse(BaseModel):
    success: bool
    message: str = ""
    inference_result: dict[str, Any] = None


class ExecuteRequest(BaseModel):
    ast: dict[str, Any]
    context: dict[str, Any] = {}
    data_manifest: dict[str, str] = {}


class ExecuteResponse(BaseModel):
    success: bool
    message: str = ""
    result: dict[str, Any] = None


class SkillExecuteRequest(BaseModel):
    """Request to run a local Bio-Skill by name."""
    skill_name: str
    inputs: dict[str, Any] = {}


class SkillExecuteResponse(BaseModel):
    """Response from a local Bio-Skill execution."""
    success: bool
    message: str = ""
    data: dict[str, Any] = None
    reproducibility_package: dict[str, Any] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/v2/parse", response_model=ParseResponse)
async def parse_gfl_endpoint(request: ParseRequest):
    """Parse GFL code and return AST"""
    try:
        # Parse the GFL code using YAML parser
        ast = parse_gfl(request.code)

        if ast is None:
            return ParseResponse(success=False, message="Failed to parse GFL code")

        return ParseResponse(success=True, ast=ast)
    except Exception as e:
        return ParseResponse(success=False, message=f"Error parsing GFL code: {str(e)}")


@app.post("/api/v2/validate", response_model=ValidateResponse)
async def validate_ast(request: ValidateRequest):
    """Validate AST"""
    try:
        # For simplicity, we're just returning a basic validation result
        # In a full implementation, this would perform detailed semantic validation
        validation_result = {"is_valid": True, "errors": [], "warnings": [], "info": []}

        return ValidateResponse(success=True, validation_result=validation_result)
    except Exception as e:
        return ValidateResponse(success=False, message=f"Error validating AST: {str(e)}")


@app.post("/api/v2/infer", response_model=InferResponse)
async def infer_ast(request: InferRequest):
    """Perform inference on AST"""
    try:
        # For simplicity, we're just returning a basic inference result
        # In a full implementation, this would perform detailed inference
        inference_result = {"inferred_types": {}, "dependencies": [], "optimizations": []}

        return InferResponse(success=True, inference_result=inference_result)
    except Exception as e:
        return InferResponse(success=False, message=f"Error performing inference: {str(e)}")


@app.post("/api/v2/execute", response_model=ExecuteResponse)
async def execute_ast(request: ExecuteRequest):
    """Execute AST with data staging support"""
    data_staging_manager = None
    try:
        # Initialize data staging manager if data manifest is provided
        if request.data_manifest:
            data_staging_manager = DataStagingManager()
            logger.info(f"Data staging enabled with {len(request.data_manifest)} files in manifest")

        # Extract plugin parameters from AST
        plugin_params = {}
        if "experiment" in request.ast and "params" in request.ast["experiment"]:
            plugin_params.update(request.ast["experiment"]["params"])
        if "analyze" in request.ast and "params" in request.ast["analyze"]:
            plugin_params.update(request.ast["analyze"]["params"])

        # Stage files if data staging manager is available
        if data_staging_manager and plugin_params:
            try:
                plugin_params = data_staging_manager.stage_files(
                    plugin_params, request.data_manifest
                )
                logger.info(f"Staged {len(data_staging_manager.staged_files)} files for execution")
            except Exception as e:
                logger.error(f"Data staging failed: {e}")
                return ExecuteResponse(success=False, message=f"Data staging failed: {str(e)}")

        # Execute the workflow with staged parameters
        # For now, we're returning a basic execution result
        # In a full implementation, this would execute the GFL workflow with the staged files
        result = {
            "status": "success",
            "output": "GFL execution completed",
            "metrics": {},
            "staged_files": (
                list(data_staging_manager.staged_files.keys()) if data_staging_manager else []
            ),
            "plugin_params": plugin_params,
        }

        return ExecuteResponse(success=True, result=result)
    except Exception as e:
        return ExecuteResponse(success=False, message=f"Error executing AST: {str(e)}")
    finally:
        # Clean up staged files
        if data_staging_manager:
            try:
                data_staging_manager.cleanup()
                logger.info("Data staging cleanup completed")
            except Exception as e:
                logger.error(f"Data staging cleanup failed: {e}")


# ---------------------------------------------------------------------------
# Auto-registration of Bio-Skills
# ---------------------------------------------------------------------------
_skills_registry: dict[str, Any] = {}

def _register_bio_skills() -> None:
    """Auto-register all available GeneForge Bio-Skills."""
    try:
        from gfl.plugins.skills.neuro_pharmgx import NeuroPharmGxSkill
        from gfl.plugins.skills.neuro_geriatric_risk import NeuroGeriatricRiskSkill
        from gfl.plugins.skills.neuro_nutrigx import NeuroNutriGxSkill
        
        skills = [
            NeuroPharmGxSkill(), 
            NeuroGeriatricRiskSkill(),
            NeuroNutriGxSkill()
        ]
        for skill in skills:
            _skills_registry[skill.name] = skill
            logger.info(f"Registered Bio-Skill: {skill.name} v{skill.version}")
    except Exception as e:
        logger.warning(f"Could not register Bio-Skills: {e}")

_register_bio_skills()


# ---------------------------------------------------------------------------
# Bio-Skills endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v2/skills/execute", response_model=SkillExecuteResponse)
async def execute_skill(request: SkillExecuteRequest):
    """
    Execute a local GeneForge Bio-Skill by name.
    Data never leaves this machine. Ships a reproducibility package.
    """
    skill_name = request.skill_name.lower()
    if skill_name not in _skills_registry:
        available = list(_skills_registry.keys())
        return SkillExecuteResponse(
            success=False,
            message=f"Skill '{skill_name}' no encontrada. Disponibles: {available}",
        )
    skill = _skills_registry[skill_name]
    try:
        result = skill.execute(request.inputs)
        return SkillExecuteResponse(
            success=result["success"],
            message="" if result["success"] else result.get("error", "Error desconocido"),
            data=result.get("data"),
            reproducibility_package=result.get("reproducibility_package"),
        )
    except Exception as e:
        logger.error(f"Skill execution failed for '{skill_name}': {e}")
        return SkillExecuteResponse(
            success=False,
            message=f"Error al ejecutar skill '{skill_name}': {str(e)}",
        )


@app.get("/api/v2/skills")
async def list_skills():
    """List all registered local Bio-Skills."""
    return {
        "success": True,
        "skills": [
            {
                "name": s.name,
                "version": s.version,
                "author": s.author,
                "description": s.description,
                "skill_type": s.skill_type,
                "local_execution": True,
            }
            for s in _skills_registry.values()
        ],
    }

@app.get("/api/v2/plugins")
async def list_plugins():
    """List available plugins"""
    # Discover plugins dynamically using entry points
    discovered_plugins = []

    # Get built-in plugins
    for name, plugin_class in plugin_registry._plugins.items():
        discovered_plugins.append(
            {
                "name": name,
                "version": getattr(plugin_class, "version", "1.0.0"),
                "description": getattr(plugin_class, "description", f"{name} plugin"),
                "capabilities": ["process_data"],
                "status": "active",
            }
        )

    # Get external plugins from entry points
    try:
        eps = entry_points(group="gfl.plugins")
        for ep in eps:
            try:
                plugin_class = ep.load()
                discovered_plugins.append(
                    {
                        "name": ep.name,
                        "version": getattr(plugin_class, "version", "1.0.0"),
                        "description": getattr(plugin_class, "description", f"{ep.name} plugin"),
                        "capabilities": ["process_data"],
                        "status": "active",
                    }
                )
            except Exception as e:
                print(f"Failed to load plugin {ep.name}: {e}")
    except Exception as e:
        print(f"Failed to discover entry point plugins: {e}")

    # Add hardcoded plugins for compatibility
    hardcoded_plugins = [
        {
            "name": "crispr_design",
            "version": "1.0.0",
            "description": "CRISPR guide design plugin",
            "capabilities": ["design_crispr_guides", "off_target_analysis"],
            "status": "active",
            "is_containerized": True,
            "container_image": "biocontainers/crispr-designer:v1.0.0_cv1",
            "inputs": [
                {
                    "name": "input_sequence",
                    "schema_type": "FASTA"
                }
            ],
            "outputs": [
                {
                    "name": "guide_rnas",
                    "schema_type": "CSV"
                }
            ]
        },
        {
            "name": "protein_design",
            "version": "1.0.0",
            "description": "Protein design plugin",
            "capabilities": ["inverse_design", "property_prediction"],
            "status": "active",
            "is_containerized": True,
            "container_image": "biocontainers/protein-designer:v1.0.0_cv1",
            "inputs": [
                {
                    "name": "target_structure",
                    "schema_type": "PDB"
                }
            ],
            "outputs": [
                {
                    "name": "designed_protein",
                    "schema_type": "PDB"
                }
            ]
        },
        {
            "name": "data_analysis",
            "version": "1.0.0",
            "description": "Data analysis plugin",
            "capabilities": ["statistical_analysis", "visualization"],
            "status": "active",
            "is_containerized": False,
            "inputs": [
                {
                    "name": "input_data",
                    "schema_type": "CSV"
                }
            ],
            "outputs": [
                {
                    "name": "analysis_results",
                    "schema_type": "JSON"
                }
            ]
        },
        {
            "name": "sequence_alignment",
            "version": "1.0.0",
            "description": "Sequence alignment plugin",
            "capabilities": ["align_sequences", "generate_bam"],
            "status": "active",
            "is_containerized": True,
            "container_image": "biocontainers/sequence-aligner:v1.0.0_cv1",
            "inputs": [
                {
                    "name": "reference_genome",
                    "schema_type": "FASTA"
                },
                {
                    "name": "reads",
                    "schema_type": "FASTQ"
                }
            ],
            "outputs": [
                {
                    "name": "aligned_reads",
                    "schema_type": "BAM"
                }
            ]
        },
        {
            "name": "variant_calling",
            "version": "1.0.0",
            "description": "Variant calling plugin",
            "capabilities": ["call_variants", "annotate_variants"],
            "status": "active",
            "is_containerized": True,
            "container_image": "biocontainers/variant-caller:v1.0.0_cv1",
            "inputs": [
                {
                    "name": "aligned_reads",
                    "schema_type": "BAM"
                }
            ],
            "outputs": [
                {
                    "name": "variants",
                    "schema_type": "VCF"
                }
            ]
        }
    ]

    # Combine all plugins
    all_plugins = discovered_plugins + hardcoded_plugins

    return {"success": True, "plugins": all_plugins}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
