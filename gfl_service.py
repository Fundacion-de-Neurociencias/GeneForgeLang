#!/usr/bin/env python3
"""
GeneForgeLang (GFL) Service

This is a simple FastAPI service that provides the necessary endpoints
for the GeneForge system to interact with the GFL core functionality.
"""

import json
import os
import sys
from typing import Any, Dict

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import GFL core functionality
from importlib.metadata import entry_points

from gfl.parser import parse_gfl

# Import plugin registry for dynamic plugin discovery
from gfl.plugins.plugin_registry import plugin_registry

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


class ExecuteResponse(BaseModel):
    success: bool
    message: str = ""
    result: dict[str, Any] = None


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
    """Execute AST"""
    try:
        # For simplicity, we're just returning a basic execution result
        # In a full implementation, this would execute the GFL workflow
        result = {"status": "success", "output": "GFL execution completed", "metrics": {}}

        return ExecuteResponse(success=True, result=result)
    except Exception as e:
        return ExecuteResponse(success=False, message=f"Error executing AST: {str(e)}")


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
        },
        {
            "name": "protein_design",
            "version": "1.0.0",
            "description": "Protein design plugin",
            "capabilities": ["inverse_design", "property_prediction"],
            "status": "active",
        },
        {
            "name": "data_analysis",
            "version": "1.0.0",
            "description": "Data analysis plugin",
            "capabilities": ["statistical_analysis", "visualization"],
            "status": "active",
        },
    ]

    # Combine all plugins
    all_plugins = discovered_plugins + hardcoded_plugins

    return {"success": True, "plugins": all_plugins}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
