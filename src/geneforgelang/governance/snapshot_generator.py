import hashlib
import json
from pathlib import Path
from typing import Any

from geneforgelang.core.api import parse
from geneforgelang.governance.semantic_projection import canonical_hash

SNAPSHOT_DIR = Path(__file__).parent / "semantic_snapshots"
FIXTURES_DIR = SNAPSHOT_DIR / "golden_fixtures"
HASH_FILE = SNAPSHOT_DIR / "golden_ast_hashes.json"


def _canonical_ast_hash(ast_dict: dict[str, Any]) -> str:
    """Computes a stable SHA-256 hash of the Canonical Semantic Projection."""
    return canonical_hash(ast_dict)


def generate_snapshots():
    if not FIXTURES_DIR.exists():
        FIXTURES_DIR.mkdir(parents=True)
        print(f"Created {FIXTURES_DIR}. Please add golden files.")
        return

    snapshots = {}
    for gfl_file in FIXTURES_DIR.glob("*.*"):
        with open(gfl_file, encoding="utf-8") as f:
            content = f.read()

        snapshot_entry = {}

        # Determine parser by extension or try both
        if gfl_file.suffix == ".yaml" or gfl_file.suffix == ".gfl":
            try:
                ast_yaml = parse(content, use_grammar=False)
                snapshot_entry["yaml_ast_hash"] = _canonical_ast_hash(ast_yaml)
            except Exception as e:
                pass

        if gfl_file.suffix == ".gflgram" or gfl_file.suffix == ".gfl":
            try:
                ast_grammar = parse(content, use_grammar=True)
                snapshot_entry["grammar_ast_hash"] = _canonical_ast_hash(ast_grammar)
            except Exception as e:
                pass

        if snapshot_entry:
            snapshots[gfl_file.name] = snapshot_entry
        else:
            print(f"[WARNING] Fixture {gfl_file.name} failed all parsers.")

    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, indent=2, sort_keys=True)
    print(f"Generated semantic snapshots for {len(snapshots)} fixtures.")


if __name__ == "__main__":
    print("Generating Candidate Semantic Snapshots...")
    generate_snapshots()
    print("Please review golden_ast_hashes.json diff before committing.")
