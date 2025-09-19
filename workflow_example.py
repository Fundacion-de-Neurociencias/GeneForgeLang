#!/usr/bin/env python3
"""
Working GFL workflow example.

This example demonstrates a complete workflow using properly implemented
plugins that are actually available in the system.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gfl.api import parse, validate, execute, list_available_plugins


def main():
    """Run a complete workflow example."""
    
    print("GFL Workflow Example")
    print("=" * 50)
    
    # Show available plugins
    print("1. Available plugins:")
    plugins = list_available_plugins()
    print(f"   Generators: {plugins['generators']}")
    print(f"   Optimizers: {plugins['optimizers']}")
    print()
    
    # Define a working GFL workflow
    gfl_code = """
design:
  entity: ProteinSequence
  model: ProteinVAEGenerator
  objective:
    maximize: stability
  count: 5
  length: 50
  output: designed_proteins

optimize:
  search_space:
    temperature: "range(25, 42)"
    concentration: "range(10, 100)"
  strategy:
    name: BayesianOptimization
  objective:
    maximize: efficiency
  budget:
    max_experiments: 5
  run:
    experiment:
      tool: simulation
      type: parameter_sweep
      params:
        temp: "${temperature}"
        conc: "${concentration}"
"""
    
    print("2. Parsing GFL code...")
    ast = parse(gfl_code)
    print(f"   AST keys: {list(ast.keys())}")
    
    print("3. Validating AST...")
    errors = validate(ast)
    if errors:
        print(f"   Validation errors: {errors}")
        return 1
    else:
        print("   Validation: Passed")
    
    print("4. Executing workflow...")
    try:
        result = execute(ast)
        
        print("   Design results:")
        if 'design' in result:
            design_result = result['design']
            print(f"     Generated {design_result['count']} sequences")
            print(f"     Method: {design_result['method']}")
        
        print("   Optimization results:")
        if 'optimize' in result:
            opt_result = result['optimize']
            print(f"     Best score: {opt_result['best_score']:.3f}")
            print(f"     Best parameters: {opt_result['best_parameters']}")
            print(f"     Iterations: {opt_result['iterations']}")
        
        print("✓ Workflow completed successfully!")
        return 0
        
    except Exception as e:
        print(f"   Execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
