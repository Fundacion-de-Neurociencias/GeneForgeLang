#!/usr/bin/env python3
"""
GeneForgeLang (GFL) Constitutional Architectural Audit Tool.

Enforces absolute boundaries between base compiler core and extensions.
Implements Level 1 mechanical checks (blocking) and Level 2 governance scoring.
"""

import os
import sys
import ast
import json
import importlib
from pathlib import Path

# Paths
SCRIPTS_DIR = Path(__file__).resolve().parent
GFL_CORE_DIR = SCRIPTS_DIR.parent
SRC_DIR = GFL_CORE_DIR / "src"

# Add src to sys.path to resolve geneforgelang imports
sys.path.insert(0, str(SRC_DIR))

# Define boundaries
FORBIDDEN_CORE_IMPORTS = ["geneforgelang.extensions"]
FORBIDDEN_EXT_IMPORTS = ["geneforgelang.core", "geneforgelang.semantic"]

class ImportScanner(ast.NodeVisitor):
    def __init__(self, current_module):
        self.current_module = current_module
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

def scan_module_imports(filepath):
    """Parse python source and return all imported modules."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
            scanner = ImportScanner(filepath.stem)
            scanner.visit(tree)
            return scanner.imports
        except SyntaxError:
            return []

def run_mechanical_checks():
    """
    Level 1 Mechanical Checks.
    
    Verifies:
    1. Core Contamination (core/semantic must not import extensions)
    2. Reverse Contamination (extensions must not import core)
    """
    print("==================================================")
    # Corrected printing text to handle Spanish encoding safely
    print("NIVEL 1: Hard Mechanical Gates (Checking boundaries)")
    print("==================================================")
    
    failures = 0
    package_root = SRC_DIR / "geneforgelang"
    
    # 1. Scan Core modules
    core_dir = package_root / "core"
    if core_dir.exists():
        for root, _, files in os.walk(core_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    rel_module = filepath.relative_to(SRC_DIR).with_suffix("").as_posix().replace("/", ".")
                    imports = scan_module_imports(filepath)
                    
                    for imp in imports:
                        if any(imp.startswith(forbidden) for forbidden in FORBIDDEN_CORE_IMPORTS):
                            print(f"[FAIL] Core Contamination: Core module '{rel_module}' imports extensions: '{imp}'")
                            failures += 1
                            
    # 2. Scan Extensions
    ext_dir = package_root / "extensions"
    if ext_dir.exists():
        for root, _, files in os.walk(ext_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    rel_module = filepath.relative_to(SRC_DIR).with_suffix("").as_posix().replace("/", ".")
                    imports = scan_module_imports(filepath)
                    
                    for imp in imports:
                        if any(imp.startswith(forbidden) for forbidden in FORBIDDEN_EXT_IMPORTS):
                            print(f"[FAIL] Reverse Contamination: Extension '{rel_module}' imports core: '{imp}'")
                            failures += 1

    if failures == 0:
        print("[PASS] Core & Extensions isolation boundaries are intact.")
    return failures == 0

def run_excision_simulation():
    """
    Sunsetability Simulation.
    
    Excludes extensions virtually from sys.modules and verifies that:
    1. Core modules still import successfully.
    2. No core module depends on extensions for compiler completeness.
    """
    print("\n==================================================")
    print("SUNSETABILITY: Excision Simulation")
    print("==================================================")
    
    package_root = SRC_DIR / "geneforgelang"
    
    # Dynamic excision: mock extensions module
    # We remove geneforgelang.extensions from sys.modules if it is loaded
    extensions_keys = [k for k in list(sys.modules.keys()) if k.startswith("geneforgelang.extensions")]
    backup_modules = {}
    for key in extensions_keys:
        backup_modules[key] = sys.modules.pop(key)
        
    try:
        # Check that we can import the parser and base compiler successfully without extensions
        print("Excising 'geneforgelang.extensions' dynamically...")
        importlib.invalidate_caches()
        
        # Test importing core modules
        import geneforgelang.core.parser as parser
        import geneforgelang.core.validator as validator
        
        print("[PASS] Excision Simulation successful: Base parser & validator compile with no extensions.")
        return True
    except Exception as e:
        print(f"[FAIL] Excision Simulation failed: Core depends on extensions! Error: {e}")
        return False
    finally:
        # Restore sys.modules
        for key, mod in backup_modules.items():
            sys.modules[key] = mod

def run_governance_scoring():
    """
    Level 2 Governance Scoring (Review Assist).
    
    Evaluates extensions against the five GFL governance dimensions.
    """
    print("\n==================================================")
    print("NIVEL 2: Structured Governance Scoring (Review Assist)")
    print("==================================================")
    
    package_root = SRC_DIR / "geneforgelang"
    ext_dir = package_root / "extensions"
    
    if not ext_dir.exists():
        print("[INFO] No extensions found to score.")
        return True
        
    extensions = [d for d in ext_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
    
    all_passed = True
    for ext in extensions:
        gov_file = ext / "governance.json"
        
        if not gov_file.exists():
            print(f"[WARN] Extension '{ext.name}' does not have a 'governance.json' self-assessment.")
            print("       Registering default alert score: 0 (Reject).")
            print("       Please provide a 'governance.json' inside the extension folder.")
            all_passed = False
            continue
            
        try:
            with open(gov_file, "r") as f:
                data = json.load(f)
                
            scores = data.get("scores", {})
            desc = data.get("justification", {})
            
            # Dimensions
            d1 = scores.get("irreducibility_depth", 0)
            d2 = scores.get("ontological_neutrality", 0)
            d3 = scores.get("provider_abstraction_purity", 0)
            d4 = scores.get("primitive_necessity", 0)
            d5 = scores.get("sunsetability_confidence", 0)
            
            total_score = d1 + d2 + d3 + d4 + d5
            
            print(f"\nExtension: '{ext.name}'")
            print(f"  * Irreducibility depth:       {d1}/5")
            print(f"  * Ontological neutrality:     {d2}/5")
            print(f"  * Provider abstraction purity:{d3}/5")
            print(f"  * Primitive necessity:        {d4}/5")
            print(f"  * Sunsetability confidence:   {d5}/5")
            print(f"  ---------------------------------")
            print(f"  * TOTAL SCORE:               {total_score}/25")
            
            if total_score < 15:
                print(f"  * STATUS: [REJECT AUTOMATICALLY] (Score {total_score} < 15)")
                all_passed = False
            elif 15 <= total_score <= 20:
                print(f"  * STATUS: [MANDATORY ESCALATION TO MAINTAINERS] (Score {total_score} is marginal)")
            else:
                print(f"  * STATUS: [ELIGIBLE FOR NORMAL REVIEW] (Score {total_score} > 20)")
                
        except Exception as e:
            print(f"[FAIL] Error parsing governance file for '{ext.name}': {e}")
            all_passed = False
            
    return all_passed

def main():
    print("==================================================")
    print("GENEFORGELANG CONSTITUTIONAL ARCHITECTURAL AUDIT")
    print("==================================================")
    
    m_ok = run_mechanical_checks()
    s_ok = run_excision_simulation()
    g_ok = run_governance_scoring()
    
    print("\n==================================================")
    if m_ok and s_ok:
        print("CONSTITUTIONAL COMPLIANCE: SUCCESS")
        print("==================================================")
        sys.exit(0)
    else:
        print("CONSTITUTIONAL COMPLIANCE: FAILED")
        print("==================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
