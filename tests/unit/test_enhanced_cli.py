"""Tests for the enhanced CLI system."""

import tempfile
from pathlib import Path

import pytest

from gfl.enhanced_cli import EnhancedCLI, OutputFormatter
from gfl.cli_utils import collect_files, process_file_batch


class TestOutputFormatter:
    """Test the output formatter."""

    def test_basic_output(self):
        """Test basic output functionality."""
        formatter = OutputFormatter(use_rich=False)

        # Should not raise exceptions
        formatter.print("Hello, World!")
        formatter.print_success("Success message")
        formatter.print_error("Error message")
        formatter.print_warning("Warning message")

    def test_json_output(self):
        """Test JSON output formatting."""
        formatter = OutputFormatter(use_rich=False)

        data = {"key": "value", "number": 42}
        formatter.print_json(data, "Test Data")

    def test_table_output(self):
        """Test table output formatting."""
        formatter = OutputFormatter(use_rich=False)

        data = [{"name": "test1", "value": 100}, {"name": "test2", "value": 200}]
        headers = ["name", "value"]

        formatter.print_table(data, headers, "Test Table")


class TestCLIUtilities:
    """Test CLI utility functions."""

    def test_collect_files(self):
        """Test file collection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test1.gfl").touch()
            (temp_path / "test2.gfl").touch()
            (temp_path / "other.txt").touch()

            # Test glob patterns
            files = collect_files([temp_path], recursive=False, pattern="*.gfl")
            assert len(files) == 2

            # Test specific file
            files = collect_files([temp_path / "test1.gfl"])
            assert len(files) == 1

    def test_process_file_batch(self):
        """Test batch file processing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gfl", delete=False) as f:
            f.write("""
experiment:
  tool: CRISPR_cas9
  type: gene_editing
            """)
            temp_path = Path(f.name)

        try:
            # Test parse action
            result = process_file_batch(temp_path, "parse")
            assert result["success"]
            assert "result" in result

            # Test validate action
            result = process_file_batch(temp_path, "validate")
            assert result["success"]

        finally:
            temp_path.unlink()


class TestEnhancedCLI:
    """Test the enhanced CLI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cli = EnhancedCLI()

    def test_cli_initialization(self):
        """Test CLI initialization."""
        assert self.cli.config is not None
        assert self.cli.formatter is not None

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        assert parser is not None

        # Test that all subcommands are present
        help_text = parser.format_help()
        expected_commands = [
            "parse",
            "validate",
            "infer",
            "format",
            "plugins",
            "config",
            "batch",
            "info",
            "perf",
        ]

        for command in expected_commands:
            assert command in help_text

    def test_info_command(self):
        """Test info command."""

        # Mock arguments
        class MockArgs:
            format = "text"
            check_deps = False

        args = MockArgs()
        result = self.cli.cmd_info(args)
        assert result == 0

    def test_config_command(self):
        """Test config command."""

        # Test show config
        class MockShowArgs:
            config_action = "show"
            key = None

        args = MockShowArgs()
        result = self.cli.cmd_config(args)
        assert result == 0

        # Test set config
        class MockSetArgs:
            config_action = "set"
            key = "test_key"
            value = "test_value"

        args = MockSetArgs()
        result = self.cli.cmd_config(args)
        assert result == 0
        assert self.cli.config.get("test_key") == "test_value"

    def test_parse_command_with_temp_file(self):
        """Test parse command with a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gfl", delete=False) as f:
            f.write("""
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
            """)
            temp_path = Path(f.name)

        try:

            class MockParseArgs:
                files = [temp_path]
                output = None
                format = "json"
                grammar = False
                validate = False
                recursive = False
                pattern = "*.gfl"

            args = MockParseArgs()
            result = self.cli.cmd_parse(args)
            assert result == 0

        finally:
            temp_path.unlink()

    def test_validate_command_with_temp_file(self):
        """Test validate command with a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gfl", delete=False) as f:
            f.write("""
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
            """)
            temp_path = Path(f.name)

        try:

            class MockValidateArgs:
                files = [temp_path]
                output = None
                format = "text"
                enhanced = True
                schema = False
                recursive = False
                fix = False
                stop_on_first = False

            args = MockValidateArgs()
            result = self.cli.cmd_validate(args)
            assert result == 0

        finally:
            temp_path.unlink()

    def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gfl", delete=False) as f:
            f.write("invalid gfl syntax here: {{{")
            temp_path = Path(f.name)

        try:

            class MockParseArgs:
                files = [temp_path]
                output = None
                format = "json"
                grammar = False
                validate = False
                recursive = False
                pattern = "*.gfl"

            args = MockParseArgs()
            result = self.cli.cmd_parse(args)
            # Should handle error gracefully and return error code
            assert result == 1

        finally:
            temp_path.unlink()

    def test_batch_command_setup(self):
        """Test batch command initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test1.gfl").write_text("""
experiment:
  tool: CRISPR_cas9
            """)
            (temp_path / "test2.gfl").write_text("""
analyze:
  strategy: differential
            """)

            class MockBatchArgs:
                action = "parse"
                input_dir = temp_path
                output_dir = None
                pattern = "*.gfl"
                recursive = False
                parallel = False
                workers = 2

            args = MockBatchArgs()
            result = self.cli.cmd_batch(args)
            assert result == 0

    def test_plugins_command_without_plugins(self):
        """Test plugins command when plugins aren't available."""

        class MockPluginsArgs:
            plugin_action = "list"
            active_only = False

        args = MockPluginsArgs()
        # Should handle gracefully even if plugins aren't available
        result = self.cli.cmd_plugins(args)
        # May return 0 or 1 depending on plugin availability
        assert result in [0, 1]

    def test_performance_command(self):
        """Test performance monitoring command."""

        class MockPerfArgs:
            perf_action = "stats"

        args = MockPerfArgs()
        result = self.cli.cmd_performance(args)
        assert result == 0


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_main_entry_point(self):
        """Test the main CLI entry point."""
        from gfl.cli_main import main

        # Test help command
        result = main(["--help"])
        # Help should return 0 (success)
        assert result == 0

    def test_version_command(self):
        """Test version display."""
        from gfl.enhanced_cli import main

        # Test version command
        result = main(["--version"])
        assert result == 0

    def test_no_command(self):
        """Test behavior with no command."""
        from gfl.enhanced_cli import main

        result = main([])
        assert result == 0  # Should show help

    def test_invalid_command(self):
        """Test behavior with invalid command."""
        from gfl.enhanced_cli import main

        result = main(["invalid_command"])
        assert result != 0  # Should return error code


@pytest.mark.integration
class TestCLIWorkflows:
    """Test complete CLI workflows."""

    def test_parse_validate_workflow(self):
        """Test a complete parse and validate workflow."""
        cli = EnhancedCLI()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".gfl", delete=False) as f:
            f.write("""
metadata:
  experiment_id: EXP001

experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53

analyze:
  strategy: differential
  data: experiment_output
            """)
            temp_path = Path(f.name)

        try:
            # Test parsing
            class MockParseArgs:
                files = [temp_path]
                output = None
                format = "json"
                grammar = False
                validate = True  # Also validate
                recursive = False
                pattern = "*.gfl"

            result = cli.cmd_parse(MockParseArgs())
            assert result == 0

        finally:
            temp_path.unlink()

    def test_batch_processing_workflow(self):
        """Test batch processing workflow."""
        cli = EnhancedCLI()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple test files
            for i in range(3):
                (temp_path / f"test{i}.gfl").write_text(f"""
experiment:
  tool: CRISPR_cas9
  params:
    target_gene: TP5{i}
                """)

            class MockBatchArgs:
                action = "validate"
                input_dir = temp_path
                output_dir = None
                pattern = "*.gfl"
                recursive = False
                parallel = False
                workers = 2

            result = cli.cmd_batch(MockBatchArgs())
            assert result == 0
