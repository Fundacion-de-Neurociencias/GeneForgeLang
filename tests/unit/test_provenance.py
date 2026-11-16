"""Tests for the provenance contract (F004).

Simulated and stub output must be labelled at the type level, warn on first use, and
never feed a decision unless the caller opts in with ``allow_simulated=True``.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib.util
import json
import subprocess
import sys
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from geneforgelang.core import api
from geneforgelang.core.execution import (
    GFLExecutionEngine,
    execute_gfl_ast,
)
from geneforgelang.ir.external.openmed_connector import OpenMedConnector
from geneforgelang.plugins.alpha_genome import AlphaGenomePlugin
from geneforgelang.plugins.builtin.protein_generator import SimpleProteinGenerator
from geneforgelang.plugins.builtin.simple_optimizer import SimpleOptimizer
from geneforgelang.plugins.plugin_registry import PluginRegistry
from geneforgelang.provenance import (
    Provenance,
    ProvenancedDict,
    ProvenancedList,
    SimulatedComponentWarning,
    SimulatedInputError,
    inherit_provenance,
    list_simulated_components,
    provenance_of,
    register_simulated_component,
    require_real_inputs,
    reset_first_use_warnings,
)
from geneforgelang.utils.example_implementations import (
    BayesianOptimizer,
    MoleculeTransformerGenerator,
    ProteinVAEGenerator,
)

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "src" / "geneforgelang"


@pytest.fixture(autouse=True)
def _fresh_warnings() -> None:
    reset_first_use_warnings()


# ------------------------------------------------------------------ the type


def test_provenance_is_frozen_and_validated() -> None:
    label = Provenance("simulated", "tests", "1.0.0")
    with pytest.raises(dataclasses.FrozenInstanceError):
        label.kind = "measured"  # type: ignore[misc]
    assert label.is_unverified
    assert not Provenance("computed", "tests", "1.0.0").is_unverified
    assert label.to_dict() == {"kind": "simulated", "source": "tests", "version": "1.0.0"}


@pytest.mark.parametrize(
    "args", [("guessed", "s", "1"), ("stub", "", "1"), ("stub", "s", "")], ids=["kind", "source", "version"]
)
def test_provenance_rejects_bad_values(args: tuple[str, str, str]) -> None:
    with pytest.raises(ValueError):
        Provenance(*args)  # type: ignore[arg-type]


def test_provenance_module_passes_mypy_strict() -> None:
    pytest.importorskip("mypy")
    import mypy.version

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--no-incremental",
            "--config-file=",
            str(PACKAGE / "provenance.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"mypy {mypy.version.__version__}: {proc.stdout}{proc.stderr}"
    assert "1 source file" in proc.stdout


def test_labelled_containers_survive_json_and_copy() -> None:
    import copy

    label = Provenance("stub", "tests", "1")
    result = ProvenancedDict({"a": 1}, label)
    assert json.loads(json.dumps(result))["provenance"]["kind"] == "stub"
    assert copy.deepcopy(result).provenance == label
    assert provenance_of(dict(result)) == label  # the plain-mapping form is recognised too
    assert ProvenancedList([1], label).provenance == label


# ------------------------------------------------------- per component: label and warning


def _kind(result: Any) -> str:
    """Return the kind carried by a result and check every way it is exposed agrees."""
    if isinstance(result, dict):
        assert result["provenance"]["kind"] == result.provenance.kind
        return str(result.provenance.kind)
    if isinstance(result, list):
        kind = result.provenance.kind
        for item in result:
            carried = getattr(item, "provenance", None)
            if carried is None and hasattr(item, "metadata"):
                carried = Provenance(**item.metadata["provenance"])
            if carried is not None:  # plain values (an embedding's floats) carry the list's label only
                assert carried.kind == kind
        return str(kind)
    return str(Provenance(**result.metadata["provenance"]).kind)


def _bayesian_step() -> Any:
    optimizer = BayesianOptimizer()
    optimizer.setup({"temperature": "range(25, 42)"}, {}, {"maximize": "yield"}, {})
    return optimizer.suggest_next([])


COMPONENTS: list[tuple[str, Callable[[], Any], str]] = [
    ("SimpleProteinGenerator", lambda: SimpleProteinGenerator().generate({"count": 2, "length": 6}), "simulated"),
    (
        "SimpleOptimizer",
        lambda: SimpleOptimizer().optimize(
            {"search_space": {"x": {"range": [0, 1]}}, "objective": {"maximize": "y"}, "max_iterations": 2}
        ),
        "simulated",
    ),
    (
        "AlphaGenomePlugin",
        lambda: AlphaGenomePlugin().execute(
            "predict_functional_tracks", {"sequence": "ACGT", "tracks": ["ATAC"]}, {}
        ),
        "stub",
    ),
    ("OpenMedConnector", lambda: OpenMedConnector().get_entity_knowledge("TP53"), "stub"),
    ("OpenMedConnector", lambda: OpenMedConnector().get_embedding("TP53"), "stub"),
    ("OpenMedConnector", lambda: OpenMedConnector().find_similar_entities("TP53"), "stub"),
    ("OpenMedConnector", lambda: OpenMedConnector().extract_entities("TP53 and cancer"), "stub"),
    ("OpenMedConnector", lambda: OpenMedConnector().search_literature("TP53"), "stub"),
    ("OpenMedConnector", lambda: OpenMedConnector().deidentify_clinical_note("Patient John Doe"), "stub"),
    (
        "ProteinVAEGenerator",
        lambda: ProteinVAEGenerator().generate("ProteinSequence", {}, [], 2),
        "simulated",
    ),
    (
        "MoleculeTransformerGenerator",
        lambda: MoleculeTransformerGenerator().generate("SmallMolecule", {}, [], 2),
        "simulated",
    ),
    ("BayesianOptimizer", _bayesian_step, "simulated"),
]


@pytest.mark.parametrize("name,call,kind", COMPONENTS, ids=[f"{n}-{i}" for i, (n, _, _) in enumerate(COMPONENTS)])
def test_component_result_is_labelled_and_warns_once(name: str, call: Callable[[], Any], kind: str) -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        first = call()
        call()
    simulated = [w for w in caught if issubclass(w.category, SimulatedComponentWarning)]
    assert len(simulated) == 1, [str(w.message) for w in simulated]
    assert name in str(simulated[0].message)
    assert _kind(first) == kind


def test_alphafold_module_is_an_alias_of_the_single_implementation() -> None:
    from geneforgelang.plugins import alphafold

    assert alphafold.AlphaGenomePlugin is AlphaGenomePlugin


def test_openmed_entities_carry_provenance() -> None:
    connector = OpenMedConnector(enable_privacy_filter=False)
    entities = connector.extract_entities("TP53 in cancer")
    assert entities
    assert {e.provenance.kind for e in entities} == {"stub"}
    similar = connector.find_similar_entities("TP53")
    assert similar
    assert {s.provenance.kind for s in similar} == {"stub"}


def test_openmed_never_claims_privacy_clearance() -> None:
    result = OpenMedConnector().deidentify_clinical_note("Patient: John Doe, DOB: 01/15/1980")
    assert result["privacy_cleared"] is False
    assert "no privacy guarantee" in result["privacy_note"]
    assert result["provenance"]["kind"] == "stub"


# ------------------------------------------------------------------ registry


EXPECTED_COMPONENTS = {
    "AlphaGenomePlugin": "stub",
    "BayesianOptimizer": "simulated",
    "MoleculeTransformerGenerator": "simulated",
    "OpenMedConnector": "stub",
    "ProteinVAEGenerator": "simulated",
    "SimpleOptimizer": "simulated",
    "SimpleProteinGenerator": "simulated",
}


def test_registry_lists_every_packaged_component() -> None:
    components = list_simulated_components()
    assert {c.name: c.kind for c in components} == EXPECTED_COMPONENTS
    assert [c.name for c in components] == sorted(c.name for c in components)
    for component in components:
        assert (ROOT / component.location).is_file(), component.location
        assert component.promotion_oracle.strip()


def test_registry_refuses_a_real_component() -> None:
    with pytest.raises(ValueError, match="only simulated or stub"):
        register_simulated_component("X", Provenance("computed", "s", "1"), "x.py", "oracle")


def test_registry_refuses_a_name_registered_elsewhere(monkeypatch: pytest.MonkeyPatch) -> None:
    from geneforgelang import provenance

    monkeypatch.setattr(provenance, "_components", dict(provenance._components))  # keep the real registry clean
    label = Provenance("stub", "s", "1")
    register_simulated_component("F004-twin", label, "a.py", "oracle")
    register_simulated_component("F004-twin", label, "a.py", "oracle")  # same location: idempotent
    with pytest.raises(ValueError, match="already registered"):
        register_simulated_component("F004-twin", label, "b.py", "oracle")


def test_components_table_agrees_with_the_registry() -> None:
    table = ROOT / ".autodev" / "system" / "components.md"
    if not table.is_file():
        pytest.skip(".autodev/ is local state; the table is absent on a public clone")
    rows = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in table.read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and not line.startswith("|--") and not line.startswith("| Component")
    ]
    states = {row[0].strip("`"): row[1] for row in rows}
    assert set(states.values()) <= {"simulated", "stub", "dead"}
    assert all(row[-1] for row in rows), "every row needs a promotion oracle"
    assert set(EXPECTED_COMPONENTS) <= set(states)
    for name, kind in EXPECTED_COMPONENTS.items():
        assert states[name] == kind


# ------------------------------------------------- completeness oracle (AST scan)

# Modules that use a stochastic or hash primitive without any output value deriving from it:
# every use is a cache or content key.
HASH_KEY_ALLOWLIST = {
    "core/parser.py": "sha256 of the input text as a parse-cache key",
    "core/performance.py": "sha256 of call arguments as a cache key",
    "core/enhanced_inference_engine.py": "sha256 of features as a cache key",
    "plugins/plugin_registry.py": "sha256 of inputs as a result-cache key",
    "governance/behavioral/semantic_hash.py": "sha256 of a serialised value as its content hash",
    "ir/fase4/cache_layer.py": "md5 of queries as cache keys",
    "ir/fase4/async_retrieval.py": "md5 of a query as a cache key",
}
_PRIMITIVE_ROOTS = {"random", "secrets", "hashlib"}


def _uses_primitive(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                a.name.split(".")[0] in _PRIMITIVE_ROOTS or a.name.startswith("numpy.random")
                for a in node.names
            ):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in _PRIMITIVE_ROOTS or module.startswith("numpy.random"):
                return True
            if module == "numpy" and any(a.name == "random" for a in node.names):
                return True
        elif (
            isinstance(node, ast.Attribute)
            and node.attr == "random"
            and isinstance(node.value, ast.Name)
            and node.value.id in {"np", "numpy"}
        ):
            return True
    return False


def _modules_using_primitives(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in sorted(root.rglob("*.py"))
        if _uses_primitive(ast.parse(path.read_text(encoding="utf-8")))
    }


def test_every_stochastic_or_hash_module_is_registered_or_allowlisted() -> None:
    registered = {
        Path(c.location).relative_to("src/geneforgelang").as_posix() for c in list_simulated_components()
    }
    found = _modules_using_primitives(PACKAGE)
    assert found - registered == set(HASH_KEY_ALLOWLIST), (
        "unregistered module with a stochastic or hash primitive, or a stale allowlist entry: "
        f"{sorted((found - registered) ^ set(HASH_KEY_ALLOWLIST))}"
    )


def test_the_scan_sees_nested_imports_and_numpy_attributes(tmp_path: Path) -> None:
    (tmp_path / "plain.py").write_text("import json\n", encoding="utf-8")
    (tmp_path / "top.py").write_text("import random\n", encoding="utf-8")
    (tmp_path / "nested.py").write_text("def f():\n    import hashlib\n", encoding="utf-8")
    (tmp_path / "attr.py").write_text("import numpy as np\nx = np.random.beta(1, 2)\n", encoding="utf-8")
    (tmp_path / "frm.py").write_text("from random import choice\n", encoding="utf-8")
    assert _modules_using_primitives(tmp_path) == {"top.py", "nested.py", "attr.py", "frm.py"}


# --------------------------------------------------- no guarantee keys (AST, not grep)

GUARANTEE_KEYS = {"privacy_cleared", "validated", "calibrated"}


def _constant_guarantees(tree: ast.AST) -> list[int]:
    """Line numbers where a guarantee-named key, keyword or subscript is set to the constant True."""

    def is_true(node: ast.AST | None) -> bool:
        return isinstance(node, ast.Constant) and node.value is True

    def key_name(node: ast.AST | None) -> str | None:
        return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None

    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            hits += [
                v.lineno for k, v in zip(node.keys, node.values) if key_name(k) in GUARANTEE_KEYS and is_true(v)
            ]
        elif isinstance(node, ast.keyword) and node.arg in GUARANTEE_KEYS and is_true(node.value):
            hits.append(node.value.lineno)
        elif isinstance(node, ast.Assign) and is_true(node.value):
            hits += [
                node.lineno
                for t in node.targets
                if isinstance(t, ast.Subscript) and key_name(t.slice) in GUARANTEE_KEYS
            ]
    return sorted(hits)


def test_no_guarantee_key_is_hardcoded_true() -> None:
    offenders = []
    for base in (PACKAGE, ROOT / "examples" / "real_project"):
        for path in sorted(base.rglob("*.py")):
            offenders += [
                f"{path.relative_to(ROOT).as_posix()}:{line}"
                for line in _constant_guarantees(ast.parse(path.read_text(encoding="utf-8")))
            ]
    assert not offenders, f"guarantee-named key set to the constant True: {offenders}"


def test_the_guarantee_check_sees_every_form() -> None:
    source = (
        "a = {'privacy_cleared': True}\n"
        'b = {"validated": True}\n'
        "c = f(calibrated=True)\n"
        "d['validated'] = True\n"
        "ok = {'validated': is_ok, 'privacy_cleared': False}\n"
    )
    assert _constant_guarantees(ast.parse(source)) == [1, 2, 3, 4]


# ------------------------------------------------------------ decision paths


class _SimulatedGenerator:
    provenance = Provenance("simulated", "tests.simulated_generator", "0.1")

    def generate(self, **kwargs: Any) -> dict[str, Any]:
        return {"sequences": ["AAA"]}


class _StubOptimizer:
    provenance = Provenance("stub", "tests.stub_optimizer", "0.1")

    def optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"best_parameters": {"x": 1}}


class _CleanOptimizer:
    provenance = Provenance("computed", "tests.clean_optimizer", "0.1")

    def optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"best_parameters": {"x": 1}}


class _UnlabelledOptimizer:
    def optimize(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"best_parameters": {"x": 1}}


OPTIMIZE_BLOCK = {
    "strategy": {"name": "opt"},
    "search_space": {"x": {"range": [0, 1]}},
    "objective": {"maximize": "y"},
    "budget": {"max_experiments": 3},
}
DESIGN_BLOCK = {"model": "gen", "entity": "ProteinSequence", "count": 1}


def _registry(optimizer: Any = None, generator: Any = None) -> PluginRegistry:
    registry = PluginRegistry()
    if optimizer is not None:
        registry.register_optimizer("opt", optimizer)
    if generator is not None:
        registry.register_generator("gen", generator)
    return registry


@pytest.mark.parametrize("plugin", [SimpleOptimizer(), _StubOptimizer()], ids=["simulated", "stub"])
def test_optimize_block_refuses_unverified_plugins(plugin: Any) -> None:
    engine = GFLExecutionEngine()
    with pytest.raises(SimulatedInputError, match="allow_simulated=True"):
        engine.execute_optimize_block(OPTIMIZE_BLOCK, _registry(optimizer=plugin))


def test_design_block_refuses_a_simulated_generator() -> None:
    with pytest.raises(SimulatedInputError):
        GFLExecutionEngine().execute_design_block(DESIGN_BLOCK, _registry(generator=_SimulatedGenerator()))


def test_allowed_decision_output_is_labelled_simulated() -> None:
    engine = GFLExecutionEngine()
    result = engine.execute_optimize_block(
        OPTIMIZE_BLOCK, _registry(optimizer=SimpleOptimizer()), allow_simulated=True
    )
    assert provenance_of(result).kind == "simulated"
    assert "SimpleOptimizer" in provenance_of(result).source
    design = GFLExecutionEngine().execute_design_block(
        DESIGN_BLOCK, _registry(generator=_SimulatedGenerator()), allow_simulated=True
    )
    assert provenance_of(design).kind == "simulated"


def test_a_stub_input_becomes_simulated_output() -> None:
    result = GFLExecutionEngine().execute_optimize_block(
        OPTIMIZE_BLOCK, _registry(optimizer=_StubOptimizer()), allow_simulated=True
    )
    assert provenance_of(result).kind == "simulated"


def test_execute_gfl_ast_refuses_then_labels_the_top_level() -> None:
    ast_ = {"optimize": OPTIMIZE_BLOCK}
    registry = _registry(optimizer=SimpleOptimizer())
    with pytest.raises(SimulatedInputError):
        execute_gfl_ast(ast_, registry)
    result = execute_gfl_ast(ast_, registry, allow_simulated=True)
    assert provenance_of(result).kind == "simulated"
    assert provenance_of(result["optimize"]).kind == "simulated"


def test_public_execute_refuses_by_default_and_accepts_the_opt_in() -> None:
    ast_ = {"optimize": OPTIMIZE_BLOCK}
    registry = _registry(optimizer=SimpleOptimizer())
    with pytest.raises(SimulatedInputError):
        api.execute(ast_, registry, validate_first=False)
    result = api.execute(ast_, registry, validate_first=False, allow_simulated=True)
    assert provenance_of(result).kind == "simulated"
    assert "allow_simulated" in api.execute.__doc__


@pytest.mark.parametrize("plugin", [_CleanOptimizer(), _UnlabelledOptimizer()], ids=["computed", "unlabelled"])
def test_clean_plugins_run_without_opt_in_and_get_no_claim(plugin: Any) -> None:
    result = GFLExecutionEngine().execute_optimize_block(OPTIMIZE_BLOCK, _registry(optimizer=plugin))
    assert result == {"best_parameters": {"x": 1}}
    assert provenance_of(result) is None
    top = execute_gfl_ast({"optimize": OPTIMIZE_BLOCK}, _registry(optimizer=plugin))
    assert provenance_of(top) is None


def test_a_simulated_workflow_state_taints_a_clean_decision() -> None:
    engine = GFLExecutionEngine()
    engine.workflow_state["earlier"] = ProvenancedDict({"x": 1}, Provenance("simulated", "tests", "1"))
    with pytest.raises(SimulatedInputError):
        engine.execute_optimize_block(OPTIMIZE_BLOCK, _registry(optimizer=_CleanOptimizer()))
    result = engine.execute_optimize_block(
        OPTIMIZE_BLOCK, _registry(optimizer=_CleanOptimizer()), allow_simulated=True
    )
    assert provenance_of(result).kind == "simulated"


def test_the_guard_scans_nested_values_and_ignores_unlabelled_ones() -> None:
    label = Provenance("simulated", "tests", "1")
    nested = {"a": [1, {"b": ProvenancedList([], label)}]}
    with pytest.raises(SimulatedInputError):
        require_real_inputs(nested, consumer="test")
    require_real_inputs(nested, consumer="test", allow_simulated=True)
    require_real_inputs({"a": [1, 2]}, "text", None, consumer="test")
    assert inherit_provenance({"a": 1}, {"a": 1}, source="s", version="1") == {"a": 1}
    assert provenance_of(inherit_provenance([1], nested, source="s", version="1")).kind == "simulated"


def test_a_serialised_label_in_the_input_is_recognised() -> None:
    serialised = {"provenance": {"kind": "stub", "source": "elsewhere", "version": "1"}}
    with pytest.raises(SimulatedInputError, match="elsewhere"):
        require_real_inputs(serialised, consumer="test")


# ------------------------------------------------------------ the example script


def test_genesis_script_engine_is_labelled_simulated(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("numpy")
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    monkeypatch.setenv("MPLBACKEND", "Agg")
    path = ROOT / "examples" / "real_project" / "execute_genesis_real.py"
    spec = importlib.util.spec_from_file_location("execute_genesis_real_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)  # a clock, not the system under test
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = module.simulate_geneforge_engine()
    assert len([w for w in caught if issubclass(w.category, SimulatedComponentWarning)]) == 1
    assert json.dumps(result, default=str)
    assert result["provenance"]["kind"] == "simulated"
    assert result.provenance.kind == "simulated"
    assert {c["provenance_kind"] for c in result["final_rankings"]} == {"simulated"}


# ---------------------------------------------------------------- public docs


def test_public_api_reference_documents_the_provenance_contract() -> None:
    text = (ROOT / "docs" / "spec" / "API_CONTRACT.md").read_text(encoding="utf-8")
    for name in (
        "Provenance",
        "allow_simulated",
        "SimulatedInputError",
        "SimulatedComponentWarning",
        "list_simulated_components",
    ):
        assert name in text, f"docs/spec/API_CONTRACT.md does not mention {name}"
