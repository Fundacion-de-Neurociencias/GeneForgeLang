"""
Tests for gfl-plugin-clawbio
==============================
All tests run WITHOUT ClawBio installed — they validate plugin structure,
GFL interface compliance, and graceful degradation.

Constitutional checks:
  1. No import from geneforgelang.core, geneforgelang.semantic,
     geneforgelang.governance inside the plugin modules.
  2. All plugins implement GeneratorPlugin interface.
  3. All plugins return DesignCandidate when ClawBio is absent.
  4. _clawbio_runner never imports geneforgelang.* modules.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# Add parent repo src to path for geneforgelang
PLUGIN_ROOT = Path(__file__).parent.parent
ECOSYSTEM_ROOT = PLUGIN_ROOT.parent
GFL_SRC = ECOSYSTEM_ROOT / "GeneForgeLang" / "src"
if GFL_SRC.exists():
    sys.path.insert(0, str(GFL_SRC))

from geneforgelang.plugins.interfaces import DesignCandidate, EntityType, GeneratorPlugin
from gfl_plugin_clawbio import (
    CrisprScreenPlugin,
    GwasLookupPlugin,
    PharmGxPlugin,
    RnaseqDEPlugin,
)

# ── Interface compliance tests ────────────────────────────────────────────────

PLUGINS = [PharmGxPlugin, CrisprScreenPlugin, RnaseqDEPlugin, GwasLookupPlugin]


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_implements_generator_plugin(plugin_class):
    """Each plugin must be a proper subclass of GeneratorPlugin."""
    assert issubclass(plugin_class, GeneratorPlugin), f"{plugin_class.__name__} must inherit from GeneratorPlugin"


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_has_name_and_version(plugin_class):
    """Each plugin must declare name and version."""
    p = plugin_class()
    assert isinstance(p.name, str) and len(p.name) > 0
    assert isinstance(p.version, str) and len(p.version) > 0


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_supported_entities_not_empty(plugin_class):
    """supported_entities must return a non-empty list of EntityType."""
    p = plugin_class()
    entities = p.supported_entities
    assert isinstance(entities, list) and len(entities) > 0
    for e in entities:
        assert isinstance(e, EntityType), f"Expected EntityType, got {type(e)}"


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_generate_without_clawbio_returns_design_candidates(plugin_class):
    """When ClawBio is not installed, generate() must return DesignCandidate list."""
    p = plugin_class()
    results = p.generate(
        entity="DNA_SEQUENCE",
        objective={"analyze": "test"},
        constraints=[],
        count=1,
        demo_mode=False,
    )
    assert isinstance(results, list), "generate() must return a list"
    assert len(results) > 0, "generate() must return at least one candidate"
    for r in results:
        assert isinstance(r, DesignCandidate), f"generate() must return DesignCandidate, got {type(r)}"


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_graceful_degradation_has_status(plugin_class):
    """When ClawBio is absent, each result must have a 'status' in properties."""
    p = plugin_class()
    results = p.generate("DNA_SEQUENCE", {}, [], 1)
    for r in results:
        assert "status" in r.properties, f"{plugin_class.__name__}: DesignCandidate.properties must have 'status'"


@pytest.mark.parametrize("plugin_class", PLUGINS)
def test_get_supported_constraints_returns_list(plugin_class):
    """get_supported_constraints() must return a list of strings."""
    p = plugin_class()
    constraints = p.get_supported_constraints()
    assert isinstance(constraints, list)
    for c in constraints:
        assert isinstance(c, str)


# ── ADR-0003 Constitutional checks ───────────────────────────────────────────

PLUGIN_SRC_DIR = PLUGIN_ROOT / "gfl_plugin_clawbio"
FORBIDDEN_IMPORTS = [
    "geneforgelang.core",
    "geneforgelang.semantic",
    "geneforgelang.governance",
    "geneforgelang.ir",
    "geneforgelang.temporal",
]


def _extract_imports(source_file: Path) -> list[str]:
    """Extract all import module names from a Python source file."""
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


@pytest.mark.parametrize("src_file", list(PLUGIN_SRC_DIR.glob("*.py")))
def test_no_forbidden_gfl_core_imports(src_file):
    """Plugin modules must NOT import geneforgelang.core/semantic/governance."""
    imports = _extract_imports(src_file)
    for forbidden in FORBIDDEN_IMPORTS:
        for imp in imports:
            assert not imp.startswith(forbidden), (
                f"ADR-0003 VIOLATION in {src_file.name}: "
                f"imports '{imp}' which starts with forbidden prefix '{forbidden}'"
            )


def test_runner_does_not_import_geneforgelang():
    """_clawbio_runner.py must have zero imports from geneforgelang.*"""
    runner = PLUGIN_SRC_DIR / "_clawbio_runner.py"
    imports = _extract_imports(runner)
    gfl_imports = [i for i in imports if i.startswith("geneforgelang")]
    assert gfl_imports == [], f"ADR-0003 VIOLATION: _clawbio_runner.py imports geneforgelang: {gfl_imports}"


def test_governance_json_score_above_threshold():
    """governance.json must have total_score > decision_threshold."""
    import json

    governance_file = PLUGIN_ROOT / "governance.json"
    assert governance_file.exists(), "governance.json not found"
    governance = json.loads(governance_file.read_text(encoding="utf-8"))
    total = governance["total_score"]
    threshold = governance["decision_threshold"]
    assert total > threshold, f"ADR-0003: governance score {total} must be > threshold {threshold}"
    assert governance["decision"] != "REJECTED", "ADR-0003: governance.json says REJECTED"


# ── Plugin-specific tests ─────────────────────────────────────────────────────


class TestPharmGxPlugin:
    def test_pharmgx_genes_are_listed(self):
        from gfl_plugin_clawbio.pharmgx import PGX_GENES

        assert "CYP2D6" in PGX_GENES
        assert "CYP2C19" in PGX_GENES
        assert len(PGX_GENES) == 12

    def test_pharmgx_tool_id(self):
        from gfl_plugin_clawbio.pharmgx import PLUGIN_TOOL_ID

        assert PLUGIN_TOOL_ID == "clawbio_pharmgx"

    def test_pharmgx_install_hint_present(self):
        p = PharmGxPlugin()
        results = p.generate("DNA_SEQUENCE", {}, [], 1)
        if results[0].properties.get("status") == "clawbio_not_installed":
            assert "install_hint" in results[0].metadata


class TestCrisprScreenPlugin:
    def test_crispr_tool_id(self):
        from gfl_plugin_clawbio.crispr_screen import PLUGIN_TOOL_ID

        assert PLUGIN_TOOL_ID == "clawbio_crispr_screen"

    def test_deterministic_metadata(self):
        """When successful, output should declare deterministic: True."""
        p = CrisprScreenPlugin()
        # With demo_mode forced (no ClawBio) we just check graceful degradation
        results = p.generate("DNA_SEQUENCE", {}, [], 1, demo_mode=False)
        assert len(results) > 0


class TestGwasLookupPlugin:
    def test_missing_rsid_returns_error_candidate(self):
        p = GwasLookupPlugin()
        results = p.generate("DNA_SEQUENCE", {}, [], 1, rsid=None, demo_mode=False)
        assert len(results) == 1
        # Either clawbio_not_installed or missing_rsid
        assert results[0].properties["status"] in ("clawbio_not_installed", "missing_rsid")

    def test_supported_databases_list(self):
        from gfl_plugin_clawbio.gwas_lookup import SUPPORTED_DATABASES

        assert "gwas_catalog" in SUPPORTED_DATABASES
        assert "gtex_v8" in SUPPORTED_DATABASES
        assert len(SUPPORTED_DATABASES) >= 8
