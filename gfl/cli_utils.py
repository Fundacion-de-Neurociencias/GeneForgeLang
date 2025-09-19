"""Utility functions for the enhanced CLI."""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def collect_files(file_paths: List[Path], recursive: bool = False, pattern: str = "*.gfl") -> List[Path]:
    """Collect files from paths, optionally recursively."""
    files = []

    for path in file_paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            if recursive:
                files.extend(path.rglob(pattern))
            else:
                files.extend(path.glob(pattern))
        else:
            # Pattern matching
            files.extend(Path.cwd().glob(str(path)))

    return sorted(set(files))


def write_output(data: Any, output_path: Path, format_type: str):
    """Write data to output file in specified format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format_type == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif format_type == "yaml" and HAS_YAML:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(data))


def check_dependencies() -> Dict[str, bool]:
    """Check availability of optional dependencies."""
    dependencies = {}

    # Check PLY
    try:
        import ply

        dependencies["ply"] = True
    except ImportError:
        dependencies["ply"] = False

    # Check Rich
    try:
        import rich

        dependencies["rich"] = True
    except ImportError:
        dependencies["rich"] = False

    # Check PyYAML
    try:
        import yaml

        dependencies["pyyaml"] = True
    except ImportError:
        dependencies["pyyaml"] = False

    # Check transformers
    try:
        import transformers

        dependencies["transformers"] = True
    except ImportError:
        dependencies["transformers"] = False

    # Check torch
    try:
        import torch

        dependencies["torch"] = True
    except ImportError:
        dependencies["torch"] = False

    return dependencies


def process_file_batch(file_path: Path, action: str, **kwargs) -> Dict[str, Any]:
    """Process a single file for batch operations."""
    try:
        from gfl.api import infer, parse, validate

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        start_time = time.time()

        if action == "parse":
            result = parse(content)
            return {
                "file": str(file_path),
                "result": result,
                "success": True,
                "duration": time.time() - start_time,
            }

        elif action == "validate":
            ast = parse(content)
            errors = validate(ast, enhanced=kwargs.get("enhanced", False))
            return {
                "file": str(file_path),
                "errors": errors,
                "success": len(errors) == 0 if isinstance(errors, list) else errors.is_valid,
                "duration": time.time() - start_time,
            }

        elif action == "infer":
            ast = parse(content)
            model = kwargs.get("model")
            if not model:
                raise ValueError("Model required for inference")

            result = infer(model, ast)
            return {
                "file": str(file_path),
                "result": result,
                "success": True,
                "duration": time.time() - start_time,
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "success": False,
            "duration": time.time() - start_time if "start_time" in locals() else 0,
        }


def create_junit_report(results: List[Dict[str, Any]], output_path: Path):
    """Create JUnit XML report for validation results."""
    try:
        from defusedxml import ElementTree as ET
    except ImportError:
        # Fallback to standard library with security warning
        import xml.etree.ElementTree as ET  # nosec B405

    root = ET.Element("testsuites")
    root.set("name", "GFL Validation")

    total_tests = len(results)
    failures = sum(1 for r in results if not r.get("valid", True))

    testsuite = ET.SubElement(root, "testsuite")
    testsuite.set("name", "GFL Files")
    testsuite.set("tests", str(total_tests))
    testsuite.set("failures", str(failures))
    testsuite.set("errors", "0")

    for result in results:
        testcase = ET.SubElement(testsuite, "testcase")
        testcase.set("name", result["file"])
        testcase.set("classname", "GFL")

        if not result.get("valid", True):
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", "Validation failed")

            error_messages = []
            for error in result.get("errors", []):
                if isinstance(error, dict):
                    error_messages.append(error.get("message", str(error)))
                else:
                    error_messages.append(str(error))

            failure.text = "\\n".join(error_messages)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def create_sarif_report(results: List[Dict[str, Any]], output_path: Path):
    """Create SARIF (Static Analysis Results Interchange Format) report."""
    sarif_report = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "GeneForgeLang Validator",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/geneforgelang/geneforgelang",
                    }
                },
                "results": [],
            }
        ],
    }

    for result in results:
        if not result.get("valid", True):
            for error in result.get("errors", []):
                if isinstance(error, dict):
                    sarif_result = {
                        "ruleId": error.get("code", "GFL_ERROR"),
                        "level": "error" if error.get("severity") == "ERROR" else "warning",
                        "message": {"text": error.get("message", "Unknown error")},
                        "locations": [{"physicalLocation": {"artifactLocation": {"uri": result["file"]}}}],
                    }

                    # Add location if available
                    if error.get("location"):
                        location_parts = error["location"].split(":")
                        if len(location_parts) == 2:
                            try:
                                line = int(location_parts[0])
                                column = int(location_parts[1])
                                sarif_result["locations"][0]["physicalLocation"]["region"] = {
                                    "startLine": line,
                                    "startColumn": column,
                                }
                            except ValueError:
                                pass

                    sarif_report["runs"][0]["results"].append(sarif_result)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sarif_report, f, indent=2, ensure_ascii=False)


# CLI utility functions to be mixed into the main CLI class
class CLIUtilsMixin:
    """Mixin class with utility methods for the CLI."""

    def _collect_files(self, file_paths: List[Path], recursive: bool = False, pattern: str = "*.gfl") -> List[Path]:
        """Collect files from paths."""
        return collect_files(file_paths, recursive, pattern)

    def _write_output(self, data: Any, output_path: Path, format_type: str):
        """Write data to output file."""
        write_output(data, output_path, format_type)

    def _check_dependencies(self) -> Dict[str, bool]:
        """Check dependencies."""
        return check_dependencies()

    def _display_results(self, results: List[Dict[str, Any]], format_type: str):
        """Display results in the specified format."""
        if format_type == "json":
            self.formatter.print_json(results)
        elif format_type == "yaml" and HAS_YAML:
            import yaml

            self.formatter.print(yaml.dump(results, default_flow_style=False))
        elif format_type == "tree" and len(results) == 1:
            self._display_ast_tree(results[0].get("ast"))
        else:
            for result in results:
                if result.get("valid", True):
                    self.formatter.print_success(f"✓ {result['file']}")
                else:
                    self.formatter.print_error(f"✗ {result['file']}")
                    if "error" in result:
                        self.formatter.print_error(f"  {result['error']}")

    def _display_validation_results(self, results: List[Dict[str, Any]], format_type: str):
        """Display validation results."""
        if format_type == "json":
            self.formatter.print_json(results)
        elif format_type == "text":
            for result in results:
                file_name = result["file"]
                if result["valid"]:
                    self.formatter.print_success(f"✓ {file_name}")
                else:
                    self.formatter.print_error(f"✗ {file_name}")
                    for error in result.get("errors", []):
                        if isinstance(error, dict):
                            location = error.get("location", "")
                            message = error.get("message", "Unknown error")
                            self.formatter.print_error(f"  {location}: {message}")
                        else:
                            self.formatter.print_error(f"  {error}")

    def _write_validation_output(self, results: List[Dict[str, Any]], output_path: Path, format_type: str):
        """Write validation results to file."""
        if format_type == "junit":
            create_junit_report(results, output_path)
        elif format_type == "sarif":
            create_sarif_report(results, output_path)
        else:
            self._write_output(results, output_path, format_type)

    def _display_ast_tree(self, ast: Dict[str, Any]):
        """Display AST as a tree structure."""
        if not HAS_RICH:
            self.formatter.print(str(ast))
            return

        from rich.tree import Tree

        def add_to_tree(node, data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        branch = node.add(f"[blue]{key}[/blue]")
                        add_to_tree(branch, value)
                    else:
                        node.add(f"[blue]{key}[/blue]: [green]{repr(value)}[/green]")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, (dict, list)):
                        branch = node.add(f"[yellow][{i}][/yellow]")
                        add_to_tree(branch, item)
                    else:
                        node.add(f"[yellow][{i}][/yellow]: [green]{repr(item)}[/green]")
            else:
                node.add(f"[green]{repr(data)}[/green]")

        tree = Tree("AST")
        add_to_tree(tree, ast)
        self.formatter.console.print(tree)

    def _batch_sequential(self, files: List[Path], args) -> int:
        """Process files sequentially."""
        results = []

        with self.formatter.progress(f"Batch {args.action}") as progress:
            task = progress.add_task("Processing", total=len(files))

            for file_path in files:
                result = process_file_batch(file_path, args.action)
                results.append(result)
                progress.update(task, advance=1)

        # Output results
        if args.output_dir:
            output_path = Path(args.output_dir) / f"batch_{args.action}_results.json"
            self._write_output(results, output_path, "json")
        else:
            self._display_results(results, "json")

        # Check for failures
        failures = sum(1 for r in results if not r["success"])
        if failures > 0:
            self.formatter.print_error(f"{failures} files failed processing")
            return 1

        self.formatter.print_success(f"Successfully processed {len(files)} files")
        return 0

    def _batch_parallel(self, files: List[Path], args) -> int:
        """Process files in parallel."""
        results = []

        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            with self.formatter.progress(f"Batch {args.action} (parallel)") as progress:
                task = progress.add_task("Processing", total=len(files))

                # Submit all tasks
                future_to_file = {
                    executor.submit(process_file_batch, file_path, args.action): file_path for file_path in files
                }

                # Collect results as they complete
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    progress.update(task, advance=1)

        # Sort results by filename for consistent output
        results.sort(key=lambda x: x["file"])

        # Output results
        if args.output_dir:
            output_path = Path(args.output_dir) / f"batch_{args.action}_results.json"
            self._write_output(results, output_path, "json")
        else:
            self._display_results(results, "json")

        # Check for failures
        failures = sum(1 for r in results if not r["success"])
        if failures > 0:
            self.formatter.print_error(f"{failures} files failed processing")
            return 1

        self.formatter.print_success(f"Successfully processed {len(files)} files")
        return 0

    def _run_benchmark(self, files: List[Path], iterations: int) -> int:
        """Run performance benchmark."""
        import statistics

        from gfl.api import parse, validate

        self.formatter.print(f"Running benchmark with {iterations} iterations per file...")

        benchmark_results = []

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                parse_times = []
                validate_times = []

                for _ in range(iterations):
                    # Benchmark parsing
                    start_time = time.time()
                    ast = parse(content)
                    parse_time = time.time() - start_time
                    parse_times.append(parse_time)

                    # Benchmark validation
                    start_time = time.time()
                    validate(ast)
                    validate_time = time.time() - start_time
                    validate_times.append(validate_time)

                file_result = {
                    "file": str(file_path),
                    "size": len(content),
                    "iterations": iterations,
                    "parse": {
                        "mean": statistics.mean(parse_times),
                        "median": statistics.median(parse_times),
                        "min": min(parse_times),
                        "max": max(parse_times),
                        "stdev": statistics.stdev(parse_times) if len(parse_times) > 1 else 0,
                    },
                    "validate": {
                        "mean": statistics.mean(validate_times),
                        "median": statistics.median(validate_times),
                        "min": min(validate_times),
                        "max": max(validate_times),
                        "stdev": statistics.stdev(validate_times) if len(validate_times) > 1 else 0,
                    },
                }

                benchmark_results.append(file_result)

            except Exception as e:
                self.formatter.print_error(f"Benchmark failed for {file_path}: {e}")

        # Display results
        self.formatter.print_json(benchmark_results, "Benchmark Results")

        return 0
