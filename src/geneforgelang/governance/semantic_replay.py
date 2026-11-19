import json
import sys
from pathlib import Path

from geneforgelang.core.api import parse
from geneforgelang.governance.snapshot_generator import _canonical_ast_hash

SNAPSHOT_DIR = Path(__file__).parent / "semantic_snapshots"
FIXTURES_DIR = SNAPSHOT_DIR / "golden_fixtures"
HASH_FILE = SNAPSHOT_DIR / "golden_ast_hashes.json"


def audit_semantics():
    print("Running Semantic Behavioral Replay...")
    if not HASH_FILE.exists():
        print(f"[FATAL] Missing golden snapshot file at {HASH_FILE}")
        sys.exit(1)

    with open(HASH_FILE) as f:
        snapshots = json.load(f)

    if not snapshots:
        print("[WARNING] No semantic snapshots found. Constitutional test bypassed.")
        sys.exit(0)

    errors = []

    for fixture_name, expected_hashes in snapshots.items():
        fixture_file = FIXTURES_DIR / fixture_name
        if not fixture_file.exists():
            errors.append(f"[ERROR] Missing golden fixture file: {fixture_name}")
            continue

        with open(fixture_file, encoding="utf-8") as f:
            content = f.read()

        # Replay YAML Parser if snapshot exists
        if "yaml_ast_hash" in expected_hashes:
            try:
                ast_yaml = parse(content, use_grammar=False)
                yaml_hash = _canonical_ast_hash(ast_yaml)
                if yaml_hash != expected_hashes["yaml_ast_hash"]:
                    errors.append(f"[ERROR] Semantic drift in YAML parser for {fixture_name}")
            except Exception as e:
                errors.append(f"[ERROR] YAML parser failed for {fixture_name}: {e}")

        # Replay Grammar Parser if snapshot exists
        if "grammar_ast_hash" in expected_hashes:
            try:
                ast_grammar = parse(content, use_grammar=True)
                grammar_hash = _canonical_ast_hash(ast_grammar)
                if grammar_hash != expected_hashes["grammar_ast_hash"]:
                    errors.append(f"[ERROR] Semantic drift in Grammar parser for {fixture_name}")
            except Exception as e:
                errors.append(f"[ERROR] Grammar parser failed for {fixture_name}: {e}")

    if errors:
        print("\n--- SEMANTIC CONTRACT AUDIT FAILED ---")
        for err in errors:
            print(err)
        print("\nCovert semantic drift detected. Behavioral invariants broken.")
        sys.exit(1)

    print(f"\n[OK] Semantic behavioral contract verified across {len(snapshots)} fixtures.")
    sys.exit(0)


if __name__ == "__main__":
    audit_semantics()
