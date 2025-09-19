"""Unified Server Launcher for GeneForgeLang.

This module provides a unified way to launch both the API server and web interface
for GeneForgeLang workflows with:
- Combined or separate server startup
- Configuration management
- Process monitoring and health checks
- Graceful shutdown handling
- Docker support preparation
"""

from __future__ import annotations

import argparse
import logging
import multiprocessing as mp
import signal
import sys
import time
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ServerProcess:
    """Manages individual server processes."""

    def __init__(self, name: str, target_func, args: tuple = (), kwargs: dict = None):
        self.name = name
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs or {}
        self.process: mp.Process | None = None
        self.start_time: float | None = None

    def start(self) -> bool:
        """Start the server process."""
        try:
            self.process = mp.Process(
                target=self.target_func,
                args=self.args,
                kwargs=self.kwargs,
                name=f"gfl_{self.name}",
            )
            self.process.start()
            self.start_time = time.time()
            logger.info(f"Started {self.name} server (PID: {self.process.pid})")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.name} server: {e}")
            return False

    def stop(self, timeout: float = 10.0) -> bool:
        """Stop the server process."""
        if not self.process or not self.process.is_alive():
            return True

        try:
            logger.info(f"Stopping {self.name} server...")
            self.process.terminate()
            self.process.join(timeout=timeout)

            if self.process.is_alive():
                logger.warning(f"Force killing {self.name} server...")
                self.process.kill()
                self.process.join(timeout=5.0)

            logger.info(f"Stopped {self.name} server")
            return True
        except Exception as e:
            logger.error(f"Error stopping {self.name} server: {e}")
            return False

    def is_running(self) -> bool:
        """Check if the server process is running."""
        return self.process is not None and self.process.is_alive()

    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        if self.start_time and self.is_running():
            return time.time() - self.start_time
        return 0.0


class GFLServerManager:
    """Manages multiple GFL server processes."""

    def __init__(self):
        self.servers: dict[str, ServerProcess] = {}
        self.shutdown_requested = False

    def add_api_server(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
        """Add API server to management."""
        try:
            from gfl.api_server import run_server

            server = ServerProcess(
                name="api",
                target_func=run_server,
                kwargs={"host": host, "port": port, "reload": reload},
            )
            self.servers["api"] = server
            logger.info(f"Configured API server for {host}:{port}")
        except ImportError:
            logger.error("Cannot import API server - ensure FastAPI dependencies are installed")

    def add_web_interface(
        self,
        host: str = "127.0.0.1",
        port: int = 7860,
        share: bool = False,
        debug: bool = False,
    ) -> None:
        """Add web interface to management."""
        try:
            from gfl.web_interface import launch_web_interface

            server = ServerProcess(
                name="web",
                target_func=launch_web_interface,
                kwargs={
                    "server_name": host,
                    "server_port": port,
                    "share": share,
                    "debug": debug,
                },
            )
            self.servers["web"] = server
            logger.info(f"Configured web interface for {host}:{port}")
        except ImportError:
            logger.error("Cannot import web interface - ensure Gradio dependencies are installed")

    def start_all(self) -> bool:
        """Start all configured servers."""
        success = True

        for _name, server in self.servers.items():
            if not server.start():
                success = False

        if success:
            logger.info(f"All {len(self.servers)} servers started successfully")
        else:
            logger.error("Some servers failed to start")

        return success

    def stop_all(self, timeout: float = 10.0) -> bool:
        """Stop all running servers."""
        self.shutdown_requested = True
        success = True

        for _name, server in self.servers.items():
            if not server.stop(timeout):
                success = False

        return success

    def get_status(self) -> dict[str, dict]:
        """Get status of all servers."""
        status = {}

        for name, server in self.servers.items():
            status[name] = {
                "running": server.is_running(),
                "uptime_seconds": server.get_uptime(),
                "pid": server.process.pid if server.process else None,
            }

        return status

    def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal or server failures."""
        try:
            while not self.shutdown_requested:
                # Check if any servers have died
                running_servers = [name for name, server in self.servers.items() if server.is_running()]

                if not running_servers:
                    logger.warning("All servers have stopped")
                    break

                time.sleep(1.0)

        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error during server monitoring: {e}")

        self.stop_all()


def setup_signal_handlers(manager: GFLServerManager) -> None:
    """Set up signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Windows-specific
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal_handler)


def check_dependencies() -> dict[str, bool]:
    """Check availability of optional dependencies."""
    deps = {}

    # FastAPI for API server
    try:
        import fastapi
        import uvicorn

        deps["fastapi"] = True
    except ImportError:
        deps["fastapi"] = False

    # Gradio for web interface
    try:
        import gradio

        deps["gradio"] = True
    except ImportError:
        deps["gradio"] = False

    # GFL API
    try:
        from gfl.api import parse

        deps["gfl_api"] = True
    except ImportError:
        deps["gfl_api"] = False

    # Enhanced inference engine
    try:
        from gfl.enhanced_inference_engine import get_inference_engine

        deps["enhanced_inference"] = True
    except ImportError:
        deps["enhanced_inference"] = False

    return deps


def print_startup_banner(config: dict) -> None:
    """Print startup banner with configuration."""
    print(
        """
╔═══════════════════════════════════════════════════════════════╗
║                    GeneForgeLang Server Suite                 ║
║           Genomic Workflow Analysis and Inference            ║
╚═══════════════════════════════════════════════════════════════╝
"""
    )

    print("Configuration:")
    print("-" * 50)

    if config.get("api_enabled"):
        print(f"🌐 API Server:     http://{config['api_host']}:{config['api_port']}")
        print(f"   📚 Docs:        http://{config['api_host']}:{config['api_port']}/docs")

    if config.get("web_enabled"):
        print(f"🖥️  Web Interface: http://{config['web_host']}:{config['web_port']}")

    print(f"🔧 Mode:          {'Development' if config.get('debug') else 'Production'}")
    print("📊 Monitoring:    Enabled")
    print()


def main():
    """Main entry point for the server launcher."""

    parser = argparse.ArgumentParser(
        description="GeneForgeLang Server Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                    # Start both API and web interface
  %(prog)s --api-only              # Start only API server
  %(prog)s --web-only              # Start only web interface
  %(prog)s --api-port 8080 --web-port 8090  # Custom ports
  %(prog)s --host 0.0.0.0 --share  # Bind to all interfaces with public sharing
        """,
    )

    # Server selection
    server_group = parser.add_mutually_exclusive_group()
    server_group.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="Start both API server and web interface (default)",
    )
    server_group.add_argument("--api-only", action="store_true", help="Start only the API server")
    server_group.add_argument("--web-only", action="store_true", help="Start only the web interface")

    # Network configuration
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind servers to (default: 127.0.0.1)",
    )
    parser.add_argument("--api-host", help="API server host (overrides --host)")
    parser.add_argument("--web-host", help="Web interface host (overrides --host)")
    parser.add_argument("--api-port", type=int, default=8000, help="API server port (default: 8000)")
    parser.add_argument("--web-port", type=int, default=7860, help="Web interface port (default: 7860)")

    # Additional options
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create public share link for web interface",
    )
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies and exit")

    args = parser.parse_args()

    # Check dependencies if requested
    if args.check_deps:
        print("Checking dependencies...")
        deps = check_dependencies()

        for dep, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"  {dep}: {status}")

        if not all(deps.values()):
            print("\nInstall missing dependencies:")
            if not deps["fastapi"]:
                print("  pip install fastapi uvicorn")
            if not deps["gradio"]:
                print("  pip install gradio")

        return

    # Resolve server selection
    if args.api_only:
        api_enabled, web_enabled = True, False
    elif args.web_only:
        api_enabled, web_enabled = False, True
    else:  # --all or default
        api_enabled, web_enabled = True, True

    # Resolve host configuration
    api_host = args.api_host or args.host
    web_host = args.web_host or args.host

    # Configuration summary
    config = {
        "api_enabled": api_enabled,
        "web_enabled": web_enabled,
        "api_host": api_host,
        "api_port": args.api_port,
        "web_host": web_host,
        "web_port": args.web_port,
        "debug": args.debug,
        "reload": args.reload,
        "share": args.share,
    }

    # Check dependencies
    deps = check_dependencies()

    if api_enabled and not deps["fastapi"]:
        logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
        return 1

    if web_enabled and not deps["gradio"]:
        logger.error("Gradio not available. Install with: pip install gradio")
        return 1

    if not deps["gfl_api"]:
        logger.error("GFL API not available. Check installation.")
        return 1

    # Print startup information
    print_startup_banner(config)

    # Create server manager
    manager = GFLServerManager()

    # Configure servers
    if api_enabled:
        manager.add_api_server(host=api_host, port=args.api_port, reload=args.reload)

    if web_enabled:
        manager.add_web_interface(host=web_host, port=args.web_port, share=args.share, debug=args.debug)

    # Set up signal handlers
    setup_signal_handlers(manager)

    # Start servers
    if not manager.start_all():
        logger.error("Failed to start servers")
        return 1

    # Print access URLs
    print("Servers started successfully!")
    print("Access URLs:")

    if api_enabled:
        print(f"  🌐 API Server:     http://{api_host}:{args.api_port}")
        print(f"  📚 API Docs:       http://{api_host}:{args.api_port}/docs")

    if web_enabled:
        print(f"  🖥️  Web Interface: http://{web_host}:{args.web_port}")

    print("\nPress Ctrl+C to stop all servers")
    print("-" * 50)

    # Monitor servers
    try:
        manager.wait_for_shutdown()
    except Exception as e:
        logger.error(f"Server management error: {e}")
        return 1

    print("\nAll servers stopped. Goodbye! 👋")
    return 0


if __name__ == "__main__":
    sys.exit(main())
