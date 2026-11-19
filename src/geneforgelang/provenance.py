"""Provenance contract: marks simulated output at the type level.

Every result of a plugin or connector that is not a measured or computed value
carries a :class:`Provenance` with a ``kind`` of ``simulated`` or ``stub``. A
decision path (optimizer selection, gating, ranking) calls
:func:`require_real_inputs` and refuses such input unless the caller passes
``allow_simulated=True``; the output it then produces is labelled ``simulated``
by :func:`inherit_provenance`.

Kinds, from weakest to strongest evidence:

* ``stub``: a placeholder that stands in for a service or model that is not
  connected (hash-derived or hardcoded values).
* ``simulated``: values drawn from a random or toy generator.
* ``computed``: a deterministic result of a documented algorithm on the input.
* ``measured``: a value obtained from an instrument or a real external service.

Nothing in this module promotes a component to ``computed`` or ``measured``.
That needs the real service and an oracle test.
"""

from __future__ import annotations

import importlib
import threading
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, TypeVar, cast, get_args

ProvenanceKind = Literal["measured", "computed", "simulated", "stub"]

#: Kinds that must never feed a decision or public text unless the caller opts in.
UNVERIFIED_KINDS: frozenset[str] = frozenset({"simulated", "stub"})

_MAX_SCAN_DEPTH = 8

_T = TypeVar("_T")


class SimulatedComponentWarning(UserWarning):
    """A simulated or stub component produced output for the first time in this process."""


class SimulatedInputError(ValueError):
    """A decision path received simulated or stub input and ``allow_simulated`` was not set."""


@dataclass(frozen=True)
class Provenance:
    """Where a result came from.

    Args:
        kind: One of ``measured``, ``computed``, ``simulated`` or ``stub``.
        source: The component that produced the result, for example
            ``geneforgelang.plugins.builtin.simple_optimizer.SimpleOptimizer``.
        version: Version of the component, or ``unversioned`` if it has none.

    Raises:
        ValueError: If ``kind`` is not one of the four kinds or ``source`` or
            ``version`` is empty.
    """

    kind: ProvenanceKind
    source: str
    version: str

    def __post_init__(self) -> None:
        if self.kind not in get_args(ProvenanceKind):
            raise ValueError(f"unknown provenance kind {self.kind!r}")
        if not self.source or not self.version:
            raise ValueError("provenance needs a non-empty source and version")

    @property
    def is_unverified(self) -> bool:
        """True when the result is ``simulated`` or ``stub``."""
        return self.kind in UNVERIFIED_KINDS

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable form."""
        return {"kind": self.kind, "source": self.source, "version": self.version}


class ProvenancedDict(dict[str, Any]):
    """A ``dict`` result that carries its :class:`Provenance`.

    The label is available as ``result.provenance`` and, so that it survives
    ``dict(result)`` and JSON, as the plain mapping ``result["provenance"]``.
    """

    provenance: Provenance

    def __init__(self, data: Mapping[str, Any], provenance: Provenance) -> None:
        super().__init__(data)
        self.provenance = provenance
        self["provenance"] = provenance.to_dict()


class ProvenancedList(list[Any]):
    """A ``list`` result that carries its :class:`Provenance` as ``result.provenance``."""

    provenance: Provenance

    def __init__(self, items: Any, provenance: Provenance) -> None:
        super().__init__(items)
        self.provenance = provenance


# ---------------------------------------------------------------- registry


@dataclass(frozen=True)
class SimulatedComponent:
    """A registered component whose output is not measured or computed."""

    name: str
    kind: ProvenanceKind
    location: str
    promotion_oracle: str


_components: dict[str, SimulatedComponent] = {}
_warned: set[str] = set()
_lock = threading.Lock()

# Modules that register components when imported. ``list_simulated_components``
# imports them so the answer does not depend on what the caller imported first.
_COMPONENT_MODULES = (
    "geneforgelang.core.alphagenome2_engine",
    "geneforgelang.plugins.biodecision_plugin",
    "geneforgelang.plugins.builtin.protein_generator",
    "geneforgelang.plugins.builtin.simple_optimizer",
    "geneforgelang.plugins.alpha_genome",
    "geneforgelang.ir.external.openmed_connector",
    "geneforgelang.utils.example_implementations",
)


def register_simulated_component(name: str, provenance: Provenance, location: str, promotion_oracle: str) -> None:
    """Record a simulated or stub component so it can be listed.

    Args:
        name: Unique component name.
        provenance: Its provenance; the kind must be ``simulated`` or ``stub``.
        location: Repository path of the code.
        promotion_oracle: What would have to exist to promote it to a real component.

    Raises:
        ValueError: If the provenance kind is not ``simulated`` or ``stub``, or the
            name is already registered for a different location.
    """
    if not provenance.is_unverified:
        raise ValueError(f"{name}: only simulated or stub components are registered")
    component = SimulatedComponent(name, provenance.kind, location, promotion_oracle)
    with _lock:
        known = _components.get(name)
        if known is not None and known.location != location:
            raise ValueError(f"{name} is already registered at {known.location}")
        _components[name] = component


def list_simulated_components() -> tuple[SimulatedComponent, ...]:
    """Return every simulated or stub component shipped in the package, sorted by name."""
    for module in _COMPONENT_MODULES:
        importlib.import_module(module)
    with _lock:
        return tuple(sorted(_components.values(), key=lambda c: c.name))


def warn_first_use(component: str, provenance: Provenance, stacklevel: int = 3) -> None:
    """Emit :class:`SimulatedComponentWarning` the first time ``component`` is used.

    Later uses in the same process are silent; :func:`reset_first_use_warnings`
    clears that memory (used by tests).
    """
    with _lock:
        if component in _warned:
            return
        _warned.add(component)
    warnings.warn(
        f"{component} returns {provenance.kind} output (source: {provenance.source}); "
        "it is not a measured or computed result and must not feed decisions or public text",
        SimulatedComponentWarning,
        stacklevel=stacklevel,
    )


def reset_first_use_warnings() -> None:
    """Forget which components already warned."""
    with _lock:
        _warned.clear()


# ---------------------------------------------------------------- decision guard


def provenance_of(value: object) -> Provenance | None:
    """Return the provenance carried by ``value``, or ``None`` if it carries none.

    Recognises a ``provenance`` attribute holding a :class:`Provenance` (also on a
    class, so a registry that stores plugin classes works) and a mapping with a
    ``provenance`` entry that is a :class:`Provenance` or its ``to_dict`` form.
    """
    attribute = getattr(value, "provenance", None)
    if isinstance(attribute, Provenance):
        return attribute
    if isinstance(value, Mapping):
        entry = value.get("provenance")
        if isinstance(entry, Provenance):
            return entry
        if isinstance(entry, Mapping):
            try:
                return Provenance(entry["kind"], entry["source"], entry["version"])
            except (KeyError, ValueError):
                return None
    return None


def _unverified(value: object, depth: int = 0) -> list[Provenance]:
    found: list[Provenance] = []
    label = provenance_of(value)
    if label is not None and label.is_unverified:
        found.append(label)
    if depth < _MAX_SCAN_DEPTH:
        if isinstance(value, Mapping):
            for item in value.values():
                found.extend(_unverified(item, depth + 1))
        elif isinstance(value, (list, tuple)):
            for item in value:
                found.extend(_unverified(item, depth + 1))
    return found


def require_real_inputs(*inputs: object, consumer: str, allow_simulated: bool = False) -> None:
    """Refuse simulated or stub input in a decision path.

    Inputs are scanned recursively through mappings, lists and tuples. Input that
    carries no provenance is not judged: absence of a label is not a claim.

    Args:
        *inputs: Plugins, results or parameters the decision depends on.
        consumer: Name of the decision path, used in the message.
        allow_simulated: Pass ``True`` to accept the input knowingly.

    Raises:
        SimulatedInputError: If any input is labelled ``simulated`` or ``stub`` and
            ``allow_simulated`` is not ``True``.
    """
    if allow_simulated:
        return
    found = [label for item in inputs for label in _unverified(item)]
    if found:
        listing = ", ".join(sorted({f"{p.kind} ({p.source})" for p in found}))
        raise SimulatedInputError(
            f"{consumer} refuses {listing}; pass allow_simulated=True to accept it. "
            "Its output will then be labelled kind='simulated'."
        )


def inherit_provenance(result: _T, *inputs: object, source: str, version: str) -> _T:
    """Label a decision's output ``simulated`` when any input was simulated or stub.

    A ``dict`` result becomes a :class:`ProvenancedDict` and a ``list`` result a
    :class:`ProvenancedList`. Any other result type cannot carry a label and is
    returned unchanged, so callers must rely on the enclosing container. The
    result is also returned unchanged when no input carries an unverified label:
    the function never adds a ``computed`` claim on its own.
    """
    found = [label for item in inputs for label in _unverified(item)]
    if not found:
        return result
    upstream = ", ".join(sorted({p.source for p in found}))
    label = Provenance("simulated", f"{source} <- {upstream}", version)
    if isinstance(result, Mapping):
        return cast(_T, ProvenancedDict(result, label))
    if isinstance(result, list):
        return cast(_T, ProvenancedList(result, label))
    return result


__all__ = [
    "UNVERIFIED_KINDS",
    "Provenance",
    "ProvenanceKind",
    "ProvenancedDict",
    "ProvenancedList",
    "SimulatedComponent",
    "SimulatedComponentWarning",
    "SimulatedInputError",
    "inherit_provenance",
    "list_simulated_components",
    "provenance_of",
    "register_simulated_component",
    "require_real_inputs",
    "reset_first_use_warnings",
    "warn_first_use",
]
