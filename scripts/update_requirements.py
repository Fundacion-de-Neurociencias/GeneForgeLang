import os
import ast
import sys
import importlib.util

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "requirements.txt")

def is_stdlib(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        if spec and "site-packages" not in (spec.origin or ""):
            return True
    except ModuleNotFoundError:
        return False
    return False

def find_imports(root_dir):
    imported = set()
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imported.add(alias.name.split(".")[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imported.add(node.module.split(".")[0])
                    except SyntaxError:
                        print(f"[WARN] Invalid syntax in {filepath}, skipping.")
    return imported

def update_requirements(imported_modules):
    if os.path.exists(REQUIREMENTS_FILE):
        with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
            existing = set(line.strip().split("==")[0] for line in f if line.strip())
    else:
        existing = set()

    new_modules = sorted([m for m in imported_modules if not is_stdlib(m) and m not in existing])

    if new_modules:
        print("[INFO] Adding new packages to requirements.txt:", new_modules)
        with open(REQUIREMENTS_FILE, "a", encoding="utf-8") as f:
            for mod in new_modules:
                f.write(f"{mod}\n")
    else:
        print("[OK] requirements.txt already includes all necessary non-stdlib packages.")

if __name__ == "__main__":
    modules = find_imports(PROJECT_ROOT)
    update_requirements(modules)
