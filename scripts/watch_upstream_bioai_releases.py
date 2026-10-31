#!/usr/bin/env python3
"""CLI Watchdog for Upstream Bio-AI Releases tracked by GeneForgeLang.

Usage:
  python scripts/watch_upstream_bioai_releases.py          # Offline baseline verification
  python scripts/watch_upstream_bioai_releases.py --live   # Live query against GitHub Releases API
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure local src/ is importable when executed directly
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from geneforgelang.core.upstream_watchdog import check_all_upstream_engines  # noqa: E402


def main() -> int:
    """Run upstream Bio-AI release watchdog check and print JSON summary."""
    parser = argparse.ArgumentParser(description="Watch upstream Bio-AI releases for GeneForgeLang contracts.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Query live GitHub Releases REST API for latest tags.",
    )
    args = parser.parse_args()

    results = check_all_upstream_engines(live=args.live)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
