#!/usr/bin/env python3
"""
Minimal GFL service for testing.
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/v2/parse", response_model=ParseResponse)
async def parse_gfl_endpoint(request: ParseRequest):
    """Parse GFL code and return AST"""
    try:
        # Parse the GFL code using YAML parser
        import yaml

        ast = yaml.safe_load(request.code)

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
    try:
        # Execute the workflow with staged parameters
        # For now, we're returning a basic execution result
        # In a full implementation, this would execute the GFL workflow with the staged files
        result = {
            "status": "success",
            "output": "GFL execution completed",
            "metrics": {},
            "staged_files": [],
            "plugin_params": {},
        }

        return ExecuteResponse(success=True, result=result)
    except Exception as e:
        return ExecuteResponse(success=False, message=f"Error executing AST: {str(e)}")


@app.get("/api/v2/plugins")
async def list_plugins():
    """List available plugins"""
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

    return {"success": True, "plugins": hardcoded_plugins}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
