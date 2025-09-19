#!/usr/bin/env python3
"""Main entry point for the GeneForgeLang CLI.

This module provides the main entry point for the GFL command-line interface,
supporting both the legacy CLI and the new enhanced CLI.
"""

import sys
from typing import List, Optional


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for the GFL CLI."""
    try:
        # Try to use the enhanced CLI first
        from .enhanced_cli import EnhancedCLI

        cli = EnhancedCLI()
        return cli.run(args)

    except ImportError as e:
        # Fallback to basic CLI if enhanced features aren't available
        print(f"Enhanced CLI not available: {e}", file=sys.stderr)
        print("Falling back to basic CLI...", file=sys.stderr)

        # Import legacy CLI functions
        try:
            from . import cli

            # Parse arguments manually for legacy CLI
            if not args:
                args = sys.argv[1:]

            if not args:
                print("Usage: gfl <command> [options]")
                print("Available commands: parse, validate, infer, schema, info")
                return 0

            command = args[0]

            # Temporarily modify sys.argv for legacy CLI
            original_argv = sys.argv[:]
            try:
                sys.argv = ["gfl"] + args

                if command == "parse":
                    cli.cmd_parse()
                elif command == "validate":
                    cli.cmd_validate()
                elif command == "infer":
                    cli.cmd_infer()
                elif command == "schema":
                    cli.cmd_schema()
                elif command == "info":
                    cli.cmd_info()
                else:
                    print(f"Unknown command: {command}", file=sys.stderr)
                    return 1

                return 0

            finally:
                sys.argv = original_argv

        except Exception as e:
            print(f"CLI execution failed: {e}", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
