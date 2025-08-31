#!/usr/bin/env python3
"""
GeneForgeLang (GFL) Service

This is a simple FastAPI service that provides the necessary endpoints
for the GeneForge system to interact with the GFL core functionality.
"""

import os
import sys
import yaml
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import GFL core functionality
from gfl.parser import parse_gfl

app = FastAPI(
    title="GeneForgeLang Service",
    description="API for parsing, validating, and processing GeneForgeLang code",
    version="1.0.0"
)

class ParseRequest(BaseModel):
    code: str
    typed: bool = True

class ParseResponse(BaseModel):
    success: bool
    message: str = ""
    ast: Dict[str, Any] = None

class ValidateRequest(BaseModel):
    ast: Dict[str, Any]
    detailed: bool = True

class ValidateResponse(BaseModel):
    success: bool
    message: str = ""
    validation_result: Dict[str, Any] = None

class InferRequest(BaseModel):
    ast: Dict[str, Any]
    context: Dict[str, Any] = {}

class InferResponse(BaseModel):
    success: bool
    message: str = ""
    inference_result: Dict[str, Any] = None

class ExecuteRequest(BaseModel):
    ast: Dict[str, Any]
    context: Dict[str, Any] = {}

class ExecuteResponse(BaseModel):
    success: bool
    message: str = ""
    result: Dict[str, Any] = None

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
            return ParseResponse(
                success=False,
                message="Failed to parse GFL code"
            )
        
        return ParseResponse(
            success=True,
            ast=ast
        )
    except Exception as e:
        return ParseResponse(
            success=False,
            message=f"Error parsing GFL code: {str(e)}"
        )

@app.post("/api/v2/validate", response_model=ValidateResponse)
async def validate_ast(request: ValidateRequest):
    """Validate AST"""
    try:
        # For simplicity, we're just returning a basic validation result
        # In a full implementation, this would perform detailed semantic validation
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        return ValidateResponse(
            success=True,
            validation_result=validation_result
        )
    except Exception as e:
        return ValidateResponse(
            success=False,
            message=f"Error validating AST: {str(e)}"
        )

@app.post("/api/v2/infer", response_model=InferResponse)
async def infer_ast(request: InferRequest):
    """Perform inference on AST"""
    try:
        # For simplicity, we're just returning a basic inference result
        # In a full implementation, this would perform detailed inference
        inference_result = {
            "inferred_types": {},
            "dependencies": [],
            "optimizations": []
        }
        
        return InferResponse(
            success=True,
            inference_result=inference_result
        )
    except Exception as e:
        return InferResponse(
            success=False,
            message=f"Error performing inference: {str(e)}"
        )

@app.post("/api/v2/execute", response_model=ExecuteResponse)
async def execute_ast(request: ExecuteRequest):
    """Execute AST"""
    try:
        # For simplicity, we're just returning a basic execution result
        # In a full implementation, this would execute the GFL workflow
        result = {
            "status": "success",
            "output": "GFL execution completed",
            "metrics": {}
        }
        
        return ExecuteResponse(
            success=True,
            result=result
        )
    except Exception as e:
        return ExecuteResponse(
            success=False,
            message=f"Error executing AST: {str(e)}"
        )

@app.get("/api/v2/plugins")
async def list_plugins():
    """List available plugins"""
    plugins = [
        {
            "name": "crispr_design",
            "version": "1.0.0",
            "description": "CRISPR guide design plugin",
            "capabilities": ["design_crispr_guides", "off_target_analysis"],
            "status": "active"
        },
        {
            "name": "protein_design",
            "version": "1.0.0",
            "description": "Protein design plugin",
            "capabilities": ["inverse_design", "property_prediction"],
            "status": "active"
        },
        {
            "name": "data_analysis",
            "version": "1.0.0",
            "description": "Data analysis plugin",
            "capabilities": ["statistical_analysis", "visualization"],
            "status": "active"
        }
    ]
    
    return {
        "success": True,
        "plugins": plugins
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")