"""Guard public text against claims without evidence.

GeneForgeLang is a public research library. Its README, docs, whitepaper and
example reports must not present simulated output as validation, imply
clinical use, or advertise a release that does not exist. This module turns
the corrections of `.autodev/spec/claims-inventory.md` (feature F002) into
checks that fail if such a claim returns.

Matching is case-insensitive. Each check reports the file and line of every
offending phrase.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

from geneforgelang.core.api import parse, validate

ROOT = Path(__file__).resolve().parents[2]

# Flip to True in the release that publishes geneforgelang on PyPI (feature F012).
PYPI_RELEASED = False

NOTICE = (
    "Research software. Not a medical device, not for clinical use, "
    "and not legal or regulatory advice."
)

SIMULATION_BANNER_TERMS = ("illustrative simulation", "np.random.beta", "not a validated study")
BANNER_WINDOW_LINES = 15

# Scores produced by np.random.beta in examples/real_project/execute_genesis_real.py.
BRCA1_FIGURES = (
    "89.7",
    "84.8",
    "3.0% off-target",
    "24 seconds",
    "<30% off-target",
    ">80% on-target",
)

# Claims denied in every public text file.
GLOBAL_DENYLIST = (
    "clinical-grade",
    "has been validated",
    "100% passing",
    "guaranteeing 100% reproducible",
    "mythos",
    "anthropic oss scanner",
    "enforced on all pull requests",
    "10.1101/2024.08.31",
)

PYPI_CLAIMS = ("img.shields.io/pypi", "pip install geneforgelang")

README_DENYLIST = (
    "scientific validation",
    "clinical relevance",
    "clinical neuro-skills",
    "high-precision",
    "revolutionary",
    "reproducibility packages",
    "5-model consensus",
    "v2.0",
    "img.shields.io/badge/version",
)

WHITEPAPER_DENYLIST = (
    "clinical modeling",
    "clinical ai chatbot",
    "validate clinical cases",
    "actionable biology",
)

SIMULATION_REPORT_DENYLIST = (
    "validate geneforgelang",
    "validates all major features",
    "readiness for",
    "clinical translation",
    "clinical applications",
    "clinical relevance",
    "suitable for both research and clinical",
)

PROPOSED_LABEL = "proposed, not implemented"
# Notation and translation features the whitepaper describes but the parser does not implement.
PROPOSED_NOTATION = re.compile(
    r"`~d`|`:r`|`\^p`|`\*p`|TIME\(|EDIT\(|MOT\(|PATHWAY:|HYPOTHESIS:|\bSBOL\b|\bGenBank\b|\bProForma\b|\bFASTA\b"
)
ZENODO_DOI = "10.5281/zenodo.15493559"

GFL_TOP_LEVEL_KEYS = frozenset(
    {
        "design",
        "optimize",
        "experiment",
        "analyze",
        "analysis",
        "simulate",
        "branch",
        "refine_data",
        "guided_discovery",
        "rules",
        "hypothesis",
        "timeline",
        "pathways",
        "complexes",
    }
)
PROPOSED_SYNTAX_MARKER = "<!-- proposed syntax: not implemented -->"
DOES_NOT_RUN_MARKER = "<!-- does not run yet: F010 -->"

FENCE = re.compile(r"^```([^\n`]*)\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _public_text_files() -> list[Path]:
    candidates = [
        ROOT / "README.md",
        ROOT / "whitepaper.md",
        ROOT / "CHANGELOG.md",
        ROOT / "SECURITY.md",
        ROOT / "CITATION.cff",
        *sorted((ROOT / "docs").rglob("*.md")),
        *sorted((ROOT / "examples" / "real_project").glob("*.md")),
    ]
    return [p for p in candidates if p.is_file()]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _find(text: str, phrases: tuple[str, ...]) -> list[str]:
    """Return 'line N: phrase' for every case-insensitive occurrence."""
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        hits.extend(f"line {number}: {phrase!r}" for phrase in phrases if phrase.lower() in lowered)
    return hits


def _has_simulation_banner(text: str) -> bool:
    head = "\n".join(text.splitlines()[:BANNER_WINDOW_LINES]).lower()
    return all(term in head for term in SIMULATION_BANNER_TERMS)


def _fences(text: str) -> list[tuple[int, str, str, str]]:
    """Return (line, language, body, preceding line) for each fenced block."""
    blocks = []
    for match in FENCE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        before = text[: match.start()].rstrip("\n").rsplit("\n", 1)[-1].strip()
        blocks.append((line, match.group(1).strip(), match.group(2), before))
    return blocks


def _gfl_mapping(source: str) -> bool:
    """True if `source` is YAML whose top level is a mapping with a GFL block key."""
    try:
        data = yaml.safe_load(source)
    except yaml.YAMLError:
        return False
    return isinstance(data, dict) and bool(GFL_TOP_LEVEL_KEYS & set(map(str, data)))


def _exists_case_sensitive(relative: str) -> bool:
    """Path check that also fails on case mismatches, which Windows and macOS would hide."""
    current = ROOT
    for part in Path(relative).parts:
        if part in {".", ""}:
            continue
        if part == ".." or not current.is_dir():
            current = current / part
            continue
        if part not in {child.name for child in current.iterdir()}:
            return False
        current = current / part
    return current.exists()


def _python_string_literals(source: str) -> list[str]:
    tree = ast.parse(source)
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _assert_valid_gfl(source: str, where: str) -> None:
    ast_ = parse(source)
    assert isinstance(ast_, dict), f"{where}: parse() returned {type(ast_).__name__}, not a mapping"
    errors = validate(ast_)
    assert not errors, f"{where}: validation errors: {[str(e) for e in errors]}"


README = ROOT / "README.md"
README_FENCES = _fences(_read(README))


# --- Denylists ---------------------------------------------------------------


@pytest.mark.parametrize("path", _public_text_files(), ids=_rel)
def test_no_global_claims(path: Path) -> None:
    phrases = GLOBAL_DENYLIST if PYPI_RELEASED else GLOBAL_DENYLIST + PYPI_CLAIMS
    hits = _find(_read(path), phrases)
    assert not hits, f"{_rel(path)} contains claims without evidence: {hits}"


def test_readme_has_no_unsupported_claims() -> None:
    hits = _find(_read(README), README_DENYLIST + BRCA1_FIGURES)
    assert not hits, f"README.md contains claims without evidence: {hits}"


def test_readme_labels_brca1_example_as_simulation() -> None:
    text = _read(README)
    match = re.search(r"^#+ [^\n]*illustrative simulation[^\n]*\n(.*?)(?=^#+ |\Z)", text, re.I | re.M | re.S)
    assert match, "README.md needs a section whose heading contains 'Illustrative simulation'"
    assert "random scores, not a validation" in match.group(1).lower()


def test_whitepaper_has_no_clinical_claims() -> None:
    lines = _read(ROOT / "whitepaper.md").splitlines()
    assert "clinical" not in lines[0].lower(), "whitepaper.md title must not claim clinical scope"
    # The Zenodo citation keeps the title of the published record verbatim.
    body = "\n".join(line for line in lines[1:] if ZENODO_DOI not in line)
    hits = _find(body, WHITEPAPER_DENYLIST)
    assert not hits, f"whitepaper.md contains unsupported claims: {hits}"


def test_whitepaper_labels_proposed_notation() -> None:
    unlabelled = []
    heading = ""
    for number, line in enumerate(_read(ROOT / "whitepaper.md").splitlines(), start=1):
        if line.startswith("#"):
            heading = line
            continue
        if PROPOSED_NOTATION.search(line) and PROPOSED_LABEL not in (line + heading).lower():
            unlabelled.append(f"line {number}: {line.strip()}")
    assert not unlabelled, f"whitepaper.md describes unimplemented notation without '{PROPOSED_LABEL}': {unlabelled}"


@pytest.mark.parametrize(
    "path", sorted((ROOT / "examples" / "real_project").glob("*.md")), ids=_rel
)
def test_simulation_reports_are_labelled(path: Path) -> None:
    text = _read(path)
    hits = _find(text, SIMULATION_REPORT_DENYLIST)
    assert not hits, f"{_rel(path)} presents simulated output as validated or clinical: {hits}"
    figures = _find(text, BRCA1_FIGURES)
    if figures:
        assert _has_simulation_banner(text), (
            f"{_rel(path)} reports simulated scores {figures} without a banner in its first "
            f"{BANNER_WINDOW_LINES} lines naming {SIMULATION_BANNER_TERMS}"
        )


# --- Notice -------------------------------------------------------------------


@pytest.mark.parametrize("path", [README, ROOT / "docs" / "index.md"], ids=_rel)
def test_intended_use_notice_present(path: Path) -> None:
    assert NOTICE in _read(path), f"{_rel(path)} is missing the notice: {NOTICE!r}"


# --- README code blocks and links ----------------------------------------------


@pytest.mark.parametrize("block", README_FENCES, ids=lambda b: f"README.md:{b[0]}")
def test_readme_fence_is_tagged(block: tuple[int, str, str, str]) -> None:
    line, language, body, _ = block
    assert language, f"README.md:{line}: code fence has no language tag"
    if _gfl_mapping(body):
        assert language in {"gfl", "yaml"}, f"README.md:{line}: GFL block tagged {language!r}, expected 'gfl' or 'yaml'"


@pytest.mark.parametrize(
    "block",
    [b for b in README_FENCES if b[1] in {"gfl", "yaml"} and b[3] != PROPOSED_SYNTAX_MARKER],
    ids=lambda b: f"README.md:{b[0]}",
)
def test_readme_gfl_block_parses_and_validates(block: tuple[int, str, str, str]) -> None:
    line, _, body, _ = block
    _assert_valid_gfl(body, f"README.md:{line}")


@pytest.mark.parametrize("block", [b for b in README_FENCES if b[1] == "python"], ids=lambda b: f"README.md:{b[0]}")
def test_readme_python_block_is_honest(block: tuple[int, str, str, str]) -> None:
    line, _, body, before = block
    if "from geneforgelang import" in body:
        assert before == DOES_NOT_RUN_MARKER, (
            f"README.md:{line}: the top-level import does not work yet; precede the block with {DOES_NOT_RUN_MARKER}"
        )
    if before == PROPOSED_SYNTAX_MARKER:
        return
    for literal in _python_string_literals(body):
        if _gfl_mapping(literal):
            _assert_valid_gfl(literal, f"README.md:{line} (embedded workflow)")


def test_readme_relative_links_resolve() -> None:
    text = _read(README)
    outside_fences = FENCE.sub("", text)
    broken = []
    for target in MARKDOWN_LINK.findall(outside_fences):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
            continue
        if not _exists_case_sensitive(target.split("#", 1)[0]):
            broken.append(target)
    assert not broken, f"README.md links to missing paths: {broken}"
