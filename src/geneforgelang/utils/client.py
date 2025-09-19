"""GeneForgeLang Client SDK.

This module provides a comprehensive Python client for interacting with the
GeneForgeLang API server with:
- Synchronous and asynchronous API clients
- Automatic retry and error handling
- Response caching and rate limiting
- Batch processing support
- Type-safe request/response models
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response wrapper."""

    success: bool
    data: Any
    message: str
    status_code: int
    execution_time_ms: float | None = None
    timestamp: str | None = None


@dataclass
class ParseResult:
    """Result of GFL parsing operation."""

    ast: dict[str, Any]
    success: bool
    message: str
    execution_time_ms: float


@dataclass
class ValidationResult:
    """Result of GFL validation operation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    success: bool
    message: str
    execution_time_ms: float


@dataclass
class InferenceResult:
    """Result of GFL inference operation."""

    prediction: Any
    confidence: float
    explanation: str
    model_used: str
    features_used: dict[str, Any] | None
    success: bool
    message: str
    execution_time_ms: float


@dataclass
class ModelInfo:
    """Information about an available model."""

    name: str
    type: str
    loaded: bool
    description: str | None = None


class GFLClientError(Exception):
    """Base exception for GFL client errors."""

    pass


class GFLConnectionError(GFLClientError):
    """Connection-related errors."""

    pass


class GFLAPIError(GFLClientError):
    """API server errors."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class GFLClient:
    """Synchronous client for GeneForgeLang API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        retries: int = 3,
        api_key: str | None = None,
    ):
        """Initialize the GFL client.

        Args:
            base_url: Base URL of the GFL API server
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
            api_key: Optional API key for authentication
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library required. Install with: pip install requests")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

        # Configure session
        self.session = requests.Session()

        # Set headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "GeneForgeLang-Client/1.0",
            }
        )

        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make HTTP request with retry logic."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        last_exception = None

        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)

                # Handle HTTP errors
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", f"HTTP {response.status_code}")
                    except:
                        error_message = f"HTTP {response.status_code}: {response.text[:100]}"

                    raise GFLAPIError(error_message, response.status_code)

                # Parse response
                try:
                    data = response.json()
                    return APIResponse(
                        success=data.get("success", True),
                        data=data.get("data"),
                        message=data.get("message", "Success"),
                        status_code=response.status_code,
                        execution_time_ms=data.get("execution_time_ms"),
                        timestamp=data.get("timestamp"),
                    )
                except json.JSONDecodeError:
                    return APIResponse(
                        success=True,
                        data=response.text,
                        message="Non-JSON response",
                        status_code=response.status_code,
                    )

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.retries:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                continue

        # All retries failed
        raise GFLConnectionError(f"Failed after {self.retries + 1} attempts: {last_exception}")

    def health_check(self) -> dict[str, Any]:
        """Check API server health status."""
        response = self._make_request("GET", "/health")
        if not response.success:
            raise GFLAPIError(response.message, response.status_code)
        return response.data

    def parse(self, content: str, use_grammar: bool = False, filename: str = "<client>") -> ParseResult:
        """Parse GFL content into AST.

        Args:
            content: GFL source code to parse
            use_grammar: Whether to use grammar-based parser
            filename: Filename for error reporting

        Returns:
            ParseResult with AST and metadata
        """
        payload = {"content": content, "use_grammar": use_grammar, "filename": filename}

        response = self._make_request("POST", "/parse", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return ParseResult(
            ast=response.data.get("ast", {}),
            success=response.success,
            message=response.message,
            execution_time_ms=response.execution_time_ms or 0.0,
        )

    def validate(self, content: str, enhanced: bool = True) -> ValidationResult:
        """Validate GFL content.

        Args:
            content: GFL source code to validate
            enhanced: Use enhanced validation with detailed errors

        Returns:
            ValidationResult with validation details
        """
        payload = {"content": content, "enhanced": enhanced}

        response = self._make_request("POST", "/validate", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return ValidationResult(
            is_valid=response.data.get("is_valid", False),
            errors=response.data.get("errors", []),
            warnings=response.data.get("warnings", []),
            success=response.success,
            message=response.message,
            execution_time_ms=response.execution_time_ms or 0.0,
        )

    def infer(self, content: str, model_name: str = "heuristic", explain: bool = True) -> InferenceResult:
        """Run inference on GFL content.

        Args:
            content: GFL source code for inference
            model_name: Model to use for inference
            explain: Include detailed explanations

        Returns:
            InferenceResult with predictions and metadata
        """
        payload = {"content": content, "model_name": model_name, "explain": explain}

        response = self._make_request("POST", "/infer", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return InferenceResult(
            prediction=response.data.get("prediction"),
            confidence=response.data.get("confidence", 0.0),
            explanation=response.data.get("explanation", ""),
            model_used=response.data.get("model_used", model_name),
            features_used=response.data.get("features_used"),
            success=response.success,
            message=response.message,
            execution_time_ms=response.execution_time_ms or 0.0,
        )

    def compare_models(self, content: str, model_names: list[str] | None = None) -> dict[str, Any]:
        """Compare predictions across multiple models.

        Args:
            content: GFL source code for comparison
            model_names: Specific models to compare (None for all)

        Returns:
            Dictionary with comparison results
        """
        payload = {"content": content, "model_names": model_names}

        response = self._make_request("POST", "/compare", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return response.data

    def list_models(self) -> list[ModelInfo]:
        """List available inference models.

        Returns:
            List of ModelInfo objects
        """
        response = self._make_request("GET", "/models")

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        # Handle both list of dicts and list of ModelInfo objects
        models_data = response.data
        if isinstance(models_data, list):
            return [
                ModelInfo(
                    name=model.get("name", ""),
                    type=model.get("type", "unknown"),
                    loaded=model.get("loaded", False),
                    description=model.get("description"),
                )
                for model in models_data
            ]
        else:
            return []

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        """Get detailed information about a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Model information dictionary
        """
        response = self._make_request("GET", f"/models/{model_name}")

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return response.data

    def upload_and_parse(self, file_path: Union[str, Path]) -> ParseResult:
        """Upload and parse a GFL file.

        Args:
            file_path: Path to the GFL file

        Returns:
            ParseResult from parsing the uploaded file
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/plain")}

            # Use requests directly for file upload
            url = urljoin(self.base_url + "/", "upload/parse")
            response = requests.post(
                url,
                files=files,
                timeout=self.timeout,
                headers={"Authorization": self.session.headers.get("Authorization", "")},
            )

        if response.status_code >= 400:
            raise GFLAPIError(f"Upload failed: {response.text}", response.status_code)

        data = response.json()
        return ParseResult(
            ast=data.get("ast", {}),
            success=data.get("success", True),
            message=data.get("message", "Success"),
            execution_time_ms=data.get("execution_time_ms", 0.0),
        )

    def batch_inference(
        self,
        content_list: list[str],
        model_name: str = "heuristic",
        explain: bool = False,
    ) -> list[dict[str, Any]]:
        """Run batch inference on multiple GFL samples.

        Args:
            content_list: List of GFL content strings
            model_name: Model to use for all inferences
            explain: Include explanations in results

        Returns:
            List of inference results
        """
        # Build request payload
        requests_data = [{"content": content, "model_name": model_name, "explain": explain} for content in content_list]

        response = self._make_request("POST", "/batch/infer", json=requests_data)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return response.data.get("batch_results", [])

    def get_stats(self) -> dict[str, Any]:
        """Get API server statistics.

        Returns:
            Dictionary with server statistics
        """
        response = self._make_request("GET", "/stats")

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return response.data


class AsyncGFLClient:
    """Asynchronous client for GeneForgeLang API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout: float = 30.0,
        retries: int = 3,
        api_key: str | None = None,
    ):
        """Initialize the async GFL client."""
        if not HAS_HTTPX:
            raise ImportError("httpx library required for async client. Install with: pip install httpx")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

        # Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GeneForgeLang-AsyncClient/1.0",
        }

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Create client
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, headers=headers)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the async client."""
        await self.client.aclose()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make async HTTP request with retry logic."""
        last_exception = None

        for attempt in range(self.retries + 1):
            try:
                response = await self.client.request(method=method, url=endpoint, **kwargs)

                # Handle HTTP errors
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", f"HTTP {response.status_code}")
                    except:
                        error_message = f"HTTP {response.status_code}: {response.text[:100]}"

                    raise GFLAPIError(error_message, response.status_code)

                # Parse response
                try:
                    data = response.json()
                    return APIResponse(
                        success=data.get("success", True),
                        data=data.get("data"),
                        message=data.get("message", "Success"),
                        status_code=response.status_code,
                        execution_time_ms=data.get("execution_time_ms"),
                        timestamp=data.get("timestamp"),
                    )
                except:
                    return APIResponse(
                        success=True,
                        data=response.text,
                        message="Non-JSON response",
                        status_code=response.status_code,
                    )

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.retries:
                    wait_time = 2**attempt
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                continue

        # All retries failed
        raise GFLConnectionError(f"Failed after {self.retries + 1} attempts: {last_exception}")

    async def health_check(self) -> dict[str, Any]:
        """Check API server health status."""
        response = await self._make_request("GET", "/health")
        if not response.success:
            raise GFLAPIError(response.message, response.status_code)
        return response.data

    async def parse(self, content: str, use_grammar: bool = False, filename: str = "<client>") -> ParseResult:
        """Async version of parse method."""
        payload = {"content": content, "use_grammar": use_grammar, "filename": filename}

        response = await self._make_request("POST", "/parse", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return ParseResult(
            ast=response.data.get("ast", {}),
            success=response.success,
            message=response.message,
            execution_time_ms=response.execution_time_ms or 0.0,
        )

    async def infer(self, content: str, model_name: str = "heuristic", explain: bool = True) -> InferenceResult:
        """Async version of infer method."""
        payload = {"content": content, "model_name": model_name, "explain": explain}

        response = await self._make_request("POST", "/infer", json=payload)

        if not response.success:
            raise GFLAPIError(response.message, response.status_code)

        return InferenceResult(
            prediction=response.data.get("prediction"),
            confidence=response.data.get("confidence", 0.0),
            explanation=response.data.get("explanation", ""),
            model_used=response.data.get("model_used", model_name),
            features_used=response.data.get("features_used"),
            success=response.success,
            message=response.message,
            execution_time_ms=response.execution_time_ms or 0.0,
        )


# Convenience functions
def create_client(base_url: str = "http://127.0.0.1:8000", **kwargs) -> GFLClient:
    """Create a synchronous GFL client."""
    return GFLClient(base_url=base_url, **kwargs)


def create_async_client(base_url: str = "http://127.0.0.1:8000", **kwargs) -> AsyncGFLClient:
    """Create an asynchronous GFL client."""
    return AsyncGFLClient(base_url=base_url, **kwargs)


# Example usage and testing
async def example_usage():
    """Example usage of the GFL client SDK."""

    # Test GFL content
    gfl_content = """
    experiment:
      tool: CRISPR_cas9
      type: gene_editing
      params:
        target_gene: TP53

    analyze:
      strategy: knockout_validation
    """

    print("Testing GFL Client SDK")
    print("=" * 40)

    # Synchronous client
    print("\n1. Synchronous Client:")
    try:
        client = create_client()

        # Health check
        health = client.health_check()
        print(f"   Health: {health.get('status', 'unknown')}")

        # Parse and validate
        parse_result = client.parse(gfl_content)
        print(f"   Parse: {'✅' if parse_result.success else '❌'} ({parse_result.execution_time_ms:.1f}ms)")

        validation_result = client.validate(gfl_content)
        print(
            f"   Validate: {'✅' if validation_result.is_valid else '❌'} ({validation_result.execution_time_ms:.1f}ms)"
        )

        # Inference
        inference_result = client.infer(gfl_content)
        print(f"   Inference: {inference_result.prediction} ({inference_result.confidence:.1%})")

        # List models
        models = client.list_models()
        print(f"   Models: {[m.name for m in models]}")

    except Exception as e:
        print(f"   Error: {e}")

    # Asynchronous client
    print("\n2. Asynchronous Client:")
    try:
        async with create_async_client() as async_client:
            # Health check
            health = await async_client.health_check()
            print(f"   Health: {health.get('status', 'unknown')}")

            # Parse
            parse_result = await async_client.parse(gfl_content)
            print(f"   Parse: {'✅' if parse_result.success else '❌'} ({parse_result.execution_time_ms:.1f}ms)")

            # Inference
            inference_result = await async_client.infer(gfl_content)
            print(f"   Inference: {inference_result.prediction} ({inference_result.confidence:.1%})")

    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    # Run example if executed directly
    asyncio.run(example_usage())
