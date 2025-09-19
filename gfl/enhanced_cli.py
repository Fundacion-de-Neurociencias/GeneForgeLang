"""Enhanced command-line interface for GeneForgeLang.

This module provides a comprehensive CLI with modern argument parsing,
rich output formatting, progress indicators, and extensive functionality
for working with GFL files and workflows.

Features:
- Rich argument parsing with subcommands
- Colorized and formatted output
- Progress indicators for long operations
- Batch processing capabilities
- Plugin management commands
- Performance monitoring and profiling
- Configuration management
- Interactive modes
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Rich output formatting (optional dependency)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
    )
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None

# Import GFL components
from gfl import __api_version__, __version__
from gfl.api import infer, parse, parse_enhanced, validate
from gfl.cli_utils import CLIUtilsMixin
from gfl.performance import get_monitor, get_optimizer

# Optional imports with fallbacks
try:
    from gfl.plugins.plugin_registry import (
        activate_plugin,
        deactivate_plugin,
        list_plugins,
        plugin_registry,
        validate_plugin_dependencies,
    )

    HAS_PLUGINS = True
except ImportError:
    HAS_PLUGINS = False

try:
    from gfl.enhanced_schema_validator import EnhancedSchemaValidator

    HAS_ENHANCED_SCHEMA = True
except ImportError:
    HAS_ENHANCED_SCHEMA = False

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CLIError(Exception):
    """Base exception for CLI errors."""

    pass


class OutputFormatter:
    """Handles output formatting with optional rich formatting."""

    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and HAS_RICH
        self.console = Console() if self.use_rich else None

    def print(self, *args, **kwargs):
        """Print with optional rich formatting."""
        if self.use_rich:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def print_json(self, data: Any, title: str = None):
        """Print JSON data with syntax highlighting."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if self.use_rich:
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            if title:
                panel = Panel(syntax, title=title, border_style="blue")
                self.console.print(panel)
            else:
                self.console.print(syntax)
        else:
            if title:
                print(f"=== {title} ===")
            print(json_str)

    def print_table(self, data: List[Dict[str, Any]], headers: List[str], title: str = None):
        """Print data as a table."""
        if self.use_rich:
            table = Table(title=title)
            for header in headers:
                table.add_column(header)

            for row in data:
                table.add_row(*[str(row.get(header, "")) for header in headers])

            self.console.print(table)
        else:
            if title:
                print(f"=== {title} ===")

            # Simple ASCII table
            if not data:
                print("No data")
                return

            # Calculate column widths
            widths = [len(h) for h in headers]
            for row in data:
                for i, header in enumerate(headers):
                    widths[i] = max(widths[i], len(str(row.get(header, ""))))

            # Print headers
            print(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
            print("-|-".join("-" * w for w in widths))

            # Print rows
            for row in data:
                print(" | ".join(str(row.get(h, "")).ljust(w) for h, w in zip(headers, widths)))

    def print_error(self, message: str, error: Exception = None):
        """Print error message."""
        if self.use_rich:
            self.console.print(f"[red]Error:[/red] {message}")
            if error and logger.isEnabledFor(logging.DEBUG):
                import traceback

                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
        else:
            print(f"Error: {message}", file=sys.stderr)
            if error and logger.isEnabledFor(logging.DEBUG):
                import traceback

                print(traceback.format_exc(), file=sys.stderr)

    def print_success(self, message: str):
        """Print success message."""
        if self.use_rich:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"✓ {message}")

    def print_warning(self, message: str):
        """Print warning message."""
        if self.use_rich:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"⚠ {message}")

    def progress(self, description: str = "Processing..."):
        """Create a progress context manager."""
        if self.use_rich:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
                expand=True,
            )
        else:
            # Simple fallback
            class SimpleProgress:
                def __enter__(self):
                    print(f"{description}...")
                    return self

                def __exit__(self, *args):
                    pass

                def add_task(self, description, total=None):
                    return 0

                def update(self, task_id, completed=None, advance=None):
                    pass

            return SimpleProgress()


class GFLConfig:
    """Configuration management for GFL CLI."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / ".gfl_config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "output_format": "rich" if HAS_RICH else "plain",
            "use_grammar_parser": False,
            "auto_validate": True,
            "show_performance": False,
            "log_level": "WARNING",
            "editor": "code",  # Default editor for --edit
            "plugin_paths": [],
            "color": True,
        }

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value


class EnhancedCLI(CLIUtilsMixin):
    """Enhanced CLI controller with comprehensive functionality."""

    def __init__(self):
        self.config = GFLConfig()
        use_rich = self.config.get("color", True) and HAS_RICH
        self.formatter = OutputFormatter(use_rich=use_rich)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            prog="gfl",
            description="GeneForgeLang CLI - A comprehensive tool for genomic workflow specification",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  gfl parse experiment.gfl --format json
  gfl validate *.gfl --recursive
  gfl infer workflow.gfl --model advanced
  gfl plugins list
  gfl config set editor vim
  gfl batch process --input-dir ./workflows

For more information, visit: https://github.com/geneforgelang/geneforgelang
            """,
        )

        # Global options
        parser.add_argument(
            "--version",
            action="version",
            version=f"GeneForgeLang {__version__} (API {__api_version__})",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increase verbosity (use multiple times)",
        )
        parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-essential output")
        parser.add_argument("--config", type=Path, help="Configuration file path")
        parser.add_argument("--no-color", action="store_true", help="Disable colored output")

        # Create subparsers
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        self._add_parse_command(subparsers)
        self._add_validate_command(subparsers)
        self._add_infer_command(subparsers)
        self._add_format_command(subparsers)
        self._add_plugins_command(subparsers)
        self._add_config_command(subparsers)
        self._add_batch_command(subparsers)
        self._add_info_command(subparsers)
        self._add_performance_command(subparsers)

        return parser

    def _add_parse_command(self, subparsers):
        """Add parse subcommand."""
        parser = subparsers.add_parser("parse", help="Parse GFL files")
        parser.add_argument("files", nargs="+", type=Path, help="GFL files to parse")
        parser.add_argument("--output", "-o", type=Path, help="Output file")
        parser.add_argument(
            "--format",
            choices=["json", "yaml", "ast", "tree"],
            default="json",
            help="Output format",
        )
        parser.add_argument("--grammar", action="store_true", help="Use grammar-based parser")
        parser.add_argument("--validate", action="store_true", help="Also validate after parsing")
        parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Process directories recursively",
        )
        parser.add_argument("--pattern", default="*.gfl", help="File pattern for recursive processing")
        parser.set_defaults(func=self.cmd_parse)

    def _add_validate_command(self, subparsers):
        """Add validate subcommand."""
        parser = subparsers.add_parser("validate", help="Validate GFL files")
        parser.add_argument("files", nargs="+", type=Path, help="GFL files to validate")
        parser.add_argument("--output", "-o", type=Path, help="Output file")
        parser.add_argument(
            "--format",
            choices=["text", "json", "junit", "sarif"],
            default="text",
            help="Output format",
        )
        parser.add_argument("--enhanced", action="store_true", help="Use enhanced validation")
        parser.add_argument("--schema", action="store_true", help="Include schema validation")
        parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Process directories recursively",
        )
        parser.add_argument("--fix", action="store_true", help="Apply suggested fixes automatically")
        parser.add_argument("--stop-on-first", action="store_true", help="Stop on first error")
        parser.set_defaults(func=self.cmd_validate)

    def _add_infer_command(self, subparsers):
        """Add infer subcommand."""
        parser = subparsers.add_parser("infer", help="Run inference on GFL files")
        parser.add_argument("files", nargs="+", type=Path, help="GFL files for inference")
        parser.add_argument("--model", default="dummy", help="Model to use")
        parser.add_argument("--output", "-o", type=Path, help="Output file")
        parser.add_argument("--format", choices=["json", "yaml"], default="json")
        parser.add_argument(
            "--confidence-threshold",
            type=float,
            default=0.5,
            help="Minimum confidence threshold",
        )
        parser.add_argument("--explain", action="store_true", help="Include explanations in output")
        parser.set_defaults(func=self.cmd_infer)

    def _add_format_command(self, subparsers):
        """Add format subcommand."""
        parser = subparsers.add_parser("format", help="Format GFL files")
        parser.add_argument("files", nargs="+", type=Path, help="GFL files to format")
        parser.add_argument("--in-place", "-i", action="store_true", help="Modify files in place")
        parser.add_argument("--check", action="store_true", help="Check if files are formatted")
        parser.add_argument("--diff", action="store_true", help="Show formatting differences")
        parser.add_argument("--indent", type=int, default=2, help="Indentation level")
        parser.set_defaults(func=self.cmd_format)

    def _add_plugins_command(self, subparsers):
        """Add plugins subcommand."""
        parser = subparsers.add_parser("plugins", help="Manage plugins")
        plugin_subparsers = parser.add_subparsers(dest="plugin_action")

        # List plugins
        list_parser = plugin_subparsers.add_parser("list", help="List available plugins")
        list_parser.add_argument("--active-only", action="store_true", help="Show only active plugins")

        # Plugin info
        info_parser = plugin_subparsers.add_parser("info", help="Show plugin information")
        info_parser.add_argument("plugin", help="Plugin name")

        # Activate/deactivate plugins
        activate_parser = plugin_subparsers.add_parser("activate", help="Activate plugin")
        activate_parser.add_argument("plugin", help="Plugin name")

        deactivate_parser = plugin_subparsers.add_parser("deactivate", help="Deactivate plugin")
        deactivate_parser.add_argument("plugin", help="Plugin name")

        # Validate dependencies
        plugin_subparsers.add_parser("validate", help="Validate plugin dependencies")

        parser.set_defaults(func=self.cmd_plugins)

    def _add_config_command(self, subparsers):
        """Add config subcommand."""
        parser = subparsers.add_parser("config", help="Manage configuration")
        config_subparsers = parser.add_subparsers(dest="config_action")

        # Show config
        show_parser = config_subparsers.add_parser("show", help="Show configuration")
        show_parser.add_argument("key", nargs="?", help="Specific key to show")

        # Set config
        set_parser = config_subparsers.add_parser("set", help="Set configuration")
        set_parser.add_argument("key", help="Configuration key")
        set_parser.add_argument("value", help="Configuration value")

        # Reset config
        reset_parser = config_subparsers.add_parser("reset", help="Reset configuration")
        reset_parser.add_argument("--confirm", action="store_true", help="Confirm reset")

        parser.set_defaults(func=self.cmd_config)

    def _add_batch_command(self, subparsers):
        """Add batch processing subcommand."""
        parser = subparsers.add_parser("batch", help="Batch processing")
        parser.add_argument(
            "action",
            choices=["parse", "validate", "infer", "format"],
            help="Action to perform",
        )
        parser.add_argument("--input-dir", "-i", type=Path, required=True, help="Input directory")
        parser.add_argument("--output-dir", "-o", type=Path, help="Output directory")
        parser.add_argument("--pattern", default="*.gfl", help="File pattern")
        parser.add_argument("--recursive", "-r", action="store_true", help="Process recursively")
        parser.add_argument("--parallel", "-p", action="store_true", help="Process files in parallel")
        parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
        parser.set_defaults(func=self.cmd_batch)

    def _add_info_command(self, subparsers):
        """Add info subcommand."""
        parser = subparsers.add_parser("info", help="Show system information")
        parser.add_argument("--format", choices=["text", "json"], default="text")
        parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
        parser.set_defaults(func=self.cmd_info)

    def _add_performance_command(self, subparsers):
        """Add performance monitoring subcommand."""
        parser = subparsers.add_parser("perf", help="Performance monitoring")
        perf_subparsers = parser.add_subparsers(dest="perf_action")

        # Show stats
        perf_subparsers.add_parser("stats", help="Show performance statistics")

        # Clear cache
        perf_subparsers.add_parser("clear", help="Clear performance caches")

        # Benchmark
        benchmark_parser = perf_subparsers.add_parser("benchmark", help="Run performance benchmark")
        benchmark_parser.add_argument("--files", nargs="+", type=Path, help="Files to benchmark")
        benchmark_parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")

        parser.set_defaults(func=self.cmd_performance)

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        try:
            parser = self.create_parser()
            parsed_args = parser.parse_args(args)

            # Configure logging level
            if parsed_args.verbose >= 2:
                logging.getLogger().setLevel(logging.DEBUG)
            elif parsed_args.verbose == 1:
                logging.getLogger().setLevel(logging.INFO)
            elif parsed_args.quiet:
                logging.getLogger().setLevel(logging.ERROR)

            # Handle color configuration
            if parsed_args.no_color:
                self.formatter = OutputFormatter(use_rich=False)

            # Load custom config if specified
            if hasattr(parsed_args, "config") and parsed_args.config:
                self.config = GFLConfig(parsed_args.config)

            # Execute command
            if hasattr(parsed_args, "func"):
                return parsed_args.func(parsed_args)
            else:
                parser.print_help()
                return 0

        except KeyboardInterrupt:
            self.formatter.print_error("Operation cancelled by user")
            return 130
        except CLIError as e:
            self.formatter.print_error(str(e))
            return 1

    # Command implementations

    def cmd_parse(self, args) -> int:
        """Handle parse command."""
        try:
            files = self._collect_files(args.files, args.recursive, args.pattern)

            if not files:
                self.formatter.print_error("No files found to parse")
                return 1

            results = []

            with self.formatter.progress("Parsing files") as progress:
                task = progress.add_task("Parsing", total=len(files))

                for file_path in files:
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        if args.grammar:
                            result = parse_enhanced(content, use_grammar=True, filename=str(file_path))
                            if result.is_valid:
                                ast = result.ast
                            else:
                                self.formatter.print_error(f"Parse failed for {file_path}")
                                for error in result.syntax_errors:
                                    self.formatter.print_error(f"  {error.message}")
                                continue
                        else:
                            ast = parse(content)

                        if args.validate:
                            validation_result = validate(ast, enhanced=True)
                            if not validation_result.is_valid:
                                self.formatter.print_warning(f"Validation issues in {file_path}")

                        results.append(
                            {
                                "file": str(file_path),
                                "ast": ast,
                                "size": len(content),
                                "valid": True,
                            }
                        )

                    except Exception as e:
                        self.formatter.print_error(f"Failed to parse {file_path}: {e}")
                        results.append({"file": str(file_path), "error": str(e), "valid": False})

                    progress.update(task, advance=1)

            # Output results
            if args.output:
                self._write_output(results, args.output, args.format)
            else:
                self._display_results(results, args.format)

            # Return error code if any files failed
            failed_count = sum(1 for r in results if not r.get("valid", False))
            if failed_count > 0:
                self.formatter.print_error(f"{failed_count} files failed to parse")
                return 1

            self.formatter.print_success(f"Successfully parsed {len(results)} files")
            return 0

        except Exception as e:
            self.formatter.print_error(f"Parse command failed: {e}")
            return 1

    def cmd_validate(self, args) -> int:
        """Handle validate command."""
        try:
            files = self._collect_files(args.files, args.recursive, args.pattern)

            if not files:
                self.formatter.print_error("No files found to validate")
                return 1

            results = []
            total_errors = 0

            with self.formatter.progress("Validating files") as progress:
                task = progress.add_task("Validating", total=len(files))

                for file_path in files:
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        # Parse first
                        if self.config.get("use_grammar_parser", False):
                            parse_result = parse_enhanced(content, use_grammar=True, filename=str(file_path))
                            if not parse_result.is_valid:
                                # Include syntax errors
                                results.append(
                                    {
                                        "file": str(file_path),
                                        "errors": [
                                            {
                                                "message": e.message,
                                                "type": "syntax",
                                                "severity": e.severity.value,
                                            }
                                            for e in parse_result.syntax_errors
                                        ],
                                        "valid": False,
                                    }
                                )
                                total_errors += len(parse_result.syntax_errors)
                                if args.stop_on_first:
                                    break
                                continue
                            ast = parse_result.ast
                        else:
                            ast = parse(content)

                        # Validate
                        if args.enhanced:
                            validation_result = validate(ast, enhanced=True)
                            errors = validation_result.semantic_errors + validation_result.schema_errors

                            results.append(
                                {
                                    "file": str(file_path),
                                    "errors": [
                                        {
                                            "message": e.message,
                                            "type": e.category.value,
                                            "severity": e.severity.value,
                                            "location": f"{e.location.line}:{e.location.column}"
                                            if e.location
                                            else None,
                                            "code": e.code,
                                            "fixes": [f.description for f in e.suggested_fixes],
                                        }
                                        for e in errors
                                    ],
                                    "valid": len(errors) == 0,
                                }
                            )
                            total_errors += len(errors)
                        else:
                            errors = validate(ast)
                            results.append(
                                {
                                    "file": str(file_path),
                                    "errors": [{"message": e, "type": "semantic"} for e in errors],
                                    "valid": len(errors) == 0,
                                }
                            )
                            total_errors += len(errors)

                        if args.stop_on_first and not results[-1]["valid"]:
                            break

                    except Exception as e:
                        self.formatter.print_error(f"Failed to validate {file_path}: {e}")
                        results.append(
                            {
                                "file": str(file_path),
                                "errors": [{"message": str(e), "type": "system"}],
                                "valid": False,
                            }
                        )
                        total_errors += 1

                    progress.update(task, advance=1)

            # Output results
            if args.output:
                self._write_validation_output(results, args.output, args.format)
            else:
                self._display_validation_results(results, args.format)

            if total_errors > 0:
                self.formatter.print_error(f"Found {total_errors} validation errors")
                return 1

            self.formatter.print_success("All files passed validation")
            return 0

        except Exception as e:
            self.formatter.print_error(f"Validation command failed: {e}")
            return 1

    def cmd_infer(self, args) -> int:
        """Handle inference command."""
        try:
            # Import models
            try:
                from gfl.models.dummy import DummyModel
            except ImportError:
                self.formatter.print_error("No inference models available")
                return 1

            files = self._collect_files(args.files, recursive=False, pattern="*.gfl")

            if not files:
                self.formatter.print_error("No files found for inference")
                return 1

            # Initialize model
            if args.model == "dummy":
                model = DummyModel()
            else:
                self.formatter.print_error(f"Unknown model: {args.model}")
                return 1

            results = []

            with self.formatter.progress("Running inference") as progress:
                task = progress.add_task("Processing", total=len(files))

                for file_path in files:
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        ast = parse(content)
                        inference_result = infer(model, ast)

                        # Filter by confidence if specified
                        if "confidence" in inference_result:
                            if inference_result["confidence"] < args.confidence_threshold:
                                self.formatter.print_warning(f"Low confidence result for {file_path}")

                        results.append(
                            {
                                "file": str(file_path),
                                "result": inference_result,
                                "model": args.model,
                            }
                        )

                    except Exception as e:
                        self.formatter.print_error(f"Inference failed for {file_path}: {e}")
                        results.append({"file": str(file_path), "error": str(e)})

                    progress.update(task, advance=1)

            # Output results
            if args.output:
                self._write_output(results, args.output, args.format)
            else:
                self._display_results(results, args.format)

            return 0

        except Exception as e:
            self.formatter.print_error(f"Inference command failed: {e}")
            return 1

    def cmd_format(self, args) -> int:
        """Handle format command."""
        self.formatter.print_error("Format command not yet implemented")
        return 1

    def cmd_plugins(self, args) -> int:
        """Handle plugins command."""
        if not HAS_PLUGINS:
            self.formatter.print_error("Plugin system not available")
            return 1

        try:
            if args.plugin_action == "list":
                plugins = list_plugins()

                if args.active_only:
                    plugins = [p for p in plugins if p.state.value == "active"]

                if not plugins:
                    self.formatter.print("No plugins found")
                    return 0

                plugin_data = []
                for plugin in plugins:
                    plugin_data.append(
                        {
                            "name": plugin.name,
                            "version": plugin.version,
                            "state": plugin.state.value,
                            "priority": plugin.priority.value,
                            "dependencies": len(plugin.dependencies),
                        }
                    )

                self.formatter.print_table(
                    plugin_data,
                    ["name", "version", "state", "priority", "dependencies"],
                    title="Available Plugins",
                )

            elif args.plugin_action == "info":
                try:
                    plugin_info = plugin_registry.get_info(args.plugin)

                    info_data = {
                        "name": plugin_info.name,
                        "version": plugin_info.version,
                        "state": plugin_info.state.value,
                        "priority": plugin_info.priority.value,
                        "dependencies": [
                            {
                                "name": dep.name,
                                "version_spec": dep.version_spec,
                                "optional": dep.optional,
                                "satisfied": dep.is_satisfied(),
                            }
                            for dep in plugin_info.dependencies
                        ],
                        "metadata": plugin_info.metadata,
                    }

                    self.formatter.print_json(info_data, f"Plugin Info: {args.plugin}")

                except ValueError:
                    self.formatter.print_error(f"Plugin '{args.plugin}' not found")
                    return 1

            elif args.plugin_action == "activate":
                try:
                    activate_plugin(args.plugin)
                    self.formatter.print_success(f"Activated plugin: {args.plugin}")
                except Exception as e:
                    self.formatter.print_error(f"Failed to activate plugin: {e}")
                    return 1

            elif args.plugin_action == "deactivate":
                try:
                    deactivate_plugin(args.plugin)
                    self.formatter.print_success(f"Deactivated plugin: {args.plugin}")
                except Exception as e:
                    self.formatter.print_error(f"Failed to deactivate plugin: {e}")
                    return 1

            elif args.plugin_action == "validate":
                issues = validate_plugin_dependencies()
                if issues:
                    self.formatter.print_error("Plugin dependency issues found:")
                    for plugin_name, missing_deps in issues.items():
                        self.formatter.print_error(f"  {plugin_name}: {', '.join(missing_deps)}")
                    return 1
                else:
                    self.formatter.print_success("All plugin dependencies satisfied")

            return 0

        except Exception as e:
            self.formatter.print_error(f"Plugin command failed: {e}")
            return 1

    def cmd_config(self, args) -> int:
        """Handle config command."""
        try:
            if args.config_action == "show":
                if args.key:
                    value = self.config.get(args.key)
                    if value is not None:
                        self.formatter.print_json({args.key: value})
                    else:
                        self.formatter.print_error(f"Configuration key '{args.key}' not found")
                        return 1
                else:
                    self.formatter.print_json(self.config.config, "GFL Configuration")

            elif args.config_action == "set":
                # Type conversion
                value = args.value
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)

                self.config.set(args.key, value)
                self.config.save_config()
                self.formatter.print_success(f"Set {args.key} = {value}")

            elif args.config_action == "reset":
                if args.confirm:
                    self.config.config = self.config.get_default_config()
                    self.config.save_config()
                    self.formatter.print_success("Configuration reset to defaults")
                else:
                    self.formatter.print_error("Use --confirm to reset configuration")
                    return 1

            return 0

        except Exception as e:
            self.formatter.print_error(f"Config command failed: {e}")
            return 1

    def cmd_batch(self, args) -> int:
        """Handle batch processing command."""
        try:
            input_dir = Path(args.input_dir)
            if not input_dir.exists():
                self.formatter.print_error(f"Input directory does not exist: {input_dir}")
                return 1

            # Collect files
            files = list(input_dir.rglob(args.pattern) if args.recursive else input_dir.glob(args.pattern))

            if not files:
                self.formatter.print_error(f"No files found matching pattern: {args.pattern}")
                return 1

            self.formatter.print(f"Processing {len(files)} files with action: {args.action}")

            if args.parallel:
                return self._batch_parallel(files, args)
            else:
                return self._batch_sequential(files, args)

        except Exception as e:
            self.formatter.print_error(f"Batch command failed: {e}")
            return 1

    def cmd_info(self, args) -> int:
        """Handle info command."""
        try:
            info_data = {
                "version": __version__,
                "api_version": __api_version__,
                "python_version": sys.version,
                "platform": sys.platform,
                "features": {
                    "rich_output": HAS_RICH,
                    "plugins": HAS_PLUGINS,
                    "enhanced_schema": HAS_ENHANCED_SCHEMA,
                },
                "config_file": str(self.config.config_file),
            }

            if args.check_deps:
                info_data["dependencies"] = self._check_dependencies()

            if args.format == "json":
                self.formatter.print_json(info_data)
            else:
                self.formatter.print("GeneForgeLang System Information")
                self.formatter.print("==============================")
                self.formatter.print(f"Version: {info_data['version']}")
                self.formatter.print(f"API Version: {info_data['api_version']}")
                self.formatter.print(f"Python: {info_data['python_version']}")
                self.formatter.print(f"Platform: {info_data['platform']}")
                self.formatter.print("")
                self.formatter.print("Features:")
                for feature, available in info_data["features"].items():
                    status = "✓" if available else "✗"
                    self.formatter.print(f"  {status} {feature}")

                if args.check_deps:
                    self.formatter.print("")
                    self.formatter.print("Dependencies:")
                    for dep, status in info_data["dependencies"].items():
                        status_str = "✓" if status else "✗"
                        self.formatter.print(f"  {status_str} {dep}")

            return 0

        except Exception as e:
            self.formatter.print_error(f"Info command failed: {e}")
            return 1

    def cmd_performance(self, args) -> int:
        """Handle performance monitoring command."""
        try:
            if args.perf_action == "stats":
                # Get performance statistics
                optimizer = get_optimizer()
                monitor = get_monitor()

                cache_stats = optimizer.get_cache_stats()
                perf_stats = monitor.get_all_stats()

                stats_data = {
                    "cache_statistics": {
                        name: {
                            "hits": stats.hits,
                            "misses": stats.misses,
                            "hit_rate": stats.hit_rate,
                            "size": stats.size,
                        }
                        if stats
                        else None
                        for name, stats in cache_stats.items()
                    },
                    "performance_statistics": perf_stats,
                }

                self.formatter.print_json(stats_data, "Performance Statistics")

            elif args.perf_action == "clear":
                optimizer = get_optimizer()
                optimizer.clear_all_caches()
                self.formatter.print_success("Performance caches cleared")

            elif args.perf_action == "benchmark":
                if not args.files:
                    self.formatter.print_error("No files specified for benchmark")
                    return 1

                return self._run_benchmark(args.files, args.iterations)

            return 0

        except Exception as e:
            self.formatter.print_error(f"Performance command failed: {e}")
            return 1


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the enhanced CLI."""
    cli = EnhancedCLI()
    return cli.run(args)


if __name__ == "__main__":
    import sys

    sys.exit(main())
