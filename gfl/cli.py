"""Command-line interface for GeneForgeLang.

Provides console commands for parsing, validation, inference, and utilities.
"""

import argparse
import json
import sys

from gfl.api import get_api_info, infer, parse, validate

try:
    from gfl.schema_validator import comprehensive_validate, load_schema

    HAS_SCHEMA = True
except ImportError:
    HAS_SCHEMA = False
    comprehensive_validate = None
    load_schema = None

try:
    from gfl.models.dummy import DummyModel

    HAS_DUMMY_MODEL = True
except ImportError:
    HAS_DUMMY_MODEL = False
    DummyModel = None


def cmd_parse():
    """Parse GFL file and output AST."""
    parser = argparse.ArgumentParser(description="Parse GFL file to AST")
    parser.add_argument("file", help="Path to GFL file")
    parser.add_argument("--typed", action="store_true", help="Use typed AST")
    parser.add_argument("--format", choices=["json", "yaml", "repr"], default="repr")
    parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

        ast = parse(text, typed=args.typed)

        if args.format == "json":
            if args.typed:
                output = json.dumps(ast.to_dict(), indent=2)
            else:
                output = json.dumps(ast, indent=2)
        elif args.format == "yaml":
            import yaml

            if args.typed:
                output = yaml.dump(ast.to_dict(), default_flow_style=False)
            else:
                output = yaml.dump(ast, default_flow_style=False)
        else:  # repr
            output = repr(ast)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"AST written to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_validate():
    """Validate GFL file semantics and schema."""
    parser = argparse.ArgumentParser(description="Validate GFL file")
    parser.add_argument("file", help="Path to GFL file")
    parser.add_argument("--detailed", action="store_true", help="Detailed validation")
    parser.add_argument("--schema", action="store_true", help="Schema validation")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

        ast = parse(text)

        if args.schema and HAS_SCHEMA:
            result = comprehensive_validate(ast)
        else:
            result = validate(ast, detailed=args.detailed)

        exit_code = 0
        if args.detailed or args.schema:
            if result.errors:
                exit_code = 1
        else:
            if result:
                exit_code = 1

        if args.format == "json":
            if args.detailed or args.schema:
                output_data = {
                    "valid": result.is_valid,
                    "errors": [str(e) for e in result.errors],
                    "warnings": [str(w) for w in result.warnings],
                }
            else:
                output_data = {"valid": len(result) == 0, "errors": result}
            output = json.dumps(output_data, indent=2)
        else:
            if args.detailed or args.schema:
                lines = []
                if result.errors:
                    lines.append("Errors:")
                    for error in result.errors:
                        lines.append(f"  - {error}")
                if not lines:
                    lines.append("✓ Validation passed")
                output = "\\n".join(lines)
            else:
                if result:
                    output = "\\n".join(f"- {e}" for e in result)
                else:
                    output = "✓ Validation passed"

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)

        sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_infer():
    """Run inference on GFL file."""
    parser = argparse.ArgumentParser(description="Run inference on GFL file")
    parser.add_argument("file", help="Path to GFL file")
    parser.add_argument("--model", choices=["dummy"], default="dummy")
    parser.add_argument("--detailed", action="store_true")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

        ast = parse(text)

        if args.model == "dummy" and HAS_DUMMY_MODEL:
            model = DummyModel()
        else:
            raise ValueError(f"Model {args.model} not available")

        result = infer(model, ast, detailed=args.detailed)

        if args.format == "json":
            if args.detailed:
                output = json.dumps(result.to_dict(), indent=2)
            else:
                output = json.dumps(result, indent=2)
        else:  # yaml
            import yaml

            if args.detailed:
                output = yaml.dump(result.to_dict(), default_flow_style=False)
            else:
                output = yaml.dump(result, default_flow_style=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_schema():
    """Work with GFL JSON schema."""
    parser = argparse.ArgumentParser(description="GFL schema operations")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show", action="store_true", help="Show schema")
    group.add_argument("--validate", metavar="FILE", help="Validate file")
    parser.add_argument("--output", "-o", help="Output file")

    args = parser.parse_args()

    try:
        if args.show:
            if not HAS_SCHEMA:
                print("Schema validation not available", file=sys.stderr)
                sys.exit(1)

            schema = load_schema()
            if schema is None:
                print("Schema not found", file=sys.stderr)
                sys.exit(1)

            output = json.dumps(schema, indent=2)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
            else:
                print(output)

        elif args.validate:
            if not HAS_SCHEMA:
                print("Schema validation not available", file=sys.stderr)
                sys.exit(1)

            with open(args.validate, encoding="utf-8") as f:
                text = f.read()

            ast = parse(text)
            result = comprehensive_validate(ast)

            if result.errors:
                print("Schema validation errors:")
                for error in result.errors:
                    print(f"  - {error}")
                sys.exit(1)
            else:
                print("✓ Schema validation passed")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_info():
    """Display GFL information."""
    parser = argparse.ArgumentParser(description="Display GFL information")
    parser.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args()

    try:
        api_info = get_api_info()

        if args.format == "json":
            print(json.dumps(api_info, indent=2))
        else:
            print("GeneForgeLang Information")
            print("========================")
            print(f"Version: {api_info['version']}")
            print(f"API Version: {api_info['api_version']}")
            print(f"Compatibility: {api_info['compatibility']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
