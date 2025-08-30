# GeneForgeLang Enhanced CLI Documentation

The GeneForgeLang Enhanced CLI provides a comprehensive command-line interface for working with GFL files and workflows.

## Installation and Setup

The enhanced CLI is automatically available when you install GeneForgeLang:

```bash
pip install geneforgelang[apps]  # For full feature set
```

Optional dependencies for enhanced features:
- `rich`: For colorized output and progress bars
- `ply`: For grammar-based parsing

## Main Commands

### Parse Command
Parse GFL files into AST format with various output options.

```bash
# Basic parsing
gfl parse experiment.gfl

# Parse with validation
gfl parse experiment.gfl --validate

# Use grammar parser
gfl parse experiment.gfl --grammar

# Parse multiple files recursively
gfl parse ./workflows/ --recursive --pattern "*.gfl"

# Output formats
gfl parse experiment.gfl --format json --output result.json
gfl parse experiment.gfl --format tree  # Visual tree output
```

### Validate Command
Comprehensive validation with rich error reporting.

```bash
# Basic validation
gfl validate experiment.gfl

# Enhanced validation with detailed errors
gfl validate experiment.gfl --enhanced

# Schema validation
gfl validate experiment.gfl --schema

# Multiple output formats
gfl validate *.gfl --format json --output validation_report.json
gfl validate *.gfl --format junit --output test-results.xml
gfl validate *.gfl --format sarif --output security-report.sarif

# Auto-fix issues (when possible)
gfl validate experiment.gfl --fix

# Stop on first error
gfl validate *.gfl --stop-on-first
```

### Inference Command
Run machine learning inference on GFL workflows.

```bash
# Basic inference
gfl infer experiment.gfl --model dummy

# With confidence filtering
gfl infer experiment.gfl --model advanced --confidence-threshold 0.8

# With explanations
gfl infer experiment.gfl --explain --format json
```

### Format Command
Code formatting and style consistency.

```bash
# Check formatting
gfl format experiment.gfl --check

# Format in place
gfl format *.gfl --in-place

# Show differences
gfl format experiment.gfl --diff

# Custom indentation
gfl format experiment.gfl --indent 4
```

### Plugin Management
Manage and interact with GFL plugins.

```bash
# List all plugins
gfl plugins list

# Show only active plugins
gfl plugins list --active-only

# Get plugin information
gfl plugins info alpha_genome

# Activate/deactivate plugins
gfl plugins activate variant_sim
gfl plugins deactivate alpha_genome

# Validate plugin dependencies
gfl plugins validate
```

### Configuration Management
Manage CLI configuration and preferences.

```bash
# Show current configuration
gfl config show

# Show specific setting
gfl config show editor

# Set configuration values
gfl config set editor vim
gfl config set use_grammar_parser true
gfl config set color false

# Reset to defaults
gfl config reset --confirm
```

### Batch Processing
Process multiple files efficiently with parallel support.

```bash
# Sequential batch processing
gfl batch parse --input-dir ./workflows --output-dir ./results

# Parallel processing
gfl batch validate --input-dir ./workflows --parallel --workers 8

# Recursive processing
gfl batch parse --input-dir ./project --recursive --pattern "**/*.gfl"

# Different actions
gfl batch validate --input-dir ./workflows --enhanced
gfl batch infer --input-dir ./workflows --model advanced
```

### System Information
Get information about the GFL installation and environment.

```bash
# Basic system info
gfl info

# Check dependencies
gfl info --check-deps

# JSON output
gfl info --format json
```

### Performance Monitoring
Monitor and optimize GFL performance.

```bash
# Show performance statistics
gfl perf stats

# Clear performance caches
gfl perf clear

# Run benchmarks
gfl perf benchmark --files *.gfl --iterations 10
```

## Global Options

Available for all commands:

```bash
# Increase verbosity
gfl --verbose parse experiment.gfl
gfl -vv validate experiment.gfl  # Very verbose

# Quiet mode
gfl --quiet batch parse --input-dir ./workflows

# Disable colored output
gfl --no-color parse experiment.gfl

# Custom configuration file
gfl --config ./custom-config.json parse experiment.gfl

# Version information
gfl --version
```

## Output Formats

### Supported Formats
- **json**: Machine-readable JSON output
- **yaml**: Human-readable YAML format
- **text**: Plain text with colors (default)
- **tree**: Visual tree representation (for ASTs)
- **junit**: JUnit XML format (for validation)
- **sarif**: SARIF format for security tools

### Rich Output Features
When the `rich` library is available:
- Colorized output with syntax highlighting
- Progress bars for long operations
- Formatted tables for structured data
- Interactive elements and better error display

## Configuration Options

The CLI supports persistent configuration via `~/.gfl_config.json`:

```json
{
  "output_format": "rich",
  "use_grammar_parser": false,
  "auto_validate": true,
  "show_performance": false,
  "log_level": "WARNING",
  "editor": "code",
  "plugin_paths": [],
  "color": true
}
```

## Examples

### Complete Workflow Example
```bash
# 1. Parse and validate a workflow
gfl parse workflow.gfl --validate --grammar --format json --output ast.json

# 2. Run comprehensive validation
gfl validate workflow.gfl --enhanced --schema --format sarif --output report.sarif

# 3. Process with inference
gfl infer workflow.gfl --model advanced --explain --output inference.json

# 4. Format the file
gfl format workflow.gfl --in-place

# 5. Check performance
gfl perf benchmark --files workflow.gfl --iterations 5
```

### Batch Processing Example
```bash
# Process an entire project
gfl batch validate \\
  --input-dir ./genomics-workflows \\
  --recursive \\
  --pattern "**/*.gfl" \\
  --parallel \\
  --workers 8 \\
  --output-dir ./validation-results

# Check results
ls ./validation-results/
```

### Plugin Development Workflow
```bash
# Check available plugins
gfl plugins list

# Validate dependencies
gfl plugins validate

# Activate needed plugins
gfl plugins activate alpha_genome
gfl plugins activate variant_sim

# Process with plugins active
gfl infer experiment.gfl --model dummy
```

## Error Handling and Debugging

### Verbose Output
```bash
# Debug level logging
gfl -vv parse problematic.gfl

# Show stack traces
gfl --verbose validate invalid.gfl
```

### Error Codes
The CLI returns standard exit codes:
- `0`: Success
- `1`: General error (validation failed, parsing error, etc.)
- `130`: Interrupted by user (Ctrl+C)

### Enhanced Error Messages
When using enhanced validation:
- Precise source locations (line:column)
- Error codes and categories
- Suggested fixes with explanations
- Context-aware error messages

## Integration with Development Tools

### IDE Integration
The CLI can be integrated with various IDEs and editors:

```bash
# Configure preferred editor
gfl config set editor "code"  # VS Code
gfl config set editor "vim"   # Vim
gfl config set editor "emacs" # Emacs
```

### CI/CD Integration
Use in continuous integration pipelines:

```bash
# Validation in CI
gfl validate ./src/**/*.gfl --format junit --output test-results.xml

# Security scanning
gfl validate ./src/**/*.gfl --format sarif --output security-report.sarif
```

### Git Hooks
Add to git pre-commit hooks:

```bash
#!/bin/bash
# .git/hooks/pre-commit
gfl validate $(git diff --cached --name-only --diff-filter=ACM | grep '\\.gfl$') --stop-on-first
```

This enhanced CLI provides a professional-grade interface for all GeneForgeLang operations, supporting both individual file processing and large-scale batch operations with comprehensive error handling and reporting capabilities.
