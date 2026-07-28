"""
_clawbio_runner.py — Thin subprocess boundary between GFL and ClawBio
=======================================================================
This is the ONLY file in gfl-plugin-clawbio that touches ClawBio.
It calls ClawBio via subprocess — never via Python import.
This guarantees:
  1. GFL core (geneforgelang.*) never depends on clawbio
  2. Plugin can load even if ClawBio is not installed
  3. Physical excision of this package leaves zero residue in GFL core

Constitutional guarantee (ADR-0003):
  ∀ module M in geneforgelang.*: M does NOT import gfl_plugin_clawbio
  ∀ module M in gfl_plugin_clawbio: M does NOT import geneforgelang.core,
                                     geneforgelang.semantic,
                                     geneforgelang.governance
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ClawBioRunResult:
    """Result of a ClawBio skill invocation via subprocess."""

    success: bool
    output: dict[str, Any]
    skill_name: str
    skill_version: str
    clawbio_installed: bool
    error_message: str | None = None
    stderr: str | None = None
    return_code: int = 0
    validation_tier: str = "BENCHMARKED"  # Tiered Validation Framework (Corpas et al. 2026)


def validate_input_file_perturbation(input_file: str | Path | None) -> tuple[bool, str | None]:
    """Perform Perturbation Test on input file to prevent silent degradation.

    Checks:
      1. File existence when explicit path provided
      2. Non-empty file (0 bytes)
      3. Valid non-comment content lines
    """
    if input_file is None:
        return True, None

    path = Path(input_file)
    if not path.exists():
        return False, f"PERTURBATION_TEST_FAILED: Input file '{input_file}' does not exist."

    if path.stat().st_size == 0:
        return (
            False,
            f"PERTURBATION_TEST_FAILED: Input file '{input_file}' is empty (0 bytes). Silent degradation prevented.",
        )

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        non_comment_lines = [
            line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")
        ]
        if len(non_comment_lines) == 0:
            return (
                False,
                f"PERTURBATION_TEST_FAILED: Input file '{input_file}' contains no valid data rows (only whitespace or comments).",
            )
    except Exception as e:
        return False, f"PERTURBATION_TEST_FAILED: Unable to read input file '{input_file}': {e}"

    return True, None


def _find_clawbio_skill(skill_name: str) -> Path | None:
    """Try to locate a ClawBio skill script.

    Search order:
    1. CLAWBIO_SKILLS_DIR environment variable
    2. Installed clawbio package location
    3. clawbio CLI --list-skills output
    """
    # Option 1: explicit env var
    env_dir = os.environ.get("CLAWBIO_SKILLS_DIR")
    if env_dir:
        candidate = Path(env_dir) / skill_name / f"{skill_name.replace('-', '_')}.py"
        if candidate.exists():
            return candidate

    # Option 2: try to find via installed clawbio package
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import clawbio; import os; print(os.path.dirname(clawbio.__file__))"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            clawbio_dir = Path(result.stdout.strip())
            skills_dir = clawbio_dir.parent / "skills"
            if skills_dir.exists():
                snake = skill_name.replace("-", "_")
                candidate = skills_dir / skill_name / f"{snake}.py"
                if candidate.exists():
                    return candidate
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def _is_clawbio_installed() -> bool:
    """Check if clawbio is importable without importing it in GFL's process."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import clawbio; print(clawbio.__version__)"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_skill(
    skill_name: str,
    params: dict[str, Any],
    demo_mode: bool = False,
) -> ClawBioRunResult:
    """Invoke a ClawBio skill via subprocess and return structured results.

    Args:
        skill_name: ClawBio skill identifier (e.g., 'pharmgx-reporter')
        params: Parameters dict to pass as JSON stdin to the skill
        demo_mode: If True, add --demo flag (uses skill's bundled demo data)

    Returns:
        ClawBioRunResult with success/failure and structured output
    """
    installed = _is_clawbio_installed()

    # Perturbation Test (Corpas et al. 2026): Check input file before execution
    input_file = params.get("input_file")
    if not demo_mode and input_file:
        valid, err = validate_input_file_perturbation(input_file)
        if not valid:
            return ClawBioRunResult(
                success=False,
                output={"status": "perturbation_test_failed", "error": err},
                skill_name=skill_name,
                skill_version="0.1.0",
                clawbio_installed=installed,
                error_message=err,
                return_code=400,
                validation_tier="BENCHMARKED",
            )

    if not installed:
        return ClawBioRunResult(
            success=False,
            output={"status": "clawbio_not_installed"},
            skill_name=skill_name,
            skill_version="unknown",
            clawbio_installed=False,
            error_message=(
                f"ClawBio is not installed. To use {skill_name}, install it with: "
                f"pip install 'gfl-plugin-clawbio[clawbio]'"
            ),
        )

    # Try to locate the skill script
    skill_path = _find_clawbio_skill(skill_name)

    if skill_path is None:
        # Fall back to openclaw CLI
        return _run_via_openclaw_cli(skill_name, params, demo_mode, installed)

    return _run_via_script(skill_path, skill_name, params, demo_mode, installed)


def _run_via_openclaw_cli(
    skill_name: str,
    params: dict[str, Any],
    demo_mode: bool,
    installed: bool,
) -> ClawBioRunResult:
    """Run skill via `openclaw` CLI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        cmd = ["clawbio", "run", skill_name, "--output", str(output_dir)]
        if demo_mode:
            cmd.append("--demo")

        # Pass params as individual flags
        for key, value in params.items():
            if value is not None:
                cmd += [f"--{key.replace('_', '-')}", str(value)]

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["MPLBACKEND"] = "Agg"
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
                env=env,
            )
            if proc.returncode != 0:
                print("CLI STDOUT:", proc.stdout)
                print("CLI STDERR:", proc.stderr)
        except subprocess.TimeoutExpired:
            return ClawBioRunResult(
                success=False,
                output={},
                skill_name=skill_name,
                skill_version="unknown",
                clawbio_installed=installed,
                error_message=f"Skill {skill_name} timed out after 300s",
                return_code=-1,
            )
        except FileNotFoundError:
            return ClawBioRunResult(
                success=False,
                output={},
                skill_name=skill_name,
                skill_version="unknown",
                clawbio_installed=installed,
                error_message="'openclaw' CLI not found. Install with: pip install clawbio",
                return_code=-2,
            )

        # Collect output files
        output_files: dict[str, Any] = {}
        for f in output_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(output_dir))
                if f.suffix == ".json":
                    try:
                        output_files[rel] = json.loads(f.read_text(encoding="utf-8"))
                    except json.JSONDecodeError:
                        output_files[rel] = f.read_text(encoding="utf-8")
                else:
                    output_files[rel] = f.read_text(encoding="utf-8", errors="replace")

        return ClawBioRunResult(
            success=proc.returncode == 0,
            output=output_files,
            skill_name=skill_name,
            skill_version="unknown",
            clawbio_installed=installed,
            error_message=None if proc.returncode == 0 else proc.stderr,
            stderr=proc.stderr,
            return_code=proc.returncode,
        )


def _run_via_script(
    skill_path: Path,
    skill_name: str,
    params: dict[str, Any],
    demo_mode: bool,
    installed: bool,
) -> ClawBioRunResult:
    """Run skill directly via its Python script."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        cmd = [sys.executable, str(skill_path), "--output", str(output_dir)]
        if demo_mode:
            cmd.append("--demo")

        for key, value in params.items():
            if value is not None and key not in ("output", "output_dir"):
                cmd += [f"--{key.replace('_', '-')}", str(value)]

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["MPLBACKEND"] = "Agg"
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=300,
                env=env,
            )
            if proc.returncode != 0:
                print("STDOUT:", proc.stdout)
                print("STDERR:", proc.stderr)
        except subprocess.TimeoutExpired:
            return ClawBioRunResult(
                success=False,
                output={},
                skill_name=skill_name,
                skill_version="unknown",
                clawbio_installed=installed,
                error_message="Skill timed out after 300s",
                return_code=-1,
            )

        output_files: dict[str, Any] = {}
        for f in output_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(output_dir))
                if f.suffix == ".json":
                    try:
                        output_files[rel] = json.loads(f.read_text(encoding="utf-8"))
                    except json.JSONDecodeError:
                        output_files[rel] = f.read_text(encoding="utf-8")
                else:
                    output_files[rel] = f.read_text(encoding="utf-8", errors="replace")

        return ClawBioRunResult(
            success=proc.returncode == 0,
            output=output_files,
            skill_name=skill_name,
            skill_version="unknown",
            clawbio_installed=installed,
            stderr=proc.stderr,
            return_code=proc.returncode,
        )
