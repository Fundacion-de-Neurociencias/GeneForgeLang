import glob
import os
import sys

sys.path.insert(0, os.path.abspath('src'))

from geneforgelang.core.parser import parse_gfl
from geneforgelang.core.validator import EnhancedSemanticValidator

files = glob.glob('tests/corpus/real_papers/*.gfl')
for f in files:
    print(f'\n--- Testing {os.path.basename(f)} ---')
    try:
        with open(f, 'r') as file:
            content = file.read()
        ast = parse_gfl(content)
        if 'metadata' in ast:
            print(f'Parsed successfully! Workflow name: {ast["metadata"].get("name")}')
            
            validator = EnhancedSemanticValidator()
            result = validator.validate_ast(ast)
            
            if not result.is_valid:
                print('Validation Errors:')
                for err in result.errors:
                    print(f'  - [{err.code}] {err.message}')
            else:
                print('Validation Successful! (No gaps detected)')
        else:
            print(f'Parse returned type {type(ast)} without metadata: {ast}')
    except Exception as e:
        print(f'Parse Exception: {e}')
