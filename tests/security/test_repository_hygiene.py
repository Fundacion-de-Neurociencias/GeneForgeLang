"""Repository hygiene rules for secrets and code-executing artifacts (F001).

These tests read only git metadata and configuration files. They never open a local
secret file: tracked paths come from ``git ls-files`` and ignore rules are checked with
``git check-ignore`` on synthetic paths.

Rules enforced:
- no tracked ``.env`` / ``.env.*`` file except ``*.env.example``;
- no tracked pickle/joblib artifact, and no code-executing deserializer in tracked code
  (docs/decisions/20261019-no-pickle-artifacts.md);
- the gitleaks configuration only allowlists the fake-secret fixture directory;
- the secret-scan workflow and the pre-commit hook are pinned.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = REPO_ROOT / ".devcontainer" / ".env.example"
GITLEAKS_CONFIG = REPO_ROOT / ".gitleaks.toml"
PRECOMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
SECRET_SCAN_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "secret-scan.yml"
SECRET_FIXTURES_DIR = "tests/fixtures/secrets/"

GITLEAKS_VERSION = "8.24.3"
GITLEAKS_LINUX_URL = (
    f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}/"
    f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz"
)
GITLEAKS_LINUX_SHA256 = "9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c"

EXPECTED_ENV_NAMES = {"GOOGLE_API_KEY", "PYTHONPATH", "GFL_ENV"}
SERIALIZED_SUFFIXES = (".pkl", ".pickle", ".joblib")
UNSAFE_DESERIALIZATION = re.compile(
    r"pickle\.loads?\(|Unpickler|read_pickle|allow_pickle\s*=\s*True|torch\.load\("
    r"|joblib\.load\(|\bdill\b|cloudpickle|\bshelve\b"
)
# Built from parts so this file does not itself contain the inline marker it forbids.
INLINE_ALLOW_MARKER = "gitleaks" + ":allow"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _in_git_checkout() -> bool:
    if shutil.which("git") is None:
        return False
    return _git("rev-parse", "--is-inside-work-tree").stdout.strip() == "true"


pytestmark = pytest.mark.skipif(not _in_git_checkout(), reason="hygiene rules apply to a git checkout (not an sdist)")


@pytest.fixture(scope="module")
def tracked_files() -> list[str]:
    result = _git("ls-files", "-z")
    assert result.returncode == 0, result.stderr
    return [path for path in result.stdout.split("\0") if path]


def _load_toml(path: Path) -> dict:
    try:
        import tomllib
    except ModuleNotFoundError:  # Python < 3.11
        tomllib = pytest.importorskip("tomli")
    with path.open("rb") as handle:
        return tomllib.load(handle)


def test_no_tracked_env_files(tracked_files: list[str]) -> None:
    offending = [
        path
        for path in tracked_files
        if (Path(path).name == ".env" or Path(path).name.startswith(".env.")) and not path.endswith(".env.example")
    ]
    assert offending == [], f"secret env files are tracked: {offending}"


def test_no_tracked_serialized_models(tracked_files: list[str]) -> None:
    offending = [path for path in tracked_files if path.lower().endswith(SERIALIZED_SUFFIXES)]
    assert offending == [], f"code-executing serialized artifacts are tracked: {offending}"


def test_env_example_names_only() -> None:
    assert ENV_EXAMPLE.is_file(), f"missing {ENV_EXAMPLE.relative_to(REPO_ROOT)}"
    names = set()
    for number, line in enumerate(ENV_EXAMPLE.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        assert re.fullmatch(r"#.*|[A-Z_][A-Z0-9_]*=", line), (
            f"line {number} must be a comment or an empty assignment NAME= (no values)"
        )
        if not line.startswith("#"):
            names.add(line[:-1])
    assert names == EXPECTED_ENV_NAMES


@pytest.mark.parametrize(
    ("path", "ignored"),
    [
        (".env", True),
        (".devcontainer/.env", True),
        ("sub/.env.local", True),
        ("model.pkl", True),
        ("a/b.pickle", True),
        ("c.joblib", True),
        (".env.example", False),
        (".devcontainer/.env.example", False),
    ],
)
def test_gitignore_blocks_secrets_and_pickles(path: str, ignored: bool) -> None:
    # --no-index evaluates the ignore rules even for paths that are (or were) tracked.
    result = _git("check-ignore", "--no-index", "--quiet", path)
    assert result.returncode in (0, 1), result.stderr
    assert (result.returncode == 0) is ignored


def test_no_code_executing_deserialization(tracked_files: list[str]) -> None:
    offending = []
    for path in tracked_files:
        if not path.endswith(".py") or path.startswith("tests/"):
            continue
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            if UNSAFE_DESERIALIZATION.search(line):
                offending.append(f"{path}:{number}")
    assert offending == [], f"code-executing deserialization found: {offending}"


def test_gitleaks_config_allowlist_is_fixture_only() -> None:
    config = _load_toml(GITLEAKS_CONFIG)
    assert config.get("extend", {}).get("useDefault") is True
    assert "allowlists" not in config, "use the single [allowlist] table"
    allowlist = config.get("allowlist")
    assert isinstance(allowlist, dict)
    assert set(allowlist) <= {"description", "paths"}
    paths = allowlist.get("paths")
    assert isinstance(paths, list) and len(paths) == 1
    assert SECRET_FIXTURES_DIR in paths[0]
    assert re.search(paths[0], SECRET_FIXTURES_DIR + "fake.txt")
    assert not re.search(paths[0], "src/geneforgelang/settings.py")
    for rule in config.get("rules", []):
        assert "allowlist" not in rule and "allowlists" not in rule, rule.get("id")


def test_no_inline_gitleaks_allow(tracked_files: list[str]) -> None:
    offending = []
    for path in tracked_files:
        # .autodev/ is local planning state (never published); its contracts name the marker.
        if path.startswith((SECRET_FIXTURES_DIR, ".autodev/")):
            continue
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            continue
        if INLINE_ALLOW_MARKER.encode() in file_path.read_bytes():
            offending.append(path)
    assert offending == [], f"inline gitleaks bypass markers found: {offending}"


def test_secret_scan_workflow_pinned() -> None:
    text = SECRET_SCAN_WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)

    # PyYAML (YAML 1.1) parses the bare key "on" as boolean True.
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["pull_request"]["branches"] == ["main"]
    assert triggers["push"]["branches"] == ["main"]
    assert workflow["permissions"] == {"contents": "read"}

    steps = workflow["jobs"]["gitleaks"]["steps"]
    for step in steps:
        if "uses" in step:
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", step["uses"]), step["uses"]
        if "run" in step:
            assert "${{" not in step["run"], f"expression inside run: in step {step.get('name')}"

    scripts = "\n".join(step.get("run", "") for step in steps)
    assert GITLEAKS_LINUX_URL in scripts
    assert f'echo "{GITLEAKS_LINUX_SHA256}  gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz" | sha256sum -c -' in scripts
    assert 'git show "$BASE_SHA:.gitleaks.toml"' in scripts, "PR scans must use the base config"
    assert "--redact" in scripts


def test_precommit_has_gitleaks() -> None:
    config = yaml.safe_load(PRECOMMIT_CONFIG.read_text(encoding="utf-8"))
    repos = [repo for repo in config["repos"] if repo["repo"] == "https://github.com/gitleaks/gitleaks"]
    assert len(repos) == 1
    assert repos[0]["rev"] == f"v{GITLEAKS_VERSION}"
    assert {hook["id"] for hook in repos[0]["hooks"]} & {"gitleaks", "gitleaks-system"}
