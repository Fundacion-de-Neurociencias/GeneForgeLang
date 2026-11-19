from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from geneforgelang.eig.ir import BiologicalPerturbation

SUPPORTED_PERTURBATIONS = (
    "missense",
    "splice",
    "promoter",
    "enhancer",
    "cnv",
    "knockout",
    "overexpression",
)


@dataclass(frozen=True)
class PerturbationSet:
    perturbations: tuple[BiologicalPerturbation, ...] = field(default_factory=tuple)

    @classmethod
    def from_specs(cls, target: str, specs: Iterable[dict[str, Any] | BiologicalPerturbation | str]) -> PerturbationSet:
        return cls(tuple(_coerce_perturbation(target, spec) for spec in specs))

    def add(self, perturbation: BiologicalPerturbation) -> PerturbationSet:
        _validate_kind(perturbation.perturbation_type)
        return PerturbationSet((*self.perturbations, perturbation))

    def by_type(self, perturbation_type: str) -> tuple[BiologicalPerturbation, ...]:
        _validate_kind(perturbation_type)
        return tuple(
            perturbation for perturbation in self.perturbations if perturbation.perturbation_type == perturbation_type
        )

    def to_eig(self) -> tuple[BiologicalPerturbation, ...]:
        return self.perturbations


def missense(target: str, substitution: str) -> BiologicalPerturbation:
    return _build(target, "missense", substitution, {"substitution": substitution})


def splice(target: str, site: str) -> BiologicalPerturbation:
    return _build(target, "splice", site, {"site": site})


def promoter(target: str, change: str) -> BiologicalPerturbation:
    return _build(target, "promoter", change, {"change": change})


def enhancer(target: str, change: str) -> BiologicalPerturbation:
    return _build(target, "enhancer", change, {"change": change})


def cnv(target: str, copy_number: int) -> BiologicalPerturbation:
    return _build(target, "cnv", str(copy_number), {"copy_number": copy_number})


def knockout(target: str) -> BiologicalPerturbation:
    return _build(target, "knockout", "loss of function", {})


def overexpression(target: str, fold_change: float | None = None) -> BiologicalPerturbation:
    parameters: dict[str, Any] = {}
    if fold_change is not None:
        parameters["fold_change"] = fold_change
    return _build(target, "overexpression", "increased expression", parameters)


def _coerce_perturbation(target: str, spec: dict[str, Any] | BiologicalPerturbation | str) -> BiologicalPerturbation:
    if isinstance(spec, BiologicalPerturbation):
        _validate_kind(spec.perturbation_type)
        return spec
    if isinstance(spec, str):
        kind, value = _parse_call(spec)
        return _build(target, kind, value, {"value": value} if value else {})
    kind = str(spec.get("type", ""))
    _validate_kind(kind)
    parameters = dict(spec.get("parameters", {}))
    value = str(spec.get("value", parameters.get("value", kind)))
    return _build(target, kind, value, parameters)


def _parse_call(value: str) -> tuple[str, str]:
    stripped = value.strip()
    if "(" not in stripped:
        _validate_kind(stripped)
        return stripped, ""
    kind, rest = stripped.split("(", 1)
    parsed_value = rest.rsplit(")", 1)[0]
    _validate_kind(kind)
    return kind, parsed_value


def _build(target: str, perturbation_type: str, description: str, parameters: dict[str, Any]) -> BiologicalPerturbation:
    _validate_kind(perturbation_type)
    value = description.replace(" ", "_") or perturbation_type
    return BiologicalPerturbation(
        id=f"perturbation:{target}:{perturbation_type}:{value}",
        target=target,
        perturbation_type=perturbation_type,
        description=f"{perturbation_type}({description})" if description else perturbation_type,
        parameters=parameters,
    )


def _validate_kind(perturbation_type: str) -> None:
    if perturbation_type not in SUPPORTED_PERTURBATIONS:
        supported = ", ".join(SUPPORTED_PERTURBATIONS)
        raise ValueError(f"unsupported perturbation '{perturbation_type}'. Supported: {supported}")
