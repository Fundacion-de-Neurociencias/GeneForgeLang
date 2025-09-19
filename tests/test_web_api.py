"""Tests for GeneForgeLang Web Interface and API Server.

This test suite covers:
- API server endpoints and functionality
- Web interface components and interactions
- Client SDK functionality
- Error handling and edge cases
- Performance and reliability testing
"""

import json
import unittest
from unittest.mock import MagicMock, patch

# Test data
SAMPLE_GFL = """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53

analyze:
  strategy: knockout_validation
"""

INVALID_GFL = """
experiment:
  tool: CRISPR_cas9
  invalid_syntax: {{{ broken
"""


class TestAPIServer(unittest.TestCase):
    """Test API server functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the GFL API imports
        self.gfl_api_patcher = patch("gfl.api_server.HAS_GFL_API", True)
        self.gfl_api_patcher.start()

        # Mock parse function
        self.parse_mock = patch("gfl.api_server.parse")
        self.parse_func = self.parse_mock.start()
        self.parse_func.return_value = {"experiment": {"tool": "CRISPR_cas9"}}

        # Mock validate function
        self.validate_mock = patch("gfl.api_server.validate")
        self.validate_func = self.validate_mock.start()
        self.validate_func.return_value = []

        # Mock inference functions
        self.infer_mock = patch("gfl.api_server.infer_enhanced")
        self.infer_func = self.infer_mock.start()
        self.infer_func.return_value = {
            "label": "edited",
            "confidence": 0.85,
            "explanation": "CRISPR gene editing detected",
        }

    def tearDown(self):
        """Clean up test fixtures."""
        self.gfl_api_patcher.stop()
        self.parse_mock.stop()
        self.validate_mock.stop()
        self.infer_mock.stop()

    def test_api_server_import(self):
        """Test that API server can be imported."""
        try:
            from gfl.api_server import app, create_app

            self.assertIsNotNone(app)
            self.assertIsNotNone(create_app)
        except ImportError as e:
            self.skipTest(f"API server dependencies not available: {e}")

    @patch("gfl.api_server.HAS_GFL_API", True)
    def test_create_success_response(self):
        """Test success response creation."""
        try:
            from gfl.api_server import create_success_response

            response = create_success_response(data={"test": "data"}, message="Test successful")

            self.assertTrue(response["success"])
            self.assertEqual(response["message"], "Test successful")
            self.assertEqual(response["data"]["test"], "data")
            self.assertIn("timestamp", response)
        except ImportError:
            self.skipTest("API server not available")

    @patch("gfl.api_server.HAS_GFL_API", True)
    def test_create_error_response(self):
        """Test error response creation."""
        try:
            from gfl.api_server import create_error_response

            response = create_error_response("Test error", 400)

            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.body)
            self.assertFalse(response_data["success"])
            self.assertEqual(response_data["message"], "Test error")
        except ImportError:
            self.skipTest("API server not available")

    def test_api_server_configuration(self):
        """Test API server configuration."""
        try:
            from gfl.api_server import create_app

            app = create_app()

            # Check basic app properties
            self.assertEqual(app.title, "GeneForgeLang API Server")
            self.assertIn("REST API for parsing", app.description)
            self.assertEqual(app.version, "1.0.0")
        except ImportError:
            self.skipTest("API server not available")

    def test_parse_request_model(self):
        """Test parse request validation."""
        try:
            from gfl.api_server import GFLParseRequest

            # Valid request
            request = GFLParseRequest(content=SAMPLE_GFL, use_grammar=False, filename="test.gfl")

            self.assertEqual(request.content, SAMPLE_GFL)
            self.assertFalse(request.use_grammar)
            self.assertEqual(request.filename, "test.gfl")

            # Test minimum length validation
            with self.assertRaises(Exception):  # Pydantic validation error
                GFLParseRequest(content="")

        except ImportError:
            self.skipTest("API server not available")

    def test_inference_request_model(self):
        """Test inference request validation."""
        try:
            from gfl.api_server import GFLInferenceRequest

            request = GFLInferenceRequest(content=SAMPLE_GFL, model_name="heuristic", explain=True)

            self.assertEqual(request.model_name, "heuristic")
            self.assertTrue(request.explain)

        except ImportError:
            self.skipTest("API server not available")


class TestWebInterface(unittest.TestCase):
    """Test web interface functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Gradio
        self.gradio_patcher = patch("gfl.web_interface.gr")
        self.gr_mock = self.gradio_patcher.start()

        # Mock GFL API
        self.gfl_api_patcher = patch("gfl.web_interface.HAS_GFL_API", True)
        self.gfl_api_patcher.start()

        # Mock parse function
        self.parse_mock = patch("gfl.web_interface.parse")
        self.parse_func = self.parse_mock.start()
        self.parse_func.return_value = {"experiment": {"tool": "CRISPR_cas9"}}

    def tearDown(self):
        """Clean up test fixtures."""
        self.gradio_patcher.stop()
        self.gfl_api_patcher.stop()
        self.parse_mock.stop()

    def test_web_interface_import(self):
        """Test that web interface can be imported."""
        try:
            from gfl.web_interface import create_interface, launch_web_interface

            self.assertIsNotNone(create_interface)
            self.assertIsNotNone(launch_web_interface)
        except ImportError as e:
            self.skipTest(f"Web interface dependencies not available: {e}")

    def test_sample_gfl_content(self):
        """Test sample GFL content availability."""
        try:
            from gfl.web_interface import SAMPLE_GFL_CONTENT

            self.assertIsInstance(SAMPLE_GFL_CONTENT, dict)
            self.assertIn("CRISPR Gene Editing", SAMPLE_GFL_CONTENT)
            self.assertIn("RNA-seq Analysis", SAMPLE_GFL_CONTENT)

            # Check sample content is valid-looking GFL
            for name, content in SAMPLE_GFL_CONTENT.items():
                self.assertIn("experiment:", content)
                self.assertIn("tool:", content)

        except ImportError:
            self.skipTest("Web interface not available")

    def test_initialize_inference_engine(self):
        """Test inference engine initialization."""
        try:
            from gfl.web_interface import initialize_inference_engine

            with patch("gfl.web_interface.get_inference_engine") as mock_engine:
                mock_engine.return_value.list_models.return_value = [
                    "heuristic",
                    "test_model",
                ]

                success, message = initialize_inference_engine()

                # Should succeed with mocked engine
                self.assertTrue(success)
                self.assertIn("models", message)

        except ImportError:
            self.skipTest("Web interface not available")

    @patch("gfl.web_interface.HAS_GFL_API", True)
    def test_parse_and_validate_gfl(self):
        """Test GFL parsing and validation function."""
        try:
            from gfl.web_interface import parse_and_validate_gfl

            # Mock validation result
            with patch("gfl.web_interface.validate") as mock_validate:
                mock_validate.return_value = []  # No errors

                is_valid, message, ast = parse_and_validate_gfl(SAMPLE_GFL)

                self.assertTrue(is_valid)
                self.assertIn("Parsed", message)
                self.assertIsNotNone(ast)

        except ImportError:
            self.skipTest("Web interface not available")

    @patch("gfl.web_interface.HAS_GFL_API", True)
    def test_parse_and_validate_gfl_error(self):
        """Test GFL parsing with errors."""
        try:
            from gfl.web_interface import parse_and_validate_gfl

            # Test empty content
            is_valid, message, ast = parse_and_validate_gfl("")

            self.assertFalse(is_valid)
            self.assertIn("Empty", message)
            self.assertIsNone(ast)

        except ImportError:
            self.skipTest("Web interface not available")

    def test_get_available_models(self):
        """Test getting available models."""
        try:
            from gfl.web_interface import get_available_models

            # Without inference engine
            models = get_available_models()
            self.assertEqual(models, ["heuristic"])  # Default fallback

            # With mocked inference engine
            with patch("gfl.web_interface.inference_engine") as mock_engine:
                mock_engine.list_models.return_value = ["heuristic", "advanced", "test"]
                models = get_available_models()
                self.assertEqual(len(models), 3)
                self.assertIn("heuristic", models)

        except ImportError:
            self.skipTest("Web interface not available")

    def test_get_system_stats(self):
        """Test system statistics generation."""
        try:
            from gfl.web_interface import get_system_stats

            stats = get_system_stats()

            self.assertIsInstance(stats, str)
            self.assertIn("System Statistics", stats)
            self.assertIn("Uptime", stats)
            self.assertIn("GFL API", stats)

        except ImportError:
            self.skipTest("Web interface not available")


class TestClientSDK(unittest.TestCase):
    """Test client SDK functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock requests
        self.requests_patcher = patch("gfl.client_sdk.HAS_REQUESTS", True)
        self.requests_patcher.start()

        self.requests_mock = patch("gfl.client_sdk.requests")
        self.requests_lib = self.requests_mock.start()

        # Mock response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "success": True,
            "data": {"test": "data"},
            "message": "Success",
        }

        self.requests_lib.Session.return_value.request.return_value = self.mock_response

    def tearDown(self):
        """Clean up test fixtures."""
        self.requests_patcher.stop()
        self.requests_mock.stop()

    def test_client_creation(self):
        """Test client creation and configuration."""
        try:
            from gfl.client_sdk import GFLClient

            client = GFLClient(base_url="http://test-server:8000", timeout=60.0, retries=5)

            self.assertEqual(client.base_url, "http://test-server:8000")
            self.assertEqual(client.timeout, 60.0)
            self.assertEqual(client.retries, 5)

        except ImportError:
            self.skipTest("Client SDK not available")

    def test_api_response_dataclass(self):
        """Test APIResponse dataclass."""
        try:
            from gfl.client_sdk import APIResponse

            response = APIResponse(
                success=True,
                data={"test": "value"},
                message="Test message",
                status_code=200,
                execution_time_ms=123.45,
            )

            self.assertTrue(response.success)
            self.assertEqual(response.data["test"], "value")
            self.assertEqual(response.execution_time_ms, 123.45)

        except ImportError:
            self.skipTest("Client SDK not available")

    def test_parse_result_dataclass(self):
        """Test ParseResult dataclass."""
        try:
            from gfl.client_sdk import ParseResult

            result = ParseResult(
                ast={"experiment": {"tool": "test"}},
                success=True,
                message="Parsed successfully",
                execution_time_ms=50.0,
            )

            self.assertTrue(result.success)
            self.assertEqual(result.ast["experiment"]["tool"], "test")

        except ImportError:
            self.skipTest("Client SDK not available")

    def test_client_make_request(self):
        """Test client HTTP request method."""
        try:
            from gfl.client_sdk import GFLClient

            client = GFLClient()

            # Mock successful response
            response = client._make_request("GET", "/test")

            self.assertTrue(response.success)
            self.assertEqual(response.data["test"], "data")

        except ImportError:
            self.skipTest("Client SDK not available")

    def test_client_error_handling(self):
        """Test client error handling."""
        try:
            from gfl.client_sdk import GFLAPIError, GFLClient

            client = GFLClient()

            # Mock error response
            self.mock_response.status_code = 400
            self.mock_response.json.return_value = {
                "success": False,
                "message": "Bad request",
            }

            with self.assertRaises(GFLAPIError) as context:
                client._make_request("GET", "/error")

            self.assertEqual(context.exception.status_code, 400)

        except ImportError:
            self.skipTest("Client SDK not available")

    def test_convenience_functions(self):
        """Test convenience functions for client creation."""
        try:
            from gfl.client_sdk import create_async_client, create_client

            sync_client = create_client("http://test:8000")
            self.assertEqual(sync_client.base_url, "http://test:8000")

            # Async client test (if httpx available)
            try:
                async_client = create_async_client("http://test:8000")
                self.assertEqual(async_client.base_url, "http://test:8000")
            except ImportError:
                pass  # httpx not available

        except ImportError:
            self.skipTest("Client SDK not available")


class TestServerLauncher(unittest.TestCase):
    """Test server launcher functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock multiprocessing
        self.mp_patcher = patch("gfl.server_launcher.mp")
        self.mp_mock = self.mp_patcher.start()

        # Mock process
        self.mock_process = MagicMock()
        self.mock_process.is_alive.return_value = True
        self.mock_process.pid = 12345
        self.mp_mock.Process.return_value = self.mock_process

    def tearDown(self):
        """Clean up test fixtures."""
        self.mp_patcher.stop()

    def test_server_process_creation(self):
        """Test ServerProcess class."""
        try:
            from gfl.server_launcher import ServerProcess

            def dummy_target():
                pass

            server = ServerProcess(
                name="test_server",
                target_func=dummy_target,
                args=(1, 2),
                kwargs={"param": "value"},
            )

            self.assertEqual(server.name, "test_server")
            self.assertEqual(server.args, (1, 2))
            self.assertEqual(server.kwargs["param"], "value")

        except ImportError:
            self.skipTest("Server launcher not available")

    def test_server_process_start(self):
        """Test server process starting."""
        try:
            from gfl.server_launcher import ServerProcess

            def dummy_target():
                pass

            server = ServerProcess("test", dummy_target)
            success = server.start()

            self.assertTrue(success)
            self.assertTrue(server.is_running())
            self.assertIsNotNone(server.start_time)

        except ImportError:
            self.skipTest("Server launcher not available")

    def test_gfl_server_manager(self):
        """Test GFLServerManager class."""
        try:
            from gfl.server_launcher import GFLServerManager

            manager = GFLServerManager()

            # Mock API server addition
            with patch("gfl.server_launcher.GFLServerManager.add_api_server"):
                manager.add_api_server(host="127.0.0.1", port=8080)

            self.assertFalse(manager.shutdown_requested)

        except ImportError:
            self.skipTest("Server launcher not available")

    def test_check_dependencies(self):
        """Test dependency checking."""
        try:
            from gfl.server_launcher import check_dependencies

            deps = check_dependencies()

            self.assertIsInstance(deps, dict)
            self.assertIn("gfl_api", deps)
            self.assertIn("enhanced_inference", deps)

            # Check that all values are boolean
            for dep_name, available in deps.items():
                self.assertIsInstance(available, bool, f"Dependency {dep_name} should be boolean")

        except ImportError:
            self.skipTest("Server launcher not available")


class TestIntegration(unittest.TestCase):
    """Integration tests for web interface and API components."""

    def test_full_workflow_mock(self):
        """Test full workflow with mocked components."""
        # This test ensures that all components can work together
        # even if the actual dependencies aren't available

        workflow_steps = []

        # Step 1: Parse GFL
        try:
            from gfl.client_sdk import ParseResult

            parse_result = ParseResult(
                ast={"experiment": {"tool": "CRISPR_cas9"}},
                success=True,
                message="Parsed successfully",
                execution_time_ms=25.5,
            )
            workflow_steps.append("parse")
            self.assertTrue(parse_result.success)
        except ImportError:
            pass

        # Step 2: Validate
        try:
            from gfl.client_sdk import ValidationResult

            validation_result = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                success=True,
                message="Validation passed",
                execution_time_ms=15.0,
            )
            workflow_steps.append("validate")
            self.assertTrue(validation_result.is_valid)
        except ImportError:
            pass

        # Step 3: Inference
        try:
            from gfl.client_sdk import InferenceResult

            inference_result = InferenceResult(
                prediction="edited",
                confidence=0.87,
                explanation="CRISPR editing detected",
                model_used="heuristic",
                features_used={"tool": "CRISPR_cas9"},
                success=True,
                message="Inference completed",
                execution_time_ms=42.1,
            )
            workflow_steps.append("infer")
            self.assertEqual(inference_result.prediction, "edited")
            self.assertGreater(inference_result.confidence, 0.8)
        except ImportError:
            pass

        # At least some components should be testable
        self.assertGreater(len(workflow_steps), 0, "No workflow components could be tested")

    def test_error_propagation(self):
        """Test that errors propagate correctly through the system."""

        # Test client error classes
        try:
            from gfl.client_sdk import GFLAPIError, GFLClientError, GFLConnectionError

            # Test basic exception
            with self.assertRaises(GFLClientError):
                raise GFLClientError("Test error")

            # Test API error with status code
            with self.assertRaises(GFLAPIError) as context:
                raise GFLAPIError("API error", 404)

            self.assertEqual(context.exception.status_code, 404)

        except ImportError:
            pass  # Client SDK not available


if __name__ == "__main__":
    unittest.main()
