#!/usr/bin/env python3
"""
Test the optimize block example file.
"""

from gfl.api import parse, validate


def test_example_optimize_file():
    """Test parsing and validating the CRISPR optimization example."""

    print("Testing CRISPR optimization example...")

    # Read the GFL file
    with open("example_crispr_optimization.gfl", "r") as f:
        gfl_content = f.read()

    print(f"GFL content ({len(gfl_content)} characters):")
    print("-" * 40)
    print(gfl_content)
    print("-" * 40)

    # Parse the file
    print("\n1. Parsing GFL file...")
    ast = parse(gfl_content)

    if ast is None:
        print("❌ Failed to parse GFL file")
        return False

    print("✓ Successfully parsed GFL file")

    # Check structure
    print("\n2. Checking AST structure...")
    required_blocks = ["metadata", "optimize"]

    for block in required_blocks:
        if block in ast:
            print(f"✓ Found {block} block")
        else:
            print(f"❌ Missing {block} block")
            return False

    # Check optimize block details
    print("\n3. Validating optimize block structure...")
    optimize = ast["optimize"]

    required_optimize_fields = ["search_space", "strategy", "objective", "budget", "run"]
    for field in required_optimize_fields:
        if field in optimize:
            print(f"✓ Found optimize.{field}")
        else:
            print(f"❌ Missing optimize.{field}")
            return False

    # Check search space
    search_space = optimize["search_space"]
    print(f"✓ Search space has {len(search_space)} parameters:")
    for param, definition in search_space.items():
        print(f"   - {param}: {definition}")

    # Check parameter injection
    experiment = optimize["run"]["experiment"]
    injected_params = [p for p in experiment["params"].values()
                      if isinstance(p, str) and p.startswith("${")]
    print(f"✓ Found {len(injected_params)} parameter injections:")
    for param in injected_params:
        print(f"   - {param}")

    # Validate the AST
    print("\n4. Running semantic validation...")
    errors = validate(ast)

    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ No validation errors")

    print("\n🎉 CRISPR optimization example works perfectly!")
    return True


if __name__ == "__main__":
    success = test_example_optimize_file()
    exit(0 if success else 1)
