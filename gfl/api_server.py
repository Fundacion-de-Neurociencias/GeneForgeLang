"""FastAPI REST API Server for GeneForgeLang Workflows.

This module provides a comprehensive REST API for GFL parsing, validation,
inference, and workflow management with:
- RESTful endpoints for all GFL operations
- Enhanced error handling and validation
- Security best practices and rate limiting
- OpenAPI documentation and schema generation
- Integration with enhanced inference engine
- Asynchronous processing support
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import GFL components
try:
    from gfl.api import (
        parse,
        validate,
        infer_enhanced,
        compare_inference_models,
        get_api_info,
    )
    from gfl.enhanced_inference_engine import get_inference_engine
    from gfl.models.advanced_models import (
        create_genomic_classification_model,
        create_multimodal_genomic_model,
    )

    HAS_GFL_API = True
except ImportError as e:
    HAS_GFL_API = False
    parse = validate = infer_enhanced = None
    logging.warning(f"GFL API not available: {e}")

# Optional dependencies
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    HAS_RATE_LIMITING = True
except ImportError:
    HAS_RATE_LIMITING = False
    Limiter = None

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global state
inference_engine = None
api_stats = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "start_time": datetime.now(),
    "endpoints_called": {},
}

# Rate limiting setup
limiter = None
if HAS_RATE_LIMITING:
    limiter = Limiter(key_func=get_remote_address)


# Pydantic models for API requests/responses
class GFLParseRequest(BaseModel):
    """Request model for GFL parsing."""

    content: str = Field(..., description="GFL source code to parse", min_length=1)
    use_grammar: bool = Field(default=False, description="Use grammar-based parser")
    filename: str = Field(default="<api>", description="Filename for error reporting")


class GFLValidateRequest(BaseModel):
    """Request model for GFL validation."""

    content: str = Field(..., description="GFL source code to validate", min_length=1)
    enhanced: bool = Field(default=True, description="Use enhanced validation")


class GFLInferenceRequest(BaseModel):
    """Request model for GFL inference."""

    content: str = Field(..., description="GFL source code for inference", min_length=1)
    model_name: str = Field(
        default="heuristic", description="Model to use for inference"
    )
    explain: bool = Field(default=True, description="Include detailed explanations")


class ModelComparisonRequest(BaseModel):
    """Request model for model comparison."""

    content: str = Field(
        ..., description="GFL source code for comparison", min_length=1
    )
    model_names: Optional[List[str]] = Field(
        default=None, description="Specific models to compare"
    )


class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution."""

    content: str = Field(..., description="GFL workflow to execute", min_length=1)
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Execution parameters"
    )
    dry_run: bool = Field(default=True, description="Perform dry run only")


# Response models
class APIResponse(BaseModel):
    """Base API response model."""

    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None


class ParseResponse(APIResponse):
    """Response model for parsing operations."""

    ast: Optional[Dict[str, Any]] = None


class ValidationResponse(APIResponse):
    """Response model for validation operations."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class InferenceResponse(APIResponse):
    """Response model for inference operations."""

    prediction: Any
    confidence: float
    explanation: str
    model_used: str
    features_used: Optional[Dict[str, Any]] = None


class ModelInfo(BaseModel):
    """Model information response."""

    name: str
    type: str
    loaded: bool
    description: Optional[str] = None


class APIStats(BaseModel):
    """API statistics response."""

    requests_total: int
    requests_successful: int
    requests_failed: int
    uptime_seconds: float
    endpoints_called: Dict[str, int]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting GFL API Server...")

    global inference_engine
    if HAS_GFL_API:
        try:
            # Initialize inference engine and register models
            inference_engine = get_inference_engine()

            # Register advanced models
            classification_model = create_genomic_classification_model()
            inference_engine.register_model(
                "genomic_classification", classification_model
            )

            multimodal_model = create_multimodal_genomic_model()
            inference_engine.register_model("multimodal", multimodal_model)

            logger.info(
                f"Inference engine initialized with models: {inference_engine.list_models()}"
            )
        except Exception as e:
            logger.warning(f"Could not initialize enhanced inference engine: {e}")

    logger.info("GFL API Server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down GFL API Server...")


# Create FastAPI app
app = FastAPI(
    title="GeneForgeLang API Server",
    description="REST API for parsing, validating, and executing GeneForgeLang workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
if HAS_RATE_LIMITING:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track API requests and performance."""
    start_time = time.time()

    # Update stats
    api_stats["requests_total"] += 1
    endpoint = f"{request.method} {request.url.path}"
    api_stats["endpoints_called"][endpoint] = (
        api_stats["endpoints_called"].get(endpoint, 0) + 1
    )

    try:
        response = await call_next(request)
        api_stats["requests_successful"] += 1
        return response
    except Exception as e:
        api_stats["requests_failed"] += 1
        logger.error(f"Request failed: {e}")
        raise
    finally:
        execution_time = (time.time() - start_time) * 1000
        logger.info(f"{endpoint} completed in {execution_time:.2f}ms")


# Utility functions
def create_error_response(message: str, status_code: int = 400) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        },
    )


def create_success_response(
    data: Any, message: str = "Success", execution_time: float = None
) -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "execution_time_ms": execution_time,
    }


# API Routes
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information."""
    if HAS_GFL_API:
        gfl_info = get_api_info()
        return create_success_response(
            data={
                "service": "GeneForgeLang API Server",
                "version": "1.0.0",
                "gfl_info": gfl_info,
                "endpoints": {
                    "parse": "/parse",
                    "validate": "/validate",
                    "infer": "/infer",
                    "compare": "/compare",
                    "models": "/models",
                    "stats": "/stats",
                    "health": "/health",
                },
            },
            message="GeneForgeLang API Server is running",
        )
    else:
        raise HTTPException(status_code=503, detail="GFL API not available")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - api_stats["start_time"]).total_seconds()

    health_status = {
        "status": "healthy",
        "uptime_seconds": uptime,
        "gfl_api_available": HAS_GFL_API,
        "inference_engine_ready": inference_engine is not None,
        "available_models": inference_engine.list_models() if inference_engine else [],
    }

    return create_success_response(health_status, "Service is healthy")


# Core GFL API endpoints
rate_limit_decorator = limiter.limit("100/minute") if HAS_RATE_LIMITING else lambda f: f


@app.post("/parse", response_model=ParseResponse)
@rate_limit_decorator
async def parse_gfl(request: Request, gfl_request: GFLParseRequest):
    """Parse GFL source code into AST."""
    if not HAS_GFL_API:
        raise HTTPException(status_code=503, detail="GFL API not available")

    start_time = time.time()

    try:
        ast = parse(
            gfl_request.content,
            use_grammar=gfl_request.use_grammar,
            filename=gfl_request.filename,
        )

        execution_time = (time.time() - start_time) * 1000

        return ParseResponse(
            success=True,
            message="GFL parsed successfully",
            ast=ast,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")


@app.post("/validate", response_model=ValidationResponse)
@rate_limit_decorator
async def validate_gfl(request: Request, gfl_request: GFLValidateRequest):
    """Validate GFL source code."""
    if not HAS_GFL_API:
        raise HTTPException(status_code=503, detail="GFL API not available")

    start_time = time.time()

    try:
        # Parse first
        ast = parse(gfl_request.content)

        # Validate
        validation_result = validate(ast, enhanced=gfl_request.enhanced)

        execution_time = (time.time() - start_time) * 1000

        # Handle different validation result types
        if gfl_request.enhanced and hasattr(validation_result, "is_valid"):
            # Enhanced validation result
            return ValidationResponse(
                success=True,
                message="Validation completed",
                is_valid=validation_result.is_valid,
                errors=[str(e) for e in getattr(validation_result, "errors", [])],
                warnings=[str(w) for w in getattr(validation_result, "warnings", [])],
                execution_time_ms=execution_time,
            )
        else:
            # Legacy validation result (list of errors)
            errors = validation_result if isinstance(validation_result, list) else []
            is_valid = len(errors) == 0

            return ValidationResponse(
                success=True,
                message="Validation completed",
                is_valid=is_valid,
                errors=errors,
                execution_time_ms=execution_time,
            )

    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")


@app.post("/infer", response_model=InferenceResponse)
@rate_limit_decorator
async def infer_gfl(request: Request, gfl_request: GFLInferenceRequest):
    """Run inference on GFL source code."""
    if not HAS_GFL_API:
        raise HTTPException(status_code=503, detail="GFL API not available")

    start_time = time.time()

    try:
        # Parse GFL content
        ast = parse(gfl_request.content)

        # Run enhanced inference
        result = infer_enhanced(
            ast, model_name=gfl_request.model_name, explain=gfl_request.explain
        )

        execution_time = (time.time() - start_time) * 1000

        return InferenceResponse(
            success=True,
            message="Inference completed successfully",
            prediction=result.get("label", result.get("prediction")),
            confidence=result.get("confidence", 0.0),
            explanation=result.get("explanation", ""),
            model_used=result.get("model_used", gfl_request.model_name),
            features_used=result.get("features_used"),
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")


@app.post("/compare")
@rate_limit_decorator
async def compare_models(request: Request, gfl_request: ModelComparisonRequest):
    """Compare predictions across multiple models."""
    if not HAS_GFL_API:
        raise HTTPException(status_code=503, detail="GFL API not available")

    start_time = time.time()

    try:
        # Parse GFL content
        ast = parse(gfl_request.content)

        # Run model comparison
        comparison_results = compare_inference_models(ast, gfl_request.model_names)

        execution_time = (time.time() - start_time) * 1000

        return create_success_response(
            data={
                "comparisons": comparison_results.get("comparisons", {}),
                "available_models": comparison_results.get("available_models", []),
                "features_used": comparison_results.get("features_used", {}),
            },
            message="Model comparison completed successfully",
            execution_time=execution_time,
        )

    except Exception as e:
        logger.error(f"Model comparison error: {e}")
        raise HTTPException(status_code=400, detail=f"Model comparison error: {str(e)}")


# Model management endpoints
@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List available inference models."""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not available")

    try:
        models = []
        for model_name in inference_engine.list_models():
            try:
                info = inference_engine.get_model_info(model_name)
                models.append(
                    ModelInfo(
                        name=model_name,
                        type=info.get("type", "unknown"),
                        loaded=info.get("loaded", False),
                        description=f"{info.get('type', 'unknown').title()} model for {model_name}",
                    )
                )
            except Exception as e:
                logger.warning(f"Could not get info for model {model_name}: {e}")
                models.append(ModelInfo(name=model_name, type="unknown", loaded=False))

        return models

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail="Error listing models")


@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get detailed information about a specific model."""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not available")

    try:
        if model_name not in inference_engine.list_models():
            raise HTTPException(
                status_code=404, detail=f"Model '{model_name}' not found"
            )

        info = inference_engine.get_model_info(model_name)
        return create_success_response(
            info, f"Model {model_name} information retrieved"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Error getting model information")


# File upload endpoints
@app.post("/upload/parse")
@rate_limit_decorator
async def upload_and_parse(request: Request, file: UploadFile = File(...)):
    """Upload and parse a GFL file."""
    if not file.filename.endswith((".gfl", ".yml", ".yaml", ".txt")):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Use .gfl, .yml, .yaml, or .txt"
        )

    try:
        content = await file.read()
        gfl_content = content.decode("utf-8")

        # Parse the content
        gfl_request = GFLParseRequest(content=gfl_content, filename=file.filename)
        return await parse_gfl(request, gfl_request)

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="Error processing uploaded file")


# Batch processing endpoints
@app.post("/batch/infer")
@rate_limit_decorator
async def batch_inference(request: Request, requests_data: List[GFLInferenceRequest]):
    """Run batch inference on multiple GFL samples."""
    if len(requests_data) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Batch size limited to 10 requests")

    results = []
    for i, gfl_request in enumerate(requests_data):
        try:
            result = await infer_gfl(request, gfl_request)
            results.append({"index": i, "result": result, "success": True})
        except Exception as e:
            results.append({"index": i, "error": str(e), "success": False})

    return create_success_response(
        data={"batch_results": results},
        message=f"Batch inference completed for {len(requests_data)} requests",
    )


# Statistics and monitoring
@app.get("/stats", response_model=APIStats)
async def get_stats():
    """Get API usage statistics."""
    uptime = (datetime.now() - api_stats["start_time"]).total_seconds()

    return APIStats(
        requests_total=api_stats["requests_total"],
        requests_successful=api_stats["requests_successful"],
        requests_failed=api_stats["requests_failed"],
        uptime_seconds=uptime,
        endpoints_called=api_stats["endpoints_called"],
    )


# Async workflow execution (placeholder for future enhancement)
@app.post("/workflow/execute")
async def execute_workflow(
    background_tasks: BackgroundTasks, gfl_request: WorkflowExecutionRequest
):
    """Execute a GFL workflow asynchronously."""
    # For now, this is a placeholder that performs validation and inference
    try:
        ast = parse(gfl_request.content)
        validation_result = validate(ast)

        if isinstance(validation_result, list) and validation_result:
            raise HTTPException(
                status_code=400, detail=f"Validation errors: {validation_result}"
            )

        # In a real implementation, this would queue the workflow for execution
        workflow_id = f"workflow_{int(time.time())}"

        return create_success_response(
            data={
                "workflow_id": workflow_id,
                "status": "queued" if not gfl_request.dry_run else "dry_run_complete",
                "message": "Workflow queued for execution"
                if not gfl_request.dry_run
                else "Dry run validation passed",
            },
            message="Workflow processing initiated",
        )

    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Workflow execution error: {str(e)}"
        )


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return create_error_response(f"Invalid input: {str(exc)}", 400)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return create_error_response("Endpoint not found", 404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return create_error_response("Internal server error", 500)


# Server configuration
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the API server."""
    config = uvicorn.Config(
        "gfl.api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GeneForgeLang API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    logger.info(f"Starting GFL API Server on {args.host}:{args.port}")
    run_server(args.host, args.port, args.reload)
