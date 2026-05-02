import json
import re
import sys
from typing import Dict, Any, List

class GFLMinimalReferenceInterpreter:
    """
    A zero-dependency reference interpreter for GFL.
    This implementation prioritizes formal compliance over performance.
    """
    def __init__(self, schema_path: str, invariants_path: str):
        self.schema = self._load_json(schema_path)
        self.invariants = self._load_json(invariants_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return json.load(f)

    def validate_semantics(self, gfl_data: Dict[str, Any]) -> List[str]:
        errors = []
        # 1. Validate against Invariants Schema
        errors.extend(self._check_invariants(gfl_data))
        
        # 2. Check for Ambiguity
        errors.extend(self._check_ambiguity(gfl_data))
        
        return errors

    def _check_invariants(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        # Example check: IUPAC Sequence Integrity
        if 'experiment' in data and 'params' in data['experiment']:
            seq = data['experiment']['params'].get('sequence')
            if seq and not re.match(r"^[ACGTUacgtu\s]+$", seq):
                errors.append(f"INVARIANT_VIOLATION: Invalid IUPAC sequence '{seq}'")
        return errors

    def _check_ambiguity(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        # Example check: Locus specificity
        if 'experiment' in data and 'params' in data['experiment']:
            locus = data['experiment']['params'].get('target_locus')
            if locus == "HERV-K": # Example ambiguous target
                errors.append(f"AMBIGUITY_DETECTED: Target locus '{locus}' matches multiple genomic locations.")
        return errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mri.py <script.json>")
        sys.exit(1)
        
    mri = GFLMinimalReferenceInterpreter(
        "schema/gfl.schema.json", 
        "schema/gfl_semantic_invariants.schema.json"
    )
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        
    errors = mri.validate_semantics(data)
    if not errors:
        print("✅ GFL MRI: Semantic Validation Successful.")
    else:
        for err in errors:
            print(f"❌ GFL MRI: {err}")
        sys.exit(1)
