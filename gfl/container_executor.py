"""Container-based execution for GFL plugins."""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

logger = logging.getLogger(__name__)


class ContainerExecutionError(Exception):
    """Exception raised during container execution."""

    pass


class ContainerExecutor:
    """Executor for running plugins in Docker containers."""

    def __init__(self):
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
            except Exception:
                logger.warning("Docker not available, container execution disabled")

    def is_container_execution_available(self) -> bool:
        """Check if container execution is available."""
        return self.docker_client is not None

    def execute_in_container(
        self,
        container_image: str,
        command: list[str],
        working_dir: str = "/workspace",
        input_files: Optional[dict[str, str]] = None,
        output_files: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Execute a command in a Docker container.

        Args:
            container_image: Docker image to use
            command: Command to execute in the container
            working_dir: Working directory inside the container
            input_files: Mapping of host paths to container paths for input files
            output_files: List of output file paths to retrieve from container

        Returns:
            Dictionary containing execution results
        """
        if not self.docker_client:
            raise ContainerExecutionError("Docker not available for container execution")

        # Create temporary directory for file I/O
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Prepare volumes for mounting
            volumes = {str(temp_path): {"bind": working_dir, "mode": "rw"}}

            # Handle input files
            if input_files:
                for host_path, container_path in input_files.items():
                    # Copy input files to temp directory
                    host_file = Path(host_path)
                    if host_file.exists():
                        container_file_path = temp_path / container_path.lstrip("/")
                        container_file_path.parent.mkdir(parents=True, exist_ok=True)
                        container_file_path.write_bytes(host_file.read_bytes())

            try:
                # Run the container
                container = self.docker_client.containers.run(
                    container_image,
                    command,
                    volumes=volumes,
                    working_dir=working_dir,
                    detach=True,
                    remove=False,  # Keep container to get logs
                )

                # Wait for completion
                result = container.wait()
                exit_code = result["StatusCode"]
                logs = container.logs().decode("utf-8")

                # Remove container
                container.remove()

                if exit_code != 0:
                    raise ContainerExecutionError(f"Container execution failed with exit code {exit_code}: {logs}")

                # Collect output files
                output_data = {}
                if output_files:
                    for output_file in output_files:
                        container_file_path = temp_path / output_file.lstrip("/")
                        if container_file_path.exists():
                            output_data[output_file] = container_file_path.read_text()

                return {"exit_code": exit_code, "logs": logs, "output_files": output_data, "success": True}

            except docker.errors.ContainerError as e:
                raise ContainerExecutionError(f"Container execution failed: {e}")
            except docker.errors.ImageNotFound:
                raise ContainerExecutionError(f"Container image '{container_image}' not found")
            except Exception as e:
                raise ContainerExecutionError(f"Container execution error: {e}")

    def execute_plugin_method_in_container(
        self,
        container_image: str,
        plugin_name: str,
        method_name: str,
        params: dict[str, Any],
        working_dir: str = "/workspace",
    ) -> dict[str, Any]:
        """
        Execute a plugin method in a container by serializing parameters and results.

        Args:
            container_image: Docker image to use
            plugin_name: Name of the plugin
            method_name: Name of the method to execute
            params: Parameters for the method
            working_dir: Working directory inside the container

        Returns:
            Method execution results
        """
        # Serialize parameters to JSON
        params_json = json.dumps(params)

        # Create command to execute in container
        command = [
            "python",
            "-c",
            f"import sys, json; "
            f"from gfl.plugins.plugin_registry import plugin_registry; "
            f"plugin = plugin_registry.get_{plugin_name}(); "
            f"params = json.loads('{params_json}'); "
            f"result = getattr(plugin, '{method_name}')(params); "
            f"print(json.dumps(result))",
        ]

        # Execute in container
        result = self.execute_in_container(container_image, command, working_dir)

        # Parse result
        if result["success"] and result["logs"]:
            try:
                output_lines = result["logs"].strip().split("\n")
                last_line = output_lines[-1]
                parsed_result = json.loads(last_line)
                result["parsed_result"] = parsed_result
            except json.JSONDecodeError:
                pass  # Keep raw logs if JSON parsing fails

        return result
