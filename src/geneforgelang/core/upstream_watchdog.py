"""Upstream Bio-AI Release Watchdog for GeneForgeLang Contracts.

Tracks official upstream releases (AlphaFold 3, Boltz, Chai-1, Protenix) against
the baseline semantic versions registered in GFL contracts, alerting when new
performance or bugfix releases (e.g., AlphaFold v3.0.5 / v3.0.6) become available.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UpstreamEngineSpec:
    """Metadata specification for a tracked upstream Bio-AI engine."""

    engine_id: str
    repo_slug: str
    gfl_baseline_version: str
    key_capability: str


UPSTREAM_BIOAI_REGISTRY: dict[str, UpstreamEngineSpec] = {
    "alphafold3": UpstreamEngineSpec(
        engine_id="alphafold3",
        repo_slug="google-deepmind/alphafold3",
        gfl_baseline_version="3.0.5",
        key_capability=">10x faster Jackhmmer MSA pipeline & diffusion co-folding",
    ),
    "boltz1": UpstreamEngineSpec(
        engine_id="boltz1",
        repo_slug="jwohlwend/boltz",
        gfl_baseline_version="0.4.0",
        key_capability="Open biomolecular interaction co-folding",
    ),
    "chai1": UpstreamEngineSpec(
        engine_id="chai1",
        repo_slug="chaidiscovery/chai-lab",
        gfl_baseline_version="0.5.2",
        key_capability="Multi-modal molecular structure prediction",
    ),
    "protenix": UpstreamEngineSpec(
        engine_id="protenix",
        repo_slug="bytedance/Protenix",
        gfl_baseline_version="0.3.0",
        key_capability="AF3-level biomolecular complex reproduction",
    ),
}


def parse_semver(version_str: str) -> tuple[int, int, int] | None:
    """Parse a semantic version string (e.g. 'v3.0.5' or '3.0.6-rc1') into a (major, minor, patch) tuple."""
    m = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", version_str)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def evaluate_release_status(
    engine_id: str,
    latest_upstream_tag: str,
    registry: dict[str, UpstreamEngineSpec] | None = None,
) -> dict[str, Any]:
    """Compare an upstream release tag against the GFL baseline version for a given engine."""
    reg = registry or UPSTREAM_BIOAI_REGISTRY
    if engine_id not in reg:
        raise KeyError(f"Unknown upstream engine_id '{engine_id}'")

    spec = reg[engine_id]
    base_tuple = parse_semver(spec.gfl_baseline_version)
    latest_tuple = parse_semver(latest_upstream_tag)

    if base_tuple is None or latest_tuple is None:
        status = "UNKNOWN_VERSION_FORMAT"
        upgrade_available = False
    elif latest_tuple > base_tuple:
        status = "UPGRADE_AVAILABLE"
        upgrade_available = True
    elif latest_tuple == base_tuple:
        status = "UP_TO_DATE"
        upgrade_available = False
    else:
        status = "AHEAD_OF_UPSTREAM"
        upgrade_available = False

    return {
        "engine_id": spec.engine_id,
        "repo_slug": spec.repo_slug,
        "gfl_baseline_version": spec.gfl_baseline_version,
        "latest_upstream_tag": latest_upstream_tag,
        "status": status,
        "upgrade_available": upgrade_available,
        "key_capability": spec.key_capability,
        "security_gate_command": "python C:\\Users\\usuario\\NeuroOS\\scripts\\security\\run_security_gate.py --report",
    }


def fetch_github_latest_tag(repo_slug: str, timeout_sec: float = 5.0) -> str | None:
    """Query the public GitHub Releases/Tags API for the latest tag of a repository."""
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo_slug):
        raise ValueError(f"Invalid GitHub repository slug: {repo_slug}")

    url = f"https://api.github.com/repos/{repo_slug}/releases/latest"
    if not url.startswith("https://api.github.com/"):
        raise ValueError("Only https://api.github.com/ endpoints are permitted")

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "GeneForgeLang-Upstream-Watchdog/2.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:  # nosec B310
            payload = json.loads(resp.read().decode("utf-8"))
            tag = payload.get("tag_name")
            return str(tag) if tag else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def check_all_upstream_engines(live: bool = False) -> list[dict[str, Any]]:
    """Check all registered Bio-AI engines, optionally querying GitHub API live."""
    results: list[dict[str, Any]] = []
    for engine_id, spec in UPSTREAM_BIOAI_REGISTRY.items():
        tag = spec.gfl_baseline_version
        if live:
            fetched = fetch_github_latest_tag(spec.repo_slug)
            if fetched is not None:
                tag = fetched
        results.append(evaluate_release_status(engine_id, tag))
    return results


__all__ = [
    "UpstreamEngineSpec",
    "UPSTREAM_BIOAI_REGISTRY",
    "parse_semver",
    "evaluate_release_status",
    "fetch_github_latest_tag",
    "check_all_upstream_engines",
]
