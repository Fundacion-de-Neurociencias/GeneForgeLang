"""
test_clawbio_perturbation.py — Unit tests for ClawBio Perturbation Guard & Validation Tier
========================================================================================
Verifies that gfl-plugin-clawbio satisfies the Perturbation Test requirement
from Corpas et al. (Cell Genomics 2026):
  1. Empty files (0 bytes) raise explicit perturbation errors instead of silent report generation.
  2. Missing files raise explicit file-format/existence errors.
  3. Content-free files (comments only) raise perturbation errors.
"""

import tempfile
from pathlib import Path

import pytest
from gfl_plugin_clawbio._clawbio_runner import (
    run_skill,
    validate_input_file_perturbation,
)


def test_empty_file_perturbation():
    """Empty files (0 bytes) must fail the perturbation test explicitly."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        path = Path(f.name)

    try:
        valid, err = validate_input_file_perturbation(path)
        assert not valid
        assert "empty (0 bytes)" in err

        # Test inside run_skill
        res = run_skill("pharmgx-reporter", {"input_file": str(path)}, demo_mode=False)
        assert not res.success
        assert res.return_code == 400
        assert "empty (0 bytes)" in res.error_message
    finally:
        if path.exists():
            path.unlink()


def test_nonexistent_file_perturbation():
    """Nonexistent input files must fail perturbation validation explicitly."""
    bogus_path = "non_existent_genome_file_12345.txt"
    valid, err = validate_input_file_perturbation(bogus_path)
    assert not valid
    assert "does not exist" in err


def test_comment_only_file_perturbation():
    """Comment-only files with no genotype/count data rows must fail perturbation validation."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False, encoding="utf-8") as f:
        f.write("# 23andMe file header\n# RSID CHROMOSOME POSITION RESULT\n# No data rows below\n")
        path = Path(f.name)

    try:
        valid, err = validate_input_file_perturbation(path)
        assert not valid
        assert "no valid data rows" in err
    finally:
        if path.exists():
            path.unlink()


def test_valid_file_passes_perturbation():
    """Valid files with data rows must pass perturbation validation."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False, encoding="utf-8") as f:
        f.write("# RSID CHROMOSOME POSITION RESULT\nrs429358 19 44908684 T\n")
        path = Path(f.name)

    try:
        valid, err = validate_input_file_perturbation(path)
        assert valid
        assert err is None
    finally:
        if path.exists():
            path.unlink()
