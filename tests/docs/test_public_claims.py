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
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

from geneforgelang.core.api import parse, validate

ROOT = Path(__file__).resolve().parents[2]

# Flip to True in the release that publishes geneforgelang on PyPI (feature F012).
PYPI_RELEASED = False

NOTICE = "Research software. Not a medical device, not for clinical use, and not legal or regulatory advice."

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
    # External resources that do not exist (HTTP 404 on 2026-10-19).
    "geneforgelang.readthedocs.io",
    "geneforgelang/discussions",
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
    "revolutionary",
    "real-world application",
    "executed on the geneforge webapp",
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
    return [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]


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


@pytest.mark.parametrize("path", sorted((ROOT / "examples" / "real_project").glob("*.md")), ids=_rel)
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


@pytest.mark.parametrize(
    "block",
    [
        b
        for b in README_FENCES
        if b[1] == "python" and b[3] not in {DOES_NOT_RUN_MARKER, PROPOSED_SYNTAX_MARKER} and "geneforgelang" in b[2]
    ],
    ids=lambda b: f"README.md:{b[0]}",
)
def test_readme_python_block_runs(block: tuple[int, str, str, str], tmp_path: Path) -> None:
    """An unmarked example that uses geneforgelang must run as a reader would run it.

    The block runs in a fresh isolated interpreter (-I) from an empty directory,
    so the repository root is not on sys.path and only the installed package is
    importable.
    """
    line, _, body, _ = block
    script = tmp_path / "readme_block.py"
    script.write_text(body, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-I", str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"README.md:{line}: example fails (exit {result.returncode}); fix it or precede it with "
        f"{DOES_NOT_RUN_MARKER}\n{result.stderr}"
    )


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


# Rows of the claims inventory owned by later features. Each guard asserts the
# claim is absent. While the claim is still in the tree the guard is a strict
# xfail naming the owning feature: when that feature removes the claim the guard
# XPASSes and fails the suite until the marker is dropped, and from then on it
# blocks the claim from returning. Only the guard's own AssertionError counts as
# the expected failure; any other exception (a missing or unreadable file) is
# reported as an error instead of being swallowed as an xfail.
def _owned_xfail(row: str, feature: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=f"{row} still present; {feature} removes it, then drop this marker",
    )


def _pyproject() -> dict:
    if tomllib is None:
        pytest.skip("tomllib needs Python 3.11")
    return tomllib.loads(_read(ROOT / "pyproject.toml"))


def _c15_version_consistent() -> list[str]:
    project = _pyproject()["project"]
    citation = yaml.safe_load(_read(ROOT / "CITATION.cff"))
    if str(citation.get("version")) != project["version"]:
        return [f"CITATION.cff version {citation.get('version')} != pyproject {project['version']}"]
    return []


def _c15_stable_major_not_beta() -> list[str]:
    project = _pyproject()["project"]
    major = int(project["version"].split(".")[0])
    beta = "Development Status :: 4 - Beta" in project.get("classifiers", [])
    return [f"version {project['version']} is a stable major but classified Beta"] if major >= 1 and beta else []


def _c16_no_calibration_claim() -> list[str]:
    hits = []
    for path in sorted((ROOT / "src").rglob("*.py")):
        hits += [f"{_rel(path)}: {h}" for h in _find(_read(path), ("ECE <= 0.08", "benchmarked at 0.068"))]
    return hits


def _c17_no_unconditional_privacy_flag() -> list[str]:
    path = ROOT / "src" / "geneforgelang" / "ir" / "external" / "openmed_connector.py"
    # A deleted connector carries no claim: the guard passes, so the strict
    # xfail XPASSes and forces the marker to be dropped.
    if not path.is_file():
        return []
    return [f"{_rel(path)}: privacy_cleared is hardcoded True"] if '"privacy_cleared": True' in _read(path) else []


def _c18_no_mocked_conformance() -> list[str]:
    hits = []
    for base in ("resources", "scripts"):
        for path in sorted((ROOT / base).rglob("conformance_runner.py")):
            hits += [f"{_rel(path)}: {h}" for h in _find(_read(path), ("Mocking success",))]
    return hits


def _c19_no_dead_docs_url() -> list[str]:
    urls = _pyproject()["project"].get("urls", {})
    return [f"pyproject.toml [project.urls]: {u}" for u in urls.values() if "readthedocs.io" in u]


def _c20_no_status_doc(name: str):
    def check() -> list[str]:
        return [f"docs/{name} exists"] if (ROOT / "docs" / name).is_file() else []

    return check


OWNED_CLAIMS = [
    pytest.param(_c15_version_consistent, id="C15-citation-matches-pyproject-F011"),
    pytest.param(_c15_stable_major_not_beta, id="C15-version-vs-beta-F011", marks=_owned_xfail("C15", "F011")),
    pytest.param(_c16_no_calibration_claim, id="C16-calibration-claim-F008"),
    pytest.param(_c17_no_unconditional_privacy_flag, id="C17-privacy-cleared-F004", marks=_owned_xfail("C17", "F004")),
    pytest.param(_c18_no_mocked_conformance, id="C18-mocked-conformance-F006", marks=_owned_xfail("C18", "F006")),
    pytest.param(_c19_no_dead_docs_url, id="C19-readthedocs-url-F011", marks=_owned_xfail("C19", "F011")),
    pytest.param(_c20_no_status_doc("END_TO_END_TRUTH_AUDIT.md"), id="C20-truth-audit-doc-F009"),
    pytest.param(
        _c20_no_status_doc("PULL_REQUEST_DESCRIPTION.md"),
        id="C20-pr-description-doc-F009",
        marks=_owned_xfail("C20", "F009"),
    ),
]


@pytest.mark.parametrize("check", OWNED_CLAIMS)
def test_owned_claim_absent(check) -> None:
    hits = check()
    assert not hits, f"Claim owned by a later feature is present: {hits}"
